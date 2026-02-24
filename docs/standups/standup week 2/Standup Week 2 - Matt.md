# Week 2 Standup - Matt
**Date:** 24th February 2026
**Sprint:** Sprint 1
**Service:** frontend-service

## Completed This Week
- Identified and fixed bug in `frontend-service` where `PLATFORM_API_URL` default was doubling up `/api` in the path, causing broken API calls
- Built product listing page — card grid layout with hero section, search bar, category dropdown and organic filter, wired into platform API filter backends
- Built product detail page — full product info, allergens, harvest/best before dates, stock levels, reviews section and breadcrumb navigation
- Built user authentication flow — login, logout and register pages using platform API JWT endpoints with Django session storage
- Register page dynamically switches between Customer and Producer profile fields based on role selection
- Added shared `base.html` layout with nav, footer and CSS variables used across all pages
- Nav updates to show logged-in username and Sign Out link when authenticated
- Added `MEDIA_BASE_URL` env var for product image loading
- Ran Django migrations on frontend service to create `django_session` table
- Raised PR for team review covering issues #9, #17, #26

## In Progress
- PR `feature/frontend-dev` open and awaiting team review
- Shopping basket and checkout flow (#18, #19) planned for next session

## Blockers / Help Needed
- Waiting on team to onboard and get comfortable with the repo and workflow
- Some learning curve around Git branch workflow and PR process during the week

## Planned for Next Week
- Get `feature/frontend-dev` PR reviewed and merged to main
- Begin shopping basket implementation (#18)
- Begin checkout flow (#19)

## Notes
- Frontend service uses Django session to store JWT token — no changes needed to platform-service
- `docker-compose exec frontend python manage.py migrate` needs to be run once to set up the session table
- Seed data available via `docker-compose exec platform-api python manage.py seed_db`

---

## Standup Scoring (Self-Assessment)
Rate yourself honestly (tutor will provide official score):

- [x] **5** - Excellent: Detailed reports, significant progress, proactive
- [ ] **4** - Good: Clear progress, engaged with team
- [ ] **3** - Satisfactory: Basic progress, meeting minimum requirements
- [ ] **2** - Poor: Limited progress, minimal engagement
- [ ] **1** - Minimal: Attended but little contribution

## Commits This Week
- `1bc3cc4`: fix: correct PLATFORM_API_URL default to remove duplicate /api path
- `c09c857`: feat: add product detail page with reviews - closes #17, closes #26
- `c86062b`: feat: add login, logout and register pages - closes #9

---

**Template Instructions:**
1. Copy this template for each weekly standup
2. Name file: `week-X-yourname.md` (e.g., `week-1-john.md`)
3. Fill out BEFORE standup meeting
4. Keep it concise (2-5 minutes to present)
5. Be honest about blockers - other team members is here to help :-)
