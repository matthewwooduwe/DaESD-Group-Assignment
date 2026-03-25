from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, ProducerPublicSerializer
from products.serializers import ProducerFullProfileSerializer

User = get_user_model()

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class UserRegistrationView(generics.CreateAPIView):
    """
    Handles public user registration.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles authenticated user profile management.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        # Always return the current authenticated user
        return self.request.user

class UserListView(generics.ListAPIView):
    """
    Admin-only endpoint to list all users.
    """
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)

    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')

class UserAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin-only endpoint to manage any user.
    """
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)

    def get_queryset(self):
        return User.objects.all()

class ProducerPublicDetailView(generics.RetrieveAPIView):
    """
    Publicly accessible endpoint to view a producer's business profile.
    """
    serializer_class = ProducerPublicSerializer
    permission_classes = (permissions.AllowAny,)
    
    def get_queryset(self):
        return User.objects.filter(role='PRODUCER')

class ProducerPublicProfileView(generics.RetrieveAPIView):
    """
    Composite endpoint to fetch a producer's full public profile,
    including their products, recipes, and farm stories in one request.
    """
    serializer_class = ProducerFullProfileSerializer
    permission_classes = (permissions.AllowAny,)
    
    def get_queryset(self):
        return User.objects.filter(role='PRODUCER').prefetch_related(
            'products', 'recipes', 'farm_stories'
        ).select_related('producer_profile')
