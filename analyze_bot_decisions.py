# analyze_bot_decisions.py

import psycopg2
import pandas as pd
import logging
from tabulate import tabulate
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432)
    )

def analyze_bot_decisions():
    try:
        with get_connection() as conn:
            df = pd.read_sql("SELECT * FROM bot_decisions", conn)

        if df.empty:
            logging.warning("⚠️ لا توجد قرارات بوت لتحليلها.")
            return

        total = len(df)
        executed = df[df["executed"] == True]
        non_executed = df[df["executed"] == False]

        win_rate = (executed["decision_result"] == "WIN").mean() * 100 if not executed.empty else 0

        summary = {
            "📦 إجمالي القرارات": total,
            "✅ نُفذت": len(executed),
            "🕒 لم تُنفذ": len(non_executed),
            "🏆 نسبة نجاح القرارات المنفذة": f"{win_rate:.2f}%"
        }

        logging.info("\n📊 ملخص قرارات البوت:")
        for k, v in summary.items():
            logging.info(f"{k}: {v}")

        # ✅ تحليل دقة كل نوع من الإشارات
        for col in ["technical_signal", "rl_decision"]:
            if col not in df.columns:
                continue

            group = df[df["executed"] == True].groupby(col)["decision_result"].value_counts().unstack().fillna(0)
            group["win_rate"] = (group["WIN"] / (group["WIN"] + group["LOSS"])) * 100
            logging.info(f"\n🔎 أداء الإشارة: {col}")
            print(tabulate(group, headers="keys", tablefmt="fancy_grid"))

    except Exception as e:
        logging.error(f"❌ [ERROR] فشل في تحليل قرارات البوت: {e}")

if __name__ == "__main__":
    analyze_bot_decisions()
