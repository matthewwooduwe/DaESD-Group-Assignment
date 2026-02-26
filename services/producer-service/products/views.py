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
        files = {key: val.file for key, val in request.FILES.items()}

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
