from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Notification
from .serializers import NotificationSerializer, CreateNotificationSerializer, UnreadCountSerializer


def verify_service_secret(request):
    secret = request.headers.get('X-Service-Secret', '')
    return secret == settings.SERVICE_SECRET_KEY


class NotificationCreateView(APIView):
    def post(self, request):
        if not verify_service_secret(request):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = CreateNotificationSerializer(data=request.data)
        if serializer.is_valid():
            notification = serializer.save()
            return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationListView(APIView):
    def get(self, request):
        recipient_id = request.query_params.get('recipient_id')
        if not recipient_id:
            return Response({'error': 'recipient_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = Notification.objects.filter(recipient_id=recipient_id)
        if request.query_params.get('unread') == 'true':
            queryset = queryset.filter(is_read=False)
        notification_type = request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        return Response(NotificationSerializer(queryset, many=True).data)


class NotificationDetailView(APIView):
    def _get_notification(self, pk, recipient_id):
        try:
            return Notification.objects.get(pk=pk, recipient_id=recipient_id)
        except Notification.DoesNotExist:
            return None

    def get(self, request, pk):
        recipient_id = request.query_params.get('recipient_id')
        if not recipient_id:
            return Response({'error': 'recipient_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        notification = self._get_notification(pk, recipient_id)
        if not notification:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(NotificationSerializer(notification).data)

    def patch(self, request, pk):
        recipient_id = request.data.get('recipient_id') or request.query_params.get('recipient_id')
        if not recipient_id:
            return Response({'error': 'recipient_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        notification = self._get_notification(pk, recipient_id)
        if not notification:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        notification.is_read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)

    def delete(self, request, pk):
        recipient_id = request.query_params.get('recipient_id')
        if not recipient_id:
            return Response({'error': 'recipient_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        notification = self._get_notification(pk, recipient_id)
        if not notification:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarkAllReadView(APIView):
    def patch(self, request):
        recipient_id = request.data.get('recipient_id')
        if not recipient_id:
            return Response({'error': 'recipient_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        updated = Notification.objects.filter(recipient_id=recipient_id, is_read=False).update(is_read=True)
        return Response({'detail': f'{updated} notification(s) marked as read.'})


class UnreadCountView(APIView):
    def get(self, request):
        recipient_id = request.query_params.get('recipient_id')
        if not recipient_id:
            return Response({'error': 'recipient_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        count = Notification.objects.filter(recipient_id=recipient_id, is_read=False).count()
        return Response(UnreadCountSerializer({'recipient_id': recipient_id, 'unread_count': count}).data)