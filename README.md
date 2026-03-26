# TRASSIR Exporter for Prometheus

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://www.docker.com/)

Prometheus exporter для сбора метрик с серверов видеонаблюдения TRASSIR. Собирает данные о состоянии серверов, камерах, загрузке CPU, статусе дисков, глубине архива и других параметрах.

## 🎯 Возможности

- Мониторинг нескольких серверов TRASSIR одновременно
- Автоматическое получение и обновление сессий
- Сбор метрик через HTTPS с поддержкой старых SSL протоколов
- Экспорт метрик в формате Prometheus
- Docker-контейнер для простого развертывания

## 📊 Собираемые метрики

| Метрика | Описание |
|---------|----------|
| `trassir_up` | Статус сервера (1=работает, 0=недоступен) |
| `trassir_cameras_total` | Общее количество камер |
| `trassir_cameras_online` | Количество работающих камер |
| `trassir_cameras_offline` | Количество неработающих камер |
| `trassir_cpu_usage_percent` | Загрузка CPU (%) |
| `trassir_uptime_seconds` | Время работы сервера (сек) |
| `trassir_disks_ok` | Статус дисков |
| `trassir_database_ok` | Статус базы данных |
| `trassir_network_ok` | Статус сети |
| `trassir_disks_stat_main_days` | Глубина архива основного потока |
| `trassir_disks_stat_subs_days` | Глубина архива дополнительного потока |

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/qtronixx/trassir-exporter.git
cd trassir-exporter
```
### 2. Настройка
```bash
cp .env.example .env
# Отредактируйте .env, добавив данные ваших TRASSIR серверов
nano .env
```
### 3. Запуск
```bash
docker compose up -d
```
### 4. Проверка
```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics | grep trassir_up
```
### 📈 Настройка Prometheus
Добавьте в prometheus.yml:

```yaml
scrape_configs:
  - job_name: 'trassir'
    scrape_interval: 60s
    static_configs:
      - targets: ['your-exporter-host:8000']
    metrics_path: '/metrics'
```
### 📊 Готовый дашборд Grafana
Импортируйте дашборд из файла grafana/dashboard.json для быстрой визуализации всех метрик.

🔧 Переменные окружения
| Переменная |	Описание	| По умолчанию |
|---------|----------|----------|
| TRASSIR_N_NAME	| Имя сервера |	Обязательно |
| TRASSIR_N_HOST	| IP адрес сервера |	Обязательно |
| TRASSIR_N_PORT	| Порт TRASSIR |	8080 |
| TRASSIR_N_USER	| Имя пользователя	| apiusr |
| TRASSIR_N_PASSWORD |	Пароль	| Обязательно |
| SCRAPE_INTERVAL	| Интервал сбора метрик (сек) |	60 |
| EXPORTER_PORT	| Порт экспортера |	8000 |
| TIMEOUT	| Таймаут запросов (сек) |	10 |

📝 Лицензия
MIT License. См. файл LICENSE.

🤝 Вклад в проект
Приветствуются pull requests и issues!
