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

load_dotenv()  # load .env

def create_app(config_name: str):
    app = Flask(__name__)
    # for now, ignore config_name except maybe printing it
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET")
    print("JWT_SECRET from env:", repr(app.config["JWT_SECRET"]))
    
    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(DATABASE)
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
            "owner_id": row["owner_id"]
        }

 

    @app.get("/")
    def hello():
        return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})

    @app.get("/recipes")
    def list_recipes():
        rows = get_db().execute("SELECT * FROM recipes ORDER BY id").fetchall()
        return jsonify([recipe_to_dict(r) for r in rows])


    @app.get("/recipes/<int:recipe_id>")
    def get_recipe(recipe_id):
        row = get_db().execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "recipe not found"}), 404
        return jsonify(recipe_to_dict(row))

    @app.post("/recipes")
    @require_auth
    def create_recipe():
        data = request.get_json(silent=True)
        if not data or not data.get("title") or not data.get("ingredients"):
            return jsonify({"error": "title and ingredients are required"}), 400
        db = get_db()
        try:
            cur = db.execute(
                "INSERT INTO recipes (title, ingredients, instructions, is_public, owner_id)"
                " VALUES (?, ?, ?, ?, ?)",
                (
                    data["title"],
                    data["ingredients"],
                    data.get("instructions", ""),
                    1 if data.get("is_public", True) else 0,
                    g.user_id,
                ),
            )
            db.commit()
        except sqlite3.IntegrityError:
            return jsonify({"error": "a recipe with that title already exists"}), 409
        row = db.execute(
            "SELECT * FROM recipes WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        return jsonify(recipe_to_dict(row)), 201

    @app.patch("/recipes/<int:recipe_id>")
    @require_auth
    def update_recipe(recipe_id):
        db = get_db()
        row = db.execute(
            "SELECT * FROM recipes WHERE id = ?",
            (recipe_id,)
        ).fetchone()

        if row is None:
            return jsonify({"error": "recipe not found"}), 404

        is_owner = (row["owner_id"] == int(g.user_id))
        is_admin = (g.role == "admin")

        if not (is_owner or is_admin):
            return jsonify(
                {"error": "You do not have permission to update this recipe"}
            ), 403

        # Only if we get here is the user the owner or an admin:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "a JSON body is required"}), 400

        fields, values = [], []
        for column in ("title", "ingredients", "instructions"):
            if column in data:
                fields.append(f"{column} = ?")
                values.append(data[column])
        if "is_public" in data:
            fields.append("is_public = ?")
            values.append(1 if data["is_public"] else 0)

        if not fields:
            return jsonify({"error": "nothing to update"}), 400

        values.append(recipe_id)

        try:
            cur = db.execute(
                f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?", values
            )
            db.commit()
        except sqlite3.IntegrityError:
            return jsonify(
                {"error": "a recipe with that title already exists"}
            ), 409

        row = db.execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()
        return jsonify(recipe_to_dict(row))

    @app.delete("/recipes/<int:recipe_id>")
    @require_auth
    def delete_recipe(recipe_id):
        db = get_db()
        row = db.execute(
            "SELECT * FROM recipes WHERE id = ?",
            (recipe_id,)
        ).fetchone()

        if row is None:
            return jsonify({"error": "recipe not found"}), 404

        is_owner = (row["owner_id"] == int(g.user_id))
        is_admin = (g.role == "admin")

        if not (is_owner or is_admin):
            return jsonify(
                {"error": "You do not have permission to delete this recipe"}
            ), 403

        db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        db.commit()
        return "", 204

    @app.post("/register")
    def register():
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Missing JSON body"}), 400
        
        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip()
        password = (data.get("password") or "").strip()
        if not username or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        password_hash = generate_password_hash(password, method="pbkdf2:sha256")

        db = get_db()
        try:
            cursor = db.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash),
            )
            db.commit()
        except sqlite3.IntegrityError:
            return jsonify({"error": "username or email already in use"}), 409
        new_id = cursor.lastrowid
        return jsonify({
            "id": new_id,
            "username": username,
            "email": email,
        }), 201



    @app.post("/login")
    def login():
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Missing JSON body"}), 400

        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        if not username or not password:
            return jsonify({"error": "Missing required fields"}), 400

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if user is None:
            # unknown username
            return jsonify({"error": "Invalid credentials"}), 401

        if not check_password_hash(user["password_hash"], password):
            # wrong password
            return jsonify({"error": "Invalid credentials"}), 401

        # At this point, credentials are valid and we know who the user is
        payload = {
            "sub": str(user["id"]),               # authenticated user ID from DB
            "username": user["username"],    # optional, still from DB
            "role": user["role"],  # 👈 new: comes from DB, not from the client
            "exp": datetime.utcnow() + timedelta(hours=1),
        }

        token = jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256")
        
        return jsonify({
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
            }
        }), 200



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
                algorithms=[JWT_ALGORITHM],
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

JWT_ALGORITHM = "HS256"  # same as you used when encoding
DATABASE = "recipes.db"














