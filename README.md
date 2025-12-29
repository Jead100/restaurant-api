# Restaurant API

A production-ready REST API for managing a restaurant's menu, carts, and orders,
built with Django REST Framework and designed around real-world backend patterns
including role-based permissions, JWT authentication, and OpenAPI documentation.

---

## Features

- Role-based access control (Manager, Delivery Crew, Customer)
- JWT authentication (access & refresh tokens)
- Demo authentication mode with auto-expiring users
- Fully documented OpenAPI schema (Swagger & Redoc)
- Menu and category management
- Cart system with unique item constraints
- Order lifecycle management (create, assign, deliver)
- Scoped throttling and rate limiting
- PostgreSQL (production) and SQLite (development) support

---

## Tech Stack

- **Python** 3.11
- **Django** & **Django REST Framework**
- **PostgreSQL** (production) / **SQLite** (local development)
- **SimpleJWT** – authentication
- **Djoser** – user management
- **drf-spectacular** – OpenAPI documentation
- **django-filter** – filtering and query support

---

## Live Demo

The API is deployed on **Render** with demo mode enabled.

- Demo users can be created via dedicated demo authentication endpoints
- Demo users automatically expire after a configurable TTL
- Intended for safe testing without persistent accounts

> ⚠️ Note: The public deployment runs with `DEBUG=False` and `DEMO_MODE=True`,
> enabling demo authentication while disabling development-only features.

---

## API Documentation

Interactive API documentation is available via:

- **Swagger UI**: `/api/schema/swagger-ui/`
- **Redoc**: `/api/schema/redoc/`
- **OpenAPI schema**: `/api/schema/`

---

## User Roles & Permissions

- **Manager**
  - Manage menu items and categories
  - View and assign orders to delivery crew
  - View all users and orders

- **Delivery Crew**
  - View assigned orders
  - Update order delivery status

- **Customer**
  - Browse menu
  - Manage cart
  - Place and view own orders

User group membership is managed through dedicated API endpoints and enforced
via role-based permissions.

---

## Authentication

The API uses JWT authentication with access and refresh tokens.

When demo mode is disabled, user creation is intentionally restricted and handled
outside the public API surface.

### Demo Authentication

When `DEMO_MODE=true`, the API exposes demo authentication endpoints
that allow clients to create temporary users without registration.

- Demo users expire automatically after `DEMO_USER_TTL_HOURS`
- Seed and initial data is protected and cannot be modified in demo mode
- Data created during demo sessions is marked as demo-specific

This mode is designed for production sandbox environments while preserving
data integrity.

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Jead100/restaurant-api.git
cd restaurant-api
````

### 2. Create and activate a virtual environment

> ⚠️ Note: On macOS and Linux, you may need to use `python3` instead of `python`.

```bash
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create environment variables

This project loads configuration (secret key, debug mode, authentication settings,
etc.) from an `.env` file.

Copy the example environment file into a new `.env` file:

```bash
cp .env.example .env      # macOS/Linux
copy .env.example .env    # Windows
```

For local development, the default values in `.env.example` are sufficient.

When `DEBUG=True`, the project automatically uses:

* SQLite as the database
* Development-friendly security settings
* Local configuration for authentication and API features

Demo authentication endpoints are **disabled by default** and can be enabled by
setting `DEMO_MODE=True`.

No additional setup is required to run the API locally.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Load seed data

Load the provided fixture `initial_data.json`, which includes sample menu items and categories.

```bash
python manage.py loaddata initial_data.json
```

### 7. Create local test users (optional)

When demo mode is disabled, the API does not expose public user registration.
To create local users for testing, run the following management command:

```bash
python manage.py create_test_users
```

This command creates test users for each role (Manager, Delivery Crew, Customer)
and prints their credentials to the terminal for local use. Use these credentials 
to obtain JWT tokens via `POST /api/v1/auth/jwt/create`.

#### Optional flags
* `--password <value>` – assign the same password to all test users
* `--reset` – reset passwords and role assignments if users already exist
* `--no-print` – suppress credential output (useful for CI)

Example:

```bash
python manage.py create_test_users --reset --password test1234
```

### 8. Run the development server

```bash
python manage.py runserver
```

The API will be available at:

```
http://127.0.0.1:8000/
```

---

## Example Endpoints

- `GET /api/v1/restaurant/items/` – list menu items
- `POST /api/v1/restaurant/cart/` – add items to cart
- `POST /api/v1/restaurant/orders/` – place an order
- `PATCH /api/v1/restaurant/orders/{id}/` – update order status
- `GET /api/v1/users/groups/customer/` – manage customer group membership

Refer to the API documentation for full details.

---

## Contact

If you'd like to get in touch, feel free to reach me at
ascanoa.jordan@gmail.com or connect with me on LinkedIn.

---

## Contributing

This project is open source but primarily serves as a personal portfolio.
If you spot an issue or have a suggestion, feel free to open an issue
or submit a pull request.

---

## License

This project is licensed under the MIT License.
