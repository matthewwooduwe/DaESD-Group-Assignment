import os
import requests
from django.shortcuts import render, redirect

# Base URL of the platform API service — no trailing slash, no /api suffix
PLATFORM_API_URL = os.environ.get('PLATFORM_API_URL', 'http://platform-api:8002')

# Used by the browser to load product images served by the platform service.
MEDIA_BASE_URL = os.environ.get('MEDIA_BASE_URL', 'http://localhost:8002')

def get_auth_headers(request):
    """Helper method to build authorization headers from session token."""
    token = request.session.get('token')
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}

def index(request):
    """
    Product browsing / listing page.
    Fetches products and categories from the platform API, supporting
    server-side filtering by category, organic status, and search term.
    """
    products = []
    categories = []
    error = None

    search = request.GET.get('search', '').strip()
    selected_category = request.GET.get('category', '').strip()
    is_organic = request.GET.get('organic', '')

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

        resp_prod = requests.get(
            f"{PLATFORM_API_URL}/api/products/",
            params=params,
            timeout=5
        )
        if resp_prod.status_code == 200:
            products = resp_prod.json()
        else:
            error = f"Could not load products (status {resp_prod.status_code})."

    except requests.exceptions.ConnectionError:
        error = "Cannot reach the platform API. Is the platform-service running?"
    except requests.exceptions.Timeout:
        error = "The platform API took too long to respond."
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

    return render(request, 'web/index.html', {
        'products': products,
        'categories': categories,
        'error': error,
        'search': search,
        'selected_category': selected_category,
        'is_organic': is_organic,
        'media_base_url': MEDIA_BASE_URL,
    })


def product_detail(request, product_id):
    """
    Individual product detail page.
    Fetches a single product and its reviews from the platform API.
    """
    product = None
    reviews = []
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
            error = f"Could not load product (status {resp.status_code})."

        # Fetch reviews for this product if we found it
        if product:
            resp_rev = requests.get(
                f"{PLATFORM_API_URL}/api/reviews/",
                params={'product': product_id},
                timeout=5
            )
            if resp_rev.status_code == 200:
                reviews = resp_rev.json()

        # Check if item is already in basket
        if request.session.get('token') and product:
            try:
                resp_basket = requests.get(
                    f"{PLATFORM_API_URL}/api/basket/",
                    headers=get_auth_headers(request),
                    timeout=5
                )
                if resp_basket.status_code == 200:
                    basket = resp_basket.json()
                    for item in basket.get('items', []):
                        if item['product']['id'] == product_id:
                            basket_quantity = item['quantity']
                            break
            except:
                pass

    except requests.exceptions.ConnectionError:
        error = "Cannot reach the platform API. Is the platform-service running?"
    except requests.exceptions.Timeout:
        error = "The platform API took too long to respond."
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

    return render(request, 'web/product_detail.html', {
        'product': product,
        'reviews': reviews,
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
                return redirect('/')
            elif resp.status_code == 401:
                error = "Incorrect username or password. Please try again."
            else:
                error = f"Login failed (status {resp.status_code}). Please try again."

        except requests.exceptions.ConnectionError:
            error = "Cannot reach the platform API. Is the platform-service running?"
        except requests.exceptions.Timeout:
            error = "The platform API took too long to respond."
        except Exception as e:
            error = f"Unexpected error: {str(e)}"

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
            form_data['full_name'] = request.POST.get('full_name', '').strip()
            form_data['delivery_address'] = request.POST.get('delivery_address', '').strip()
            form_data['customer_postcode'] = request.POST.get('customer_postcode', '').strip()

            payload = {
                'username': form_data['username'],
                'password': request.POST.get('password', ''),
                'email': form_data['email'],
                'phone_number': form_data['phone_number'],
                'role': 'CUSTOMER',
                'customer_profile': {
                    'full_name': form_data['full_name'],
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
                error = f"Registration failed (status {resp.status_code}). Please try again."

        except requests.exceptions.ConnectionError:
            error = "Cannot reach the platform API. Is the platform-service running?"
        except requests.exceptions.Timeout:
            error = "The platform API took too long to respond."
        except Exception as e:
            error = f"Unexpected error: {str(e)}"

    return render(request, 'web/register.html', {
        'error': error,
        'success': success,
        'form_data': form_data,
    })

def basket_view(request):
    """
    Display the customer's basket with all items.
    """
    basket = None
    error = None

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
        except:
            pass
        
        return render(request, 'web/basket.html', {
            'basket': basket,
            'error': error,
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