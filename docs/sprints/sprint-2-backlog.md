# Sprint 2 Backlog
**Duration:** Weeks 7-9 of Term 2  
**Status:** In Progress  
**Goals:** Expand on basic functionalities developed in Sprint 1, integrate all developed features together, complete basic order processing, and address high priority test cases.

### Sprint 2 Highlevel Objectives
1. Assign development tasks in the Product Backlog (Kanban) based on the high priority (and remaining critical) test cases.
2. Expand on developed Producer functionalities (surplus discounts, seasonal availability, settlements..)
3. Expand on developed Customer functionalities (order placement for multi-vendor and single-vendor orders, order history, reordering from history..)
4. Integrate developed components with eachother to show a clear process flow of:
    - producer creates account → logs in → adds a product listing
    - customer creates account → logs in → views that product's listing → adds it to their basket → views order summary and clicks checkout → payment is processed through external mock → success message with recepit is returned and order is placed.
5. Add a user profile page with the options to view and update user account details.

## Sprint 2 Tasks Breakdown

## Week 1: Independent Development

#### Assigned To: Matt Wood
- [x] Create a user profile's view page with functionality to:
    - modify email, phone number, full name, delivery address, and postcode.
    - change password.
    - delete user account.

#### Assigned to: Amine Ziani
- [] finish integration between customer checkout button and external payment processing
    - add fields for delivery address, delivery type, and payment receipt review before proceeding with payment

#### Assigned To: Dina Metwalli
- [] Complete single-vendor and multi-vendor order placement
    - [] when a customer checks out with items from different producers in their baskets, the order model should keep clear records of the producer, creating separate orders for each with the correct payment assigned.
    - [] if multiple items are under a single producer, they should all be placed in the same order.
    - [] if the basket contains items only from one producer, it should ignore splitting orders and place it all under one order.

#### Assigned To: Leon Stansfield
- [] Develop an order view for producers
    - [] producers should see a highlevel view of incoming orders including a timestamp of when they were placed.
    - [] producers should be able to click on each order to view its details, including order number, the products, each product's amount, order subtotal, and the customer contact details.

#### Assigned To: Kaan Karadag
- [] Notifications integration for order placement
    - [] implement functionality to notify producers of an incoming order
    - [] customers should get a notification on every order status update when a producer updates it, including pending, confirmed, ready (for delivery or collection), delivered or completed, and cancelled.

## Week 2: Any Remaining Functionalities

#### Assigned To: Matt Wood
- [] Work on payment processing to be integrated with external mock and placed orders
- [] Add discount management for payments including bulk order discounts and surplus discounts.
    - This should be reflected on the items and inside the customer's basket when items are added to it, showing the discount that will be applied and the order summary's subtotal with the added discount.

#### Assigned to: Amine Ziani
- [] Add payment fallback handling and processing in case of failure. This includes:
    - [] transaction retries in case of failed transactions (not enough balance, API failure...)
    - [] refunds in case of order cancellation by customer.

#### Assigned To: Dina Metwalli
- [] Complete/continue single-vendor and multi-vendor order placement
    - [] in either case of single or multi-vendor orders, each order should be linked back to an overall order receipt for the customer to view what they ordered regardless of its producer.
    - [] each order should also link back to the items its associated with depending on the producer.
- [] Start developing order history view for customers
- [] Add functionality for customers to reorder the same orders from their history

#### Assigned To: Leon Stansfield
- [] Continue developing order view for producers
    - [] integrate a 48-hour lead time to ensure producers have enough time to prepare.
    - [] add functionality for producers to view the order delivery type

#### Assigned To: Kaan Karadag
- [] Notifications integration for order placement
    - [] implement functionality to notify producers of an incoming order
    - [] customers should get a notification on every order status update when a producer updates it, including pending, confirmed, ready (for delivery or collection), and delivered or completed.

## Week 3: Integration

#### Assigned To: All Members
- [] cleanup any failed or incomplete functionalities assigned to you and test on related test cases to ensure success.
- [] add any remaining error handling cases for user authorization and process failures.

#### Assigned To: Matt Wood
- [] Integrate developed payment processing with discounts to the basket view and external mock
    - [] modify the data fields currently sent to the external payment system as needed.
- [] Add the UI elements needed to show the integrated discounts processing.

#### Assigned to: Amine Ziani
- [] Implement the frontend web templates to show payment status:
    - this includes success, failure, refund, etc.

#### Assigned To: Leon Stansfield
- [] implement the needed UI template with the correct styling to order the orders by date of placement.
- [] Add functionality for producers to modify the order status (initially set to pending, then they can update to confirmed, ready for collection, or delivered).

#### Assigned To: Kaan Karadag
- [] Dispatch notifications when an order status is updated by a producer user.

#### Assigned To: Dina Metwalli
- [] Integrate discounts and payment receipts to the customer's order history as needed, as well as the overall order status.

## Sprint 2 Deliverables

### 1. Multi-vendor and single-vendor order split
Orders are split and recorded in the DB accordingly depending on if the order items are from a single producer or multiple.

### 2. Producer Advanced Order View
Producers should now be able to view incoming orders, update order status, and see each orders details along with its customer's contact information.

### 3. Notifications & Updates
Customers should get notifications of their order status and changes made to it by Producers. They should also have availability to cancel orders and producers be notified of that.

### 4. Payment Integration
Payment integration through Stripe when a customer clicks on Checkout, with the ability to cancel and refund when needed.

### 5. Discounts
The application of discounts on producer items and their calculation in order summary subtotal in the customer's basket.