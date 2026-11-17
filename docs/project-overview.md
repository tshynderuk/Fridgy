# Fridgy — Project Overview

## 1. Project Description

Fridgy is an AI-powered Android application designed
to help users decide what to cook using ingredients
they already have at home.

The application generates three recipe suggestions based on
available ingredients and the maximum cooking time specified
by the user, and keeps a local history of successful results.

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
7. The AI provider (Google Gemini) generates three recipes.
8. Backend validates the AI response.
9. Android receives the recipes.
10. The application displays three recipe cards.
11. The validated result is saved to the local history.

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
- Local database: Room.

### Backend

- Programming language: Python.
- Framework: FastAPI.
- Request validation: Pydantic.
- Server: Uvicorn.
- Layers: api, services, domain, infrastructure, core (package `backend/fridgy`).
- Tests: pytest, httpx.

### AI Integration

- AI provider: Google Gemini (GeminiProvider) or a fake provider (MockProvider).
- Integration: Google GenAI Python SDK, used only in GeminiProvider.
- API key is stored in backend environment configuration.

## 5. Current Application Features

The implemented MVP supports:

- Manual ingredient input.
- Maximum cooking time selection.
- Input validation.
- AI generation of three recipes.
- Structured recipe responses.
- Recipe name, cooking time, ingredient list and step-by-step instructions.
- Loading, success and error UI states.
- Backend connectivity check.
- Local history of successful results, details screen and deletion (Lab 4).
- Layered backend with an AI provider interface and tests (Lab 5).

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
- POST /recipe — generates three recipes.

The recipe request contains:

- ingredients: List<String>
- max_time_minutes: Int

The response is a list of three recipes. Each recipe contains:

- recipe_name
- cooking_time_minutes
- ingredients
- instructions
- source

Every response has the X-Request-ID header.

## 8. Current MVP Limitations

The application does not yet have confirmed
implementations of:

- Favorite recipes.
- Camera-based ingredient recognition.
- User authentication.
- Nutritional analysis.
- Offline requests with "pending" status.

## 9. Planned Development

Possible next steps:

- A fallback provider when Gemini fails.
- Favorite recipes.
- Dietary preferences.
- Automated tests for the Android application.

## 10. Development Principle

All future changes must be based on
the actual project architecture.

The existing Android application,
FastAPI backend and Gemini integration
must be extended without unnecessary
rewriting or unrelated refactoring.
