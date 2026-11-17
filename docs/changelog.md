# Fridgy — Changelog

## Lab 5 — Backend architecture, variant B (2026-11-17)

### Added
- Package `backend/fridgy` with layers: api, services, domain, infrastructure, core.
- RecipeProvider interface (Protocol) with two implementations:
  GeminiProvider and MockProvider.
- RecipeService with the business rules and the timeout.
- Domain errors and central HTTP error mapping.
- Composition root with FastAPI Depends and the AI_PROVIDER setting
  (gemini or mock) in backend/.env.
- Centralized configuration (core/config.py).
- Control extension: end-to-end request_id (X-Request-ID response header and
  request id in every log line).
- Automated tests (65, without network and API keys), requirements-dev.txt, pytest.ini.

### Changed
- backend/main.py is now a 43-line entry point.
- Response `source` is "mock" when AI_PROVIDER=mock.
- Server startup uses lifespan instead of deprecated on_event handlers.
- FastAPI application version 2.3.0.

### Not changed
- Android application, API contract (GET /health, POST /recipe, JSON format),
  run command (uvicorn main:app).

### Documentation
- Updated: README, architecture.md (before / after), decisions.md,
  known-limitations.md, testing.md, ai-component.md, api-contract.md,
  project-overview.md.

## Lab 4 — Local history (2026-11-14)

### Added
- Room database `fridgy.db` (version 1) with table `history_entries`.
- HistoryEntity, HistoryDao, AppDatabase (package `data.local`).
- HistoryRepository between the DAO and ViewModels.
- HistoryViewModel and screens: history list (loading, empty state, list)
  and details (input, three recipes, mark "saved result").
- Deletion of a single record and clearing of the whole history,
  both with a confirmation dialog.
- Button "Історія рецептів" on the main screen and a simple
  screen switcher (FridgyApp).
- Dependencies: Room 2.8.4 (runtime, ktx, compiler) and the KSP plugin.

### Changed
- RecipeViewModel became AndroidViewModel. After a validated result
  (exactly three recipes) it saves a new history record.
  Error branches save nothing.

### Not changed
- Backend, AI component and the API contract (GET /health, POST /recipe).

### Documentation
- Updated: README, architecture.md, requirements.md, testing.md,
  known-limitations.md, decisions.md.
- Corrected outdated statements about "one recipe per request"
  and "multiple recipes planned" in requirements.md and known-limitations.md.

### Not implemented
- Advanced level: offline requests with status "pending".
- Automated tests for local storage.

## Earlier work (Labs 1–3)

See the lab reports and the Git history of the repository.
