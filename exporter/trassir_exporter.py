#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TRASSIR Prometheus Exporter
Collects metrics from TRASSIR video surveillance servers and exports them
in Prometheus format.

Usage:
    docker compose up -d
    curl http://localhost:8000/metrics

Environment variables:
    TRASSIR_N_NAME, TRASSIR_N_HOST, TRASSIR_N_PORT, TRASSIR_N_USER, TRASSIR_N_PASSWORD
    SCRAPE_INTERVAL, EXPORTER_PORT, TIMEOUT
"""

import os
import time
import logging
import threading
import re
import json
from datetime import datetime
from typing import Dict, List, Optional

import requests
import urllib3
from prometheus_client import Gauge, generate_latest, CollectorRegistry
from flask import Flask, Response
from dotenv import load_dotenv

# Отключаем предупреждения о самоподписанных сертификатах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения
EXPORTER_PORT = int(os.getenv('EXPORTER_PORT', 8000))
TIMEOUT = int(os.getenv('TIMEOUT', 10))
SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', 60))

# Сессия с отключенной проверкой SSL (для старых сертификатов)
session = requests.Session()
session.verify = False

# Регистр метрик
registry = CollectorRegistry()

# Метрики
trassir_up = Gauge('trassir_up', 'TRASSIR server is up (1) or down (0)', ['server'], registry=registry)
trassir_version = Gauge('trassir_version_info', 'TRASSIR server version', ['server', 'version'], registry=registry)
trassir_cameras_total = Gauge('trassir_cameras_total', 'Total number of cameras', ['server'], registry=registry)
trassir_cameras_online = Gauge('trassir_cameras_online', 'Number of online cameras', ['server'], registry=registry)
trassir_cameras_offline = Gauge('trassir_cameras_offline', 'Number of offline cameras', ['server'], registry=registry)
trassir_cpu_usage = Gauge('trassir_cpu_usage_percent', 'CPU usage percent', ['server'], registry=registry)
trassir_disks_ok = Gauge('trassir_disks_ok', 'Disks status (1=ok, 0=error)', ['server'], registry=registry)
trassir_database_ok = Gauge('trassir_database_ok', 'Database status (1=ok, 0=error)', ['server'], registry=registry)
trassir_network_ok = Gauge('trassir_network_ok', 'Network status (1=ok, 0=error)', ['server'], registry=registry)
trassir_automation_ok = Gauge('trassir_automation_ok', 'Automation status (1=ok, 0=error)', ['server'], registry=registry)
trassir_uptime = Gauge('trassir_uptime_seconds', 'Server uptime in seconds', ['server'], registry=registry)
trassir_disks_stat_main_days = Gauge('trassir_disks_stat_main_days', 'Main stream archive depth in days', ['server'], registry=registry)
trassir_disks_stat_subs_days = Gauge('trassir_disks_stat_subs_days', 'Sub stream archive depth in days', ['server'], registry=registry)
trassir_scrape_duration = Gauge('trassir_scrape_duration_seconds', 'Scrape duration', ['server'], registry=registry)
trassir_last_scrape = Gauge('trassir_last_scrape_timestamp', 'Last scrape timestamp', ['server'], registry=registry)


def clean_json_response(text: str) -> str:
    """Удаляет комментарии в стиле C (/* ... */) из JSON ответа"""
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    return text.strip()


def get_servers() -> List[Dict]:
    """Загружает список TRASSIR серверов из переменных окружения"""
    servers = []
    i = 1
    while True:
        name = os.getenv(f'TRASSIR_{i}_NAME')
        host = os.getenv(f'TRASSIR_{i}_HOST')
        if not name or not host:
            break
        servers.append({
            'name': name,
            'host': host,
            'port': os.getenv(f'TRASSIR_{i}_PORT', '8080'),
            'user': os.getenv(f'TRASSIR_{i}_USER', ''),
            'password': os.getenv(f'TRASSIR_{i}_PASSWORD', ''),
        })
        i += 1
    logger.info(f"Loaded {len(servers)} TRASSIR servers")
    return servers


def get_session(server: Dict) -> Optional[str]:
    """Получает сессию для работы с TRASSIR через login"""
    try:
        base_url = f"https://{server['host']}:{server['port']}"
        params = {'username': server['user'], 'password': server['password']}
        response = session.get(f"{base_url}/login", params=params, timeout=TIMEOUT)
        if response.status_code == 200:
            cleaned_text = clean_json_response(response.text)
            data = json.loads(cleaned_text)
            if data.get('success') == 1:
                return data.get('sid')
            logger.error(f"{server['name']}: Login failed - {data}")
        else:
            logger.error(f"{server['name']}: Login HTTP {response.status_code}")
    except Exception as e:
        logger.error(f"{server['name']}: Failed to get session - {e}")
    return None


def fetch_server_status(server: Dict, sid: str) -> Optional[Dict]:
    """Получает статус сервера через TRASSIR API с использованием сессии"""
    start_time = time.time()
    
    try:
        base_url = f"https://{server['host']}:{server['port']}"
        
        response = session.get(f"{base_url}/health", params={'sid': sid}, timeout=TIMEOUT)
        if response.status_code != 200:
            logger.warning(f"{server['name']}: Health HTTP {response.status_code}")
            return None
        
        cleaned_text = clean_json_response(response.text)
        try:
            data = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error(f"{server['name']}: JSON decode error - {e}")
            logger.debug(f"Raw response (first 500 chars): {response.text[:500]}")
            return None
        
        channels_response = session.get(f"{base_url}/channels", params={'sid': sid}, timeout=TIMEOUT)
        
        total_cameras = 0
        online_cameras = 0
        
        if channels_response.status_code == 200:
            cleaned_channels = clean_json_response(channels_response.text)
            try:
                channels_data = json.loads(cleaned_channels)
                channels = channels_data.get('channels', [])
                total_cameras = len(channels)
                for ch in channels:
                    if ch.get('have_mainstream') == '1' or ch.get('have_substream') == '1':
                        online_cameras += 1
            except json.JSONDecodeError as e:
                logger.error(f"{server['name']}: Channels JSON decode error - {e}")
        
        duration = time.time() - start_time
        
        return {
            'version': data.get('version', 'unknown'),
            'cpu_load': float(data.get('cpu_load', 0)),
            'uptime': int(data.get('uptime', 0)),
            'disks': data.get('disks', '0') == '1',
            'database': data.get('database', '0') == '1',
            'network': data.get('network', '0') == '1',
            'automation': data.get('automation', '0') == '1',
            'channels_total': total_cameras,
            'channels_online': online_cameras,
            'channels_offline': total_cameras - online_cameras,
            'disks_stat_main_days': float(data.get('disks_stat_main_days', 0)),
            'disks_stat_subs_days': float(data.get('disks_stat_subs_days', 0)),
            'scrape_duration': duration,
            'timestamp': datetime.now().timestamp()
        }
        
    except requests.exceptions.Timeout:
        logger.error(f"{server['name']}: Timeout")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"{server['name']}: Connection error - {e}")
        return None
    except Exception as e:
        logger.error(f"{server['name']}: Error - {e}")
        return None


def update_metrics():
    """Обновляет все метрики для всех серверов"""
    for server in get_servers():
        logger.info(f"Scraping {server['name']} at {server['host']}:{server['port']}...")
        
        sid = get_session(server)
        if not sid:
            trassir_up.labels(server=server['name']).set(0)
            logger.warning(f"❌ {server['name']}: DOWN - authentication failed")
            continue
        
        data = fetch_server_status(server, sid)
        if data:
            trassir_up.labels(server=server['name']).set(1)
            trassir_version.labels(server=server['name'], version=data['version']).set(1)
            trassir_cameras_total.labels(server=server['name']).set(data['channels_total'])
            trassir_cameras_online.labels(server=server['name']).set(data['channels_online'])
            trassir_cameras_offline.labels(server=server['name']).set(data['channels_offline'])
            trassir_cpu_usage.labels(server=server['name']).set(data['cpu_load'])
            trassir_uptime.labels(server=server['name']).set(data['uptime'])
            trassir_disks_ok.labels(server=server['name']).set(1 if data['disks'] else 0)
            trassir_database_ok.labels(server=server['name']).set(1 if data['database'] else 0)
            trassir_network_ok.labels(server=server['name']).set(1 if data['network'] else 0)
            trassir_automation_ok.labels(server=server['name']).set(1 if data['automation'] else 0)
            trassir_disks_stat_main_days.labels(server=server['name']).set(data['disks_stat_main_days'])
            trassir_disks_stat_subs_days.labels(server=server['name']).set(data['disks_stat_subs_days'])
            trassir_scrape_duration.labels(server=server['name']).set(data['scrape_duration'])
            trassir_last_scrape.labels(server=server['name']).set(data['timestamp'])
            
            logger.info(f"✅ {server['name']}: {data['channels_online']}/{data['channels_total']} cameras, "
                       f"CPU {data['cpu_load']}%, Uptime {data['uptime']}s, "
                       f"Archive: {data['disks_stat_main_days']:.1f}/{data['disks_stat_subs_days']:.1f} days")
        else:
            trassir_up.labels(server=server['name']).set(0)
            logger.warning(f"❌ {server['name']}: DOWN - no data")


def background_scraper():
    """Фоновый сбор метрик"""
    logger.info(f"Starting scraper (interval: {SCRAPE_INTERVAL}s)")
    while True:
        try:
            update_metrics()
        except Exception as e:
            logger.error(f"Scraper error: {e}")
        time.sleep(SCRAPE_INTERVAL)


@app.route('/metrics')
def metrics():
    """Endpoint для Prometheus"""
    return Response(generate_latest(registry), mimetype='text/plain')


@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.route('/')
def index():
    """Информационная страница"""
    return {
        "service": "TRASSIR Prometheus Exporter",
        "version": "1.0.0",
        "endpoints": {
            "metrics": "/metrics",
            "health": "/health"
        }
    }


# Запускаем фоновый сбор метрик при старте приложения (для Gunicorn)
background_thread = threading.Thread(target=background_scraper, daemon=True)
background_thread.start()

# Для локального запуска (flask run)
if __name__ == '__main__':
    logger.info(f"Starting TRASSIR exporter on port {EXPORTER_PORT}")
    app.run(host='0.0.0.0', port=EXPORTER_PORT, debug=False)
