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
- `app/__init__.py` contains the application factory, the shared DB helper, the root route, and the JWT auth decorator.
- `app/config.py` defines the config classes and the environment variables required by the app.
- `app/init_db.py` creates and seeds the SQLite database.
- `app/routes/auth.py` defines the auth blueprint and the registration/login endpoints.
- `app/routes/recipes.py` defines the recipes blueprint and the recipe CRUD endpoints.
- `recipes.db`, `recipes_dev.db`, and `recipes_test.db` are SQLite database files present in the repository. The code uses different filenames depending on config, but only the first two are referenced directly by the application config.
- `postman/` contains API testing artifacts such as collections, environments, and related workspace files.
- `README.md`, `SECURITY_NOTES.md`, and `REFACTOR_PLAN.md` are documentation/support files rather than runtime code.

## Flask Application Flow

The application is created in `app/__init__.py` by `create_app(config_name)`.

- `create_app` builds a `Flask` instance and selects a config class from a small `config_map`.
- The current supported config names are `development` and `production`.
- The app config is loaded from `DevelopmentConfig` or `ProductionConfig` in `app/config.py`.
- Inside the factory, a lazy `get_db()` helper opens a SQLite connection, sets `row_factory` to `sqlite3.Row`, and enables foreign keys with `PRAGMA foreign_keys = ON`.
- A teardown handler closes the per-request DB connection stored on `g`.
- `recipe_to_dict()` converts a recipe row into JSON-friendly output and intentionally omits `owner_id`.
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

- `GET /recipes` - List all recipes.
- `GET /recipes/<int:recipe_id>` - Fetch a single recipe by ID.
- `POST /recipes` - Create a recipe.
- `PATCH /recipes/<int:recipe_id>` - Update a recipe.
- `DELETE /recipes/<int:recipe_id>` - Delete a recipe.

## Authentication and Security

User registration and login live in `app/routes/auth.py`.

- Registration accepts JSON with `username`, `email`, and `password`.
- Passwords are hashed with Werkzeug using `pbkdf2:sha256` before being stored.
- The user row is inserted into the `users` table and the response returns the new `id`, `username`, and `email`.
- Login accepts JSON with `username` and `password`.
- Credentials are checked against the `users` table with `check_password_hash`.
- On success, the app creates a JWT with `sub` set to the user ID, `username` set from the DB row, and `exp` set to one hour in the future.
- The token is signed with `JWT_SECRET` using the configured `JWT_ALGORITHM` (`HS256`).

Route protection is handled by `require_auth` in `app/__init__.py`.

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

- `get_db()` is defined inside `create_app` in `app/__init__.py` and duplicated in `app/routes/auth.py`.
- Both versions open the database from `app.config["DATABASE"]`, cache the handle on `g.db`, set `row_factory` to `sqlite3.Row`, and enable foreign keys.
- The factory-attached helper `app.get_db` is used by `app/init_db.py`.
- `app/init_db.py` runs inside an app context, creates tables with `executescript`, checks whether `recipes` already contains rows, and seeds the DB only when it is empty.

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