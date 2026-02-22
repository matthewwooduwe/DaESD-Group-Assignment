# Bristol Regional Food Network Requirements

## Functional Requirements

### Product & Inventory Management

**FR1 - Producer Registration:** Producers MUST be able to register on the platform by creating an account using username, email, password, business address, and phone number.

**FR2 - Producer Listings:** Producers MUST be able to list products with names, detailed descriptions, pricing, and availability timeframes.

**FR3 - Seasonal Management:** The system MUST support frequent seasonal updates and display seasonal availability indicators to customers.

**FR4 - Detailed Attributes:** Product listings MUST clearly indicate:

* Organic certification status.
* Allergen warnings.
* Harvest dates and best-before dates.

**FR5 - Inventory Tracking:** Producers MUST have access to basic inventory management tools within their service portal.

**FR6 - Order Fulfillment:** Producers SHOULD be able to choose the order status through the order lifecycle to fulfillment.

**FR7 - Restocking:** Producers SHOULD receive notifications to restock a product on low stock to facilitate order fulfillment.

### Customer Experience & Ordering

**FR8 - Customer Registration:** Producers MUST be able to register on the platform by creating an account using username, email, password, delivery address, and phone number.

**FR9 - Browsing & Search:** Customers MUST be able to browse by category (vegetables, dairy, bakery, etc.) and search for specific items.

**FR10 - Transparency:** Every product MUST display its specific farm origin information.

**FR11 - Multi-Vendor Basket:** The checkout process MUST handle both single-producer orders and multi-producer orders by aggregating items from multiple vendors into a single transaction while maintaining transparency about individual supplier responsibilities.

**FR12 - Order Info:** The platform SHOULD update customers through notifications on the change in status of their order.

**FR13 - Fulfillment Info:** The platform MUST clearly communicate delivery arrangements and collection procedures to the customer.

**FR14 - Recurring Orders:** Customers (as an independent restaurant) COULD establish/specify recurring weekly orders for their business through platform functionality.

**FR15 - Order History:** Customers MUST be able to view their ordering history to reorder the same products and track purchases.

**FR16 - Products filtering:** Customers SHOULD be able to filter products organic certification to view only certified organic items.

**FR17 - Product Reviews:** Customers COULD access a rating system for reviewing previously purchased products and share their experience.

### Order Fulfillment & Finance

**FR18 - Producer Dashboard:** Producers MUST be provided with a dedicated view to manage incoming orders with a minimum 48-hour lead time for preparation.

**FR19 - Automated Commission:** The platform MUST automatically deduct a five percent (5%) network commission from every transaction.

**FR20 - Financial Settlements:** The platform MUST manage & provide weekly payment settlements to producers.

**FR21 - Audit Trails:** The platform MUST maintain transparent records for all transactions to satisfy accounting and tax requirements.

### Community & Environmental Features

**FR22 - Food Miles Calculation:** The system COULD calculate distances using postcode-to-postcode measurements to evaluate "food miles."

**FR23 - Waste Reduction:** Producers MUST be able to send "Surplus Produce Alerts" with last-minute discount capabilities.

**FR24 - Educational Content:** The platform COULD allow producers to host seasonal recipes, storage guidance, and "Farm Stories."

**FR25 - Traceability & Safety:** The system MUST maintain direct links between customers, products, and producers to facilitate rapid communication regarding food safety or quality issues.

## Non-Functional Requirements

### Technical Architecture

**NFR1 - Microservices Structure:** The application MUST be deployed as a suite of 6 Docker containers:

    frontend-service

    customer-service

    platform-service

    producer-service

    payment-gateway-service (Mock)

    mysql-db (Shared Database)

**NFR2 - Containerization:** Docker Compose MUST be used for orchestration to ensure environment parity across development and production.

**NFR3 - Inter-service Communication:** Services MUST communicate via REST APIs using secure JSON Web Tokens (JWT) for authentication.

### Security & Compliance

**NFR4 - Sandbox Payments:** Live payment data WON'T be used.

**NFR5 - Payments Development:** Developers MUST use Stripe/PayPal sandboxes or a mock service.

**NFR6 - Data Protection:** The system's design MUST comply with current data protection (GDPR) and financial services regulations, adhering to LESP considerations.

**NFR7 - Auth Guarding:** Every API operation MUST be guarded by robust authentication and authorization checks.

**NFR8 - Secure Access Control:** The platform MUST ensure the protection of user accounts and data through the necessary authentication and authorisation mechanisms (e.g. minimum password length, logging in, session management).

**NFR9 - Session Management:** The platform MUST handle user sessions correctly, where sessions only persist if users choose so.

### Usability & Reliability

**NFR10 - Producer Accessibility:** The UI for producers MUST be designed for users with varying levels of technical proficiency.

**NFR11 - System Health:** The database MUST implement health checks to ensure dependent services do not attempt to start before the DB is ready.

**NFR12 - Responsiveness:** The frontend MUST be fully responsive to accommodate customers using mobile devices and producers in field environments.

**NFR13 - User Registration:** The platform WON'T allow users to reuse the same email address to create a second account if an existing one is already registered for it.

**NFR14 - User-error handling:** The system MUST handle all user input errors gracefully, ensuring both success and failure paths are accounted for.

### Performance & Quality

**NFR15 - Test Coverage:** The project SHOULD cover a minimum of 70% test coverage across the microservices suite.

**NFR16 - Lead Time Logic:** The system MUST programmatically enforce a 48-hour buffer between order placement and fulfillment.