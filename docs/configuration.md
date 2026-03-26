# Конфигурация TRASSIR Exporter

## Переменные окружения

### Настройка серверов TRASSIR

Для каждого сервера нужно указать:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `TRASSIR_N_NAME` | Имя сервера (для меток) | `main-server` |
| `TRASSIR_N_HOST` | IP адрес или имя хоста | `192.168.1.10` |
| `TRASSIR_N_PORT` | Порт TRASSIR API | `8080` |
| `TRASSIR_N_USER` | Имя пользователя | `apiusr` |
| `TRASSIR_N_PASSWORD` | Пароль | `password123` |

**Важно:** Нумерация должна быть последовательной (1, 2, 3...).

### Общие настройки

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `SCRAPE_INTERVAL` | Интервал сбора метрик (сек) | `60` |
| `EXPORTER_PORT` | Порт экспортера | `8000` |
| `TIMEOUT` | Таймаут запросов к TRASSIR (сек) | `10` |

## Пример .env файла

```env
# Сервер 1 - Основной
TRASSIR_1_NAME=moscow-hq
TRASSIR_1_HOST=10.10.10.248
TRASSIR_1_PORT=8080
TRASSIR_1_USER=apiusr
TRASSIR_1_PASSWORD=password123

# Сервер 2 - Резервный
TRASSIR_2_NAME=spb-office
TRASSIR_2_HOST=10.10.10.251
TRASSIR_2_PORT=8080
TRASSIR_2_USER=apiusr
TRASSIR_2_PASSWORD=password123

# Сервер 3 - Тестовый
TRASSIR_3_NAME=test-lab
TRASSIR_3_HOST=10.10.10.249
TRASSIR_3_PORT=8080
TRASSIR_3_USER=apiusr
TRASSIR_3_PASSWORD=password123

# Настройки
SCRAPE_INTERVAL=60
EXPORTER_PORT=8000
TIMEOUT=10
```
Docker Compose конфигурация
```yaml
version: '3.8'

services:
  trassir-exporter:
    build: ./exporter
    container_name: trassir-exporter
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - SCRAPE_INTERVAL=${SCRAPE_INTERVAL:-60}
      - EXPORTER_PORT=${EXPORTER_PORT:-8000}
      - TIMEOUT=${TIMEOUT:-10}
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```
Prometheus конфигурация
```yaml
scrape_configs:
  - job_name: 'trassir'
    scrape_interval: 60s
    scrape_timeout: 30s
    metrics_path: '/metrics'
    static_configs:
      - targets:
          - '10.10.64.100:8000'
        labels:
          environment: 'production'
          service: 'cctv'
          site: 'you_site_name'
```
Grafana конфигурация
Добавление источника данных
Перейдите в Configuration → Data Sources

Нажмите Add data source

Выберите Prometheus

URL: http://prometheus:9090

Нажмите Save & Test

Импорт дашборда
Перейдите в Dashboards → Import

Загрузите файл grafana/dashboard.json

Выберите источник данных Prometheus

Нажмите Import
