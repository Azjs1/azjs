import os
import json
import pandas as pd
import subprocess
from notifier import send_telegram_message

# عدد الصفقات المطلوبة قبل إعادة التدريب
TRAINING_INTERVAL = 50
DECISIONS_FILE = "bot_decisions.csv"
STATUS_FILE = "training_status.json"

# تحميل الحالة السابقة
def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {"last_trained_count": 0}

# حفظ الحالة الجديدة
def save_status(status):
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=4)

# تنفيذ سكربت تدريب
def run_script(script_path):
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    return result.stdout + "\n" + result.stderr

# الدالة الرئيسية
def main():
    if not os.path.exists(DECISIONS_FILE):
        print("❌ لا يوجد ملف bot_decisions.csv")
        return

    df = pd.read_csv(DECISIONS_FILE)
    executed_df = df[df["executed"] == True]
    executed_count = len(executed_df)

    status = load_status()
    last_trained = status.get("last_trained_count", 0)

    # تحقق إذا وصلنا للحد
    if executed_count - last_trained >= TRAINING_INTERVAL:
        send_telegram_message(f"🧠 بدأ تدريب النماذج بعد {executed_count} صفقة منفذة...")

        # ✅ تدريب LSTM
        lstm_output = run_script("train_lstm_model.py")
        # ✅ تدريب XGB
        xgb_output = run_script("train_xgb.py")

        send_telegram_message("✅ *تم الانتهاء من تدريب النماذج*\n📊 LSTM و XGBoost جاهزين!")

        # حفظ الحالة الجديدة
        status["last_trained_count"] = executed_count
        save_status(status)
    else:
        print("🔁 لم يتم الوصول إلى عدد الصفقات المطلوب للتدريب.")

if __name__ == "__main__":
    main()
