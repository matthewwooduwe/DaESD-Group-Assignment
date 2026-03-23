# Standup Week 4 - Dina Metwalli
**Date:** 10/03/2026
**Sprint:** [Sprint 2]

## Completed This Week
- revised the basket component to follow the test cases properly by grouping the items by their producers.
- completed the checkout page for customers to put down their collection type be it delivery or collection from producer's address, and the delivery date they would like.
- I also started working on the customer orders by creating a customerorders model for storing the overall order and its status for the customer to view based on the product status log implemented by Leon, and that model will link to the orders model so that it can be split up to go to each producer on their own.
- I did the UI for all of that as well.
- And I reviewed the producer dashboard orders PR by Leon.

## In Progress
- Completing the customer orders model and tying the checkout and basket views to it so the order is recorded in the database and also goes out to its producers.

## Blockers Encountered
- None this week! :D

## Planned for Next Week
- Finish highlevel customer orders implementation.
- Integrate the orders placement with the external Payment process by Amine on returning a successful payment.
- Clearing out the basket once the order has been placed.
---