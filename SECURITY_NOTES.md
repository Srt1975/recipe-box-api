# Security Notes – Open Recipe API

2026-09-11

- Anonymous requester
  - `GET /recipes` → 200 OK, returns full list of recipes.
  - `PATCH /recipes/1` → 200 OK, updates recipe without any authentication.
  - `DELETE /recipes/1` → 204 No Content, deletes recipe without any authentication.

  
Identity	Action	Recipe	Expected	Actual	Result
Anonymous	PUT /recipes/5	5	401	401	✅ blocked
stevens_test	PUT /recipes/5	5	200	200	✅ owner OK
stevens_test	DELETE /recipes/4	4	403	403	✅ blocked
Owner of 4	DELETE /recipes/4	4	204	204	✅ deleted
admin	PUT /recipes/5	5	200	200	✅ admin OK
admin	DELETE /recipes/5	5	204	204	✅ admin OK
