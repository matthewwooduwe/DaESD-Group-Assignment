# Standup Week 3 - Kaan
**Date:** 03/03/2026
**Sprint:** Sprint 1

---

## Completed This Week
- Identified that my service ownership is the **Notifications API** — a standalone microservice at `services/notifications-service/` on Port 8001, separate from the Platform API
- Audited the existing `notifications-service` codebase and identified all missing components
- Built the full `notifications` app from scratch inside `services/notifications-service/notifications/`
  - Created `Notification` model with 10 notification types: `ORDER_PLACED`, `ORDER_CONFIRMED`, `ORDER_READY`, `ORDER_DELIVERED`, `ORDER_CANCELLED`, `LOW_STOCK`, `OUT_OF_STOCK`, `SURPLUS_DEAL`, `PAYMENT_RECEIVED`, `SETTLEMENT_READY`
  - Used `recipient_id` integer field instead of a ForeignKey — correct pattern for microservices since there is no shared User model across containers
  - Created `NotificationSerializer`, `CreateNotificationSerializer`, and `UnreadCountSerializer`
  - Built 5 API endpoints:
    - `POST /api/notifications/` — create a notification (called by other services, secured by `X-Service-Secret` header)
    - `GET /api/notifications/list/?recipient_id=X` — list all notifications for a user, supports `?unread=true` and `?type=` filters
    - `GET /api/notifications/unread-count/?recipient_id=X` — unread badge count for the frontend
    - `PATCH /api/notifications/read-all/` — mark all notifications as read
    - `GET` / `PATCH` / `DELETE /api/notifications/<id>/` — single notification operations
  - Registered the app in `settings.py` and `urls.py`
- Fixed `settings.py`:
  - Added `rest_framework`, `corsheaders`, `notifications` to `INSTALLED_APPS`
  - Added `corsheaders.middleware.CorsMiddleware` to `MIDDLEWARE`
  - Added `SERVICE_SECRET_KEY` and `PLATFORM_API_URL` config for inter-service communication

---

## In Progress
- Running migrations for the new `notifications` table:
  ```bash
  docker-compose exec notifications-api python manage.py makemigrations notifications
  docker-compose exec notifications-api python manage.py migrate
  ```
- Testing the create endpoint manually using Postman:
  ```
  POST http://localhost:8001/api/notifications/
  Header: X-Service-Secret: change-this-secret-key-for-jwt-tokens
  Body: { "recipient_id": 1, "recipient_role": "PRODUCER", "notification_type": "ORDER_PLACED",
          "title": "New Order Received", "message": "Order #1 placed. Delivery: 2026-03-05." }
  ```

---

## Blockers
- Need to coordinate with Leon and Dina (Platform API) on adding notification calls into `orders/views.py` — when an order is placed or status changes, platform-api should send a `POST` to this service
- Need to confirm `requirements.txt` includes `djangorestframework` and `django-cors-headers`

---

## Planned for Next Week (Sprint 2)
- Coordinate with platform-api team to auto-trigger notifications on order status changes (TC-010)
- Implement low stock threshold notification trigger (TC-023)
- Add surplus deal notification support (TC-019)
- Add unit tests for all 5 endpoints