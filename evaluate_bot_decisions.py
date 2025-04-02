# evaluate_bot_decisions.py

import psycopg2
import pandas as pd
import logging
from dotenv import load_dotenv
import os
from datetime import timedelta

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

def evaluate_bot_decisions():
    try:
        with get_connection() as conn:
            decisions = pd.read_sql("SELECT * FROM bot_decisions WHERE executed = true", conn)
            trades = pd.read_sql("SELECT * FROM closed_trades", conn)

            if decisions.empty or trades.empty:
                logging.warning("⚠️ لا توجد بيانات كافية للتقييم.")
                return

            decisions["timestamp"] = pd.to_datetime(decisions["timestamp"])
            trades["timestamp"] = pd.to_datetime(trades["timestamp"])

            # ربط كل قرار بأقرب صفقة منفذة بعده مباشرة (خلال 10 دقائق)
            updated = 0
            with conn.cursor() as cur:
                for _, row in decisions.iterrows():
                    decision_time = row["timestamp"]
                    symbol = row["symbol"]

                    match = trades[
                        (trades["symbol"] == symbol) &
                        (trades["timestamp"] >= decision_time) &
                        (trades["timestamp"] <= decision_time + timedelta(minutes=10))
                    ]

                    if not match.empty:
                        trade = match.iloc[0]
                        result = "WIN" if trade["pnl"] > 0 else "LOSS"
                    else:
                        result = "NA"

                    cur.execute("""
                        UPDATE bot_decisions
                        SET decision_result = %s
                        WHERE id = %s
                    """, (result, row["id"]))
                    updated += 1

                conn.commit()

            logging.info(f"✅ تم تقييم {updated} قرار وربطه بنتائج الصفقات.")

    except Exception as e:
        logging.error(f"❌ [Evaluation Error] فشل في تحليل دقة القرارات: {e}")

if __name__ == "__main__":
    evaluate_bot_decisions()
