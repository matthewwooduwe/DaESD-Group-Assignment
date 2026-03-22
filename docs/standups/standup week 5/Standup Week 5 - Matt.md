# Week 5 Standup - Matt Wood
**Date:** 17/03/2026  
**Sprint:** Sprint 2  
**Service:** Frontend Service / Platform API

## Completed This Week

- Fixed admin edit modal breaking on special characters — users with apostrophes in their data (e.g. `Bob's Farm`) caused the modal to fail silently; resolved by moving user data into `<script type="application/json">` tags and parsing with `JSON.parse()` instead of inline JavaScript strings
- Fixed `seed_db.py` to use `first_name` and `last_name` instead of `full_name` following the `CustomerProfile` model change from last week
- PR #67 (admin dashboard, profile page, name field fixes) reviewed, approved and merged into main
- Reviewed Leon's PR #68 (surplus deals) — identified conflict with `full_name`/`first_name` model changes, flagged for resolution before merge
- Implemented commission logic (#22) — `commission_total` is now automatically calculated and saved on order creation as 5% of `total_amount`, satisfying TC-012
- Fixed `OrderSerializer` to use `customer_first_name` and `customer_last_name` instead of `customer_full_name` to align with model changes
- Removed duplicate `Product` imports from `orders/serializers.py`
- Verified commission calculation via curl and database inspection — £3.00 order correctly produces `commission_total` of £0.15

## In Progress

- Commission logic PR open on `feat/commission-logic` branch — awaiting review
- Surplus discounts (#56) — next task

## Blockers / Help Needed

- Checkout (#19) still blocked by Amine's payment integration and Dina's multi-vendor order splitting
- Leon's surplus deals PR (#68) needs updating to use `first_name`/`last_name` before it can merge

## Planned for Next Week

- Surplus produce discounts (#56) — platform API and frontend
- Begin checkout flow (#19) if Amine and Dina's work lands

## Notes

- Commission is calculated at two levels: per `OrderItem` (was already working) and per `Order` (fixed this week)
- Team should be aware that `seed_db` requires the updated file after pulling branches based on our model changes

---

## Standup Scoring (Self-Assessment)

- [x] **5** - Excellent: Detailed reports, significant progress, proactive
- [ ] **4** - Good: Clear progress, engaged with team
- [ ] **3** - Satisfactory: Basic progress, meeting minimum requirements
- [ ] **2** - Poor: Limited progress, minimal engagement
- [ ] **1** - Minimal: Attended but little contribution

## Commits This Week

- `fix(admin)`: Fix edit modal breaking on special characters in user data
- `fix(seed)`: Update seed_db to use first_name and last_name instead of full_name
- `feat(orders)`: Calculate and save commission_total on order creation - closes #22
