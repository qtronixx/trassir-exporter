FROM python:3.11-slim

LABEL maintainer="Your Name <your.email@example.com>"
LABEL description="TRASSIR Prometheus Exporter"
LABEL version="1.0.0"

WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY trassir_exporter.py .

# Создаем непривилегированного пользователя
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "trassir_exporter.py"]
