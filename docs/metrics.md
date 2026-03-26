# Метрики TRASSIR Exporter

## Список метрик

| Метрика | Тип | Описание | Пример |
|---------|-----|----------|--------|
| `trassir_up` | gauge | Статус сервера (1=работает, 0=недоступен) | `1` |
| `trassir_version_info` | gauge | Версия TRASSIR (значение всегда 1, метка version) | `1` |
| `trassir_cameras_total` | gauge | Общее количество камер | `16` |
| `trassir_cameras_online` | gauge | Количество работающих камер | `16` |
| `trassir_cameras_offline` | gauge | Количество неработающих камер | `0` |
| `trassir_cpu_usage_percent` | gauge | Загрузка CPU в процентах | `9.24` |
| `trassir_uptime_seconds` | gauge | Время работы сервера в секундах | `11750830` |
| `trassir_disks_ok` | gauge | Статус дисков (1=OK, 0=ошибка) | `1` |
| `trassir_database_ok` | gauge | Статус базы данных (1=OK, 0=ошибка) | `1` |
| `trassir_network_ok` | gauge | Статус сети (1=OK, 0=ошибка) | `1` |
| `trassir_automation_ok` | gauge | Статус автоматизации (1=OK, 0=ошибка) | `1` |
| `trassir_disks_stat_main_days` | gauge | Глубина архива основного потока (дни) | `211.6` |
| `trassir_disks_stat_subs_d
