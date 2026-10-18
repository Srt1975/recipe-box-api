# Architecture

## Overview

This repository contains a small Flask API for managing recipes with user authentication. The current codebase uses Flask, SQLite, Werkzeug password hashing, and JSON Web Tokens (JWT) for auth. The public API includes user registration/login plus recipe CRUD endpoints.

The app is organized around a Flask application factory, two blueprints, and a lightweight SQLite database layer built directly on `sqlite3`. Route protection is handled with a JWT-based decorator rather than a separate auth middleware package.

## Project Structure

```text
recipe-box-api/
├── app.py
├── wsgi.py
├── auth_utils.py
├── print_configs.py
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── middleware.py
│   ├── init_db.py
│   └── routes/
│       ├── auth.py
│       └── recipes.py
├── recipes.db
├── recipes_dev.db
├── recipes_test.db
├── README.md
├── SECURITY_NOTES.md
├── REFACTOR_PLAN.md
└── postman/
```

- `app.py` is the local bootstrap module. It imports `create_app` and instantiates the app in development mode.
- `wsgi.py` exists as a deployment-oriented entry file, but in the current tree it does not define a Flask application object or a callable WSGI entry point.
- `auth_utils.py` provides password hashing helpers built on Werkzeug. The route modules currently duplicate some of this logic instead of importing it directly.
- `print_configs.py` is a small helper for inspecting development and production config values.
- `app/__init__.py` contains the application factory, root route, and blueprint registration. It no longer defines `get_db`, `close_db`, or `recipe_to_dict`; those concerns were moved into dedicated modules.
- `app/db.py` owns the SQLite connection lifecycle and low-level queries. It provides:
  - `get_db()` – returns a per-request SQLite connection using `current_app.config["DATABASE"]`, sets `row_factory`, and enables foreign keys.
  - `close_db()` – closes and clears the connection stored on `g`; registered with `app.teardown_appcontext(close_db)` in `create_app`.
  - query helpers such as `get_all_recipes_rows()` that encapsulate raw SQL.
- `app/models.py` owns data representation helpers for rows coming from the database, such as `recipe_to_dict(row)`, which converts a `sqlite3.Row` into a JSON‑ready dict.
- `app/middleware.py` contains request‑boundary helpers such as the `require_auth` decorator built on JWT. Route modules import decorators from this module rather than from `app.__init__`.
- `app/routes/auth.py` defines the auth blueprint and the registration/login endpoints.
- `app/routes/recipes.py` defines the recipes blueprint and the recipe CRUD endpoints. Route functions are responsible only for HTTP translation (reading `request`, calling helpers, and returning `jsonify(...)`); they delegate business rules and data access to service/data modules.
- `app/config.py` defines the config classes and the environment variables required by the app.
- `app/init_db.py` creates and seeds the SQLite database.
- `recipes.db`, `recipes_dev.db`, and `recipes_test.db` are SQLite database files present in the repository. The code uses different filenames depending on config, but only the first two are referenced directly by the application config.
- `postman/` contains API testing artifacts such as collections, environments, and related workspace files.
- `README.md`, `SECURITY_NOTES.md`, and `REFACTOR_PLAN.md` are documentation/support files rather than runtime code.

## Flask Application Flow

The application is created in `app/__init__.py` by `create_app(config_name)`.

- `create_app` builds a `Flask` instance and selects a config class from a small `config_map`.
- The current supported config names are `development` and `production`.
- The app config is loaded from `DevelopmentConfig` or `ProductionConfig` in `app/config.py`.
- Inside the factory, `app.teardown_appcontext(close_db)` registers the DB teardown handler from `app.db`. The actual connection logic lives in `get_db()` in `app.db` and uses `current_app.config["DATABASE"]`.
- `recipe_to_dict()` is now defined in `app/models.py` and converts a recipe row into JSON-friendly output while omitting `owner_id`.
- The root route `/` returns a small JSON payload with a message and a pointer to `/recipes`.
- The factory registers the auth and recipes blueprints with no `url_prefix`, so their route decorators define the final public paths directly.

### Blueprints

#### `app.routes.auth`

- Blueprint object: `auth_bp`
- Registration: `app.register_blueprint(auth_bp)` in `create_app`
- URL prefix: none

Routes:

- `POST /register` - Create a new user account.
- `POST /login` - Authenticate a user and return a JWT.

#### `app.routes.recipes`

- Blueprint object: `recipes_bp`
- Registration: `app.register_blueprint(recipes_bp)` in `create_app`
- URL prefix: none

Routes:

