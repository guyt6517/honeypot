from flask import Flask, request
import datetime
import json
import os

app = Flask(__name__)

LOG_FILE = "honeypot_log.txt"

def log_attempt(ip, headers, payload):
    timestamp = datetime.datetime.now().isoformat()

    log_entry = {
        "timestamp": timestamp,
        "ip": ip,
        "headers": dict(headers),
        "payload": payload
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, indent=2) + "\n\n")

    print(f"[{timestamp}] Attempt logged from {ip}")

@app.route("/", methods=["POST"])
def fake_webhook():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    headers = request.headers
    try:
        payload = request.get_json(force=True)
    except:
        payload = request.data.decode("utf-8")

    log_attempt(ip, headers, payload)
    return "", 204  # Mimic Discord's empty 204 No Content response

@app.route("/", methods=["GET"])
def index():
    return "This is a fake Discord webhook endpoint for security monitoring."

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
