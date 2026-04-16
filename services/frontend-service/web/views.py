import os
import json
import requests
from datetime import date, timedelta, datetime
from urllib.parse import quote
from django.shortcuts import render, redirect

# Base URL of the platform API service — no trailing slash, no /api suffix
PLATFORM_API_URL = os.environ.get('PLATFORM_API_URL', 'http://platform-api:8002')

# Used by the browser to load product images served by the platform service.
MEDIA_BASE_URL = os.environ.get('MEDIA_BASE_URL', 'http://localhost:8002')
PAYMENT_GATEWAY_URL = os.environ.get('PAYMENT_GATEWAY_URL', 'http://payment-gateway:8003')

# UK 14 Major Allergens
UK_ALLERGENS = [
    'Celery', 'Cereals containing gluten', 'Crustaceans', 'Eggs',
    'Fish', 'Lupin', 'Milk', 'Molluscs', 'Mustard', 'Tree nuts',
    'Peanuts', 'Sesame', 'Soya', 'Sulphur dioxide/sulphites',
]

def get_auth_headers(request):
    """Helper method to build authorization headers from session token."""
    token = request.session.get('token')
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}

def _api_error_message(status_code):
    """
    Returns a user-friendly error message for a given HTTP status code.
    Never exposes the raw status code to the user.
    """
    if status_code == 403:
        return "You do not have permission to access this. Please sign in and try again."
    elif status_code == 404:
        return "The requested resource could not be found."
    elif status_code == 500:
        return "The server encountered an error. Please try again shortly."
    elif status_code == 503:
        return "The service is temporarily unavailable. Please try again in a few moments."
    else:
        return "Something went wrong. Please try again shortly."


AUTH_EXPIRED_ERROR = '__AUTH_EXPIRED__'


def _build_payment_checkout_payload(*, basket, pending_order_reference):
    """
    Build the JSON payload expected by payment-gateway /payments/api/checkout/
    from the current basket snapshot.
    """
    items = []
    basket_items = basket.get('items') or []
    total_amount = basket.get('total_price')

    for basket_item in basket_items:
        product = basket_item.get('product') or {}
        unit_price = product.get('current_price') or product.get('price')
        if unit_price in (None, ''):
            continue

        items.append(
            {
                'product_name': product.get('name') or f"Product {product.get('id', '')}".strip(),
                'description': product.get('description') or '',
                'quantity': basket_item.get('quantity', 1),
                'price_at_sale': str(unit_price),
            }
        )

    payload = {
        'order_id': pending_order_reference,
        'currency': 'gbp',
        'items': items,
    }

    if not items and total_amount not in (None, ''):
        payload['total_amount'] = str(total_amount)
        payload['title'] = f'Order {pending_order_reference}'

    return payload


def _extract_error_from_response(response, default_message):
    try:
        data = response.json()
    except ValueError:
        return default_message

    if isinstance(data, dict):
        return data.get('error') or data.get('detail') or default_message
    return default_message


def _finalize_pending_order(request, *, payment_id, session_id, order_reference):
    pending_checkout = request.session.get('pending_checkout')
    if not isinstance(pending_checkout, dict):
        return None, 'No pending checkout found. Please checkout again.'

    expected_reference = str(pending_checkout.get('order_reference') or '')
    if expected_reference and order_reference and str(order_reference) != expected_reference:
        return None, 'Payment reference mismatch. Please checkout again.'

    finalized_payment_id = str(request.session.get('finalized_payment_id') or '')
    if payment_id and finalized_payment_id == str(payment_id):
        finalized_order_id = request.session.get('finalized_order_id')
        if finalized_order_id:
            return finalized_order_id, None

    if not payment_id or not session_id:
        return None, 'Missing Stripe payment confirmation details.'

    try:
        verify_resp = requests.get(
            f"{PAYMENT_GATEWAY_URL}/payments/api/payment-status/",
            params={'payment_id': payment_id, 'session_id': session_id},
            timeout=10
        )
    except requests.exceptions.ConnectionError:
        return None, 'Cannot reach payment service to verify payment status.'
    except requests.exceptions.Timeout:
        return None, 'Payment verification timed out. Please refresh in a few seconds.'
    except Exception as exc:
        return None, f'Unexpected payment verification error: {str(exc)}'

    if verify_resp.status_code != 200:
        verify_error = _extract_error_from_response(
            verify_resp,
            f'Could not verify payment status (status {verify_resp.status_code}).',
        )
        return None, verify_error

    verify_data = verify_resp.json()
    if verify_data.get('status') != 'SUCCESS':
        return None, 'Payment is not marked as successful yet.'

    try:
        place_resp = requests.post(
            f"{PLATFORM_API_URL}/api/orders/place/",
            headers=get_auth_headers(request),
            json={
                'delivery_dates': pending_checkout.get('delivery_dates', {}),
                'collection_types': pending_checkout.get('collection_types', {}),
            },
            timeout=10
        )
    except requests.exceptions.ConnectionError:
        return None, 'Cannot reach platform API to place the order.'
    except requests.exceptions.Timeout:
        return None, 'Order placement timed out after payment.'
    except Exception as exc:
        return None, f'Unexpected order placement error: {str(exc)}'

    if place_resp.status_code == 201:
        customer_order_id = place_resp.json().get('id')
        request.session['finalized_payment_id'] = str(payment_id)
        request.session['finalized_order_id'] = customer_order_id
        request.session.pop('pending_checkout', None)
        request.session.modified = True
        return customer_order_id, None

    if place_resp.status_code == 401:
        request.session.flush()
        return None, AUTH_EXPIRED_ERROR

    placement_error = _extract_error_from_response(
        place_resp,
        f'Could not place order after payment (status {place_resp.status_code}).',
    )
    return None, placement_error


def index(request):
    """
    Product browsing / listing page.
    Fetches products and categories from the platform API, supporting
    server-side filtering by category, organic status, search term and allergen exclusion.
    """
    products = []
    categories = []
    error = None

    search = request.GET.get('search', '').strip()
    selected_category = request.GET.get('category', '').strip()
    is_organic = request.GET.get('organic', '')
    exclude_allergens = request.GET.getlist('exclude_allergen')

    try:
        # Fetch available categories for the filter dropdown
        resp_cat = requests.get(
            f"{PLATFORM_API_URL}/api/products/categories/",
            timeout=5
        )
        if resp_cat.status_code == 200:
            categories = resp_cat.json()

        # Build query params to pass to the platform API's filter backends
        params = {}
        if search:
            params['search'] = search
        if selected_category:
            params['category__name'] = selected_category
        if is_organic:
            params['is_organic'] = 'true'
        if exclude_allergens:
            params['exclude_allergen'] = exclude_allergens

        resp_prod = requests.get(
            f"{PLATFORM_API_URL}/api/products/",
            params=params,
            timeout=5
        )
        if resp_prod.status_code == 200:
            products = resp_prod.json()
        else:
            error = _api_error_message(resp_prod.status_code)

    except requests.exceptions.ConnectionError:
        error = "Cannot reach the platform API. Please check the service is running."
    except requests.exceptions.Timeout:
        error = "The request took too long to respond. Please try again."
    except requests.exceptions.RequestException:
        error = "A network error occurred. Please try again."
    except Exception:
        error = "An unexpected error occurred. Please try again or contact support if the problem persists."

    return render(request, 'web/index.html', {
        'products': products,
        'categories': categories,
        'error': error,
        'search': search,
        'selected_category': selected_category,
        'is_organic': is_organic,
        'exclude_allergens': exclude_allergens,
        'allergen_list': UK_ALLERGENS,
        'media_base_url': MEDIA_BASE_URL,
    })


