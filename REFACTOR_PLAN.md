## REFACTOR_PLAN.md
Responsibilities: 6
Total acceptance items: 7

This refactor may change the internal file/module structure, but must not change the public contract: endpoint paths, HTTP methods, status codes, response bodies, authentication behavior, or database-visible effects.

Final structure:
app.py - app entrypoint
app/__init__.py - app factory and blueprint registration
app/config.py - config and secrets
app/db.py - database setup and helpers
app/models.py - database models
app/middleware.py - JWT middleware for auth checks
app/users.py - user helper logic / current-user support
app/routes/auth.py - auth routes
app/routes/recipes.py - recipe routes
app/services/auth.py - password hashing and auth helpers
app/services/user.py - user lookup and fetch logic

Auth logic now lives in app/middleware.py for JWT validation, app/services/auth.py for password hashing and token-related logic, and app/services/user.py / app/users.py for user lookup and current-user resolution.

GET /me
request: GET /me with Bearer token
expected: status 200, response JSON with the current authenticated user

POST /register 
request: JSON body with name, email, password
expected: status 201 (created), db contains new user including password hash 

POST /login 
request: JSON body with valid username and password 
expected: status 200, response JSON with valid token

POST /recipes (create) 
request: JSON body with recipe fields, valid token(for ownership) 
expected: status 201(created), db contains new recipe

GET /recipes (list)
request: GET /recipes (no auth required)
expected: status 200, response JSON list of all recipes

GET /recipes/<int:recipe_id>
request: GET /recipes/<id> (no auth required)
expected: status 200, response JSON recipe if it exists, 404 in not exists

PATCH /recipes (update)
request: PATCH /recipes, JSON body with fields to update, valid token (admin or owner)
expected: status 200, response JSON recipe with updated fields, db recipe updated

DELETE /recipes/<int:recipe_id>
request: DELETE /recipes/, valid token (admin or owner)
expected: status 204, recipe deleted from db

Refactor Results:
All 7 original acceptance endpoints were re-run after the refactor and still return the same status codes and response shapes as before. The refactor preserved the public contract: endpoint paths, methods, auth behavior, and database-visible effects remained unchanged.


