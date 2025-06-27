import os
import json
import datetime
import requests
from flask import Flask, request

app = Flask(__name__)

LOG_FILE = "honeypot_log.txt"
ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK")  # Your Discord alert webhook URL here


def log_attempt(ip, headers, payload):
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    log_entry = {
        "timestamp": timestamp,
        "ip": ip,
        "headers": dict(headers),
        "payload": payload
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, indent=2) + "\n\n")

    print(f"[{timestamp}] Logged attempt from IP: {ip}")


def send_alert(ip, payload):
    if ALERT_WEBHOOK:
        try:
            msg = f"🚨 **Honeypot triggered** by `{ip}`\n```json\n{json.dumps(payload, indent=2)}\n```"
            requests.post(ALERT_WEBHOOK, json={"content": msg})
        except Exception as e:
            print(f"Failed to send alert: {e}")


@app.route("/", methods=["POST"])
def fake_webhook():
    # Get IP (support proxies)
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    headers = request.headers
    try:
        payload = request.get_json(force=True)
    except Exception:
        payload = request.data.decode("utf-8")

    # Log all attempts for evidence
    log_attempt(ip, headers, payload)

    # Send alert to Discord
    send_alert(ip, payload)

    # Respond with 204 No Content (like Discord)
    return "", 204


@app.route("/", methods=["GET"])
def index():
    return "This is a fake Discord webhook endpoint for security monitoring."


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
