# Week 4 Standup - Matt Wood
**Date:** 10/03/2026  
**Sprint:** Sprint 2  
**Service:** Frontend Service

## Completed This Week

- Built the admin dashboard (`/admin-dashboard/`) — an admin-only page showing platform-wide stats (total users, products, revenue, commission) with tabbed views for users, products and orders
- Built the user profile page (`/profile/`) — allows all authenticated users to update contact details, profile information (name, address, postcode), change password and delete their account
- Fixed customer profile data not saving to the database on registration — the serializer was only creating a profile row if data was provided; it now always creates one
- Split `full_name` into `first_name` and `last_name` across the `CustomerProfile` model, serializer, registration form, profile page and admin modal — with a corresponding migration (`0007`)
- Added full user editing functionality to the admin dashboard — Edit button per user row opens a pre-filled modal covering account fields and role-appropriate profile fields (Customer/Producer)
- Fixed raw API error messages being exposed to users on the profile page — replaced with friendly human-readable messages
- Resolved merge conflict in `urls.py` when pulling latest main

## In Progress

- PR open for admin dashboard, profile page and profile fixes — awaiting review

## Blockers / Help Needed

- None at this time

## Planned for Next Week

- Implement checkout flow (issue #19)
- Collaborate with Kaan on catalogue and payments tasks

## Notes

- The `CustomerProfile` model change requires teammates to run `docker compose run platform-api python manage.py migrate` after pulling
- Admin dashboard reads from the platform API — dependent on platform API being up

---

## Standup Scoring (Self-Assessment)

- [x] **5** - Excellent: Detailed reports, significant progress, proactive
- [ ] **4** - Good: Clear progress, engaged with team
- [ ] **3** - Satisfactory: Basic progress, meeting minimum requirements
- [ ] **2** - Poor: Limited progress, minimal engagement
- [ ] **1** - Minimal: Attended but little contribution

## Commits This Week

- `feat(frontend)`: Add base functionality for administrator page and user management page
- `feat(frontend)`: Split full_name into first_name and last_name, fix profile saving, add admin user edit modal - closes #34
- `chore`: Merge main into branch, resolve url conflicts
