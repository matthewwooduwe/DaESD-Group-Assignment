
I have started working on the database and platform service, which acts as the central backend. It manages the core data entities: **Users** and **Products**, and connects to the shared MySQL database.

### Database
I have made two Django apps to handle our specific requirements. I have also customized the table names to be cleaner:
- `users`: Main user table.
- `users_groups` & `users_permissions`: Custom join tables for cleaner permissions.
- `products`: Main product table.

Users App (`services/platform-service/users`)

Extends the default Django User model to include:
- role: Classifies users as ADMIN, PRODUCER, or CUSTOMER.

Products App (`services/platform-service/products`)

Manages inventory and product details:
- producer: Links every product to a specific Producer user.
- category: Classifies items (Vegetables, Dairy, Bakery, etc.).
- stock_quantity: Tracks available inventory.
- image: Supports product image uploads.
- allergen_info: Text field for allergen warnings.

### How It Works@

- The service runs in a Docker container (`platform-api`) and communicates with the MySQL container (`db`) over the internal Docker network.
- DB passwords and Secret Keys are injected via environment variables defined in `.env` and `docker-compose.yml`.
- Image Processing: The `Pillow` library is installed to handle image uploads.

### Next Steps:

Now that the database foundation is laid, here is how we proceed:

API Development:
    - Build REST API endpoints (using Django Rest Framework) to expose this data to the frontend.
    - Create serializers for `User` and `Product` models.

Frontend Integration:
    - Connect the `frontend-service` to these APIs to display products and allow user registration.

Data Population:
    - Create seed data (fixtures) for initial testing.
