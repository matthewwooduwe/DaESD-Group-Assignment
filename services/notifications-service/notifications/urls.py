from django.urls import path
from .views import (
    NotificationCreateView,
    NotificationListView,
    NotificationDetailView,
    MarkAllReadView,
    UnreadCountView,
)

urlpatterns = [
    path('', NotificationCreateView.as_view(), name='notification-create'),
    path('list/', NotificationListView.as_view(), name='notification-list'),
    path('unread-count/', UnreadCountView.as_view(), name='notification-unread-count'),
    path('read-all/', MarkAllReadView.as_view(), name='notification-read-all'),
    path('<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
]