
# Fridgy — AI Coding Instructions

## General Rules

1. Before making changes, read the project documentation in docs/ and inspect the actual repository structure and relevant source files.

2. First explain the current implementation and propose a clear implementation plan before writing code.

3. Always list the files that need to be changed and explain why each change is necessary.

4. Never rewrite the entire project or replace existing architecture for a small feature. Make minimal, focused changes.

5. Do not change the API contract without explaining why the change is necessary and updating the corresponding documentation and Android models.

6. Do not add new dependencies without explaining their purpose and why existing libraries are insufficient.

7. Never store API keys, passwords, tokens or other secrets in source code, prompts, logs or Git commits.

8. Add or update tests for new functionality. Also verify that existing functionality continues to work.

9. After implementation, summarize:
    - Files changed.
    - Changes made.
    - Tests and commands executed.
    - Test results.
    - Known risks and remaining issues.
    - Documentation that needs updating.

## Fridgy-Specific Rules

10. Preserve the existing architecture:
    - Android: Kotlin, Jetpack Compose, ViewModel, StateFlow.
    - Networking: Retrofit and Gson.
    - Backend: Python and FastAPI.
    - AI: Google Gemini API on the backend.

11. Never move Gemini API calls or API keys into the Android application. Keep AI integration on the backend.

12. Preserve the existing recipe generation workflow and cooking time validation. A recipe must not exceed the maximum cooking time specified by the user.

13. Do not assume that a feature exists just because it is described in a project idea. Check the actual implementation before modifying it.

14. Preserve compatibility with the existing API endpoints:
    - GET /health
    - POST /recipe

    Any required API changes must be coordinated between Android and backend.

15. Do not modify unrelated files or perform unnecessary refactoring.

16. The POST /recipe endpoint must return exactly three recipe suggestions. Keep the backend response schema and Android List<RecipeResponse> model synchronized.
## Development Workflow

For every new feature:

1. Analyze the existing implementation.
2. Read relevant Knowledge Base documents.
3. Propose a minimal implementation plan.
4. Wait for approval before making code changes.
5. Implement one small step at a time.
6. Review the Git diff.
7. Run relevant tests and verify the previous functionality.
8. Update Knowledge Base documentation.

If something is unclear, ask for clarification instead of inventing an implementation.
