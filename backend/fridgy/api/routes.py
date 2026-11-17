"""HTTP-маршрути. Роутер лише приймає запит, викликає сервіс і повертає відповідь."""
from typing import List

from fastapi import APIRouter, Depends

from fridgy.api.dependencies import get_recipe_service
from fridgy.api.schemas import RecipeRequest, RecipeResponse
from fridgy.services.recipe_service import RecipeService

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/recipe", response_model=List[RecipeResponse])
async def get_recipe(
    request: RecipeRequest,
    service: RecipeService = Depends(get_recipe_service),
) -> List[RecipeResponse]:
    recipes = await service.suggest(request.to_query())
    return [RecipeResponse.from_domain(recipe) for recipe in recipes]
