# Frontend Service — Developer Guide

The frontend service is a Django application that serves the web interface for the Bristol Regional Food Network. It communicates with the Platform API to fetch and display data, and handles user authentication via JWT tokens stored in Django sessions.

This guide covers everything you need to know to develop new pages and features within the frontend service.

---

## Table of Contents

1. [Service Overview](#1-service-overview)
2. [Creating a New Page](#2-creating-a-new-page)
3. [Templates & Base Layout](#3-templates--base-layout)
4. [Design System](#4-design-system)
5. [Calling the Platform API](#5-calling-the-platform-api)
6. [Authentication & Sessions](#6-authentication--sessions)
7. [Environment Variables](#7-environment-variables)
8. [Code Standards](#8-code-standards)
9. [Checklist Before Committing](#9-checklist-before-committing)

---

## 1. Service Overview

| Property | Value |
|---|---|
| **Port** | 8000 |
| **Framework** | Django 4.2 |
| **Template engine** | Django Templates |
| **Auth method** | JWT via Platform API, stored in Django session |
| **Styling** | Plain CSS — no frameworks |
| **Fonts** | Cormorant Garamond (headings), Source Sans 3 (body) |

The frontend service contains **no database models** of its own. All data comes from the Platform API over HTTP. The only database table used is `django_session` for session storage.

## 2. Creating a New Page

Every new page requires three things: a **view**, a **URL**, and a **template**. Follow this pattern for consistency.

### Step 1 — Add a view in `web/views.py`

```python
def my_page(request):
    """
    Brief description of what this view does.
    """
    data = []
    error = None

    try:
        resp = requests.get(
            f"{PLATFORM_API_URL}/api/some-endpoint/",
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
        else:
            error = f"Could not load data (status {resp.status_code})."

    except requests.exceptions.ConnectionError:
        error = "Cannot reach the platform API. Is the platform-service running?"
    except requests.exceptions.Timeout:
        error = "The platform API took too long to respond."
    except Exception as e:
        error = f"Unexpected error: {str(e)}"

    return render(request, 'web/my_page.html', {
        'data': data,
        'error': error,
    })
```

### Step 2 — Register the URL in `frontend/urls.py`

```python
from web import views

urlpatterns = [
    # ... existing routes ...
    path('my-page/', views.my_page, name='my_page'),
]
```

### Step 3 — Create the template at `web/templates/web/my_page.html`

```django
{% extends "web/base.html" %}

{% block title %}Page Title — Bristol Regional Food Network{% endblock %}

{% block extra_styles %}
/* Page-specific CSS goes here */
.my-section { padding: 2rem 0; }
{% endblock %}

{% block content %}
<section class="my-section">
    <div class="container">

        {% if error %}
        <div class="error-banner">{{ error }}</div>
        {% endif %}

        <!-- Page content here -->

    </div>
</section>
{% endblock %}
```

---

## 3. Templates & Base Layout

All pages extend `base.html`, which provides the nav, footer, fonts, CSS variables and utility classes.

### Available blocks

| Block | Purpose |
|---|---|
| `{% block title %}` | Sets the `<title>` tag |
| `{% block extra_styles %}` | Add page-specific CSS inside the `<style>` tag |
| `{% block content %}` | Main page content inside `<main>` |

### Accessing the session in templates

The request object is available in all templates via the `request` context processor:

```django
{% if request.session.username %}
    <p>Hello, {{ request.session.username }}</p>
{% else %}
    <a href="/login/">Sign in</a>
{% endif %}
```

### Linking between pages

Use hardcoded paths rather than `{% url %}` tags for simplicity:

```django
<a href="/products/{{ product.id }}/">View product</a>
<a href="/login/">Sign in</a>
<a href="/">Back to browse</a>
```

---

## 4. Design System

All styles are defined as CSS custom properties in `base.html`. **Always use these variables** — never hardcode colour values or shadows in page-specific CSS.

### Colour tokens

| Variable | Value | Usage |
|---|---|---|
| `--bg` | `#fdf9f3` | Page background |
| `--card-bg` | `#ffffff` | Cards and panels |
| `--nav-bg` | `#2e7d4f` | Navigation and footer |
| `--green` | `#2e7d4f` | Primary colour — buttons, prices, links |
| `--green-light` | `#e8f5ee` | Subtle green backgrounds |
| `--terra` | `#c85a1e` | Call-to-action buttons |
| `--terra-light` | `#e06b2a` | CTA hover state |
| `--cream` | `#fdf9f3` | Warm off-white sections |
| `--cream-dark` | `#f0ebe0` | Slightly darker cream — trust strips, borders |
| `--text` | `#1a1a14` | Primary body text |
| `--text-muted` | `#6b6b58` | Secondary/helper text |
| `--border` | `#e0dbd0` | Borders and dividers |

### Typography

| Use | Font | Class/Selector |
|---|---|---|
| Headings, product names, prices | Cormorant Garamond | `font-family: 'Cormorant Garamond', serif` |
| Body text, labels, buttons | Source Sans 3 | Default body font |

### Shadows

```css
box-shadow: var(--shadow);        /* Resting state */
box-shadow: var(--shadow-hover);  /* Hover state */
```

### Border radius

```css
border-radius: var(--radius);  /* 8px — use on cards, inputs, panels */
```

### Badge classes

Use these pre-built badge classes for status indicators:

```django
<span class="badge badge-organic">Organic</span>
<span class="badge badge-category">{{ product.category }}</span>
<span class="badge badge-low-stock">Low stock</span>
<span class="badge badge-unavailable">Unavailable</span>
```

### Utility classes

```django
<!-- Max-width centred container with horizontal padding -->
<div class="container"> ... </div>

<!-- Red error message banner -->
<div class="error-banner">Something went wrong.</div>
```

### Example: consistent button styles

```css
/* Primary action button */
.btn-primary {
    background: var(--terra);
    color: #fff;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: var(--radius);
    font-family: 'Source Sans 3', sans-serif;
    font-weight: 700;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background 0.2s;
}

.btn-primary:hover { background: var(--terra-light); }

/* Secondary / outline button */
.btn-secondary {
    background: transparent;
    color: var(--green);
    border: 1.5px solid var(--green);
    padding: 0.7rem 1.5rem;
    border-radius: var(--radius);
    font-family: 'Source Sans 3', sans-serif;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
}

.btn-secondary:hover {
    background: var(--green);
    color: #fff;
}
```

---

## 5. Calling the Platform API

All API communication goes through the `requests` library. The base URL is set via the `PLATFORM_API_URL` environment variable, which is already imported at the top of `views.py`.

### Unauthenticated request (public endpoints)

```python
resp = requests.get(
    f"{PLATFORM_API_URL}/api/products/",
    params={'category__name': 'Vegetables'},
    timeout=5
)
if resp.status_code == 200:
    products = resp.json()
```

### Authenticated request (protected endpoints)

Pass the JWT token from the session as a Bearer token:

```python
token = request.session.get('token')

resp = requests.get(
    f"{PLATFORM_API_URL}/api/baskets/",
    headers={'Authorization': f'Bearer {token}'},
    timeout=5
)
```

### POST request

```python
resp = requests.post(
    f"{PLATFORM_API_URL}/api/baskets/",
    json={'product': product_id, 'quantity': 1},
    headers={'Authorization': f'Bearer {token}'},
    timeout=5
)
```

### Error handling pattern

Always wrap API calls in the following pattern — every view should handle these three exception types:

```python
try:
    resp = requests.get(f"{PLATFORM_API_URL}/api/...", timeout=5)
    if resp.status_code == 200:
        data = resp.json()
    elif resp.status_code == 404:
        error = "This item could not be found."
    elif resp.status_code == 401:
        return redirect('/login/')
    else:
        error = f"Something went wrong (status {resp.status_code})."

except requests.exceptions.ConnectionError:
    error = "Cannot reach the platform API. Is the platform-service running?"
except requests.exceptions.Timeout:
    error = "The platform API took too long to respond."
except Exception as e:
    error = f"Unexpected error: {str(e)}"
```

### Available Platform API endpoints

| Method | Endpoint | Auth required |
|---|---|---|
| `GET` | `/api/products/` | No |
| `GET` | `/api/products/{id}/` | No |
| `GET` | `/api/products/categories/` | No |
| `GET` | `/api/reviews/?product={id}` | No |
| `POST` | `/api/auth/login/` | No |
| `POST` | `/api/auth/register/` | No |
| `GET` | `/api/auth/me/` | Yes |
| `GET` | `/api/baskets/` | Yes |
| `POST` | `/api/baskets/` | Yes |
| `GET` | `/api/orders/` | Yes |
| `POST` | `/api/checkout/` | Yes |

### Product images

Product images are served by the platform service. Construct the full URL using `MEDIA_BASE_URL`:

```django
<img src="{{ media_base_url }}/media/{{ product.image }}" alt="{{ product.name }}">
```

Always include a fallback for missing images — see `product_detail.html` for the pattern.

---

## 6. Authentication & Sessions

The frontend stores the JWT access token and username in Django's session after a successful login.

### Checking if a user is logged in (in a view)

```python
def my_protected_view(request):
    token = request.session.get('token')
    if not token:
        return redirect('/login/')
    # ... rest of view
```

### Accessing session data

```python
token    = request.session.get('token')     # JWT access token
username = request.session.get('username')  # Logged in username
```

### Checking login state in a template

```django
{% if request.session.username %}
    <!-- User is logged in -->
{% else %}
    <!-- User is not logged in -->
{% endif %}
```

### Clearing the session (logout)

```python
request.session.flush()
return redirect('/')
```

---

## 7. Environment Variables

These are set in the root `.env` file and passed to the frontend container via `docker-compose.yml`.

| Variable | Example | Description |
|---|---|---|
| `PLATFORM_API_URL` | `http://platform-api:8002` | Internal URL for container-to-container API calls. Do not use `localhost` here. |
| `MEDIA_BASE_URL` | `http://localhost:8002` | Public URL for the browser to load product images from. Uses `localhost` because it is called by the browser, not by the container. |
| `SECRET_KEY` | `your-secret-key` | Django secret key |
| `DEBUG` | `True` | Set to `False` in production |

> **Important:** `PLATFORM_API_URL` and `MEDIA_BASE_URL` are intentionally different. `PLATFORM_API_URL` uses the Docker internal hostname (`platform-api`) for server-side requests. `MEDIA_BASE_URL` uses `localhost` because image URLs are loaded by the user's browser.

---

## 8. Code Standards

### Views

- Every view function must have a docstring
- Always handle `ConnectionError`, `Timeout`, and generic `Exception` when calling the API
- Never hardcode the platform API URL — always use `PLATFORM_API_URL`
- Redirect to `/login/` if a protected endpoint returns `401`

### Templates

- Always extend `base.html`
- Page-specific CSS goes in `{% block extra_styles %}` only
- Never hardcode colours — use CSS variables from `base.html`
- Use the `.container` class for all page-level content width control
- Use the `.error-banner` class for all error messages

### Naming conventions

| Thing | Convention | Example |
|---|---|---|
| View functions | `snake_case` | `product_detail`, `basket_view` |
| Template files | `snake_case.html` | `product_detail.html` |
| CSS classes | `kebab-case` | `.card-body`, `.filter-btn` |
| URL paths | `kebab-case/` | `/my-orders/`, `/add-to-basket/` |

### Commit messages

Follow the project-wide convention from `CONTRIBUTING.md`:

```
feat(frontend): add basket page with item list and quantity controls

Closes #18
```

---

## 9. Checklist Before Committing

- [ ] Page extends `base.html` and uses the correct `{% block %}` structure
- [ ] All colours use CSS variables — no hardcoded hex values
- [ ] API calls follow the error handling pattern (ConnectionError, Timeout, Exception)
- [ ] Protected pages redirect to `/login/` if no session token is found
- [ ] No `print()` statements left in views
- [ ] Tested locally with `docker-compose up`
- [ ] Template renders correctly when the API returns no data (empty state handled)
- [ ] Commit message references the relevant GitHub issue number

---

## Questions?

Ask in the team Teams channel or tag **@matthewwooduwe** (me) on GitHub.
