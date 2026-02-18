
I have started working on the database and platform service, which acts as the central backend. It manages the core data entities: Users and Products, and connects to the shared MySQL database.
I have made two Django apps in the platform service for users and products, and the respective database tables.

#### Database Tables
- `users`: Main user table.
- `users_groups` & `users_permissions` (join tables).
- `products`: Main product table.

#### Users App (`services/platform-service/users`)

Extends the default Django User model to include:
- role: Classifies users as ADMIN, PRODUCER, or CUSTOMER.

#### Products App (`services/platform-service/products`)

Manages inventory and product details:
- producer: Links every product to a specific Producer user. (this should prob be replaced with being linked to a farms/companies table at some point)
- category: Classifies items (Vegetables, Dairy, Bakery, etc.).
- stock_quantity: Tracks available inventory.
- image: Supports product image uploads.
- allergen_info: Text field for allergen warnings.

### How It Works@

- The service runs in a Docker container (`platform-api`) and communicates with the MySQL container (`db`) over the internal Docker network.
- DB passwords and Secret Keys are injected via environment variables defined in `.env` and `docker-compose.yml`.
- Image Processing: The `Pillow` library is installed to handle image uploads.

### Usage

Authentication
- Register: `POST /api/auth/register/`
- Login: `POST /api/auth/login/` (Returns JWT `access` and `refresh` tokens)

Products
- List All: `GET /api/products/`
- Create: `POST /api/products/` (Requires `Authorization: Bearer <token>` and `role=PRODUCER`)

Testing:

the database will now migrate and seed automatically on startup.

Run the included test script to test the API
```bash
docker-compose exec platform-api python test_api.py
```

I also made a very basic frontend to verify the API: [http://localhost:8000/](http://localhost:8000/)

(admin credentials: admin/admin)

### Next Steps:

1. Frontend Integration:
    - Connect the frontend-service to these APIs to display products and allow user registration.

2. Data Population:
    - Create test data.
