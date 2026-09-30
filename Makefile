.PHONY: install dev test lint format clean

install:
	@echo "Weaving dependencies..."
	@uv sync

dev:
	@echo "Igniting the Engine..."
	@uv run uvicorn engine.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "Entering the Proving Grounds..."
	@uv run pytest

lint:
	@echo "Inspecting the weave..."
	@uv run ruff check .
	@uv run mypy engine/

format:
	@echo "Polishing the architecture..."
	@uv run ruff format .
	@uv run ruff check --fix .

clean:
	@echo "Purging the shadows..."
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@find . -type d -name ".pytest_cache" -exec rm -r {} +
	@find . -type d -name ".mypy_cache" -exec rm -r {} +
