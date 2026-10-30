# Security Notes – Recipe API

Status: in progress

This project has moved beyond the original insecure baseline. The app now stores hashed passwords, validates JWT bearer tokens, and checks recipe ownership before allowing updates or deletes.

## Current security posture

- Passwords are hashed with PBKDF2 via Werkzeug before they are stored.
- The middleware in `app/middleware.py` reads `Authorization: Bearer ...` headers and rejects missing, malformed, or expired tokens with `401`.
- Protected recipe routes use `g.user_id` and `g.role` to enforce access rules.
- A non-owner cannot patch or delete someone else’s recipe; an admin is allowed to act on other users’ content.
- Public recipe reads remain available without auth, while write actions require a valid authenticated identity.

## Expected behavior

- `GET /recipes` without a token → `200`, public listing remains available.
- `POST /recipes` without a token → `401`, recipe not created.
- `POST /recipes` with an expired token → `401`, recipe not created.
- `PATCH /recipes/<id>` by a non-owner → `403`, recipe unchanged.
- `DELETE /recipes/<id>` by an owner → allowed with the proper token.
- `DELETE /recipes/<id>` by an admin → allowed with the proper token.

## Remaining work

The project is still progressing through the later lessons, so the final privacy model for `is_public` recipes is not yet considered completely finalized. The immediate focus is to finish the remaining authorization details and keep the documentation aligned with the current app behavior.
