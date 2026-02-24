# Standup Week 2 - Kaan
**Date:** 24/02/2026
**Sprint:** Sprint 1

---

## Completed This Week
- Reviewed the Platform API codebase and understood the existing structure (users, products, orders, reviews apps)
- Familiarised myself with Django REST Framework patterns used across the project — models, serializers, views, and URL routing
- Implemented the `notifications` app for the Platform API, which was identified as a missing Sprint 1 deliverable
  - Created `Notification` model with 6 notification types: `ORDER_PLACED`, `ORDER_CONFIRMED`, `ORDER_READY`, `ORDER_DELIVERED`, `LOW_STOCK`, `GENERAL`
  - Created `NotificationSerializer` to convert model instances to JSON
  - Built 4 API endpoints:
    - `GET /api/notifications/` — list all notifications for the logged-in user
    - `GET /api/notifications/<id>/` — retrieve a single notification
    - `PATCH /api/notifications/<id>/read/` — mark one notification as read
    - `PATCH /api/notifications/read-all/` — mark all notifications as read
  - Registered the app in `settings.py` and `urls.py`

---

## In Progress
- Running migrations for the new `notifications` table:
  ```bash
  docker-compose exec platform-api python manage.py makemigrations notifications
  docker-compose exec platform-api python manage.py migrate
  ```
- Testing endpoints manually using the existing `test_api.py` script as a reference

---

## Blockers
- No major blockers
- Need to coordinate with the team on when notifications should be automatically triggered (e.g. when an order is created in the orders app, should it call the notifications app to create a record?)

---

## Planned for Next Week (Sprint 2)
- Add automatic notification creation when an order is placed (hook into `orders/views.py`)
- Begin work on the `payments` app — commission tracking (5%) and weekly settlement records
- Add unit tests for the notifications endpoints
