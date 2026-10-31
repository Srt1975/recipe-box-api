from flask import Blueprint, jsonify, request, g
from app.models import Recipe, recipe_to_dict
from app.middleware import require_auth
from app.services.recipe_service import create_rating_service, create_recipe_service, get_rating_summary_service, list_recipes_service, get_recipe_service, update_recipe_service, delete_recipe_service 
from app.extensions import cache

recipes_bp = Blueprint("recipes", __name__)

@recipes_bp.get("/recipes")
@cache.cached(key_prefix="list_recipes", timeout=30)  # Cache for 30 seconds
def list_recipes():
    return list_recipes_service()

@recipes_bp.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    return get_recipe_service(recipe_id)

@recipes_bp.post("/recipes")
@require_auth
def create_recipe():
    data = request.get_json(silent=True)
    response = create_recipe_service(data, g.user_id)
    cache.delete("list_recipes")  # Invalidate the cache for the list of recipes
    return response

@recipes_bp.patch("/recipes/<int:recipe_id>")
@require_auth
def update_recipe(recipe_id):
    data = request.get_json(silent=True)
    return update_recipe_service(recipe_id, data, g.user_id, g.role)

@recipes_bp.delete("/recipes/<int:recipe_id>")
@require_auth
def delete_recipe(recipe_id):
    data = request.get_json(silent=True)
    return delete_recipe_service(recipe_id, g.user_id, g.role)

@recipes_bp.post("/recipes/<int:recipe_id>/ratings")
@require_auth
def rate_recipe(recipe_id):
    data = request.get_json(silent=True)
    score = data.get("score") if data else None
    if score is None:
        return jsonify({"error": "score is required"}), 400
    
    try:
        score = int(score)
    except (TypeError, ValueError):
        return jsonify({"error": "score must be an integer"}), 400
    
    current_user_id = g.user_id
    try:
        rating = create_rating_service(recipe_id, current_user_id, score)
    except ValueError as e:
        msg = str(e)
        if msg == "Recipe not found":
            return jsonify({"error": msg}), 404
        if msg == "Score must be between 1 and 5":
            return jsonify({"error": msg}), 400
        if msg == "User has already rated this recipe":
            return jsonify({"error": msg}), 400

        return jsonify({"error": msg}), 500
    # success path:
    cache_key = CACHE_KEY_RECIPE_RATING.format(recipe_id=recipe_id)
    cache.delete(cache_key)
    return jsonify({
        "message": "rating created successfully",
        "rating": {
            "id": rating.id,
            "recipe_id": rating.recipe_id,
            "user_id": rating.user_id,
            "score": rating.score,
        },
    }), 201

CACHE_KEY_RECIPE_RATING = "recipe_rating_summary:{recipe_id}"

@recipes_bp.get("/recipes/<int:recipe_id>/rating-summary")
def get_recipe_rating_summary(recipe_id):
    """Get the rating summary for a specific recipe."""
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if recipe is None:
        return jsonify({"error": "Recipe not found"}), 404

    cache_key = CACHE_KEY_RECIPE_RATING.format(recipe_id=recipe_id)
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    average_score, count = get_rating_summary_service(recipe_id)

    payload = {
        "recipe_id": recipe_id,
        "average_score": average_score,
        "count": count,
    }
    cache.set(cache_key, payload)
    return jsonify(payload), 200