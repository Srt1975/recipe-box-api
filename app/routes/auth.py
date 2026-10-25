from flask import Blueprint, request, jsonify, g  # plus any other imports you need
from datetime import datetime, timedelta
from app.models import db, User
from flask import current_app as app
import jwt
from app.services.user import fetch_user
from app.middleware import require_auth 
from app.services.auth import hash_password, verify_password

auth_bp = Blueprint("auth", __name__)  # 1) define it first

@auth_bp.get("/me")
@require_auth
def me():
    user = User.query.get(g.user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    })

@auth_bp.post("/register")
def register():
    user = User(
        username=username,
        email=email,
        password_hash=hash_password
    )
    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "could not create user"}), 500
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
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

    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({"error": "Invalid username or password"}), 401

    if not verify_password(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    payload = {
        "sub": str(user.id),
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    token = jwt.encode(payload, app.config["JWT_SECRET"], algorithm=app.config["JWT_ALGORITHM"])
    
    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
        }
    }), 200
