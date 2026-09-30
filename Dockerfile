FROM python:3.12-slim-bookworm

# Copy static uv binary directly from Astral official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_URL="sqlite:////app/data/ash_archive.db" \
    PATH="/app/.venv/bin:$PATH"

# Install dependencies using uv into system environment
COPY pyproject.toml* uv.lock* requirements.txt* ./
RUN if [ -f pyproject.toml ]; then uv pip install --system --no-cache -r pyproject.toml || uv sync --system; \
    elif [ -f requirements.txt ]; then uv pip install --system --no-cache -r requirements.txt; \
    else uv pip install --system --no-cache fastapi "uvicorn[standard]" sqlalchemy pydantic httpx; fi

# Ensure persistent ledger mount directory exists
RUN mkdir -p /app/data

# Copy application files
COPY engine/ /app/engine/
COPY rituals/ /app/rituals/
COPY visualizer.html /app/visualizer.html

EXPOSE 8000

# Invoke module directly to prevent PATH lookup issues
CMD ["python", "-m", "uvicorn", "engine.main:app", "--host", "0.0.0.0", "--port", "8000"]
