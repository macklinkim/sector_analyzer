# Stage 1: Build frontend
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend + serve static
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install backend dependencies
COPY backend/pyproject.toml backend/
RUN pip install --no-cache-dir -e backend/

# Copy backend source
COPY backend/app/ backend/app/

# Copy frontend build output
COPY --from=frontend-build /app/frontend/dist/ frontend/dist/

# Environment
ENV PORT=8000
EXPOSE 8000

# Single worker: APScheduler runs in-process background thread
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
