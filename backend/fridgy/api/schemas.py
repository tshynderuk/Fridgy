"""HTTP-схеми (Pydantic). Відокремлені від доменних моделей.

RecipeRequest / RecipeResponse описують JSON-контракт з Android-застосунком.
Перетворення на доменні моделі та назад виконується тут, а не в роутері.
"""
from typing import List

from pydantic import BaseModel, Field, field_validator

from fridgy.domain.models import Recipe, RecipeQuery


class RecipeRequest(BaseModel):
    ingredients: List[str] = Field(min_length=1, max_length=30)
    max_time_minutes: int = Field(ge=5, le=180)

    @field_validator("ingredients")
    @classmethod
    def validate_ingredients(cls, values: List[str]) -> List[str]:
        cleaned = []
        seen = set()

        for item in values:
            name = " ".join(item.split())

            if not name:
                continue

            if len(name) > 50:
                raise ValueError("Назва продукту не може перевищувати 50 символів.")

            normalized = name.casefold()
            if normalized not in seen:
                cleaned.append(name)
                seen.add(normalized)

        if not cleaned:
            raise ValueError("Додайте хоча б один продукт.")

        return cleaned

    def to_query(self) -> RecipeQuery:
        return RecipeQuery(
            ingredients=list(self.ingredients),
            max_time_minutes=self.max_time_minutes,
        )


class RecipeResponse(BaseModel):
    recipe_name: str
    cooking_time_minutes: int
    ingredients: List[str]
    instructions: List[str]
    source: str

    @classmethod
    def from_domain(cls, recipe: Recipe) -> "RecipeResponse":
        return cls(
            recipe_name=recipe.name,
            cooking_time_minutes=recipe.cooking_time_minutes,
            ingredients=list(recipe.ingredients),
            instructions=list(recipe.instructions),
            source=recipe.source,
        )
