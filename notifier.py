import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logging.info("📤 تم إرسال إشعار Telegram بنجاح.")
        else:
            logging.warning(f"⚠️ فشل إرسال Telegram: {response.text}")
    except Exception as e:
        logging.error(f"❌ [Telegram Error] {e}")

def notify_trade_decision(symbol, decision, confidence, executed):
    """
    ترسل إشعار احترافي عند اتخاذ قرار تداول.
    """
    emoji = "✅" if executed else "ℹ️"
    message = (
        f"{emoji} *قرار تداول جديد*\n\n"
        f"🔹 *الرمز:* `{symbol}`\n"
        f"🧠 *القرار:* `{decision}`\n"
        f"📊 *الثقة:* `{confidence:.2f}`\n"
        f"⚙️ *تم التنفيذ:* `{executed}`"
    )
    send_telegram_message(message)
