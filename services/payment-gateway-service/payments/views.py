import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import urlencode

try:
    import stripe
except ModuleNotFoundError:
    stripe = None

from django.conf import settings
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Payment


class CheckoutError(Exception):
    """Raised when the incoming order payload is not usable for checkout."""


@csrf_exempt
def create_checkout(request):
    """Create a Stripe-hosted checkout session from an order JSON payload."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    try:
        _require_stripe()
        payload = _parse_request_payload(request)
        session, payment = _create_checkout_session(request=request, payload=payload)
        return JsonResponse(
            {
                'url': session.url,
                'session_id': session.id,
                'payment_id': payment.id,
                'order_id': payment.order_id,
            }
        )
    except CheckoutError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Request body must be valid JSON.'}, status=400)
    except stripe.error.RateLimitError:
        return JsonResponse({'error': 'Stripe rate limit hit'}, status=400)
    except stripe.error.InvalidRequestError as exc:
        return JsonResponse({'error': f'Invalid Stripe request: {exc}'}, status=400)
    except stripe.error.AuthenticationError:
        return JsonResponse({'error': 'Stripe authentication failed'}, status=401)
    except stripe.error.APIConnectionError:
        return JsonResponse({'error': 'Stripe API connection failed'}, status=503)
    except stripe.error.StripeError as exc:
        return JsonResponse({'error': f'Stripe error: {exc}'}, status=400)
    except Exception as exc:
        return JsonResponse({'error': f'Unexpected error: {exc}'}, status=500)


def list_transactions(request):
    """List recent Stripe checkout transactions for admin reporting."""
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    try:
        _require_stripe()
        if not _stripe_is_configured():
            raise CheckoutError('Add your Stripe test keys to the environment before fetching transactions.')

        stripe.api_key = settings.STRIPE_SECRET_KEY
        limit = _coerce_limit(request.GET.get('limit'))

        sessions = stripe.checkout.Session.list(limit=limit)
        session_rows = sessions.get('data', [])
        session_ids = [s.get('id') for s in session_rows if s.get('id')]

        payments_by_session = {
            p.stripe_session_id: p
            for p in Payment.objects.filter(stripe_session_id__in=session_ids)
        }

        transactions = []
        for session in session_rows:
            session_id = session.get('id')
            local_payment = payments_by_session.get(session_id)
            amount_total = session.get('amount_total')
            created_unix = session.get('created')
            metadata = session.get('metadata') or {}

            transactions.append(
                {
                    'session_id': session_id,
                    'order_id': (local_payment.order_id if local_payment else '') or metadata.get('order_id') or '',
                    'customer_email': session.get('customer_email') or '',
                    'amount_total': _format_amount(amount_total),
                    'currency': (session.get('currency') or '').upper(),
                    'payment_status': session.get('payment_status') or 'unknown',
                    'status': local_payment.status if local_payment else '',
                    'created_at': _format_unix(created_unix),
                    'payment_intent': session.get('payment_intent') or '',
                    'url': session.get('url') or '',
                }
            )

        return JsonResponse({'transactions': transactions})
    except CheckoutError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    except stripe.error.AuthenticationError:
        return JsonResponse({'error': 'Stripe authentication failed'}, status=401)
    except stripe.error.APIConnectionError:
        return JsonResponse({'error': 'Stripe API connection failed'}, status=503)
    except stripe.error.StripeError as exc:
        return JsonResponse({'error': f'Stripe error: {exc}'}, status=400)
    except Exception as exc:
        return JsonResponse({'error': f'Unexpected error: {exc}'}, status=500)


def checkout_success(request):
    """Verify Stripe success, then redirect to frontend homepage with a success flag."""
    payment = _get_payment_from_request(request)
    session_id = request.GET.get('session_id')
    message = 'Stripe confirmed the checkout and the payment record has been updated.'
    checkout_paid = False

    if session_id and _stripe_is_configured():
        _require_stripe()
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.InvalidRequestError:
            message = 'Payment completed, but the returned session id was invalid. Check success_url token formatting.'
        else:
            if not payment:
                payment = Payment.objects.filter(stripe_session_id=session_id).first()
            if payment and session.payment_status == 'paid':
                checkout_paid = True
                payment.status = 'SUCCESS'
                payment.stripe_payment_intent = session.payment_intent
                payment.save(update_fields=['status', 'stripe_payment_intent', 'updated_at'])
            elif payment:
                message = 'Checkout returned, but Stripe has not marked this session as paid yet.'

    if checkout_paid and payment:
        return redirect(_frontend_success_redirect_url(payment=payment))

    return render(
        request,
        'payments/result.html',
        {
            'payment': payment,
            'heading': 'Payment successful',
            'message': message,
            'is_success': True,
        },
    )


def checkout_cancel(request):
    """Show a simple cancel page when the hosted checkout is abandoned."""
    payment = _get_payment_from_request(request)
    session_id = request.GET.get('session_id')

    if not payment and session_id:
        payment = Payment.objects.filter(stripe_session_id=session_id).first()
    if payment and payment.status == 'PENDING':
        payment.status = 'CANCELLED'
        payment.save(update_fields=['status', 'updated_at'])

    return render(
        request,
        'payments/result.html',
        {
            'payment': payment,
            'heading': 'Payment cancelled',
            'message': 'The hosted checkout was cancelled before payment completed.',
            'is_success': False,
        },
    )


@csrf_exempt
def webhook(request):
    """Handle Stripe webhook events when a webhook secret is configured."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    if not settings.STRIPE_WEBHOOK_SECRET:
        return JsonResponse({'error': 'STRIPE_WEBHOOK_SECRET is not configured.'}, status=400)

    _require_stripe()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        payment = Payment.objects.filter(stripe_session_id=session['id']).first()
        if payment:
            payment.status = 'SUCCESS'
            payment.stripe_payment_intent = session.get('payment_intent')
            payment.save(update_fields=['status', 'stripe_payment_intent', 'updated_at'])

    if event['type'] == 'checkout.session.expired':
        session = event['data']['object']
        payment = Payment.objects.filter(stripe_session_id=session['id']).first()
        if payment and payment.status == 'PENDING':
            payment.status = 'FAILED'
            payment.save(update_fields=['status', 'updated_at'])

    return JsonResponse({'status': 'received'})


