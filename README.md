# FastAPI — Enterprise-ready template

This repository is a ready-to-use FastAPI starter with an opinionated, production-oriented layout:

- Async SQLAlchemy (asyncpg or aiosqlite)
- Routers → Services → Repositories separation
- Pydantic settings (.env-aware)
- Alembic-ready metadata import
- Docker + docker-compose (Postgres)
- Testing example (pytest + httpx)
- CI example (GitHub Actions) and pre-commit hooks

## Quick start (development)

1. Copy `.env.example` -> `.env` and customize (or rely on defaults).
2. Start Postgres + app (optional): `docker-compose up --build`.
3. For local quick run without Postgres the default DATABASE_URL is `sqlite+aiosqlite:///./app.db`.

4. Run the app:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Visit http://localhost:8000/docs

