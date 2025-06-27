import os
import json
import datetime
import requests
from flask import Flask, request

app = Flask(__name__)

LOG_FILE = "honeypot_log.txt"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")  # Your Discord webhook URL here

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

def send_discord_message(ip, content):
    if not DISCORD_WEBHOOK:
        return
    try:
        message = f"Webhook triggered by IP: `{ip}`.\nMessage:\n```{content}```"
        requests.post(DISCORD_WEBHOOK, json={"content": message})
    except Exception as e:
        print(f"Failed to send Discord message: {e}")

@app.route("/", methods=["POST"])
def fake_webhook():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    headers = request.headers
    try:
        payload = request.get_json(force=True)
    except Exception:
        payload = request.data.decode("utf-8")

    log_attempt(ip, headers, payload)

    # Extract message content for Discord message
    content = ""
    if isinstance(payload, dict):
        content = payload.get("content", str(payload))
    else:
        content = str(payload)

    send_discord_message(ip, content)

    return "", 204

@app.route("/", methods=["GET"])
def index():
    return "Fake Discord webhook endpoint for security monitoring."

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
