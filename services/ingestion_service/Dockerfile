FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY services/ingestion_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY shared_lib ./shared_lib
COPY services/ingestion_service ./services/ingestion_service

EXPOSE 8000

WORKDIR /app/services/ingestion_service
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
