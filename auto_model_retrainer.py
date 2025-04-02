# auto_model_retrainer.py

import logging
from train_lstm_model import train_lstm_model
from train_xgb import train_xgb_model
from weights_optimizer import optimize_weights
from notifier import send_telegram_message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ✅ تدريب جميع النماذج تلقائيًا
def retrain_all_models():
    try:
        send_telegram_message("🧠 بدء إعادة تدريب نماذج التداول...")
        logging.info("🔁 بدء تدريب نموذج LSTM...")
        train_lstm_model()

        logging.info("🔁 بدء تدريب نموذج XGBoost...")
        train_xgb_model()

        logging.info("🔁 تحسين الأوزان بناءً على الأداء...")
        optimize_weights()

        send_telegram_message("✅ تم الانتهاء من إعادة تدريب النماذج وتحسين الأوزان.")
        logging.info("🎯 تم إعادة تدريب كل النماذج بنجاح.")

    except Exception as e:
        logging.error(f"❌ [Auto Retrainer] فشل في إعادة التدريب: {e}")
        send_telegram_message(f"❌ فشل في إعادة التدريب التلقائي: {e}")