def product_detail(request, product_id):
    """
    Individual product detail page.
    Fetches a single product and its reviews from the platform API.
    """
    product = None
    reviews = []
    recipes = []
    error = None

    try:
        resp = requests.get(
            f"{PLATFORM_API_URL}/api/products/{product_id}/",
            timeout=5
        )
        if resp.status_code == 200:
            product = resp.json()
        elif resp.status_code == 404:
            error = "This product could not be found."
        else:
            error = _api_error_message(resp.status_code)

        # Fetch reviews for this product if we found it
        if product:
            resp_rev = requests.get(
                f"{PLATFORM_API_URL}/api/reviews/",
                params={'product': product_id},
                timeout=5
            )
            if resp_rev.status_code == 200:
                reviews = resp_rev.json()
                
            # Fetch linked recipes
            resp_rec = requests.get(
                f"{PLATFORM_API_URL}/api/products/recipes/",
                params={'products__id': product_id},
                timeout=5
            )
            if resp_rec.status_code == 200:
                recipes = resp_rec.json()

    except requests.exceptions.ConnectionError:
        error = "Cannot reach the platform API. Please check the service is running."
    except requests.exceptions.Timeout:
        error = "The request took too long to respond. Please try again."
    except requests.exceptions.RequestException:
        error = "A network error occurred. Please try again."
    except Exception:
        error = "An unexpected error occurred. Please try again or contact support if the problem persists."

    return render(request, 'web/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'recipes': recipes,
        'error': error,
        'media_base_url': MEDIA_BASE_URL,
    })


