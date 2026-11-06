# Architecture

## Overview

This repository is a Flask API built around an application factory and layered request flow. The current codebase includes user registration/login, JWT validation, protected recipe actions, rating support, and lightweight caching/rate limiting. It is no longer a no-auth recipe skeleton; it is a working mid-course API with a few incomplete pieces still in progress.

## Current project structure

```text
recipe-box-api/
├── app.py
├── wsgi.py
├── print_configs.py
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── REFACTOR_PLAN.md
├── SECURITY_NOTES.md
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── middleware.py
│   ├── models.py
│   ├── users.py
│   ├── routes/
│   │   ├── auth.py
│   │   └── recipes.py
│   ├── services/
│   │   ├── auth.py
│   │   ├── recipe_service.py
│   │   └── user.py
│   └── init_db.py
├── async_lab/
├── migrations/
├── postman/
├── recipes_dev.db
├── recipes_test.db
├── recipes.db
├── test_*.py
└── .env / .env.example
```

- `app/__init__.py` creates the Flask app, loads the selected config, initializes SQLAlchemy, migrations, cache, and rate limiting, then registers the auth and recipe blueprints.
- `app/config.py` reads environment values and defines development, production, and testing app settings.
- `app/extensions.py` initializes the Flask-Limiter instance and the cache object.
- `app/models.py` defines the SQLAlchemy models for `User`, `Recipe`, and `Rating`.
- `app/middleware.py` validates the bearer token and stores `g.user_id` and `g.role` for protected routes.
- `app/routes/auth.py` handles `/register`, `/login`, and `/me`, and applies per-endpoint rate limiting.
- `app/routes/recipes.py` handles recipe CRUD, rating creation, and rating-summary reads.
- `app/services/auth.py` provides password hashing and verification.
- `app/services/recipe_service.py` contains the recipe business logic, authorization checks, and rating operations.
- `app/users.py` provides user lookup helpers used by the app.

## Layering

- Routes: request parsing, validation, JSON responses, HTTP status handling, and cache invalidation.
- Services: business rules such as creation, updates, ownership checks, and rating validation.
- Models/data: SQLAlchemy models and persistence through the Flask-SQLAlchemy session.
- Middleware: bearer-token validation and request-context population for authenticated endpoints.

## Authentication flow

The current auth flow is:

1. `POST /register` validates the incoming JSON payload, hashes the password, and creates a new user.
2. `POST /login` validates the username/password pair and issues a JWT with the current user ID and expiry.
3. `require_auth` reads the `Authorization: Bearer ...` header, decodes the token, and stores `g.user_id` and `g.role` on the Flask request context.
4. `GET /me` reads the current user from `g.user_id` and returns the authenticated profile.

The JWT payload currently includes the user ID (as `sub`) and username, plus an expiry timestamp. The `role` claim is optional and defaults to `"user"` when it is absent. In other words, the app is prepared for role-based checks, but the login flow itself does not yet mint an `admin` role for normal users.

## Authorization and recipe rules

The current write rules are enforced in the service layer:

- recipe creation requires a valid auth token
- recipe updates require a valid auth token and a matching `owner_id`, or a token with `role == "admin"`
- recipe deletion follows the same owner/admin check
- users can rate a recipe once per recipe using a score between 1 and 5

The `Recipe` model includes an `is_public` column and the create/update flow accepts an `is_public` field, but the visibility enforcement is not yet complete. In the current implementation, the list and detail endpoints do not filter recipes by public/private visibility; they simply return the stored rows. This is still one of the remaining in-progress items.

## Rating and caching behavior

The API also includes rating support:

- `POST /recipes/<id>/ratings` creates a new rating for the current user
- `GET /recipes/<id>/rating-summary` returns the average score and count
- recipe-list and rating-summary responses are cached for short intervals to reduce repeated reads

These features are implemented and working as part of the current codebase, even though the private/public visibility work is still pending.

## Security status

The repository has moved well beyond the original no-auth baseline. Current protections include:

- password hashing before storage
- bearer-token required for protected routes
- role-aware permission checks in the service layer
- per-endpoint rate limiting on register/login
- guarded JWT decoding and expiry handling

The remaining work is focused on completing the public/private recipe visibility rules, tightening login-side role assignment, and cleaning up any startup/documentation gaps that are still present.
