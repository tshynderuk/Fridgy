
# Fridgy — Project Overview

## 1. Project Description

Fridgy is an AI-powered Android application designed
to help users decide what to cook using ingredients
they already have at home.

The application generates recipes based on available
ingredients and the maximum cooking time specified
by the user.

The main goal is to simplify everyday meal planning
and reduce food waste.

## 2. Target Audience

Fridgy is designed for users who:
- Want to decide quickly what to cook.
- Have a limited selection of ingredients.
- Need recipes that fit their available time.
- Prefer personalized AI-generated suggestions.

## 3. Main User Scenario

1. The user opens the Fridgy application.
2. Enters available ingredients.
3. Specifies the maximum cooking time.
4. Presses the recipe generation button.
5. Android sends a request to the backend.
6. Backend validates the request.
7. Google Gemini generates a recipe.
8. Backend validates the AI response.
9. Android receives the recipe.
10. The application displays the result.

## 4. Technology Stack

### Android Application

- Programming language: Kotlin.
- UI framework: Jetpack Compose.
- Design system: Material 3.
- Architecture: MVVM.
- State management: StateFlow.
- Asynchronous operations: Kotlin Coroutines.
- HTTP client: Retrofit.
- JSON converter: Gson.

### Backend

- Programming language: Python.
- Framework: FastAPI.
- Request validation: Pydantic.
- Server: Uvicorn.

### AI Integration

- AI provider: Google Gemini.
- Integration: Google GenAI Python SDK.
- API key is stored in backend environment configuration.

## 5. Current Application Features

The implemented MVP supports:

- Manual ingredient input.
- Maximum cooking time selection.
- Input validation.
- AI recipe generation.
- Structured recipe responses.
- Recipe name display.
- Cooking time display.
- Ingredient list display.
- Step-by-step cooking instructions.
- Loading, success and error UI states.
- Backend connectivity check.

## 6. Input Restrictions

The current Android implementation validates:

- At least one ingredient.
- Maximum 30 ingredients.
- Maximum 50 characters per ingredient.
- Cooking time from 5 to 180 minutes.
- Only valid integer cooking time values.

## 7. Current API

The Android application communicates
with the backend through Retrofit.

Available endpoints:

- GET /health — checks backend availability.
- POST /recipe — generates one recipe.

The recipe request contains:

- ingredients: List<String>
- max_time_minutes: Int

The recipe response contains:

- recipe_name
- cooking_time_minutes
- ingredients
- instructions
- source

## 8. Current MVP Limitations

The current implementation generates
one recipe per request.

The application does not yet have confirmed
implementations of:

- Multiple recipe suggestions.
- Recipe history.
- Favorite recipes.
- Camera-based ingredient recognition.
- User authentication.
- Nutritional analysis.

## 9. Planned Development

The next planned feature is Multiple Recipe Suggestions.

The goal is to allow users to receive
three different recipe options based on
the same ingredient list.

Each recipe must respect the maximum
cooking time specified by the user.

The new feature must preserve the existing
Fridgy architecture and functionality.

## 10. Development Principle

All future changes must be based on
the actual project architecture.

The existing Android application,
FastAPI backend and Gemini integration
must be extended without unnecessary
rewriting or unrelated refactoring.
