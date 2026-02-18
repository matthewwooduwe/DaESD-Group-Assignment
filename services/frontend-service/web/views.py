from django.shortcuts import render
import requests
import os

PLATFORM_API_URL = os.environ.get('PLATFORM_API_URL', 'http://platform-api:8002/api')

def index(request):
    products = []
    error = None
    try:
        # Ensure we hit the /api/products/ endpoint
        api_url = f"{PLATFORM_API_URL.rstrip('/')}/api/products/"
        response = requests.get(api_url)
        if response.status_code == 200:
            products = response.json()
        else:
            error = f"Error fetching products: {response.status_code}"
    except Exception as e:
        error = f"Could not connect to API: {str(e)}"

    return render(request, 'web/index.html', {
        'products': products, 
        'error': error,
        'api_base_url': 'http://localhost:8002/api' # Client-side URL
    })
