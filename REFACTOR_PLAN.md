## REFACTOR_PLAN.md

Status: in progress

This repository has moved beyond the original no-auth baseline and is now working through the lessons on JWT authentication, authorization, and protected route handling. The refactor goal remains to keep the public recipe API stable while improving security and code structure behind the scenes.

## Current structure

```text
app/__init__.py          - application factory and blueprint registration
app/config.py            - environment-driven settings and JWT configuration
app/extensions.py        - cache and migration extensions
app/models.py            - SQLAlchemy models for users and recipes
app/middleware.py        - JWT auth guard and g.user_id / g.role injection
app/users.py             - lightweight user lookup helpers
app/routes/auth.py       - register, login, and /me routes
app/routes/recipes.py   - public recipe endpoints plus protected writes
app/services/auth.py     - password hashing and verification
app/services/user.py     - user-fetch helper functions
app/services/recipe_service.py - recipe CRUD, ownership, and admin checks
```

## Completed work

- Application factory and blueprint wiring are in place.
- User registration and login are active.
- Passwords are stored as PBKDF2 hashes.
- JWT middleware enforces bearer-token authorization for protected routes.
- `/register` and `/login` each implement per-endpoint rate limiting using Flask-Limiter.
- `GET /me` returns the current authenticated user.
- Recipe updates and deletes are restricted to owners or admins.

## Still in progress

- Finalize the `is_public` privacy rules for private recipe visibility.
- Tighten startup and environment documentation around `.env` and app-factory usage.
- Continue cleaning up migration-era or transitional files so the repo reflects a single consistent implementation.
- Confirm and document final authorization behavior across all recipe routes.

## Acceptance direction

The app is expected to preserve the original public recipe endpoints while adding stronger security for write actions. The current focus is on authenticated identity, role checks, and ownership validation rather than changing the basic recipe contract itself.


