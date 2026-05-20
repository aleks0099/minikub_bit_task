import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Summary, generate_latest

app = Flask(__name__)

CONFIG_DIR = Path("/app/config")
LOGS_DIR = Path("/app/logs")
LOG_FILE = LOGS_DIR / "app.log"

LOG_REQUESTS_TOTAL = Counter(
    "app_log_requests_total",
    "Total number of /log requests.",
)
LOG_ATTEMPTS_TOTAL = Counter(
    "app_log_write_attempts_total",
    "Total number of logging attempts.",
    ["result"],
)
LOG_REQUEST_PROCESSING_SECONDS = Summary(
    "app_log_request_processing_seconds",
    "Time spent processing /log requests.",
)
LOG_REQUEST_PROCESSING_SECONDS_AVERAGE = Gauge(
    "app_log_request_processing_seconds_average",
    "Average time spent processing /log requests.",
)
LOG_REQUEST_DURATION_LOCK = Lock()
LOG_REQUEST_DURATION_TOTAL = 0.0
LOG_REQUEST_DURATION_COUNT = 0


def create_log_file():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.touch()


def get_config_value(name: str, default: str):
    config_file = CONFIG_DIR / name
    if config_file.exists():
        value = config_file.read_text(encoding="utf-8").strip()
        if value:
            return value
    value = os.getenv(name)
    if value:
        return value
    return default


def create_log_msg(message: str):
    ts = datetime.now(timezone.utc).isoformat()
    line = f"{ts} {message}\n"
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line)
    print(line, end="", flush=True)


def read_logs():
    if not LOG_FILE.exists():
        return ""
    return LOG_FILE.read_text(encoding="utf-8")


def record_log_duration(duration: float):
    global LOG_REQUEST_DURATION_COUNT, LOG_REQUEST_DURATION_TOTAL
    LOG_REQUEST_PROCESSING_SECONDS.observe(duration)
    with LOG_REQUEST_DURATION_LOCK:
        LOG_REQUEST_DURATION_TOTAL += duration
        LOG_REQUEST_DURATION_COUNT += 1
        LOG_REQUEST_PROCESSING_SECONDS_AVERAGE.set(
            LOG_REQUEST_DURATION_TOTAL / LOG_REQUEST_DURATION_COUNT
        )


@app.get("/")
def root():
    return get_config_value("WELCOME_MESSAGE", "Welcome to the custom app")


@app.get("/status")
def status():
    return jsonify({"status": "ok"})


@app.post("/log")
def write_log():
    start = time.perf_counter()
    LOG_REQUESTS_TOTAL.inc()
    try:
        payload = request.get_json(silent=True) or {}
        message = payload.get("message")
        if not message or not isinstance(message, str):
            LOG_ATTEMPTS_TOTAL.labels(result="failure").inc()
            return jsonify({"error": "message is required"}), 400
        delay_seconds = request.headers.get("X-Delay-Seconds")
        if delay_seconds:
            try:
                time.sleep(float(delay_seconds))
            except ValueError:
                pass
        create_log_msg(message)
        LOG_ATTEMPTS_TOTAL.labels(result="success").inc()
        return jsonify({"result": "written"})
    except Exception:
        LOG_ATTEMPTS_TOTAL.labels(result="failure").inc()
        raise
    finally:
        record_log_duration(time.perf_counter() - start)


@app.get("/logs")
def logs():
    return read_logs(), 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    create_log_file()
    log_level = get_config_value("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
    port = int(get_config_value("APP_PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
