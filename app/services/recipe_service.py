from flask import jsonify
from app.models import Rating, db, Recipe
from app.extensions import cache

def list_recipes_service():
    recipes = Recipe.query.order_by(Recipe.id).all()
    return jsonify([recipe_to_dict_from_model(r) for r in recipes])

def get_recipe_service(recipe_id: int):
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404
    return jsonify(recipe_to_dict_from_model(recipe))

def create_recipe_service(data, user_id):
    if not data or not data.get("title") or not data.get("ingredients"):
        return jsonify({"error": "title and ingredients are required"}), 400

    recipe = Recipe(
        title=data["title"],
        ingredients=data["ingredients"],
        instructions=data.get("instructions", ""),
        is_public=bool(data.get("is_public", True)),
        owner_id=user_id,
    )

    try:
        db.session.add(recipe)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("CREATE RECIPE ERROR:", repr(e))
        return jsonify({"error": "could not create recipe"}), 500

    return jsonify(recipe_to_dict_from_model(recipe)), 201

def update_recipe_service(recipe_id: int, data, user_id, role):
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404

    is_owner = (recipe.owner_id == user_id)
    is_admin = (role == "admin")

    if not (is_owner or is_admin):
        return jsonify({"error": "You do not have permission to update this recipe"}), 403

    if not data:
        return jsonify({"error": "a JSON body is required"}), 400

    for column in ("title", "ingredients", "instructions"):
        if column in data:
            setattr(recipe, column, data[column])
    if "is_public" in data:
        recipe.is_public = bool(data["is_public"])

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "could not update recipe"}), 500

    return jsonify(recipe_to_dict_from_model(recipe)), 200

def delete_recipe_service(recipe_id: int, user_id, role):
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404

    is_owner = (recipe.owner.id == int(user_id))
    is_admin = (role == "admin")

    if not (is_owner or is_admin):
        return jsonify({"error": "You do not have permission to delete this recipe"}), 403

    try:
        db.session.delete(recipe)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "could not delete recipe"}), 500
    cache.delete(f"recipe_rating_summary:{recipe_id}")  # Invalidate the cache for this recipe's rating summary
    return jsonify({"message": "recipe deleted successfully"}), 200

def get_rating_summary_service(recipe_id: int):
    ratings = Rating.query.filter_by(recipe_id=recipe_id).all()
    if not ratings:
        return None, 0  # No ratings found
    count = len(ratings)
    average_score = sum(r.score for r in ratings) / count
    return average_score, count
    # returns (average_score: float or None, count: int)

def create_rating_service(recipe_id: int, user_id: int, score: int):
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if recipe is None:
        raise ValueError("Recipe not found")
    if score < 1 or score > 5:
        raise ValueError("Score must be between 1 and 5")
    existing = Rating.query.filter_by(recipe_id=recipe_id, user_id=user_id).first()
    if existing:
        raise ValueError("User has already rated this recipe")
    rating = Rating(recipe_id=recipe_id, user_id=user_id, score=score)
    try:
        db.session.add(rating)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Could not create rating"), repr(e)
        raise ValueError("Could not create rating")
    
    return rating

def recipe_to_dict_from_model(recipe: Recipe):
    return {
        "id": recipe.id,
        "title": recipe.title,
        "prep_time_minutes": recipe.prep_time_minutes,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "is_public": bool(recipe.is_public),
        "owner_id": recipe.owner_id,
    }