def _parse_request_payload(request):
    if request.content_type and 'application/json' in request.content_type:
        return json.loads(request.body.decode('utf-8') or '{}')
    return {}


def _create_checkout_session(*, request, payload):
    _require_stripe()
    if not _stripe_is_configured():
        raise CheckoutError('Add your Stripe test keys to the environment before starting checkout.')

    checkout_data = _build_checkout_data(payload)

    payment = Payment.objects.create(
        order_id=checkout_data['order_id'],
        amount=checkout_data['amount'],
        currency=checkout_data['currency'],
        status='PENDING',
        request_payload=payload,
    )

    stripe.api_key = settings.STRIPE_SECRET_KEY
    session_kwargs = {
        'mode': 'payment',
        'payment_method_types': ['card'],
        'line_items': checkout_data['line_items'],
        'metadata': {
            'payment_id': str(payment.id),
            'order_id': checkout_data['order_id'],
        },
        'success_url': checkout_data['success_url'] or _default_success_url(request, payment.id),
        'cancel_url': checkout_data['cancel_url'] or _default_cancel_url(request, payment.id),
    }
    if checkout_data['customer_email']:
        session_kwargs['customer_email'] = checkout_data['customer_email']

    session = stripe.checkout.Session.create(**session_kwargs)
    payment.stripe_session_id = session.id
    payment.save(update_fields=['stripe_session_id', 'updated_at'])
    return session, payment


def _build_checkout_data(payload):
    if not isinstance(payload, dict) or not payload:
        raise CheckoutError('Send a JSON object containing the order details.')

    order = payload.get('order') if isinstance(payload.get('order'), dict) else payload
    items = payload.get('items') or order.get('items') or []
    order_id = str(payload.get('order_id') or order.get('order_id') or order.get('id') or '')
    currency = str(payload.get('currency') or order.get('currency') or settings.STRIPE_CURRENCY).lower()
    customer_email = payload.get('customer_email') or order.get('customer_email') or order.get('email')

    if items:
        line_items, amount = _build_line_items(items=items, currency=currency, order_id=order_id)
    else:
        amount = _coerce_decimal(
            payload.get('total_amount') or order.get('total_amount'),
            field_name='total_amount',
        )
        line_items = [
            {
                'price_data': {
                    'currency': currency,
                    'unit_amount': _decimal_to_cents(amount),
                    'product_data': {
                        'name': payload.get('title') or f'Order #{order_id or "payment"}',
                        'description': payload.get('description') or 'Regional Food Network checkout',
                    },
                },
                'quantity': 1,
            }
        ]

    return {
        'amount': amount,
        'currency': currency,
        'customer_email': customer_email,
        'line_items': line_items,
        'order_id': order_id,
        'success_url': payload.get('success_url'),
        'cancel_url': payload.get('cancel_url'),
    }


