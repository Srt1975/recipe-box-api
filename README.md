# Course
Maestro Authentication, Authorization, and Middleware

# Recipe Box API

This repository began as a small Flask + SQLite recipe API and has evolved as the authentication and authorization lessons progressed. The current codebase is a mid-course implementation: users can register and log in, JWTs are validated through middleware, and recipe updates/deletes are limited by ownership and role checks.

## Current state

- User registration and login are implemented through `/register` and `/login`.
- JWTs are issued for authenticated sessions and checked by the `require_auth` middleware.
- `/register` and `/login` are rate-limited to 5 requests per minute per client.
- `GET /me` returns the current authenticated user.
- Recipe creation, update, and delete actions require a valid bearer token.
- Ownership and admin checks are enforced in the recipe service layer.
- Private/public visibility enforcement for recipes is still being finalized as the remaining lessons continue.

## Setup

1. Create a local `.env` file with the required secrets:

```env
JWT_SECRET=your_secret_here
DATABASE=recipes.db
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
pip install PyJWT python-dotenv
```

3. Run the app using the Flask application factory:

```bash
flask --app 'app:create_app("development")' run
```

You can also do this with the environment variable pattern:

```bash
export FLASK_APP='app:create_app("development")'
flask run
```

## Example flow

```bash
curl -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@example.com","password":"secret123"}'

curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"secret123"}'

curl http://127.0.0.1:5000/me \
  -H "Authorization: Bearer <token>"

curl http://127.0.0.1:5000/recipes

curl -X POST http://127.0.0.1:5000/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title":"Toast","ingredients":"bread","instructions":"Toast until golden."}'
```

## Endpoints

| Method | Path | Success | Errors |
|---|---|---|---|
| POST | /register | 201 | 400 missing body / invalid input · 429 rate limit exceeded |
| POST | /login | 200 | 400 missing body · 401 bad credentials · 429 rate limit exceeded |
| GET | /me | 200 | 401 invalid token · 404 user missing |
| GET | /recipes | 200 | |
| GET | /recipes/&lt;id&gt; | 200 | 404 |
| POST | /recipes | 201 | 400 bad body · 401 missing/expired token |
| PATCH | /recipes/&lt;id&gt; | 200 | 400 · 403 forbidden · 404 |
| DELETE | /recipes/&lt;id&gt; | 204 | 403 forbidden · 404 |

`is_public` is still part of the recipe model, but the remaining privacy enforcement is part of the in-progress work for the later lessons.
