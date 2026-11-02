
# Fridgy — Project Requirements

## 1. Project Purpose

Fridgy is an AI-powered Android application
that generates recipes using ingredients
available to the user.

The application helps users decide what to cook
while considering their available ingredients
and maximum cooking time.

## 2. Functional Requirements

### FR-01: Ingredient Input

Status: IMPLEMENTED

The user must be able to enter available ingredients.

Requirements:
- At least 1 ingredient.
- Maximum 30 ingredients.
- Maximum 50 characters per ingredient.
- Empty ingredients must be rejected.
- Duplicate ingredients are removed by backend.
- Ingredient names are normalized.

### FR-02: Cooking Time Input

Status: IMPLEMENTED

The user must specify the maximum cooking time.

Requirements:
- Minimum: 5 minutes.
- Maximum: 180 minutes.
- The value must be an integer.
- Invalid values must be rejected.

### FR-03: AI Recipe Generation

Status: IMPLEMENTED

The application must generate a recipe using
the ingredients provided by the user.

The generated recipe must contain:
- Recipe name.
- Cooking time.
- Ingredients with approximate quantities.
- Cooking instructions.
- AI source.

The current implementation generates one recipe
per API request.

### FR-04: Cooking Time Validation

Status: IMPLEMENTED

The maximum cooking time must be passed
to the Gemini model.

Backend must validate the returned cooking time.

A recipe whose reported cooking time exceeds
the user's limit must be rejected.

Note:
This is validation of the AI-reported time,
not measurement of actual cooking duration.

### FR-05: Recipe Presentation

Status: IMPLEMENTED

The Android application must display
the received recipe.

The result contains:
- Recipe name.
- Cooking time.
- Ingredient list.
- Cooking instructions.

### FR-06: UI State Management

Status: IMPLEMENTED

The application must support four UI states:

- Idle.
- Loading.
- Success.
- Error.

State management uses StateFlow
and RecipeUiState.

### FR-07: Backend Communication

Status: IMPLEMENTED

Android communicates with FastAPI
through Retrofit.

Required endpoints:

- GET /health
- POST /recipe

Data exchange uses JSON.

### FR-08: Error Handling

Status: IMPLEMENTED

The application must handle:
- Network connection errors.
- HTTP errors.
- AI timeout.
- AI service unavailability.
- Invalid AI responses.

The user must receive understandable
error messages.

### FR-09: Multiple Recipe Suggestions

Status: PLANNED

The application should generate
three different recipe suggestions
from the same ingredient list.

Each suggestion must:
- Have a different recipe name.
- Include ingredients.
- Include cooking instructions.
- Respect the maximum cooking time.

This feature is not implemented yet.

## 3. Non-Functional Requirements

### NFR-01: Performance

The application must perform network
operations asynchronously.

Android uses Kotlin Coroutines.

Backend uses asynchronous Gemini requests.

### NFR-02: Reliability

The application must not crash
when the backend is unavailable.

Errors must be handled gracefully.

### NFR-03: Security

- Gemini API key must remain on backend.
- Secrets must not be stored in Android source code.
- Environment variables are used for backend configuration.
- Sensitive information must not be committed to Git.

### NFR-04: Maintainability

The application uses separate components
for UI state management, data access
and network communication.

Backend and Android responsibilities
must remain separated.

### NFR-05: Compatibility

The Android application is tested
using Pixel 7 API 35 emulator
with Android 15.

## 4. Current Implementation Status

| Feature | Status |
|---|---|
| Ingredient input | Implemented |
| Cooking time input | Implemented |
| Input validation | Implemented |
| Gemini integration | Implemented |
| Recipe generation | Implemented |
| Time validation | Implemented |
| Recipe presentation | Implemented |
| Loading and error states | Implemented |
| Backend connection | Implemented |
| Multiple recipes | Planned |
| Recipe history | Not implemented |
| Favorite recipes | Not implemented |
| Camera recognition | Not implemented |
| User authentication | Not implemented |

## 5. Acceptance Criteria

The current MVP is considered functional
when the following conditions are satisfied:

1. User can enter available ingredients.
2. User can specify cooking time.
3. Invalid input is rejected.
4. Backend receives a valid JSON request.
5. Gemini generates a structured recipe.
6. Backend validates the AI response.
7. Cooking time does not exceed the requested limit.
8. Android displays the generated recipe.
9. Application handles server errors.
10. Existing functionality remains operational
    after future modifications.

## 6. Future Development

Planned improvements:

- Three alternative recipe suggestions.
- Improved cooking time accuracy.
- Recipe history.
- Favorite recipes.
- Dietary preferences.
- More advanced recipe presentation.
