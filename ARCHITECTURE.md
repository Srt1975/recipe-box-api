# Architecture

## Overview

This repository is a small Flask API for managing recipes with JWT-based user authentication. The app is organized around an application factory, route blueprints, service-layer helpers, and direct SQLite access. The public API keeps the original recipe and auth endpoints intact, and the newer /me route is an additive convenience for fetching the authenticated user.

## Project Structure

```text
recipe-box-api/
├── app.py
├── wsgi.py
├── print_configs.py
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── init_db.py
│   ├── middleware.py
│   ├── models.py
│   ├── users.py
│   ├── routes/
│   │   ├── auth.py
│   │   └── recipes.py
│   └── services/
│       ├── auth.py
│       └── user.py
├── recipes.db
├── recipes_dev.db
├── recipes_test.db
├── README.md
├── SECURITY_NOTES.md
├── REFACTOR_PLAN.md
├── postman/
└── .venv/
```

- `app.py` is the local bootstrap entry file.
- `wsgi.py` creates the Flask app with `create_app("development")` for a WSGI-style startup path.
- `app/__init__.py` defines the application factory and registers the auth and recipe blueprints.
- `app/config.py` contains the app configuration classes and environment settings.
- `app/db.py` owns the SQLite connection lifecycle and shared query helpers.
- `app/models.py` converts database rows into JSON-friendly dictionaries.
- `app/middleware.py` contains the JWT auth guard via `require_auth`.
- `app/init_db.py` creates and seeds the database.
- `app/routes/auth.py` handles registration, login, and `/me`.
- `app/routes/recipes.py` handles recipe CRUD routes.
- `app/services/auth.py` contains password hashing and verification helpers.
- `app/services/user.py` wraps user lookup logic.
- `app/users.py` provides direct database access for user fetches by ID.

## Layering

- Routes: HTTP translation only. The route modules read request data, call service helpers, and return JSON responses. See `app/routes/auth.py` and `app/routes/recipes.py`.
- Services: business rules and security logic. Password hashing and verification live in `app/services/auth.py`, while user retrieval helpers live in `app/services/user.py`.
- Data: direct SQLite access and schema setup. This includes `app/db.py`, `app/users.py`, and the seed/init code in `app/init_db.py`.

## Authentication Flow

Login validates the submitted username and password, then issues a JWT containing the authenticated user ID and expiry time. The token is verified by `require_auth` in `app/middleware.py`, which reads the `Authorization: Bearer ...` header, decodes the token, and stores `g.user_id` and `g.role` for protected routes.

`GET /me` is handled in `app/routes/auth.py`. It calls the user lookup service, verifies the current user exists, and returns that user as JSON. This endpoint requires a valid bearer token and is additive: it does not replace any of the original API behavior.

## Public API Contract

The original seven endpoints retained their same paths, methods, status codes, and response shapes. `/me` is an additional authenticated endpoint and does not change the earlier contract. In other words, the refactor preserved the public API while cleanly separating route logic, service logic, and database access.
