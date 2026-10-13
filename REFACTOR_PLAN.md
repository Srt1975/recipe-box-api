## REFACTOR_PLAN.md
Responsibilities: 6
Total acceptance items: 7

This refactor may change the internal file/module structure, but must not change the public contract: endpoint paths, HTTP methods, status codes, response bodies, authentication behavior, or database-visible effects.

app.py- app start
app/config.py - config and secrets
app/db.py - db setup
app/auth.py - auth
app/users.py- user routes
app/recipes.py - recipe routes

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



