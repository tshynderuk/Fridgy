
# Fridgy — Architecture Decision Records

## 1. Purpose

This document describes the main technical decisions
used in the Fridgy project.

AI assistants must consider these decisions before
suggesting or implementing code changes.

## 2. Android Technology

Decision:
Use native Android development with Kotlin.

Reason:
Kotlin provides native Android support and integrates
with Jetpack Compose and Android Jetpack libraries.

Selected technologies:
- Kotlin
- Jetpack Compose
- Material 3
- ViewModel
- Kotlin Coroutines
- StateFlow
- Room (local history, see section 13)

Constraint:
Do not replace the existing Android stack with Flutter,
React Native or another framework.

## 3. UI Architecture

Decision:
Use Jetpack Compose for the user interface.

Decision:
Use RecipeViewModel to manage UI state and application logic.

The current UI state is represented by RecipeUiState:
- Idle
- Loading
- Success
- Error

Constraint:
Preserve the existing UI states when adding new features.

## 4. Backend Technology

Decision:
Use Python and FastAPI for the backend.

Reason:
FastAPI provides HTTP endpoints, request validation
and asynchronous request handling.

Selected technologies:
- Python
- FastAPI
- Pydantic
- Uvicorn
- asyncio
- pytest and httpx (automated tests, Lab 5)

Constraint:
Do not move Gemini API calls into the Android application.

## 5. AI Integration

Decision:
Use Google Gemini API for recipe generation.

Reason:
Gemini can generate contextual recipes using
the ingredients provided by the user.

AI integration is implemented on the backend.

Constraint:
The Gemini API key must remain on the server.

Since Lab 5 the Gemini SDK is used only inside
GeminiProvider (fridgy/infrastructure/providers/gemini_provider.py).

Note:
An experiment with calling Gemini directly from the
Android app (Firebase AI Logic) was kept in a separate
Git branch and is not part of the main architecture.

## 6. API Communication

Decision:
Use Retrofit for Android HTTP communication.

Decision:
Use GsonConverterFactory for JSON serialization.

Current endpoints:
- GET /health
- POST /recipe

Current emulator Base URL:
http://10.0.2.2:8000/

Constraint:
Preserve the existing API contract unless
a feature explicitly requires an API change.

If the API contract changes:
1. Update backend models.
2. Update Android request or response models.
3. Update API documentation.
4. Test the complete integration.

## 7. Data Validation

Decision:
Use Pydantic for backend request validation.

Current restrictions:
- 1–30 ingredients.
- Maximum 50 characters per ingredient.
- Cooking time from 5 to 180 minutes.

Decision:
Validate the AI response before returning it
to the Android application.

Constraint:
Never trust an AI response without validation.

## 8. Security

Decision:
Store sensitive configuration in backend/.env.

Decision:
Exclude .env and virtual environment files
from version control using .gitignore.

Constraint:
Never commit real API keys.
Never expose secrets in Android source code.
Never include API keys in logs or API responses.
Never write secrets or technical error messages
to the local history.

Note:
app/google-services.json (left over from the Firebase experiment)
must not be committed.

## 9. Error Handling

Decision:
Use HTTP status codes to represent backend errors.

Decision:
Keep technical exception details in server logs
and return understandable messages to users.

Android must preserve its Error UI state.

## 10. Cooking Time

Decision:
The user's maximum cooking time is a required
constraint for recipe generation.

Backend passes the limit to Gemini and checks
the returned cooking_time_minutes value.

Constraint:
A recipe with a returned time greater than
the user's limit must not be returned as successful.

Important:
This validates the AI-reported time,
not the actual measured cooking duration.

## 11. Development Principles

When implementing new features:

1. Prefer extending existing classes.
2. Avoid unnecessary architectural changes.
3. Keep Android and backend responsibilities separate.
4. Keep network operations asynchronous.
5. Preserve existing functionality.
6. Validate all external AI responses.
7. Update documentation when API contracts change.
8. Test existing functionality after modifications.

## 12. Future Architecture Decisions

The following features may require new decisions:

- Offline requests with "pending" status.
- Favorite recipes.
- Dietary preferences.
- Camera-based ingredient recognition.

These features are not part of the confirmed
current implementation.

## 13. Local Storage Technology (Lab 4, 2026-11-14)

Decision:
Use Room (SQLite) for the local history.

Alternatives considered:
- DataStore: suited for settings and flags, not for a list of records.
- Plain files: no queries, sorting or reactive updates.
- In-memory list: data is lost when the application process ends.

Reason:
The history is a list of structured records that must be sorted,
read individually, deleted and observed reactively (Flow).
Room is recommended for this by the Android documentation.

New dependencies (justification):
- androidx.room:room-runtime and room-ktx (version 2.8.4).
- androidx.room:room-compiler through KSP, because the code is in Kotlin.
Existing libraries cannot provide a persistent database.

Constraint:
Screens must not access the database directly.
The chain is DAO -> Repository -> ViewModel -> Screen.

## 14. History Record Structure (Lab 4)

Decision:
One successful request = one row in table history_entries.
The three recipes are stored together in one text column
(recipesJson) as JSON produced by Gson.

Fields:
id (auto-generated), createdAt, inputSummary, maxTimeMinutes,
resultSummary, recipesJson, status.

