from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    recipes = db.relationship("Recipe", back_populates="owner")

class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    prep_time_minutes = db.Column(db.Integer, nullable=True)
    ingredients = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)   # default '' in DB is fine
    is_public = db.Column(db.Boolean, nullable=False, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", back_populates="recipes")
    

def recipe_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "prep_time_minutes": row["prep_time_minutes"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
        "owner_id": row["owner_id"],
    }

