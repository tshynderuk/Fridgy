import asyncio
import logging
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, field_validator

# Завжди читаємо .env саме з папки backend, а не з поточної робочої директорії.
load_dotenv(dotenv_path=Path(__file__).resolve().with_name(".env"), override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fridgy")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
AI_TIMEOUT_S = float(os.getenv("AI_TIMEOUT_S", "180"))

app = FastAPI(
    title="Fridgy API",
    description="AI-підбір рецептів за продуктами користувача",
    version="2.1.0",
)

# Один клієнт на весь процес сервера. Використовуємо async API,
# щоб скасування запиту не залишало фоновий Python-потік працювати далі.
gemini_client = (
    genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=int(AI_TIMEOUT_S * 1000)),
    )
    if GEMINI_API_KEY
    else None
)


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


class GeneratedRecipe(BaseModel):
    recipe_name: str = Field(description="Коротка зрозуміла назва страви українською.")
    cooking_time_minutes: int = Field(description="Загальний час приготування у хвилинах.")
    ingredients: List[str] = Field(description="Список інгредієнтів із приблизною кількістю.")
    instructions: List[str] = Field(description="Від 3 до 10 послідовних кроків приготування.")

class GeneratedRecipes(BaseModel):
    recipes: List[GeneratedRecipe] = Field(
        description="Список рівно з трьох різних рецептів."
    )

    @field_validator("recipes")
    @classmethod
    def validate_recipe_count(
        cls,
        values: List[GeneratedRecipe]
    ) -> List[GeneratedRecipe]:
        if len(values) != 3:
            raise ValueError("AI має повернути рівно три рецепти.")
        return values

class RecipeResponse(BaseModel):
    recipe_name: str
    cooking_time_minutes: int
    ingredients: List[str]
    instructions: List[str]
    source: str



async def generate_recipe_with_gemini(
    ingredients: List[str],
    max_time_minutes: int,
) -> GeneratedRecipes:
    if gemini_client is None:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    ingredient_list = "\n".join(
        f"- {item}" for item in ingredients
    )

    prompt = f"""
Ти — кулінарний AI-помічник мобільного застосунку Fridgy.

Створи РІВНО ТРИ різні, реалістичні та смачні рецепти українською мовою.

Продукти, які користувач має:
{ingredient_list}

Максимальний час приготування для КОЖНОЇ страви:
{max_time_minutes} хвилин.

Кількість порцій: 1–2.

Обов'язкові правила:

1. Створи рівно три різні страви.
2. Рецепти повинні відрізнятися за назвою та способом приготування.
3. Використовуй надані продукти як основу кожного рецепта.
4. Не вимагай інших основних продуктів, яких немає у списку.
5. Сіль, перець, вода та олія можуть бути необов'язковими базовими продуктами.
6. Не вигадуй, що користувач має інші продукти.
7. Час приготування КОЖНОГО рецепта не повинен перевищувати {max_time_minutes} хвилин.
8. Вкажи приблизну кількість кожного інгредієнта.
9. Для кожного рецепта дай від 3 до 7 послідовних кроків.
10. Для м'яса, птиці, риби та яєць забезпечуй достатню термічну обробку.
11. Не повторюй одну страву під різними назвами.
12. Поверни лише дані відповідно до JSON-схеми.

Усі текстові значення мають бути українською мовою.
"""

    logger.info(
        "Sending 3 recipes request to Gemini model %s",
        GEMINI_MODEL,
    )

    response = await gemini_client.aio.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=2400,
            response_mime_type="application/json",
            response_schema=GeneratedRecipes,
            thinking_config=types.ThinkingConfig(
                thinking_level="low"
            ),
        ),
    )

    parsed = getattr(response, "parsed", None)

    if parsed is not None:
        result = GeneratedRecipes.model_validate(parsed)
    else:
        response_text = response.text

        if not response_text:
            raise ValueError("AI повернув порожню відповідь.")

        result = GeneratedRecipes.model_validate_json(
            response_text
        )

    recipe_names = set()

    for recipe in result.recipes:
        recipe.recipe_name = recipe.recipe_name.strip()

        recipe.ingredients = [
            item.strip()
            for item in recipe.ingredients
            if item.strip()
        ]

        recipe.instructions = [
            item.strip()
            for item in recipe.instructions
            if item.strip()
        ]

        if not recipe.recipe_name:
            raise ValueError("AI не повернув назву страви.")

        normalized_name = recipe.recipe_name.casefold()

        if normalized_name in recipe_names:
            raise ValueError("AI повернув повторювані рецепти.")

        recipe_names.add(normalized_name)

        if not recipe.ingredients:
            raise ValueError("AI не повернув інгредієнти.")

        if not 3 <= len(recipe.instructions) <= 10:
            raise ValueError("AI повернув некоректну кількість кроків.")

        if not 1 <= recipe.cooking_time_minutes <= max_time_minutes:
            raise ValueError(
                "AI повернув час, що перевищує обмеження користувача."
            )

    return result



@app.on_event("startup")
async def log_configuration():
    logger.info(
        "Fridgy backend ready. Gemini model=%s, thinking_level=low, timeout=%ss",
        GEMINI_MODEL,
        AI_TIMEOUT_S,
    )


@app.on_event("shutdown")
async def close_gemini_client():
    if gemini_client is not None:
        await gemini_client.aio.aclose()
        gemini_client.close()


@app.get("/health")
def health():
    return {"status": "ok"}



@app.post("/recipe", response_model=List[RecipeResponse])
async def get_recipe(request: RecipeRequest) -> List[RecipeResponse]:
    if gemini_client is None:
        raise HTTPException(
            status_code=503,
            detail="AI ще не налаштований. Додайте GEMINI_API_KEY у файл backend/.env.",
        )

    try:
        result = await asyncio.wait_for(
            generate_recipe_with_gemini(
                request.ingredients,
                request.max_time_minutes,
            ),
            timeout=AI_TIMEOUT_S,
        )

        return [
            RecipeResponse(
                recipe_name=recipe.recipe_name,
                cooking_time_minutes=recipe.cooking_time_minutes,
                ingredients=recipe.ingredients,
                instructions=recipe.instructions,
                source="gemini",
            )
            for recipe in result.recipes
        ]

    except asyncio.TimeoutError:
        logger.warning(
            "Gemini request timed out after %s seconds.",
            AI_TIMEOUT_S,
        )
        raise HTTPException(
            status_code=504,
            detail="AI довго не відповідає. Спробуйте ще раз.",
        )

    except Exception as exc:
        logger.exception("Recipe generation failed.")
        error_text = str(exc).upper()

        if "503" in error_text or "UNAVAILABLE" in error_text:
            raise HTTPException(
                status_code=503,
                detail="Gemini тимчасово перевантажений. Спробуйте трохи пізніше.",
            )

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            raise HTTPException(
                status_code=429,
                detail="Перевищено ліміт запитів Gemini. Спробуйте пізніше.",
            )

        raise HTTPException(
            status_code=502,
            detail="Не вдалося створити рецепти через AI. Перевірте журнал сервера.",
        )
