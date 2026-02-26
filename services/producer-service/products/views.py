import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class ProductProxyView(APIView):
    """
    Proxies product creation requests to the Platform API.
    Specifically designed for producers to add their products.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        platform_url = f"{settings.PLATFORM_API_URL}/api/products/"
        headers = {}
        
        # Forward the Authorization header so platform-service can identify the producer
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            headers['Authorization'] = auth_header

        # Separate data and files for multipart/form-data forwarding
        # request.data contains both form data and potentially files in DRF
        data = request.POST.dict()  # Use POST.dict() for form fields
        files = {key: (val.name, val.file, val.content_type) for key, val in request.FILES.items()}

        try:
            # We don't use 'json=data' when sending files, we use 'data=data, files=files'
            response = requests.post(platform_url, data=data, files=files, headers=headers, timeout=5)
            
            # Forward the response back to the client
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text

            return Response(response_data, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Failed to communicate with Platform API: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class ProductDetailProxyView(APIView):
    """
    Proxies product update and delete requests to the Platform API.
    """
    permission_classes = [IsAuthenticated]

    def _get_headers(self, request):
        headers = {}
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            headers['Authorization'] = auth_header
        return headers

    def get(self, request, pk, *args, **kwargs):
        platform_url = f"{settings.PLATFORM_API_URL}/api/products/{pk}/"
        try:
            response = requests.get(platform_url, headers=self._get_headers(request), timeout=5)
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
            return Response(response_data, status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def put(self, request, pk, *args, **kwargs):
        platform_url = f"{settings.PLATFORM_API_URL}/api/products/{pk}/"
        data = request.POST.dict() if request.POST else request.data
        files = {key: (val.name, val.file, val.content_type) for key, val in request.FILES.items()} if request.FILES else None
        
        try:
            if files:
                response = requests.put(platform_url, data=data, files=files, headers=self._get_headers(request), timeout=5)
            else:
                response = requests.put(platform_url, json=data, headers=self._get_headers(request), timeout=5)
                
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
            return Response(response_data, status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def patch(self, request, pk, *args, **kwargs):
        platform_url = f"{settings.PLATFORM_API_URL}/api/products/{pk}/"
        data = request.POST.dict() if request.POST else request.data
        if 'image' in data and not data['image']:
            data.pop('image', None)
            
        files = {key: (val.name, val.file, val.content_type) for key, val in request.FILES.items()} if request.FILES else None
        
        try:
            if files:
                response = requests.patch(platform_url, data=data, files=files, headers=self._get_headers(request), timeout=5)
            else:
                response = requests.patch(platform_url, json=data, headers=self._get_headers(request), timeout=5)
                
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
            return Response(response_data, status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def delete(self, request, pk, *args, **kwargs):
        platform_url = f"{settings.PLATFORM_API_URL}/api/products/{pk}/"
        try:
            response = requests.delete(platform_url, headers=self._get_headers(request), timeout=5)
            # DELETE usually returns 204 No Content
            if response.status_code == 204:
                return Response(status=status.HTTP_204_NO_CONTENT)
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
            return Response(response_data, status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
