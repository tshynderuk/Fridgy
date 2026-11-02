
# Fridgy — Known Limitations

## 1. General Limitations

Fridgy is currently an MVP (Minimum Viable Product).

The application supports basic recipe generation using products entered by the user and a maximum cooking time.

The current implementation does not include all planned features.

## 2. AI Limitations

- One API request generates only one recipe.
- AI-generated recipes may vary in quality.
- Recipe generation depends on Google Gemini availability.
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

The current RecipeResponse contains:

- recipe_name
- cooking_time_minutes
- ingredients
- instructions
- source

There is no confirmed support for:
- Multiple alternative recipes.
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

- One recipe result state.
- Loading state.
- Success state.
- Error state.
- Manual ingredient input.
- Manual cooking time input.

The current RecipeUiState.Success stores one RecipeResponse.

Multiple recipe cards are not supported by the current response model.

## 8. Features Not Confirmed in the Reviewed Code

The following features have not been confirmed in the reviewed implementation:

- User authentication.
- Cloud database.
- Recipe history.
- Favorite recipes.
- User profiles.
- Camera-based ingredient recognition.
- Barcode scanning.
- Offline recipe generation.
- Automated unit and integration tests.

These features must not be assumed to exist.

## 9. Development Constraints

When modifying Fridgy:

1. Preserve the existing Android architecture.
2. Preserve the existing API contract unless an API change is required.
3. Do not expose the Gemini API key in Android code.
4. Keep network requests asynchronous.
5. Preserve existing loading, success and error states.
6. Validate AI responses on the backend.
7. Check cooking time against the user's maximum.
8. Avoid unnecessary changes to unrelated files.

## 10. Future Improvements

Potential improvements:

- Generate three alternative recipes.
- Improve cooking time accuracy.
- Add recipe favorites.
- Add recipe history.
- Introduce dietary preferences.
- Improve recipe presentation.
- Add automated tests.
