# Architecture

## Overview

This repository is being evolved from the original recipe-only course skeleton into a layered Flask API with JWT-based authentication and authorization. The app now uses an application factory in `app/__init__.py`, route blueprints for auth and recipes, a middleware guard for bearer-token validation, and service logic for the recipe access rules.

## Current project structure

```text
recipe-box-api/
├── app.py
├── wsgi.py
├── print_configs.py
├── .env
├── .env.example
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
├── migrations/
├── postman/
├── recipes.db
├── recipes_dev.db
├── recipes_test.db
└── test_*.py
```

- `app/__init__.py` creates the Flask app and registers the auth and recipe blueprints.
- `app/config.py` loads config values from the environment and defines the development/production/testing app settings.
- `app/extensions.py` attaches the cache and migrations helpers.
- `app/models.py` defines the SQLAlchemy `User` and `Recipe` models.
- `app/middleware.py` validates the bearer token and stores `g.user_id` and `g.role` for protected routes.
- `app/routes/auth.py` handles `/register`, `/login`, and `/me`.
- `app/routes/recipes.py` manages the recipe endpoints and protects write actions.
- `app/services/auth.py` handles password hashing and verification.
- `app/services/recipe_service.py` contains recipe CRUD logic plus ownership/admin permission checks.
- `app/users.py` provides simple user lookup helpers.

## Layering

- Routes: request parsing, response formatting, and HTTP status handling. The route files are intentionally thin and delegate business rules to services.
- Services: business rules and authorization checks. Recipe updates/deletes are approved only when the current user is the owner or an admin.
- Data: database model definitions and the SQLAlchemy session used for persistence.

## Authentication flow

The login route validates the username and password, then issues a JWT containing the authenticated user identifier and expiry. The token is then decoded in `require_auth`, which reads the `Authorization: Bearer ...` header and either populates `g.user_id` / `g.role` or returns `401` when the token is missing, malformed, or expired.

`GET /me` reads the current user ID from the validated request context and returns the authenticated profile. This is additive to the original recipe endpoints and is part of the current lessons on JWT-based identity.

## Security status

The repository has moved past the original no-auth baseline. Passwords are hashed before being stored, bearer tokens are required for protected actions, and recipe writes are restricted to the owner or admin role. The remaining work is focused on finishing the private-vs-public recipe visibility rules and cleaning up the documentation/startup details still in progress.
