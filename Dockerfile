FROM python:3.12-slim
WORKDIR /app

# Install timezone data (python:3.12-slim lacks it)
RUN apt-get update && apt-get install -y --no-install-recommends tzdata && rm -rf /var/lib/apt/lists/*

# Install backend dependencies
COPY backend/pyproject.toml backend/
COPY backend/app/ backend/app/
RUN pip install --no-cache-dir backend/

# Environment
ENV PORT=8000
EXPOSE 8000

WORKDIR /app/backend

# Single worker: APScheduler runs in-process background thread
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
