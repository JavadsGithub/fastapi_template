.PHONY: run up tests lint migrate

run:
	uvicorn app.main:app --reload

up:
	docker-compose up --build

migrate:
	alembic upgrade head

tests:
	pytest

lint:
	ruff check .
