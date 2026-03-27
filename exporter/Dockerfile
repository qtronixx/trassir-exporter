FROM python:3.11-slim

LABEL maintainer="Dmitry <qtronixx@example.com>"
LABEL description="TRASSIR Prometheus Exporter"
LABEL version="1.0.0"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY trassir_exporter.py .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Запускаем через gunicorn вместо flask
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--access-logfile", "-", "--error-logfile", "-", "trassir_exporter:app"]