def _build_line_items(*, items, currency, order_id):
    line_items = []
    total_amount = Decimal('0.00')

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise CheckoutError('Each item in items must be a JSON object.')

        quantity = _coerce_quantity(item.get('quantity', 1))
        unit_price = _coerce_item_price(item)
        product_name = item.get('name') or item.get('product_name') or item.get('title') or f'Order {order_id or ""} item {index}'.strip()

        product_data = {'name': product_name}
        description = item.get('description')
        if description:
            product_data['description'] = description

        image_url = item.get('image_url') or item.get('image')
        if image_url:
            product_data['images'] = [image_url]

        line_items.append(
            {
                'price_data': {
                    'currency': currency,
                    'unit_amount': _decimal_to_cents(unit_price),
                    'product_data': product_data,
                },
                'quantity': quantity,
            }
        )
        total_amount += unit_price * quantity

    if not line_items:
        raise CheckoutError('At least one order item is required.')

    return line_items, total_amount


def _coerce_item_price(item):
    if item.get('unit_amount') not in (None, ''):
        try:
            unit_amount = int(item['unit_amount'])
        except (TypeError, ValueError) as exc:
            raise CheckoutError('unit_amount must be an integer amount in pence.') from exc
        if unit_amount < 1:
            raise CheckoutError('unit_amount must be greater than zero.')
        return (Decimal(unit_amount) / Decimal('100')).quantize(Decimal('0.01'))

    for field_name in ('price_at_sale', 'unit_price', 'price', 'amount'):
        if item.get(field_name) not in (None, ''):
            return _coerce_decimal(item[field_name], field_name=field_name)

    raise CheckoutError('Each order item must include unit_amount or a price field.')


def _coerce_decimal(value, *, field_name):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise CheckoutError(f'{field_name} must be a valid amount.') from exc

    if amount <= 0:
        raise CheckoutError(f'{field_name} must be greater than zero.')
    return amount.quantize(Decimal('0.01'))


def _coerce_quantity(value):
    try:
        quantity = int(value)
    except (TypeError, ValueError) as exc:
        raise CheckoutError('quantity must be a whole number.') from exc

    if quantity < 1:
        raise CheckoutError('quantity must be at least 1.')
    return quantity


def _decimal_to_cents(value):
    return int((value * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def _default_success_url(request, payment_id):
    return (
        f"{request.scheme}://{request.get_host()}{reverse('payments:success')}"
        f"?payment_id={payment_id}&session_id={{CHECKOUT_SESSION_ID}}"
    )


def _default_cancel_url(request, payment_id):
    return (
        f"{request.scheme}://{request.get_host()}{reverse('payments:cancel')}"
        f"?payment_id={payment_id}"
    )


def _frontend_success_redirect_url(*, payment):
    frontend_base = (settings.FRONTEND_URL or 'http://localhost:8000').rstrip('/')
    query = {'payment': 'success'}
    if payment.order_id:
        query['order_id'] = payment.order_id
    return f'{frontend_base}/orders/?{urlencode(query)}'


def _coerce_limit(value):
    default_limit = 50
    max_limit = 100
    if value in (None, ''):
        return default_limit
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default_limit
    if parsed < 1:
        return default_limit
    return min(parsed, max_limit)


def _format_amount(value):
    if value in (None, ''):
        return ''
    return str((Decimal(value) / Decimal('100')).quantize(Decimal('0.01')))


def _format_unix(value):
    if value in (None, ''):
        return ''
    try:
        timestamp = int(value)
    except (TypeError, ValueError):
        return ''
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def _get_payment_from_request(request):
    payment_id = request.GET.get('payment_id')
    if not payment_id:
        return None
    return Payment.objects.filter(pk=payment_id).first()


def _stripe_is_configured():
    secret_key = settings.STRIPE_SECRET_KEY or ''
    return secret_key.startswith('sk_') and 'FILL_ME_IN' not in secret_key


def _require_stripe():
    if stripe is None:
        raise CheckoutError('Stripe is not installed. Install the payment service requirements first.')
