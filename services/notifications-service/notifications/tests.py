
# Create your tests here.

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Notification


class NotificationCreateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_secret = 'change-this-secret-key-for-jwt-tokens'
        self.url = '/api/notifications/'

    def test_create_notification_valid_secret(self):
        response = self.client.post(
            self.url,
            {'user': 1, 'message': 'Test notification', 'type': 'ORDER_PLACED'},
            format='json',
            HTTP_X_SERVICE_SECRET=self.valid_secret
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(), 1)

    def test_create_notification_invalid_secret(self):
        response = self.client.post(
            self.url,
            {'user': 1, 'message': 'Test', 'type': 'ORDER_PLACED'},
            format='json',
            HTTP_X_SERVICE_SECRET='wrongsecret'
        )
        self.assertEqual(response.status_code, 401)

    def test_create_notification_missing_secret(self):
        response = self.client.post(
            self.url,
            {'user': 1, 'message': 'Test', 'type': 'ORDER_PLACED'},
            format='json'
        )
        self.assertEqual(response.status_code, 401)


class NotificationListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        Notification.objects.create(
            recipient_id=1,
            notification_type='ORDER_PLACED',
            message='Test notification',
        )

    def test_list_notifications(self):
        response = self.client.get('/api/notifications/list/?recipient_id=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_notifications_missing_recipient(self):
        response = self.client.get('/api/notifications/list/')
        self.assertEqual(response.status_code, 400)

    def test_list_unread_filter(self):
        response = self.client.get('/api/notifications/list/?recipient_id=1&unread=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class UnreadCountViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        Notification.objects.create(
            recipient_id=1,
            notification_type='ORDER_PLACED',
            message='Test',
        )

    def test_unread_count(self):
        response = self.client.get('/api/notifications/unread-count/?recipient_id=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

    def test_unread_count_missing_recipient(self):
        response = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(response.status_code, 400)


class MarkAllReadViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        Notification.objects.create(
            recipient_id=1,
            notification_type='ORDER_PLACED',
            message='Test',
        )

    def test_mark_all_read(self):
        response = self.client.patch(
            '/api/notifications/read-all/',
            {'recipient_id': 1},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notification.objects.filter(is_read=False).count(), 0)

    def test_mark_all_read_missing_recipient(self):
        response = self.client.patch(
            '/api/notifications/read-all/',
            {},
            format='json'
        )
        self.assertEqual(response.status_code, 400)