from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser

class StatelessUser:
    """
    A mock user object for stateless authentication.
    """
    def __init__(self, token):
        self.id = token.get('user_id')
        self.is_authenticated = True
        self.is_active = True
        self.token = token


class StatelessJWTAuthentication(JWTAuthentication):
    """
    Validates a JWT but bypasses local database user lookup.
    Used for proxy services that don't maintain their own user tables.
    """
    def get_user(self, validated_token):
        """
        Returns a mock user object based on the token rather than querying the database.
        """
        if 'user_id' not in validated_token:
            return AnonymousUser()
            
        return StatelessUser(validated_token)
