from flask import Blueprint, jsonify, request, g
from app.models import recipe_to_dict
from app.middleware import require_auth
from app.services.recipe_service import create_recipe_service, list_recipes_service, get_recipe_service, update_recipe_service, delete_recipe_service 

recipes_bp = Blueprint("recipes", __name__)
@recipes_bp.get("/recipes")
def list_recipes():
    return list_recipes_service()

@recipes_bp.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    return get_recipe_service(recipe_id)

@recipes_bp.post("/recipes")
@require_auth
def create_recipe():
    data = request.get_json(silent=True)
    return create_recipe_service(data, g.user_id)

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
