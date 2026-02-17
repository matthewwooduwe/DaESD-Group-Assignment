## Bristol Regional Food Network Requirements

### Functional Requirements

#### Product & Inventory Management

Producer Listings: Producers must be able to list products with names, detailed descriptions, pricing, and availability timeframes.

Seasonal Management: The system must support frequent seasonal updates and display seasonal availability indicators to customers.

Detailed Attributes: Product listings must clearly indicate:

Organic certification status.

Allergen warnings.

Harvest dates and best-before dates.

Inventory Tracking: Producers must have access to basic inventory management tools within their service portal.

#### Customer Experience & Ordering

Browsing & Search: Customers must be able to browse by category (vegetables, dairy, bakery, etc.) and search for specific items.

Transparency: Every product must display its specific farm origin information.

Multi-Vendor Basket: The checkout process must aggregate items from multiple vendors into a single transaction while maintaining transparency about individual supplier responsibilities.

Fulfillment Info: The platform must clearly communicate delivery arrangements and collection procedures to the customer.

#### Order Fulfillment & Finance

Producer Dashboard: Producers require a dedicated view to manage incoming orders with a minimum 48-hour lead time for preparation.

Automated Commission: The system must automatically deduct a five percent (5%) network commission from every transaction.

Financial Settlements: The platform must manage weekly payment settlements to producers.

Audit Trails: Maintain transparent records for all transactions to satisfy accounting and tax requirements.

#### Community & Environmental Features

Food Miles Calculation: The system must calculate distances using postcode-to-postcode measurements to report on "food miles."

Waste Reduction: Producers must be able to send "Surplus Produce Alerts" with last-minute discount capabilities.

Educational Content: The platform should host seasonal recipes, storage guidance, and "Farm Stories."

Traceability & Safety: The system must maintain direct links between customers, products, and producers to facilitate rapid communication regarding food safety or quality issues.

### Non-Functional Requirements

#### Technical Architecture

Microservices Structure: The application must be deployed as a suite of 6 Docker containers:

frontend-service

customer-service

platform-service

producer-service

payment-gateway-service (Mock)

mysql-db (Shared Database)

Containerization: Use Docker Compose for orchestration to ensure environment parity across development and production.

Inter-service Communication: Services must communicate via REST APIs using secure JSON Web Tokens (JWT) for authentication.

#### Security & Compliance

Sandbox Payments: Under no circumstances should live payment data be used. Developers must use Stripe/PayPal sandboxes or the internal mock service.

Data Protection: System design must comply with current data protection (GDPR) and financial services regulations.

Auth Guarding: Every API operation must be guarded by robust authentication and authorization checks.

#### Usability & Reliability

Producer Accessibility: The UI for producers must be designed for users with varying levels of technical proficiency.

System Health: The database must implement health checks to ensure dependent services do not attempt to start before the DB is ready.

Responsiveness: The frontend must be fully responsive to accommodate customers using mobile devices and producers in field environments.

#### Performance & Quality

Test Coverage: The project aims for a minimum of 70% test coverage across the microservices suite.

Lead Time Logic: The system must programmatically enforce a 48-hour buffer between order placement and fulfillment.