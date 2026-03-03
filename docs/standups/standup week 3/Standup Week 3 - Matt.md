# Week 3 Standup - Matt Wood
**Date:** 03/03/2026
**Sprint:** Sprint 1
**Service:** Frontend Service

## Completed This Week

- Redesigned the frontend UI with a Waitrose-inspired deep forest green colour scheme, warm cream background and terracotta accents — replacing the previous earthy brown palette
- Built a detailed SVG illustration of the Clifton Suspension Bridge as the homepage hero, featuring the Avon Gorge, river, rolling hills and daytime sky
- Improved error handling across all views in `views.py` — added a `_api_error_message()` helper so no raw HTTP status codes are ever shown to users, with specific handling for 403, 500 and 503 responses
- Added `requests.exceptions.RequestException` catch to handle network edge cases (DNS failures, SSL errors) across all views
- Added client-side JavaScript validation to the registration form — blocks emojis and invalid characters across all fields before submission, preventing partial database writes (closes #38)
- Created `FRONTEND.md` — a developer guide covering page creation, template structure, design system tokens, API communication patterns, auth/session handling, environment variables and code standards
- Fixed nav link contrast, removed price block gradient and improved seller name readability on the product detail page following team feedback
- Opened PR #49 covering issues #37, #38, #39 and #40

## In Progress


## Blockers / Help Needed

- None at this time 

## Planned for Next Week

- Implement shopping basket page (issue #18)
- Implement checkout flow (issue #19)
- Collaborate with Kaan on platform API payments and catalogue tasks

## Notes

- The frontend now has a consistent design system documented in `FRONTEND.md` — all team members building frontend pages should refer to this before starting work
- Registration validation fixes the root cause of the error 500 issue when users submitted emojis or non-ASCII characters

---

## Standup Scoring (Self-Assessment)

- [x] **5** - Excellent: Detailed reports, significant progress, proactive
- [ ] **4** - Good: Clear progress, engaged with team
- [ ] **3** - Satisfactory: Basic progress, meeting minimum requirements
- [ ] **2** - Poor: Limited progress, minimal engagement
- [ ] **1** - Minimal: Attended but little contribution

## Commits This Week

- `feat(frontend)`: Redesign UI with Clifton Suspension Bridge hero and green colour scheme - closes #39
- `docs(frontend)`: Add frontend developer guide - closes #40
- `feat(frontend)`: Improve error handling and add registration input validation - closes #37, closes #38
- `fix(frontend)`: Improve nav link contrast, remove price block gradient and fix seller name readability