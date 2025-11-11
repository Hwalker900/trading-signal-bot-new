from flask import Flask, request
import requests
import datetime
import logging
import os  # ← REQUIRED FOR PORT

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# === HARDCODED: NEW GROUP (TGBOT2) ===
BOT_TOKEN = "8591457462:AAGQfrP-rZ3QJCBp3oro8KfMWX5B083NYJ8"
CHAT_ID = "-1003236207321"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10
        )
        r.raise_for_status()
        log.info("SENT TO NEW GROUP")
    except Exception as e:
        log.error(f"TELEGRAM ERROR: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        log.info(f"WEBHOOK RECEIVED: {data}")
    except Exception as e:
        log.error(f"INVALID JSON: {e}")
        return "Invalid JSON", 400

    if data.get('ticker') != 'XAUUSD':
        log.warning(f"REJECTED: {data.get('ticker')} (only XAUUSD allowed)")
        return "Only XAUUSD allowed", 400

    signal = data.get('signal')
    if signal not in ['BUY', 'SELL']:
        log.warning(f"REJECTED: invalid signal {signal}")
        return "Invalid signal", 400

    entry = data.get('entry')
    sl = data.get('sl')
    if entry is None or sl is None:
        return "Missing entry/sl", 400

    try:
        float(entry), float(sl)
    except:
        return "Invalid numbers", 400

    t = datetime.datetime.now(datetime.UTC).strftime('%d %b %H:%M UTC')
    msg = f"**XAU/USD {signal}**\nEntry: {entry}\nSL: {sl}\nTime: {t}"
    send_telegram(msg)
    log.info(f"SIGNAL PROCESSED: {signal} at {entry}")

    return "OK", 200

# ADD THIS EXACTLY HERE
@app.route('/health')
def health():
    return "OK", 200
# END OF /health ENDPOINT

log.info("TGBOT2 STARTED — NO DISK, $0 — READY FOR SIGNALS")

# === KEEP FLASK ALIVE ===
if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
