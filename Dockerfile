FROM python:3.13-slim AS backend

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache -e ".[all]"

COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

EXPOSE 8000

CMD ["uvicorn", "studyagent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
