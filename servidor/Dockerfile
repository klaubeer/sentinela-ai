FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

RUN pip install --no-cache-dir \
    fastapi>=0.111 \
    "uvicorn[standard]>=0.30" \
    "sqlalchemy[asyncio]>=2.0" \
    asyncpg>=0.29 \
    alembic>=1.13 \
    pydantic>=2.0 \
    pydantic-settings>=2.0 \
    openai>=1.30 \
    python-dotenv>=1.0 \
    httpx>=0.27 \
    "celery[redis]>=5.3"

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
