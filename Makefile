.PHONY: run up tests lint migrate dev dev-watch dev-db dev-web

CREATE_DB_SCRIPT=create_db.py

run:
	pdm run uvicorn app.main:app --reload

up:
	docker compose up --build

dev-db:
	docker compose up --build -d db

dev-web:
	@echo "Starting web service with local Python environment..."
	pdm run uvicorn app.main:app --reload

dev: dev-db dev-web

create_db:
	pdm run python3 $(CREATE_DB_SCRIPT)

migrate:
	pdm run alembic upgrade head

tests:
	pytest

lint:
	ruff check .
