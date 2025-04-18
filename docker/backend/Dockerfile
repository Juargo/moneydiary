FROM python:3.11-slim AS builder

WORKDIR /app

COPY apps/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY apps/api /app/apps/api

# Stage de producción
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/apps/api /app/apps/api

ARG APP_VERSION
ENV APP_VERSION=${APP_VERSION}

EXPOSE 8000

CMD ["uvicorn", "apps.api.app.main:app", "--host", "0.0.0.0"]
