# Установка TRASSIR Exporter

## Требования

- Docker 20.10+
- Docker Compose 2.0+
- Доступ к TRASSIR серверам по HTTPS (порт 8080)
- Prometheus 2.x (для сбора метрик)
- Grafana (для визуализации, опционально)

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-org/trassir-exporter.git
cd trassir-exporter
```
2. Настройка переменных окружения
```bash
cp .env.example .env
nano .env
```
Заполните данные ваших TRASSIR серверов:

env
TRASSIR_1_NAME=main-server
TRASSIR_1_HOST=192.168.1.10
TRASSIR_1_PORT=8080
TRASSIR_1_USER=apiusr
TRASSIR_1_PASSWORD=your_password

TRASSIR_2_NAME=backup-server
TRASSIR_2_HOST=192.168.1.11
TRASSIR_2_PORT=8080
TRASSIR_2_USER=apiusr
TRASSIR_2_PASSWORD=your_password
3. Запуск экспортера
```bash
docker compose up -d
```
4. Проверка работы
```bash
# Health check
curl http://localhost:8000/health

# Проверка метрик
curl http://localhost:8000/metrics | grep trassir_up
```
5. Просмотр логов
```bash
docker compose logs -f trassir-exporter
```
Установка без Docker
1. Установка Python зависимостей
```bash
cd exporter
pip install -r requirements.txt
```
2. Настройка переменных окружения
```bash
export TRASSIR_1_NAME=main-server
export TRASSIR_1_HOST=192.168.1.10
export TRASSIR_1_PORT=8080
export TRASSIR_1_USER=apiusr
export TRASSIR_1_PASSWORD=your_password
export SCRAPE_INTERVAL=60
export EXPORTER_PORT=8000
export TIMEOUT=10
```
3. Запуск
```bash
python trassir_exporter.py
```
Настройка Prometheus
Добавьте в prometheus.yml:

```yaml
scrape_configs:
  - job_name: 'trassir'
    scrape_interval: 60s
    static_configs:
      - targets: ['10.10.64.100:8000']
    metrics_path: '/metrics'
```
Перезагрузите Prometheus:

```bash
curl -X POST http://localhost:9090/-/reload
```
Настройка Grafana
Добавьте источник данных Prometheus

Импортируйте дашборд из grafana/dashboard.json

Настройте алерты при необходимости

Проверка работы
Откройте в браузере:

Экспортер: http://10.10.64.100:8000/metrics

Prometheus: http://localhost:9090/targets

Grafana: http://localhost:3000


## 📄 docs/configuration.md


## 📄 docs/metrics.md