Reason:
The three recipes always belong to one request and are shown together,
so a single table keeps the model simple. The list screen needs only
the summary columns; the details screen parses recipesJson.

Principle:
Store facts (input, result, time). Compute derived values
(date format, labels such as "Variant 1 of 3") when displaying.

Constraint:
Never use OnConflictStrategy.REPLACE for history.
The history is a log of facts: each run adds a new row.
The list is ordered by createdAt DESC.

## 15. Single Save Point (Lab 4)

Decision:
The result is saved in one place only: in RecipeViewModel,
immediately after the response is validated
(exactly three recipes received) and before the state becomes Success.

Reason:
Error branches (HTTP errors, network errors, invalid response)
must never create a "ready" record.

Decision:
A failure to save must not hide the recipes from the user.
The save is wrapped in its own try/catch.

## 16. Screen Navigation (Lab 4)

Decision:
Switch between the main, history and details screens
with a simple state variable in FridgyApp
instead of adding the Navigation library.

Reason:
Three screens do not justify a new dependency.

## 17. Database Schema Version (Lab 4)

Decision:
AppDatabase has version 1 and exportSchema = false.
No migrations exist yet and no destructive fallback is configured.

Constraint:
Any future schema change requires either a Room Migration
or an explicit decision to use a destructive fallback,
documented in known-limitations.md.

## 18. Data That Is Not Stored (Lab 4)

- API keys, tokens and other secrets.
- Backend errors and technical error messages.
- Incomplete or invalid AI responses.
- Requests that did not produce a result.
- Derived values (formatted dates, labels).

## 19. Lab 5 Scope: Variant B, One Scenario (2026-11-17)

Decision:
Refactor the FastAPI backend (variant B) for one scenario:
generation of three recipes (POST /recipe).

Reason:
The backend is a single file (main.py) that mixed routing,
prompt building, the Gemini SDK call, validation and error mapping.
Backend tests also need no emulator.

Constraint:
The Android application, the API contract and the run command
(uvicorn main:app) must not change.

## 20. Provider Interface and Two Implementations (Lab 5)

Decision:
Hide the external AI behind RecipeProvider (typing.Protocol) with one method:
generate(query) -> list[Recipe].
Two implementations: GeminiProvider (real) and MockProvider (fake,
success and error modes).

Reason:
The Gemini call is the external dependency that makes the application
logic impossible to test without network and an API key.
Protocol was chosen because implementations do not need a common base class.

Constraint:
AI SDK types must not leave the infrastructure layer
(gemini_provider.py). The provider returns domain Recipe objects
or domain errors.

## 21. Service Owns Business Rules (Lab 5)

Decision:
RecipeService calls the provider with a timeout and validates the result:
exactly three recipes, non-empty unique names (case-insensitive),
ingredients present, 3-10 steps, cooking time from 1 minute to the user's limit.

Reason:
These rules belong to the application, not to a particular AI provider,
so they must hold for every provider.

## 22. Domain Errors and Central HTTP Mapping (Lab 5)

Decision:
Errors are categories in fridgy/domain/errors.py. The mapping to HTTP codes
and user messages is done in one place: api/error_handlers.py.

Mapping:
NotConfigured 503, Unavailable 503, QuotaExceeded 429, Timeout 504,
InvalidResponse 502, other provider errors 502.

Constraint:
The user never receives a stack trace or the technical error text.
User-facing messages are kept identical to the pre-refactoring ones.

Known compromise:
GeminiProvider still classifies SDK errors by searching substrings
in the error text. The fragile code is isolated in one function.

## 23. Manual Dependency Injection with FastAPI Depends (Lab 5)

Decision:
Create dependencies in one composition root (api/dependencies.py) using
FastAPI Depends. Replace implementations in tests with
app.dependency_overrides. No DI framework is used.

Reason:
There are only three dependencies (settings, provider, service);
a DI framework would add complexity without benefit.

## 24. Centralized Configuration (Lab 5)

Decision:
All settings (AI_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL, AI_TIMEOUT_S)
are read in fridgy/core/config.py from backend/.env.
AI_PROVIDER selects the implementation: gemini (default) or mock.

Constraint:
Secrets stay in backend/.env and are never logged or committed.
Changing .env requires restarting the server.

## 25. Entry Point and Contract Compatibility (Lab 5)

Decision:
backend/main.py remains the entry point and exposes the app object.
The JSON contract is unchanged. Two additions do not break clients:
the response header X-Request-ID, and source = "mock" when the mock
provider is selected.

## 26. Control Extension: request_id (Lab 5)

Decision:
Every response carries the X-Request-ID header and every log line
contains the request id. A safe incoming X-Request-ID
(letters, digits, dot, underscore, hyphen, up to 64 characters) is reused,
otherwise a new identifier is generated.

Reason:
The request id is kept in a contextvar, so it reaches the service and the
provider without changing their code. This shows that the new boundaries work.

## 27. Tests Without External Dependencies (Lab 5)

Decision:
Tests use MockProvider, a fake Gemini client and dependency_overrides.
They do not call the network and do not use real API keys.
The baseline tests written before the refactoring (commit 4a59838)
were replaced by tests of the new structure that check the same HTTP codes.
