from functools import wraps
from flask import request, jsonify, g, current_app
import jwt

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]

        try:
            claims = jwt.decode(
                token,
                current_app.config["JWT_SECRET"],
                algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired.  Please log in again."}), 401
        except jwt.InvalidTokenError as e:
            print("JWT decode error:", repr(e))
            return jsonify({"error": "Invalid or expired token"}), 401

        # store for routes to use
        g.user_id = claims["sub"]
        g.role = claims.get("role", "user")

        return f(*args, **kwargs)
    return wrapper
