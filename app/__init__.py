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
from app.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from app.db import close_db
from app.routes.auth import auth_bp
from app.routes.recipes import recipes_bp

load_dotenv()  # load .env

def create_app(config_name: str):
    app = Flask(__name__)
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }

    config_class = config_map[config_name]
    app.config.from_object(config_class)

    app.teardown_appcontext(close_db)
    @app.teardown_appcontext
    def teardown_db(exception):
        close_db(exception)


 

    @app.get("/")
    def hello():
        return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})

    app.register_blueprint(auth_bp)  # no url_prefix for now
    app.register_blueprint(recipes_bp)  # no url_prefix for now
    # probably return app here (temporarily) while we move code
    return app

