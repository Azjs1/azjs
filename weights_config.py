import json
import os
import logging

WEIGHTS_FILE = "weights_config.json"

# ✅ تحميل الأوزان من الملف
def load_weights():
    if not os.path.exists(WEIGHTS_FILE):
        logging.warning(f"⚠️ لم يتم العثور على {WEIGHTS_FILE}، سيتم استخدام أوزان افتراضية.")
        return {
            "lstm": 1.0,
            "xgb": 1.0,
            "technical": 1.0,
            "sentiment": 1.0,
            "liquidity": 1.0,
            "rl": 1.0,
            "gpt": 1.0
        }

    with open(WEIGHTS_FILE, "r") as f:
        return json.load(f)
