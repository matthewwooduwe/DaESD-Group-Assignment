import os
import requests
from django.shortcuts import render

# Base URL of the platform API service — no trailing slash, no /api suffix
PLATFORM_API_URL = os.environ.get('PLATFORM_API_URL', 'http://platform-api:8002')

# Used by the browser to load product images served by the platform service.
# In development this is localhost:8002; in production point to a CDN or shared media host.
MEDIA_BASE_URL = os.environ.get('MEDIA_BASE_URL', 'http://localhost:8002')


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
