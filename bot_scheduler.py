# bot_scheduler.py

import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from bot import run_bot_once
from auto_model_retrainer import retrain_all_models
from evaluate_bot_decisions import evaluate_bot_decisions
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ جدولة تنفيذ البوت كل دقيقة
def schedule_bot_run():
    scheduler = BlockingScheduler()

    # 🧠 كل دقيقة: تشغيل البوت
    scheduler.add_job(run_bot_once, 'interval', minutes=1, id='run_bot', name='تشغيل البوت')

    # 📈 كل ساعة: تحليل قرارات البوت وتحديث الدقة
    scheduler.add_job(evaluate_bot_decisions, 'interval', hours=1, id='evaluate_bot', name='تقييم قرارات البوت')

    # 🤖 كل 6 ساعات: إعادة تدريب النماذج وتحسين الأوزان
    scheduler.add_job(retrain_all_models, 'interval', hours=6, id='retrain_models', name='تدريب النماذج')

    logging.info("✅ تم بدء جدولة تشغيل البوت...")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.warning("🛑 تم إيقاف الجدولة.")

if __name__ == "__main__":
    schedule_bot_run()
