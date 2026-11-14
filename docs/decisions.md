
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
