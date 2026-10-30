"""Recipe Box API — BE104 course skeleton.

A working Flask + SQLite CRUD API for recipes. It stores data perfectly —
and it trusts everyone. There is no authentication and no authorization yet.
That is the point: you will add both, lesson by lesson, in Units 2 and 3.
"""
from flask import Flask, jsonify
from app.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from app.routes.auth import auth_bp
from app.routes.recipes import recipes_bp
from app.models import db
from .extensions import migrate, cache, init_limiter



def create_app(config_name: str):
    app = Flask(__name__)
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }

    config_class = config_map[config_name]
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    init_limiter(app)

    @app.get("/")
    def hello():
        return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})

    app.register_blueprint(auth_bp)  # no url_prefix for now
    app.register_blueprint(recipes_bp)  # no url_prefix for now
    # probably return app here (temporarily) while we move code
    return app

