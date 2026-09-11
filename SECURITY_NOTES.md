# Security Notes – Open Recipe API

2026-09-11

- Anonymous requester
  - `GET /recipes` → 200 OK, returns full list of recipes.
  - `PATCH /recipes/1` → 200 OK, updates recipe without any authentication.
  - `DELETE /recipes/1` → 204 No Content, deletes recipe without any authentication.