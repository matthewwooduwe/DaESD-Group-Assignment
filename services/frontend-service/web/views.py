from django.shortcuts import render
import requests
import os

PLATFORM_API_URL = os.environ.get('PLATFORM_API_URL', 'http://platform-api:8002/api')

def index(request):
    """
    Main portal view. Orchestrates server-side fetching of products, reviews, 
    and orders from the Platform API.
    """
    products = []
    orders = []
    reviews = []
    error = None
    
    # Authenticate as admin to fetch protected order data for the status dashboard.
    # NOTE: This is for demonstration purposes in the MVP.
    token = None
    try:
        auth_response = requests.post(f"{PLATFORM_API_URL.rstrip('/')}/api/auth/login/", 
                                      json={'username': 'admin', 'password': 'admin'})
        if auth_response.status_code == 200:
            token = auth_response.json()['access']
    except Exception:
        pass # Silently fail if auth service is unavailable

    try:
        # 1. Fetch Products
        resp_prod = requests.get(f"{PLATFORM_API_URL.rstrip('/')}/api/products/")
        if resp_prod.status_code == 200:
            products = resp_prod.json()
        
        # 2. Fetch Reviews
        resp_rev = requests.get(f"{PLATFORM_API_URL.rstrip('/')}/api/reviews/")
        if resp_rev.status_code == 200:
            reviews = resp_rev.json()

        # 3. Fetch Orders (Protected)
        if token:
            headers = {'Authorization': f'Bearer {token}'}
            resp_ord = requests.get(f"{PLATFORM_API_URL.rstrip('/')}/api/orders/", headers=headers)
            if resp_ord.status_code == 200:
                orders = resp_ord.json()
            else:
                orders = [{'id': 'Error', 'status': f'Failed to fetch orders: {resp_ord.status_code}'}]
        else:
             orders = [{'id': 'Info', 'status': 'Login as admin to see orders'}]

    except Exception as e:
        error = f"Could not connect to API: {str(e)}"

    return render(request, 'web/index.html', {
        'products': products, 
        'orders': orders,
        'reviews': reviews,
        'error': error,
        'api_base_url': 'http://localhost:8002/api'
    })
