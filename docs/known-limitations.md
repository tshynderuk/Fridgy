
# Fridgy — Known Limitations

## 1. General Limitations

Fridgy is currently an MVP (Minimum Viable Product).

The application supports recipe generation using products entered by the user and a maximum cooking time, and keeps a local history of successful results.

The current implementation does not include all planned features.

## 2. AI Limitations

- One API request generates three recipes.
- AI-generated recipes may vary in quality.
- Recipe generation depends on Google Gemini availability and daily quota.
- Gemini may return 429 (quota) or 503 (high demand); these errors are temporary.
- AI response time may vary.
- The model may occasionally return an invalid response.
- Recipe recommendations are generated dynamically and are not retrieved from a verified recipe database.

## 3. Cooking Time Limitations

- Cooking time is estimated by Gemini.
- Backend checks that the returned time does not exceed the user's limit.
- The application does not measure actual cooking duration.
- The system does not independently verify the real-world preparation time.

Important:
The time validation checks the value returned by AI. It does not guarantee that the dish can actually be prepared within that duration.

## 4. Ingredient Limitations

Current input restrictions:

- Minimum: 1 product.
- Maximum: 30 products.
- Maximum product name length: 50 characters.

The Android ViewModel splits the entered ingredient text using commas.

Backend removes duplicate products and normalizes whitespace.

The backend prompt instructs Gemini to use the provided products as the main ingredients.

However, backend does not independently verify that every ingredient in the generated recipe exists in the user's original list.

## 5. Response Limitations

The current RecipeResponse (one recipe) contains:

- recipe_name
- cooking_time_minutes
- ingredients
- instructions
- source

POST /recipe returns a list of exactly three RecipeResponse objects.

There is no confirmed support for:
- Nutritional information.
- Calorie calculation.
- Dietary classification.
- Allergen detection.
- Recipe images.
- Ingredient substitution recommendations.

## 6. Backend Limitations

- Backend currently runs on a local development server.
- Android Emulator uses 10.0.2.2 to access the host computer.
- Gemini API requires an internet connection.
- Gemini API may return 429, 503 or other errors.
- AI generation may exceed the configured timeout.

## 7. Android Limitations

The reviewed Android implementation includes:

- Loading, success and error states.
- Manual ingredient input.
- Manual cooking time input.
- Display of three recipe cards.
- Local history, history details and deletion (see section 8).

RecipeUiState.Success stores a list of recipes (List<RecipeResponse>).

Screen switching (main / history / details) is implemented with a simple state variable, not with the Navigation library.

## 8. Local History Limitations (Lab 4)

Stored per record: local id, date and time, a short summary of the input (up to 150 characters), the time limit, the names of the dishes, the full result as JSON, the status.

Deliberately not stored:
- API keys, tokens and other secrets.
- Backend errors and technical error messages.
- Incomplete or invalid AI responses.
- Requests that did not produce a result.

Limitations:
- The history exists only on the device. There is no synchronization between devices.
- Uninstalling the application removes the history.
- The full result is stored as JSON produced by Gson from RecipeResponse. Renaming or removing fields in RecipeResponse may make old records unreadable. In that case the details screen shows a "record not found or cannot be read" message.
- If saving to the local database fails, the error is not shown to the user: the recipes are still displayed, but no history record is created.
- The database schema has version 1 and no migrations. A future schema change requires a Room Migration or an explicitly documented destructive fallback. The schema is not exported (exportSchema = false).
- The AndroidManifest has allowBackup="true" with the default backup rules, so the application data may be included in Android automatic backup depending on device settings. This has not been configured or tested.
- There is no undo for deletion, no filtering by date and no pagination of the list.
- Requests made without network are not saved for later sending (the advanced level of Lab 4, status "pending", is not implemented).
- The saved results are historical. Open recipes are not re-validated and are not updated when the backend changes.
- Automated tests for the local storage are not implemented; verification was done manually on the emulator.

## 9. Features Not Confirmed in the Reviewed Code

The following features have not been confirmed in the reviewed implementation:

- User authentication.
- Cloud database.
- Favorite recipes.
- User profiles.
- Camera-based ingredient recognition.
- Barcode scanning.
- Offline recipe generation.
- Automated unit and integration tests.

These features must not be assumed to exist.

## 10. Development Constraints

When modifying Fridgy:

1. Preserve the existing Android architecture.
2. Preserve the existing API contract unless an API change is required.
3. Do not expose the Gemini API key in Android code.
4. Keep network requests asynchronous.
5. Preserve existing loading, success and error states.
6. Validate AI responses on the backend.
7. Check cooking time against the user's maximum.
8. Save to the local history only after a validated successful result.
9. Do not use OnConflictStrategy.REPLACE for history records; every run adds a new row.
10. Avoid unnecessary changes to unrelated files.

## 11. Future Improvements

Potential improvements:

- Improve cooking time accuracy.
- Add recipe favorites.
- Introduce dietary preferences.
- Improve recipe presentation.
- Add automated tests (including: backend error -> 0 records in the database).
- Add undo for deletion and filtering history by date.
- Add offline requests with "pending" status.
