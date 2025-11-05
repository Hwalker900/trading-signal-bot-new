from flask import Flask, request
import requests
import datetime
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# === HARDCODED: NEW GROUP (TGBOT2) ===
BOT_TOKEN = "7776677134:AAGJo3VfwiB5gDpCE5e5jvtHonhTcjv-NWc"
CHAT_ID   = "-1002123456789"  # ← YOUR NEW GROUP ID

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10
        )
        r.raise_for_status()
        log.info("Sent to new group")
    except Exception as e:
        log.error(f"Telegram error: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        log.info(f"Webhook: {data}")
    except:
        return "Invalid JSON", 400

    if data.get('ticker') != 'XAUUSD':
        return "Only XAUUSD allowed", 400

    signal = data.get('signal')
    if signal in ['BUY', 'SELL']:
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

    return "OK", 200

log.info("TGBOT2 started — NO DISK, $0")
