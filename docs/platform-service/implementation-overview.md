
I have expanded the platform service to integrate the full database schema, managing Users, Profiles, Products, Orders, and Reviews.

#### Database Tables and Models
- `users`: Extended User model with roles (ADMIN, PRODUCER, CUSTOMER).
- `producer_profiles`: Business details for producers (business name, address, bio).
- `customer_profiles`: Personal details for customers (delivery address).
- `categories`: Product categories (Vegetables, Dairy, etc.).
- `products`: Detailed product inventory with stock, pricing, and seasonal info.
- `orders`: Order management linked to customers.
- `order_items`: Individual items in an order with snapshot pricing and commission calculation.
- `reviews`: Customer reviews for products and orders.
- `surplus_deals`: Management of surplus produce (model created, pending API logic).

#### Users App (`services/platform-service/users`)

Extends the default Django User model and adds profiles:
- **Roles**: Classifies users as ADMIN, PRODUCER, or CUSTOMER.
- **Profiles**: Automatically created/updated alongside user registration.
- **Endpoints**:
    - Register: `POST /api/auth/register/` (Supports nested profile data)
    - Login: `POST /api/auth/login/` (Returns JWT tokens)
    - Me: `GET /api/auth/me/` (Retrieve own user and profile details)

#### Products App (`services/platform-service/products`)

Manages the product catalog:
- **Categories**: Dynamic category management.
- **Inventory**: Tracks `stock_quantity`, `unit`, `harvest_date`, `best_before_date`.
- **Search & Filter**: Filter by category, producer, organic status, availability.
- **Endpoints**:
    - List/Create Products: `GET/POST /api/products/`
    - Product Details: `GET/PUT/DELETE /api/products/<id>/`
    - Categories: `GET/POST /api/products/categories/`

#### Orders App (`services/platform-service/orders`)

Handles order processing and commission:
- **Order Creation**: Validates stock, calculates totals.
- **Commission**: Automatically calculates 5% network commission and 95% producer payout per item.
- **Endpoints**:
    - List/Create Orders: `GET/POST /api/orders/`
    - Order Details: `GET/PUT/DELETE /api/orders/<id>/`

#### Reviews App (`services/platform-service/reviews`)

Manages customer feedback:
- **Reviews**: Links customers to products and optional orders.
- **Endpoints**:
    - List/Create Reviews: `GET/POST /api/reviews/`
    - Review Details: `GET/PUT/DELETE /api/reviews/<id>/`

### How It Works

- The service runs in a Docker container (`platform-api`) and communicates with any MySQL container (`db`) over the internal Docker network.
- **Authentication**: Uses JWT (JSON Web Tokens) for secure API access.
- **Permissions**:
    - Producers can manage their own products and see their orders (logic to be refined).
    - Customers can place orders and write reviews.
    - Read-only access for public product listings.

### Usage

**Testing:**

Run the included test script to verify the full flow (Registration -> Product -> Order -> Review):
```bash
docker compose exec platform-api python test_api.py
```

To seed the db use:
```bash
docker compose exec platform-api python manage.py seed_db
```

**API Verification:**
You can also use tools like Postman or the basic frontend (if running) to interact with the endpoints.

### Next Steps:

1. **Frontend Integration**:
    - Connect the frontend-service to these new APIs.
    - Build UI for Profile management, Order history, and Product catalog.

2. **Refinement**:
    - Implement `SurplusDeals` logic.
    - Refine Producer order views (filtering order items by producer).