- `GET /recipes` - Return a list of recipes. The handler is responsible only for HTTP translation: it calls `get_all_recipes_rows()` from `app.db`, maps each row through `recipe_to_dict()` from `app.models`, and returns the result via `jsonify(...)`. No raw SQL or connection management appears in this route.
- Other recipe CRUD routes follow the same pattern: routes handle HTTP concerns, while business rules and database access live in dedicated modules.

## Authentication and Security

User registration and login live in `app/routes/auth.py`.

- Registration accepts JSON with `username`, `email`, and `password`.
- Passwords are hashed with Werkzeug using `pbkdf2:sha256` before being stored.
- The user row is inserted into the `users` table and the response returns the new `id`, `username`, and `email`.
- Login accepts JSON with `username` and `password`.
- Credentials are checked against the `users` table with `check_password_hash`.
- On success, the app creates a JWT with `sub` set to the user ID, `username` set from the DB row, and `exp` set to one hour in the future.
- The token is signed with `JWT_SECRET` using the configured `JWT_ALGORITHM` (`HS256`).

Route protection is handled by require_auth in app/middleware.py.

- It expects an `Authorization` header that starts with `Bearer `.
- It decodes the token with the configured JWT secret and algorithm.
- Expired tokens return a 401 with a dedicated expiry message.
- Other decode failures return a 401 and log the JWT error.
- When decoding succeeds, it stores `g.user_id` and `g.role` for downstream route logic.

Protected routes in the current code:

- `POST /recipes`
- `PATCH /recipes/<int:recipe_id>`
- `DELETE /recipes/<int:recipe_id>`

Additional access checks inside the recipe routes:

- Update and delete are only allowed when the caller is the recipe owner or has `g.role == "admin"`.
- The login payload currently does not include a `role` claim, so `g.role` falls back to `user` unless a token with that claim is supplied.
- The `is_public` field is stored on recipes, but the current `GET` routes do not enforce public/private visibility.

## Database Layer

The app uses raw SQLite connections rather than an ORM.

- `get_db()` and `close_db()` are defined in `app/db.py`. `get_db()` opens the database from `current_app.config["DATABASE"]`, caches the handle on `g.db`, sets `row_factory` to `sqlite3.Row`, and enables foreign keys. `close_db()` clears and closes `g.db` and is registered in the app factory with `app.teardown_appcontext(close_db)`.
- Higher-level code (routes, init scripts) import `get_db` or query helpers (such as `get_all_recipes_rows()`) from `app.db` instead of accessing `sqlite3` directly.
- `app/init_db.py` runs inside an app context, uses the configured database path, creates tables with `executescript`, checks whether `recipes` already contains rows, and seeds the DB only when it is empty.

Database files and config:

- `DevelopmentConfig` uses `recipes_dev.db`.
- `ProductionConfig` uses `recipes_prod.db`.
- The repository currently contains `recipes.db`, `recipes_dev.db`, and `recipes_test.db`.
- `app.py` creates the app with `create_app("development")`, so the local app path points at `recipes_dev.db`.
- `app/init_db.py` says it creates and seeds `recipes.db` in its docstring, but the actual code uses the development config, so it initializes the development database filename from config.
- The repo does not currently include `recipes_prod.db`.

Schema as defined in `app/init_db.py`:

- `recipes`: `id`, `title`, `ingredients`, `instructions`, `is_public`
- `users`: `id`, `username`, `email`, `password_hash`

## Public API Contract

| Method | Path | Description | Auth required |
|---|---|---|---|
| GET | `/` | Basic health-style landing response with a pointer to recipes | No |
| POST | `/register` | Register a new user | No |
| POST | `/login` | Log in and return a JWT | No |
| GET | `/recipes` | List all recipes | No |
| GET | `/recipes/<int:recipe_id>` | Get a single recipe | No |
| POST | `/recipes` | Create a new recipe | Yes |
| PATCH | `/recipes/<int:recipe_id>` | Update a recipe | Yes |
| DELETE | `/recipes/<int:recipe_id>` | Delete a recipe | Yes |

## Current Notes

- The codebase is intentionally small and direct, but some responsibilities are split across modules in a loose way. `auth_utils.py` exists as a reusable helper module, while the current auth route still calls Werkzeug directly.
- The recipe routes reference `owner_id` and role-based access control, but the current initialization schema does not define an `owner_id` column on `recipes` or a `role` column on `users`. That means the current security logic is only partially supported by the schema as written.
- `wsgi.py` is present but does not currently act as a real WSGI bootstrap module.
- Route handlers in `app/routes/*.py` are being refactored toward a single responsibility: HTTP translation. They call helpers in `app/db.py` for database work and `app/models.py` for data representation instead of embedding SQL or row-to-dict logic directly.
- Cross-cutting auth concerns are centralized in `app/middleware.py` to avoid circular imports between `app.__init__` and the route modules.