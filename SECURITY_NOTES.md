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

# Security Audit - Recipe API

Date: 2026-09-16
Auditor: Steven Thomure

## Password storage

- `users.password` uses PBKDF2 SHA-256 hashes.
- No plaintext passwords present in DB.

## Identity enforcement

- `POST /recipes` without `Authorization` → `401`, no recipe created.
- `POST /recipes` with expired token → `401`, no recipe created.

## Access control

- Alice (id=3) creates recipe id=9.
- `PATCH /recipes/9` as stevens_test (id=5) → `403`, recipe unchanged.
- `DELETE /recipes/9` as stevens_test → `403`, recipe not deleted.
- `DELETE /recipes/9` as admin (role=admin) → `204`, recipe removed.

## Regression of prior exploits

- Anonymous recipe creation:
  - Old behavior: recipe could be created without auth.
  - Current behavior: `401` and no DB change (verified before/after DB snapshot).