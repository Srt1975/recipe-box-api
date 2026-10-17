"""Recipe Box API — BE104 course skeleton.

A working Flask + SQLite CRUD API for recipes. It stores data perfectly —
and it trusts everyone. There is no authentication and no authorization yet.
That is the point: you will add both, lesson by lesson, in Units 2 and 3.
"""
import os
import sqlite3
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, g, jsonify, request, current_app
from functools import wraps
from app.config import Config, DevelopmentConfig, ProductionConfig
from app.routes.auth import auth_bp
from app.routes.recipes import recipes_bp

load_dotenv()  # load .env

def create_app(config_name: str):
    app = Flask(__name__)
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }

    config_class = config_map[config_name]
    app.config.from_object(config_class)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def recipe_to_dict(row):
        return {
            "id": row["id"],
            "title": row["title"],
            "ingredients": row["ingredients"],
            "instructions": row["instructions"],
            "is_public": bool(row["is_public"]),
            # "owner_id": row["owner_id"],
        }

 

    @app.get("/")
    def hello():
        return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})



    app.get_db = get_db
    app.register_blueprint(auth_bp)  # no url_prefix for now
    app.register_blueprint(recipes_bp)  # no url_prefix for now
    # probably return app here (temporarily) while we move code
    return app


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
