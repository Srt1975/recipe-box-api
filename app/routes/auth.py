from flask import Blueprint, request, jsonify, g  # plus any other imports you need
from datetime import datetime, timedelta
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db
from flask import current_app as app
import jwt

auth_bp = Blueprint("auth", __name__)  # 1) define it first


@auth_bp.post("/register")
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

@auth_bp.post("/login")
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
        #"role": user["role"],  # 👈 new: comes from DB, not from the client
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    token = jwt.encode(payload, app.config["JWT_SECRET"], algorithm=app.config["JWT_ALGORITHM"])
    
    return jsonify({
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
        }
    }), 200
