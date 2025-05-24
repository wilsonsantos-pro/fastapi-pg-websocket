# FROM python:3.10-slim

# WORKDIR /app

# COPY . .

# RUN pip install --no-cache-dir fastapi[standard] sqlalchemy psycopg2-binary

# # CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# Base stage: installs deps
FROM python:3.10-slim AS base

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Poetry and system deps
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false \
 && poetry install --no-root

# App source
COPY . .

# ------------------------------------------------
# Dev stage: uses base, adds dev dependencies
FROM base AS dev

RUN poetry install --only dev

CMD ["fastapi", "dev", "fastapi_pg_websocket/main.py", "--host", "0.0.0.0"]

# ------------------------------------------------
# Test stage: uses base, runs tests
FROM base AS test

RUN poetry install --only dev

CMD ["pytest", "tests/"]

# ------------------------------------------------
# Prod stage: optimized for deployment
FROM base AS prod

RUN poetry install --only main

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