def login_view(request):
    """
    Login page. POSTs credentials to the platform API JWT endpoint,
    stores the token and username in the Django session on success.
    """
    if request.session.get('token'):
        return redirect('/')

    error = None
    username = ''

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            resp = requests.post(
                f"{PLATFORM_API_URL}/api/auth/login/",
                json={'username': username, 'password': password},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                request.session['token'] = data['access']
                request.session['username'] = username
                
                # Fetch user profile to get the role
                role = 'CUSTOMER' # Default
                try:
                    profile_resp = requests.get(
                        f"{PLATFORM_API_URL}/api/auth/me/",
                        headers={'Authorization': f"Bearer {data['access']}"},
                        timeout=5
                    )
                    if profile_resp.status_code == 200:
                        role = profile_resp.json().get('role', 'CUSTOMER')
                except:
                    pass
                
                request.session['role'] = role
                
                if role == 'PRODUCER':
                    return redirect('/dashboard/')
                return redirect('/')
            elif resp.status_code == 401:
                error = "Incorrect username or password. Please try again."
            else:
                error = _api_error_message(resp.status_code)

        except requests.exceptions.ConnectionError:
            error = "Cannot reach the platform API. Please check the service is running."
        except requests.exceptions.Timeout:
            error = "The request took too long to respond. Please try again."
        except requests.exceptions.RequestException:
            error = "A network error occurred. Please try again."
        except Exception:
            error = "An unexpected error occurred. Please try again or contact support if the problem persists."

    return render(request, 'web/login.html', {
        'error': error,
        'username': username,
    })


def logout_view(request):
    """
    Clears the session and redirects to the homepage.
    """
    request.session.flush()
    return redirect('/')


def register_view(request):
    """
    Registration page. Builds the correct payload for the platform API
    based on the selected role (CUSTOMER or PRODUCER).
    """
    if request.session.get('token'):
        return redirect('/')

    error = None
    success = None
    form_data = {}

    if request.method == 'POST':
        role = request.POST.get('role', 'CUSTOMER')
        form_data = {
            'username': request.POST.get('username', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'phone_number': request.POST.get('phone_number', '').strip(),
            'role': role,
        }

        # Build the nested profile payload based on role
        if role == 'CUSTOMER':
            form_data['first_name'] = request.POST.get('first_name', '').strip()
            form_data['last_name'] = request.POST.get('last_name', '').strip()
            form_data['delivery_address'] = request.POST.get('delivery_address', '').strip()
            form_data['customer_postcode'] = request.POST.get('customer_postcode', '').strip()

            payload = {
                'username': form_data['username'],
                'password': request.POST.get('password', ''),
                'email': form_data['email'],
                'phone_number': form_data['phone_number'],
                'role': 'CUSTOMER',
                'customer_profile': {
                    'first_name': form_data['first_name'],
                    'last_name': form_data['last_name'],
                    'delivery_address': form_data['delivery_address'],
                    'postcode': form_data['customer_postcode'],
                }
            }
        else:
            form_data['business_name'] = request.POST.get('business_name', '').strip()
            form_data['business_address'] = request.POST.get('business_address', '').strip()
            form_data['producer_postcode'] = request.POST.get('producer_postcode', '').strip()
            form_data['bio'] = request.POST.get('bio', '').strip()

            payload = {
                'username': form_data['username'],
                'password': request.POST.get('password', ''),
                'email': form_data['email'],
                'phone_number': form_data['phone_number'],
                'role': 'PRODUCER',
                'producer_profile': {
                    'business_name': form_data['business_name'],
                    'business_address': form_data['business_address'],
                    'postcode': form_data['producer_postcode'],
                    'bio': form_data['bio'],
                }
            }

        try:
            resp = requests.post(
                f"{PLATFORM_API_URL}/api/auth/register/",
                json=payload,
                timeout=5
            )
            if resp.status_code == 201:
                success = "Account created! You can now sign in."
                form_data = {}
            elif resp.status_code == 400:
                # Surface validation errors from the API
                errors = resp.json()
                error = ". ".join(
                    f"{field}: {', '.join(msgs) if isinstance(msgs, list) else msgs}"
                    for field, msgs in errors.items()
                )
            else:
                error = _api_error_message(resp.status_code)

        except requests.exceptions.ConnectionError:
            error = "Cannot reach the platform API. Please check the service is running."
        except requests.exceptions.Timeout:
            error = "The request took too long to respond. Please try again."
        except requests.exceptions.RequestException:
            error = "A network error occurred. Please try again."
        except Exception:
            error = "An unexpected error occurred. Please try again or contact support if the problem persists."

    return render(request, 'web/register.html', {
        'error': error,
        'success': success,
        'form_data': form_data,
    })

def profile_view(request):
    """
    User profile page — view/update details, change password, delete account.
    """
    if not request.session.get('token'):
        return redirect('/login/')

    headers = get_auth_headers(request)
    error = None
    success = None
    user = None

    # Fetch current user data to pre-fill the form
    try:
        resp = requests.get(f"{PLATFORM_API_URL}/api/auth/me/", headers=headers, timeout=5)
        if resp.status_code == 200:
            user = resp.json()
        elif resp.status_code == 401:
            request.session.flush()
            return redirect('/login/')
    except Exception as e:
        error = f"Could not load profile: {str(e)}"

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_details':
            payload = {
                'email': request.POST.get('email', '').strip(),
                'phone_number': request.POST.get('phone_number', '').strip(),
            }
            role = request.session.get('role')
            if role == 'CUSTOMER':
                payload['customer_profile'] = {
                    'first_name': request.POST.get('first_name', '').strip(),
                    'last_name': request.POST.get('last_name', '').strip(),
                    'delivery_address': request.POST.get('delivery_address', '').strip(),
                    'postcode': request.POST.get('postcode', '').strip(),
                }
            elif role == 'PRODUCER':
                payload['producer_profile'] = {
                    'business_name': request.POST.get('business_name', '').strip(),
                    'business_address': request.POST.get('business_address', '').strip(),
                    'postcode': request.POST.get('postcode', '').strip(),
                    'bio': request.POST.get('bio', '').strip(),
                }
            try:
                resp = requests.patch(
                    f"{PLATFORM_API_URL}/api/auth/me/",
                    json=payload,
                    headers=headers,
                    timeout=5
                )
                if resp.status_code == 200:
                    success = "Your details have been updated."
                    user = resp.json()
                else:
                    error = f"Could not update details: {resp.text}"
            except Exception as e:
                error = f"Unexpected error: {str(e)}"

        elif action == 'change_password':
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            if new_password != confirm_password:
                error = "Passwords do not match."
            elif len(new_password) < 8:
                error = "Password must be at least 8 characters."
            else:
                try:
                    resp = requests.patch(
                        f"{PLATFORM_API_URL}/api/auth/me/",
                        json={'password': new_password},
                        headers=headers,
                        timeout=5
                    )
                    if resp.status_code == 200:
                        success = "Password changed successfully."
                    else:
                        error = f"Could not change password: {resp.text}"
                except Exception as e:
                    error = f"Unexpected error: {str(e)}"

        elif action == 'delete_account':
            try:
                resp = requests.delete(
                    f"{PLATFORM_API_URL}/api/auth/me/",
                    headers=headers,
                    timeout=5
                )
                if resp.status_code == 204:
                    request.session.flush()
                    return redirect('/')
                else:
                    error = "Could not delete account. Please try again."
            except Exception as e:
                error = f"Unexpected error: {str(e)}"

    return render(request, 'web/profile.html', {
        'user': user,
        'error': error,
        'success': success,
    })


def admin_dashboard(request):
    """
    Admin dashboard with tabs for users, products, orders, and commission.
    """
    if not request.session.get('token') or request.session.get('role') != 'ADMIN':
        return redirect('/login/')

    headers = get_auth_headers(request)
    users, products, orders = [], [], []
    error = None

    try:
        resp_users = requests.get(f"{PLATFORM_API_URL}/api/auth/users/", headers=headers, timeout=5)
        if resp_users.status_code == 200:
            users = resp_users.json()

        resp_products = requests.get(f"{PLATFORM_API_URL}/api/products/", headers=headers, timeout=5)
        if resp_products.status_code == 200:
            products = resp_products.json()

        resp_orders = requests.get(f"{PLATFORM_API_URL}/api/orders/", headers=headers, timeout=5)
        if resp_orders.status_code == 200:
            orders = resp_orders.json()

    except requests.exceptions.ConnectionError:
        error = "Cannot reach the platform API. Please check the service is running."
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

    total_revenue = sum(float(o.get('total_amount', 0)) for o in orders)
    total_commission = sum(float(o.get('commission_total') or 0) for o in orders)
    total_producer_payout = total_revenue - total_commission
    customers = [u for u in users if u.get('role') == 'CUSTOMER']
    producers = [u for u in users if u.get('role') == 'PRODUCER']

    # Build producer breakdown from all orders
    producer_breakdown = {}
    for o in orders:
        producer = o.get('producer') or o.get('producer_name') or 'Unknown'
        if producer not in producer_breakdown:
            producer_breakdown[producer] = {'producer': producer, 'order_count': 0, 'total_revenue': 0.0, 'total_commission': 0.0, 'total_payout': 0.0}
        rev = float(o.get('total_amount', 0))
        com = float(o.get('commission_total') or 0)
        producer_breakdown[producer]['order_count'] += 1
        producer_breakdown[producer]['total_revenue'] += rev
        producer_breakdown[producer]['total_commission'] += com
        producer_breakdown[producer]['total_payout'] += (rev - com)

    producer_breakdown_list = sorted(producer_breakdown.values(), key=lambda x: x['total_commission'], reverse=True)

    return render(request, 'web/admin.html', {
        'users': users,
        'products': products,
        'all_orders': orders,
        'error': error,
        'total_revenue': total_revenue,
        'total_commission': total_commission,
        'total_producer_payout': total_producer_payout,
        'producer_breakdown': producer_breakdown_list,
        'customer_count': len(customers),
        'producer_count': len(producers),
        'media_base_url': MEDIA_BASE_URL,
    })


def admin_delete_user(request, user_id):
    """Admin-only: delete a user."""
    if not request.session.get('token') or request.session.get('role') != 'ADMIN':
        return redirect('/login/')
    if request.method == 'POST':
        try:
            requests.delete(
                f"{PLATFORM_API_URL}/api/auth/users/{user_id}/",
                headers=get_auth_headers(request),
                timeout=5
            )
        except Exception:
            pass
    return redirect('/admin-dashboard/')


def admin_edit_user(request, user_id):
    """Admin-only: edit a user's details, profile and role."""
    if not request.session.get('token') or request.session.get('role') != 'ADMIN':
        return redirect('/login/')
    if request.method == 'POST':
        role = request.POST.get('role', 'CUSTOMER')
        payload = {
            'username': request.POST.get('username', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'phone_number': request.POST.get('phone_number', '').strip(),
            'role': role,
        }
        if role == 'CUSTOMER':
            payload['customer_profile'] = {
                'first_name': request.POST.get('first_name', '').strip(),
                'last_name': request.POST.get('last_name', '').strip(),
                'delivery_address': request.POST.get('delivery_address', '').strip(),
                'postcode': request.POST.get('postcode', '').strip(),
            }
        elif role == 'PRODUCER':
            payload['producer_profile'] = {
                'business_name': request.POST.get('business_name', '').strip(),
                'business_address': request.POST.get('business_address', '').strip(),
                'postcode': request.POST.get('postcode', '').strip(),
                'bio': request.POST.get('bio', '').strip(),
            }
        try:
            requests.patch(
                f"{PLATFORM_API_URL}/api/auth/users/{user_id}/",
                json=payload,
                headers=get_auth_headers(request),
                timeout=5
            )
        except Exception:
            pass
    return redirect('/admin-dashboard/')


def admin_delete_product(request, product_id):
    """Admin-only: delete any product."""
    if not request.session.get('token') or request.session.get('role') != 'ADMIN':
        return redirect('/login/')
    if request.method == 'POST':
        try:
            requests.delete(
                f"{PLATFORM_API_URL}/api/products/{product_id}/",
                headers=get_auth_headers(request),
                timeout=5
            )
        except Exception:
            pass
    return redirect('/admin-dashboard/')


    """
    Dashboard for producers to manage their products.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')

    products = []
    error = None
    username = request.session.get('username')

    try:
        resp = requests.get(
            f"{PLATFORM_API_URL}/api/products/",
            params={'producer__username': username},
            timeout=5
        )
        if resp.status_code == 200:
            products = resp.json()
        elif resp.status_code == 401:
            request.session.flush()
            return redirect('/login/')
        else:
            error = f"Could not load your products (status {resp.status_code})."
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

    return render(request, 'web/dashboard.html', {
        'products': products,
        'error': error,
        'media_base_url': MEDIA_BASE_URL,
    })

def producer_dashboard(request):
    """
    Dashboard for producers to manage their products.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')

    products = []
    error = None
    username = request.session.get('username')

    try:
        resp = requests.get(
            f"{PLATFORM_API_URL}/api/products/",
            params={'producer__username': username},
            timeout=5
        )
        if resp.status_code == 200:
            products = resp.json()
        elif resp.status_code == 401:
            request.session.flush()
            return redirect('/login/')
        else:
            error = f"Could not load your products (status {resp.status_code})."
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

    return render(request, 'web/dashboard.html', {
        'products': products,
        'error': error,
        'media_base_url': MEDIA_BASE_URL,
    })


def add_product_view(request):
    """
    Form view for adding a new product.
    Submits to the producer-service proxy using the user's token.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')

    categories = []
    error = None
    success = False

    try:
        resp_cat = requests.get(f"{PLATFORM_API_URL}/api/products/categories/", timeout=5)
        if resp_cat.status_code == 200:
            categories = resp_cat.json()
    except Exception:
        pass

    if request.method == 'POST':
        # Prepare the multipart form data using 'requests' library
        # By separating 'data' and 'files'
        form_data = request.POST.dict()
        # Remove csrf token if present
        form_data.pop('csrfmiddlewaretoken', None)
        
        # Handle boolean fields properly
        form_data['is_organic'] = 'is_organic' in request.POST
        # Handle availability status
        availability_status = request.POST.get('availability_status', 'ALWAYS')
        if availability_status == 'OUT_OF_STOCK':
            form_data['is_available'] = False
            form_data.pop('seasonal_start_month', None)
            form_data.pop('seasonal_end_month', None)
            form_data['seasonal_start_month'] = ''
            form_data['seasonal_end_month'] = ''
        elif availability_status == 'IN_SEASON':
            form_data['is_available'] = True
            # Keep seasonal_start_month and seasonal_end_month
        else: # ALWAYS
            form_data['is_available'] = True
            form_data.pop('seasonal_start_month', None)
            form_data.pop('seasonal_end_month', None)
            form_data['seasonal_start_month'] = ''
            form_data['seasonal_end_month'] = ''
        
        for key in ['seasonal_start_month', 'seasonal_end_month', 'harvest_date', 'best_before_date', 'unit', 'allergen_info', 'description']:
            if not form_data.get(key):
                form_data.pop(key, None)

        # Handle allergens as JSON list
        allergens = request.POST.getlist('allergens')
        form_data['allergens'] = json.dumps(allergens)

        # Handle surplus fields
        is_surplus = 'is_surplus' in request.POST
        form_data['is_surplus'] = str(is_surplus).lower()
        if is_surplus:
            surplus_deal = {}
            if form_data.get('discount_percentage'):
                surplus_deal['discount_percentage'] = form_data.pop('discount_percentage')
            if form_data.get('surplus_expiry'):
                surplus_deal['expiry_date'] = form_data.pop('surplus_expiry')
            if form_data.get('surplus_note'):
                surplus_deal['deal_note'] = form_data.pop('surplus_note')
            
            if surplus_deal:
                for k, v in surplus_deal.items():
                    form_data[f'surplus_deal.{k}'] = v
        else:
             # Remove them from form_data so they don't get sent accidentally
             form_data.pop('discount_percentage', None)
             form_data.pop('surplus_expiry', None)
             form_data.pop('surplus_note', None)

        files = {}
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            files['image'] = (image_file.name, image_file.read(), image_file.content_type)

        try:
            resp = requests.post(
                f"{PLATFORM_API_URL}/api/products/",
                headers={'Authorization': f"Bearer {request.session.get('token')}"},
                data=form_data,
                files=files,
                timeout=10
            )
            if resp.status_code == 201:
                return redirect('/dashboard/')
            elif resp.status_code == 401:
                request.session.flush()
                return redirect('/login/')
            else:
                error_msg = resp.text
                try:
                    error_data = resp.json()
                    error_msg = str(error_data)
                except ValueError:
                    pass
                error = f"Failed to create product. Reason: {error_msg}"
        except Exception as e:
            error = f"Error sending data to Producer API: {str(e)}"

    return render(request, 'web/add_product.html', {
        'categories': categories,
        'error': error,
        'success': success,
        'allergen_list': UK_ALLERGENS,
    })

def edit_product_view(request, product_id):
    """
    Form view for editing an existing product.
    Submits to the producer-service proxy using the user's token.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')

    categories = []
    product = None
    error = None

    try:
        resp_cat = requests.get(f"{PLATFORM_API_URL}/api/products/categories/", timeout=5)
        if resp_cat.status_code == 200:
            categories = resp_cat.json()
    except Exception:
        pass

    # Fetch existing product details
    try:
        resp_prod = requests.get(
            f"{PLATFORM_API_URL}/api/products/{product_id}/",
            headers={'Authorization': f"Bearer {request.session.get('token')}"},
            timeout=5
        )
        if resp_prod.status_code == 200:
            product = resp_prod.json()
        elif resp_prod.status_code == 404:
            return redirect('/dashboard/')
        elif resp_prod.status_code == 401:
            request.session.flush()
            return redirect('/login/')
        else:
            error = f"Failed to load product details: {resp_prod.status_code}"
    except Exception as e:
        error = f"Error communicating with API: {str(e)}"

    if request.method == 'POST':
        form_data = request.POST.dict()
        form_data.pop('csrfmiddlewaretoken', None)
        
        # Handle boolean fields properly
        form_data['is_organic'] = 'is_organic' in request.POST
        # Handle availability status
        availability_status = request.POST.get('availability_status', 'ALWAYS')
        if availability_status == 'OUT_OF_STOCK':
            form_data['is_available'] = False
            form_data.pop('seasonal_start_month', None)
            form_data.pop('seasonal_end_month', None)
            form_data['seasonal_start_month'] = ''
            form_data['seasonal_end_month'] = ''
        elif availability_status == 'IN_SEASON':
            form_data['is_available'] = True
            # Keep seasonal_start_month and seasonal_end_month
        else: # ALWAYS
            form_data['is_available'] = True
            form_data.pop('seasonal_start_month', None)
            form_data.pop('seasonal_end_month', None)
            form_data['seasonal_start_month'] = ''
            form_data['seasonal_end_month'] = ''
        
        for key in ['seasonal_start_month', 'seasonal_end_month', 'harvest_date', 'best_before_date', 'unit', 'allergen_info', 'description']:
            if not form_data.get(key):
                form_data.pop(key, None)

        # Handle allergens as JSON list
        allergens = request.POST.getlist('allergens')
        form_data['allergens'] = json.dumps(allergens)

        # Handle surplus fields
        is_surplus = 'is_surplus' in request.POST
        form_data['is_surplus'] = str(is_surplus).lower()
        if is_surplus:
            surplus_deal = {}
            if form_data.get('discount_percentage'):
                surplus_deal['discount_percentage'] = form_data.pop('discount_percentage')
            if form_data.get('surplus_expiry'):
                surplus_deal['expiry_date'] = form_data.pop('surplus_expiry')
            if form_data.get('surplus_note'):
                surplus_deal['deal_note'] = form_data.pop('surplus_note')
            
            if surplus_deal:
                for k, v in surplus_deal.items():
                    form_data[f'surplus_deal.{k}'] = v
        else:
             # Remove them from form_data so they don't get sent accidentally
             form_data.pop('discount_percentage', None)
             form_data.pop('surplus_expiry', None)
             form_data.pop('surplus_note', None)

        files = {}
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            files['image'] = (image_file.name, image_file.read(), image_file.content_type)
        else:
            # Prevent sending an empty string for the image if no file was uploaded
            form_data.pop('image', None)

        try:
            resp = requests.patch(
                f"{PLATFORM_API_URL}/api/products/{product_id}/",
                headers={'Authorization': f"Bearer {request.session.get('token')}"},
                data=form_data,
                files=files if files else None,
                timeout=10
            )
            if resp.status_code == 200:
                return redirect('/dashboard/')
            elif resp.status_code == 401:
                request.session.flush()
                return redirect('/login/')
            else:
                error_msg = resp.text
                try:
                    error_data = resp.json()
                    error_msg = str(error_data)
                except ValueError:
                    pass
                error = f"Failed to update product. Reason: {error_msg}"
        except Exception as e:
            error = f"Error sending data to Producer API: {str(e)}"

    return render(request, 'web/edit_product.html', {
        'categories': categories,
        'product': product,
        'error': error,
        'media_base_url': MEDIA_BASE_URL,
        'allergen_list': UK_ALLERGENS,
    })

def delete_product_view(request, product_id):
    """
    Handles deleting a product. Only accepts POST requests.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')

    if request.method == 'POST':
        try:
            requests.delete(
                f"{PLATFORM_API_URL}/api/products/{product_id}/",
                headers={'Authorization': f"Bearer {request.session.get('token')}"},
                timeout=5
            )
        except Exception:
            pass # Silently fail
            
    return redirect('/dashboard/')

def basket_view(request):
    """
    Display the customer's basket with all items.
    """
    basket = None
    error = None
    items_by_producer = None

    if not request.session.get('token'):
        error = "Please log in to view your basket."
        return render(request, 'web/login.html', {
            'error': error,
        })

    try:
        resp = requests.get(
            f"{PLATFORM_API_URL}/api/basket/",
            headers=get_auth_headers(request),
            timeout=5
        )
        if resp.status_code == 200:
            basket = resp.json()
            items_by_producer = basket.get('items_by_producer')
        elif resp.status_code == 401:
            error = "Your session has expired. Please log in again."
            request.session.flush()
            return render(request, 'web/login.html', {
                'error': error,
            })
        elif resp.status_code == 403:
            error = "Only customers can access baskets."
            return render(request, 'web/index.html', {
                'error': error,
            })
        else:
            error = f"Unexpected error: could not load basket (status {resp.status_code})."

    except requests.exceptions.ConnectionError:
        error = "Cannot reach the platform API. Is the platform-service running?"
    except requests.exceptions.Timeout:
        error = "The platform API took too long to respond."
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

    return render(request, 'web/basket.html', {
        'basket': basket,
        'items_by_producer': items_by_producer,
        'error': error,
        'media_base_url': MEDIA_BASE_URL,
    })


def add_to_basket(request, product_id):
    """
    Add a product to the basket.
    """
    error = None
    success = None

    if not request.session.get('token'):
        error = "Please log in to add items to your basket."
        return render(request, 'web/login.html', {
            'error': error,
        })

    if request.method == 'POST':
        quantity = request.POST.get('quantity', 1)

        try:
            resp = requests.post(
                f"{PLATFORM_API_URL}/api/basket/add/",
                headers=get_auth_headers(request),
                json={'product_id': product_id, 'quantity': int(quantity)},
                timeout=5
            )
            
            if resp.status_code == 200:
                success = "Item successfully added to your basket! Go to your basket from the navigation bar to check it."

                product = None
                reviews = []
                try:
                    resp_prod = requests.get(f"{PLATFORM_API_URL}/api/products/{product_id}/", timeout=5)
                    if resp_prod.status_code == 200:
                        product = resp_prod.json()
                    
                    resp_rev = requests.get(
                        f"{PLATFORM_API_URL}/api/reviews/",
                        params={'product': product_id},
                        timeout=5
                    )
                    if resp_rev.status_code == 200:
                        reviews = resp_rev.json()
                except:
                    pass
                
                return render(request, 'web/product_detail.html', {
                    'product': product,
                    'reviews': reviews,
                    'success': success,
                    'media_base_url': MEDIA_BASE_URL,
                })
                
            elif resp.status_code == 401:
                error = "Your session has expired. Please log in again."
                request.session.flush()
                return render(request, 'web/login.html', {
                    'error': error,
                })
            elif resp.status_code == 403:
                error = "Only customers can add items to basket."
            elif resp.status_code == 400:
                data = resp.json()
                error = data.get('error', 'Could not add item to basket.')
            else:
                error = f"Failed to add item (status {resp.status_code})."

        except requests.exceptions.ConnectionError:
            error = "Cannot reach the platform API. Is the platform-service running?"
        except requests.exceptions.Timeout:
            error = "The platform API took too long to respond."
        except Exception as e:
            error = f"Unexpected error: {str(e)}"

    # Re-render the detail page if there was an error
    if error:
        product = None
        reviews = []
        try:
            resp = requests.get(f"{PLATFORM_API_URL}/api/products/{product_id}/", timeout=5)
            if resp.status_code == 200:
                product = resp.json()
            
            resp_rev = requests.get(
                f"{PLATFORM_API_URL}/api/reviews/",
                params={'product': product_id},
                timeout=5
            )
            if resp_rev.status_code == 200:
                reviews = resp_rev.json()
        except:
            pass
        
        return render(request, 'web/product_detail.html', {
            'product': product,
            'reviews': reviews,
            'error': error,
            'media_base_url': MEDIA_BASE_URL,
        })
    
    return redirect(f'/products/{product_id}/')


def update_basket_item(request, item_id):
    """
    Update the quantity of a basket item.
    """
    error = None

    if not request.session.get('token'):
        error = "Please log in to view your basket."
        return render(request, 'web/login.html', {
            'error': error,
        })

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        action = request.POST.get('action')
        
        # Calculate new quantity based on the user action
        if action == 'increase':
            new_quantity = quantity + 1
        elif action == 'decrease':
            new_quantity = quantity - 1
        else:
            new_quantity = quantity

        try:
            resp = requests.patch(
                f"{PLATFORM_API_URL}/api/basket/items/{item_id}/",
                headers=get_auth_headers(request),
                json={'quantity': new_quantity},
                timeout=5
            )
            if resp.status_code == 200:
                return redirect('/basket/')
            elif resp.status_code == 400:
                data = resp.json()
                error = data.get('error', 'Could not update item.')
            else:
                error = f"Failed to update item (status {resp.status_code})."

        except requests.exceptions.ConnectionError:
            error = "Cannot reach the platform API. Is the platform-service running?"
        except requests.exceptions.Timeout:
            error = "The platform API took too long to respond."
        except Exception as e:
            error = f"Unexpected error: {str(e)}"

    # Re-fetch basket and display page if there was an error
    if error:
        basket = None
        try:
            resp = requests.get(
                f"{PLATFORM_API_URL}/api/basket/",
                headers=get_auth_headers(request),
                timeout=5
            )
            if resp.status_code == 200:
                basket = resp.json()
                items_by_producer = basket.get('items_by_producer', [])
        except:
            pass
        
        return render(request, 'web/basket.html', {
            'basket': basket,
            'error': error,
            'items_by_producer': items_by_producer,
            'media_base_url': MEDIA_BASE_URL,
        })
    
    return redirect('/basket/')


def remove_from_basket(request, item_id):
    """
    Remove an item from the basket.
    """
    error = None

    if not request.session.get('token'):
        error = "Please log in to view your basket."
        return render(request, 'web/login.html', {
            'error': error,
        })

    if request.method == 'POST':
        try:
            resp = requests.delete(
                f"{PLATFORM_API_URL}/api/basket/items/{item_id}/remove/",
                headers=get_auth_headers(request),
                timeout=5
            )
            if resp.status_code == 200:
                return redirect('/basket/')
            else:
                error = "Could not remove item."

        except requests.exceptions.ConnectionError:
            error = "Cannot reach the platform API. Is the platform-service running?"
        except requests.exceptions.Timeout:
            error = "The platform API took too long to respond."
        except Exception as e:
            error = f"Unexpected error: {str(e)}"

    # Re-fetch basket and display page if there was an error
    if error:
        basket = None
        try:
            resp = requests.get(
                f"{PLATFORM_API_URL}/api/basket/",
                headers=get_auth_headers(request),
                timeout=5
            )
            if resp.status_code == 200:
                basket = resp.json()
        except:
            pass
        
        return render(request, 'web/basket.html', {
            'basket': basket,
            'error': error,
            'media_base_url': MEDIA_BASE_URL,
        })
    
    return redirect('/basket/')

def clear_basket(request):
    """
    Remove an item from the basket.
    """
    success = None
    error = None
    basket = None

    if not request.session.get('token'):
        error = "Please log in to view your basket."
        return render(request, 'web/login.html', {
            'error': error,
        })

    if request.method == 'POST':
        try:
            resp = requests.delete(
                f"{PLATFORM_API_URL}/api/basket/clear/",
                headers=get_auth_headers(request),
                timeout=5
            )

            resp_basket = requests.get(f"{PLATFORM_API_URL}/api/basket/", timeout=5)
            if resp_basket.status_code == 200:
                basket = resp_basket.json()
            
            if resp.status_code == 200:
                success = "Successfully cleared all items from your basket!"
                return render(request, 'web/basket.html', {
                    'basket' : basket,
                    'success': success,
                    'media_base_url': MEDIA_BASE_URL,
                })
            else:
                error = "Could not clear basket."

        except requests.exceptions.ConnectionError:
            error = "Cannot reach the platform API. Is the platform-service running?"
        except requests.exceptions.Timeout:
            error = "The platform API took too long to respond."
        except Exception as e:
            error = f"Unexpected error: {str(e)}"

    # Re-fetch basket and display page if there was an error
    if error:
        basket = None
        try:
            resp = requests.get(
                f"{PLATFORM_API_URL}/api/basket/",
                headers=get_auth_headers(request),
                timeout=5
            )
            if resp.status_code == 200:
                basket = resp.json()
        except:
            pass
        
        return render(request, 'web/basket.html', {
            'basket': basket,
            'error': error,
            'media_base_url': MEDIA_BASE_URL,
        })
    
    return redirect('/basket/')

def checkout_view(request):
    """
    Display the customer's basket with all items.
    """
    basket = None
    error = request.GET.get('error')
    items_by_producer = None
    minimum_delivery_date = (date.today() + timedelta(days=2)).isoformat()

    if not request.session.get('token'):
        error = "Please log in to checkout."
        return render(request, 'web/login.html', {
            'error': error,
        })

    try:
        resp = requests.get(
            f"{PLATFORM_API_URL}/api/basket/",
            headers=get_auth_headers(request),
            timeout=5
        )
        if resp.status_code == 200:
            basket = resp.json()
            items_by_producer = basket.get('items_by_producer')
        
        elif resp.status_code == 401:
            error = "Your session has expired. Please log in again."
            request.session.flush()
            return render(request, 'web/login.html', {
                'error': error,
            })
        else:
            error = f"Unexpected error: could not load checkout page (status {resp.status_code})."

    except requests.exceptions.ConnectionError:
        error = "Cannot reach the platform API. Is the platform-service running?"
    except requests.exceptions.Timeout:
        error = "The platform API took too long to respond."
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

    return render(request, 'web/checkout.html', {
        'basket': basket,
        'items_by_producer': items_by_producer,
        'minimum_delivery_date': minimum_delivery_date,
        'error': error,
        'media_base_url': MEDIA_BASE_URL,
    })

def create_order(request):
    """
    Starts Stripe checkout and postpones platform order creation until payment success.
    """
    if not request.session.get('token'):
        error = "Please log in to place an order."
        return render(request, 'web/login.html', {
            'error': error,
        })
    
    if request.method != 'POST':
        return redirect('/basket/checkout/')

    error = None
    delivery_dates = {}
    collection_types = {}

    for key, value in request.POST.items():
        if key.startswith('delivery_date_'):
            producer_id = key.replace('delivery_date_', '')
            delivery_dates[producer_id] = value
        elif key.startswith('collection_type_'):
            producer_id = key.replace('collection_type_', '')
            collection_types[producer_id] = value

    try:
        basket_resp = requests.get(
            f"{PLATFORM_API_URL}/api/basket/",
            headers=get_auth_headers(request),
            timeout=10
        )
    except requests.exceptions.ConnectionError:
        error = "Cannot reach the platform API. Is the platform-service running?"
        return redirect(f'/basket/checkout/?error={quote(error)}')
    except requests.exceptions.Timeout:
        error = "The platform API took too long to respond."
        return redirect(f'/basket/checkout/?error={quote(error)}')
    except Exception as e:
        error = f"Unexpected error: {str(e)}"
        return redirect(f'/basket/checkout/?error={quote(error)}')

    if basket_resp.status_code == 401:
        error = "Your session has expired. Please log in again."
        request.session.flush()
        return render(request, 'web/login.html', {
            'error': error,
        })

    if basket_resp.status_code != 200:
        error = f"Could not load basket for checkout (status {basket_resp.status_code})."
        return redirect(f'/basket/checkout/?error={quote(error)}')

    basket = basket_resp.json()
    if not basket.get('items'):
        error = "Your basket is empty."
        return redirect(f'/basket/checkout/?error={quote(error)}')

    pending_order_reference = (
        f"pending-{request.session.get('username', 'customer')}-{int(datetime.utcnow().timestamp())}"
    )
    request.session['pending_checkout'] = {
        'delivery_dates': delivery_dates,
        'collection_types': collection_types,
        'order_reference': pending_order_reference,
    }
    request.session.pop('finalized_payment_id', None)
    request.session.pop('finalized_order_id', None)
    request.session.modified = True

    checkout_payload = _build_payment_checkout_payload(
        basket=basket,
        pending_order_reference=pending_order_reference,
    )

    try:
        checkout_resp = requests.post(
            f"{PAYMENT_GATEWAY_URL}/payments/api/checkout/",
            json=checkout_payload,
            timeout=10
        )
    except requests.exceptions.ConnectionError:
        error = "Cannot reach payment service."
        return redirect(f'/basket/checkout/?error={quote(error)}')
    except requests.exceptions.Timeout:
        error = "Payment service timed out."
        return redirect(f'/basket/checkout/?error={quote(error)}')
    except Exception as e:
        error = f"Unexpected payment error: {str(e)}"
        return redirect(f'/basket/checkout/?error={quote(error)}')

    if checkout_resp.status_code == 200:
        checkout_url = checkout_resp.json().get('url')
        if checkout_url:
            return redirect(checkout_url)
        error = "Stripe checkout did not return a redirect URL."
        return redirect(f'/basket/checkout/?error={quote(error)}')

    gateway_error = _extract_error_from_response(
        checkout_resp,
        "Could not start Stripe checkout.",
    )
    error = f"Payment could not start. {gateway_error}"
    return redirect(f'/basket/checkout/?error={quote(error)}')

def customer_order_history_view(request):
    if not request.session.get('token'):
        error = "Please log in to place an order."
        return render(request, 'web/login.html', {
            'error': error,
        })

    orders = None
    success = None
    error = request.GET.get('error')
    payment_status = request.GET.get('payment')
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    session_id = request.GET.get('session_id')

    if payment_status == 'success':
        pending_checkout = request.session.get('pending_checkout')
        if pending_checkout:
            finalized_order_id, finalize_error = _finalize_pending_order(
                request,
                payment_id=payment_id,
                session_id=session_id,
                order_reference=order_id,
            )
            if finalize_error == AUTH_EXPIRED_ERROR:
                return redirect('/login/')
            if finalized_order_id:
                return redirect(f'/orders/customer/{finalized_order_id}/?payment=success')
            if finalize_error:
                error = finalize_error
            else:
                success = "Payment successful."
        elif order_id and str(order_id).isdigit():
            return redirect(f'/orders/customer/{order_id}/?payment=success')
        else:
            success = "Payment successful."
    elif payment_status == 'cancelled':
        error = "Payment was cancelled. Your basket is unchanged."
    elif payment_status == 'error':
        error = "Payment did not complete."

    try:
        resp = requests.get(
            f"{PLATFORM_API_URL}/api/orders/customer-orders/",
            headers=get_auth_headers(request),
            timeout=5
        )
        if resp.status_code == 200:
            orders = resp.json()
        
        elif resp.status_code == 401:
            request.session.flush()
            return redirect('/login/')
        
        else:
            error = f"Could not load orders (status {resp.status_code})."
    
    except requests.exceptions.ConnectionError:
        error = "Cannot reach the platform API."
    except requests.exceptions.Timeout:
        error = "Request timed out."
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

    return render(request, 'web/customer_order_history.html', {
        'orders': orders,
        'success': success,
        'error': error,
    })

def write_review_view(request, product_id):
    """
    Allow a customer to write a review for a purchased product from a delivered order.
    """
    token = request.session.get('token')
    if not token:
        # Redirect or show error, but we return a general response
        return redirect('login')

    headers = {'Authorization': f'Bearer {token}'}
    platform_api_url = PLATFORM_API_URL

    success = request.GET.get('success')
    error = request.GET.get('error')

    # GET: Form display with product info
    if request.method == 'GET':
        # Fetch the product details to display on the review page
        prod_resp = requests.get(f"{platform_api_url}/api/products/{product_id}/", headers=headers)
        
        if prod_resp.status_code == 200:
            product = prod_resp.json()
        else:
            return redirect(f"/orders/?error=Could not fetch product details.")

        return render(request, 'web/write_review.html', {
            'product': product,
            'media_base_url': platform_api_url,
            'success': success,
            'error': error
        })
        
    # POST: Submit review data
    elif request.method == 'POST':
        # Collect post data
        rating = request.POST.get('rating')
        title = request.POST.get('title', '')
        comment = request.POST.get('comment', '')
        is_anonymous = request.POST.get('is_anonymous') == 'true'

        payload = {
            'product': product_id,
            'rating': rating,
            'title': title,
            'comment': comment,
            'is_anonymous': is_anonymous
        }

        # Send POST to Platform Service Review endpoint
        review_resp = requests.post(f"{platform_api_url}/api/reviews/", json=payload, headers=headers)
        
        if review_resp.status_code == 201:
            # Redirect to the product detail page for the given product
            return redirect(f"/products/{product_id}/?success=Your review has been submitted successfully!")
        else:
            try:
                err_data = review_resp.json()
                if isinstance(err_data, list) and len(err_data) > 0:
                    err_msg = err_data[0]
                elif 'non_field_errors' in err_data:
                    err_msg = err_data['non_field_errors'][0]
                else:
                    # Generic dictionary error handling
                    if isinstance(err_data, dict):
                        err_msg = next(iter(err_data.values()))[0] if err_data else "Unknown error"
                    else:
                        err_msg = str(err_data)
            except:
                err_msg = "Could not submit your review. Please try again."

            return redirect(f"/reviews/create/{product_id}/?error=Review error: {err_msg}")

def delete_review_view(request, review_id):
    """
    Allow a customer to delete their previously submitted review.
    """
    headers = get_auth_headers(request)
    if not headers:
        return redirect('login')
    
    product_id = request.POST.get('product_id')
    
    resp = requests.delete(f"{PLATFORM_API_URL}/api/reviews/{review_id}/", headers=headers)
    
    if resp.status_code == 204:
        msg = "Your review has been deleted."
        return redirect(f"/products/{product_id}/?success={msg}") if product_id else redirect('customer-orders')
    else:
        err_msg = "Could not delete review."
        return redirect(f"/products/{product_id}/?error={err_msg}") if product_id else redirect('customer-orders')

def customer_order_detail_view(request, order_id):
    """
    Displays order confirmation and details to the customer after checkout.
    """
    if not request.session.get('token'):
        error = "Please log in to place an order."
        return render(request, 'web/login.html', {
            'error': error,
        })

    order = None
    payment_error = request.GET.get('payment_error')
    payment_status = request.GET.get('payment')
    success = "Payment successful." if payment_status == 'success' else None
    error = None

    try:
        resp = requests.get(
            f"{PLATFORM_API_URL}/api/orders/customer-orders/{order_id}/",
            headers=get_auth_headers(request),
            timeout=5
        )
        
        if resp.status_code == 200:
            order = resp.json()
        elif resp.status_code == 404:
            error = "Order not found."
        elif resp.status_code == 401:
            error = "Your session has expired. Please log in again."
            request.session.flush()
            return redirect('/login/')
        else:
            error = f"Could not load order (status {resp.status_code})."

    except requests.exceptions.ConnectionError:
        error = "Cannot reach the platform API."
    except requests.exceptions.Timeout:
        error = "Request timed out."
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

    return render(request, 'web/customer_order_detail.html', {
        'order': order,
        'payment_error': payment_error,
        'success': success,
        'error': error,
    })

def producer_orders_view(request):
    """
    Dashboard section for producers to view incoming orders.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')

    orders = []
    error = None

    try:
        resp = requests.get(
            f"{PLATFORM_API_URL}/api/orders/",
            headers=get_auth_headers(request),
            timeout=5
        )
        if resp.status_code == 200:
            orders = resp.json()
        elif resp.status_code == 401:
            request.session.flush()
            return redirect('/login/')
        else:
            error = f"Could not load your orders (status {resp.status_code})."
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

    return render(request, 'web/producer_orders.html', {
        'orders': orders,
        'error': error,
    })

def producer_order_detail_view(request, order_id):
    """
    Dashboard section for producers to view details of a specific incoming order.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')

    order = None
    error = request.GET.get('error')

    try:
        resp = requests.get(
            f"{PLATFORM_API_URL}/api/orders/{order_id}/",
            headers=get_auth_headers(request),
            timeout=5
        )
        if resp.status_code == 200:
            order = resp.json()
        elif resp.status_code == 404:
            return redirect('/dashboard/orders/')
        elif resp.status_code == 401:
            request.session.flush()
            return redirect('/login/')
        else:
            error = f"Failed to load order details (status {resp.status_code})."
    except Exception as e:
        error = f"Error communicating with API: {str(e)}"

    return render(request, 'web/producer_order_detail.html', {
        'order': order,
        'error': error,
    })

def producer_update_order_status_view(request, order_id):
    """
    Handle POST request to update an order's status and add a note.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')

    if request.method == 'POST':
        status_val = request.POST.get('status')
        note = request.POST.get('note', '')

        try:
            resp = requests.patch(
                f"{PLATFORM_API_URL}/api/orders/{order_id}/status/",
                headers=get_auth_headers(request),
                json={'status': status_val, 'note': note},
                timeout=5
            )
            
            if resp.status_code == 401:
                request.session.flush()
                return redirect('/login/')
            elif resp.status_code != 200:
                try:
                    error_msg = resp.json().get('error', 'Update failed.')
                except:
                    error_msg = "Unknown error occurred."
                from urllib.parse import quote_plus
                return redirect(f'/dashboard/orders/{order_id}/?error={quote_plus(error_msg)}')

        except Exception as e:
            from urllib.parse import quote_plus
            return redirect(f'/dashboard/orders/{order_id}/?error={quote_plus(str(e))}')

    return redirect(f'/dashboard/orders/{order_id}/')

def producer_content_dashboard(request):
    """
    Dashboard for producers to manage their recipes and farm stories.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')
    
    recipes, stories = [], []
    error = None
    username = request.session.get('username')
    
    try:
        resp_r = requests.get(f"{PLATFORM_API_URL}/api/products/recipes/", params={'producer__username': username}, timeout=5)
        if resp_r.status_code == 200:
            recipes = resp_r.json()
            
        resp_s = requests.get(f"{PLATFORM_API_URL}/api/products/farm-stories/", params={'producer__username': username}, timeout=5)
        if resp_s.status_code == 200:
            stories = resp_s.json()
    except Exception as e:
        error = f"Could not load content: {str(e)}"
        
    return render(request, 'web/content_dashboard.html', {
        'recipes': recipes,
        'stories': stories,
        'error': error,
        'media_base_url': MEDIA_BASE_URL
    })

def add_recipe_view(request):
    """
    Form view for adding a new recipe.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')
        
    error = None
    products = []
    
    try:
        resp_p = requests.get(f"{PLATFORM_API_URL}/api/products/", params={'producer__username': request.session.get('username')}, timeout=5)
        if resp_p.status_code == 200:
            products = resp_p.json()
    except:
        pass
        
    if request.method == 'POST':
        form_data = request.POST.dict()
        form_data.pop('csrfmiddlewaretoken', None)
        
        files = {}
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            files['image'] = (image_file.name, image_file.read(), image_file.content_type)
            
        selected_products = request.POST.getlist('products')
        
        data_tuples = []
        for k, v in form_data.items():
            if k != 'products':
                data_tuples.append((k, v))
                
        for pid in selected_products:
            data_tuples.append(('products', pid))
            
        try:
            resp = requests.post(
                f"{PLATFORM_API_URL}/api/products/recipes/",
                headers={'Authorization': f"Bearer {request.session.get('token')}"},
                data=data_tuples,
                files=files if files else None,
                timeout=10
            )
            if resp.status_code == 201:
                return redirect('/dashboard/content/')
            else:
                error = f"Failed to create recipe: {resp.text}"
        except Exception as e:
            error = f"Error: {str(e)}"
            
    return render(request, 'web/add_recipe.html', {
        'products': products,
        'error': error
    })

def add_farm_story_view(request):
    """
    Form view for adding a new farm story.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')
        
    error = None
    
    if request.method == 'POST':
        form_data = request.POST.dict()
        form_data.pop('csrfmiddlewaretoken', None)
        
        files = {}
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            files['image'] = (image_file.name, image_file.read(), image_file.content_type)
            
        try:
            resp = requests.post(
                f"{PLATFORM_API_URL}/api/products/farm-stories/",
                headers={'Authorization': f"Bearer {request.session.get('token')}"},
                data=form_data,
                files=files if files else None,
                timeout=10
            )
            if resp.status_code == 201:
                return redirect('/dashboard/content/')
            else:
                error = f"Failed to create story: {resp.text}"
        except Exception as e:
            error = f"Error: {str(e)}"
            
    return render(request, 'web/add_farm_story.html', {
        'error': error
    })

def producer_public_profile(request, producer_id):
    """
    Public profile for a producer showing their products, recipes, and stories.
    Uses the composite platform-api endpoint to fetch all data in one request.
    """
    profile_data = {}
    error = None
    
    try:
        # Fetch the composite profile data (batch request)
        resp = requests.get(f"{PLATFORM_API_URL}/api/auth/public-producers/{producer_id}/profile/", timeout=5)
        if resp.status_code == 200:
            profile_data = resp.json()
        elif resp.status_code == 404:
            error = "Producer not found."
        else:
            error = f"Error fetching producer profile (Status {resp.status_code})."
    except Exception as e:
        error = f"Error communicating with API: {str(e)}"
    
    # Map the nested data to template context variables
    return render(request, 'web/producer_public_profile.html', {
        'producer': profile_data, # Contains basic info and producer_profile nested
        'products': profile_data.get('products', []),
        'recipes': profile_data.get('recipes', []),
        'stories': profile_data.get('farm_stories', []),
        'error': error,
        'media_base_url': MEDIA_BASE_URL
    })

def delete_recipe_view(request, recipe_id):
    """
    Delete a recipe.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')
        
    try:
        resp = requests.delete(
            f"{PLATFORM_API_URL}/api/products/recipes/{recipe_id}/",
            headers={'Authorization': f"Bearer {request.session.get('token')}"},
            timeout=5
        )
    except:
        pass
        
    return redirect('/dashboard/content/')

def delete_farm_story_view(request, story_id):
    """
    Delete a farm story.
    """
    if not request.session.get('token') or request.session.get('role') != 'PRODUCER':
        return redirect('/login/')
        
    try:
        resp = requests.delete(
            f"{PLATFORM_API_URL}/api/products/farm-stories/{story_id}/",
            headers={'Authorization': f"Bearer {request.session.get('token')}"},
            timeout=5
        )
    except:
        pass
        
    return redirect('/dashboard/content/')

def custom_404(request, exception=None):
    """Custom 404 page."""
    return render(request, 'web/404.html', status=404)
