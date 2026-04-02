import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)

LOGS_DIR = Path("/app/logs")
LOG_FILE = LOGS_DIR / "app.log"


def create_log_file():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.touch()


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


@app.get("/")
def root():
    return os.getenv("WELCOME_MESSAGE", "Welcome to the custom app")


@app.get("/status")
def status():
    return jsonify({"status": "ok"})


@app.post("/log")
def write_log():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message")
    if not message or not isinstance(message, str):
        return jsonify({"error": "message is required"}), 400
    create_log_msg(message)
    return jsonify({"result": "written"})


@app.get("/logs")
def logs():
    return read_logs(), 200, {"Content-Type": "text/plain; charset=utf-8"}


if __name__ == "__main__":
    create_log_file()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
    port = int(os.getenv("APP_PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
