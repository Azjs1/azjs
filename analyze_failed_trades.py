# analyze_failed_trades.py

import psycopg2
import pandas as pd
import logging
from dotenv import load_dotenv
import os
from tabulate import tabulate

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

def analyze_failed_trades():
    try:
        with get_connection() as conn:
            df = pd.read_sql("SELECT * FROM closed_trades", conn)

        if df.empty:
            logging.warning("⚠️ لا توجد صفقات لتحليلها.")
            return

        # ✅ استخراج الخسائر فقط
        losses = df[df["pnl"] < 0].copy()
        if losses.empty:
            logging.info("✅ لا توجد صفقات خاسرة.")
            return

        losses["date"] = pd.to_datetime(losses["timestamp"]).dt.date

        logging.info(f"❌ عدد الصفقات الخاسرة: {len(losses)}")
        logging.info(f"📉 إجمالي الخسائر: {losses['pnl'].sum():.2f} USDT")

        # أكبر 5 خسائر
        top_losses = losses.sort_values(by="pnl").head(5)
        logging.info("\n💥 أكبر 5 خسائر:")
        print(tabulate(top_losses[["timestamp", "symbol", "entry_price", "exit_price", "pnl"]], headers="keys", tablefmt="fancy_grid"))

        # تحليل حسب الرمز
        by_symbol = losses.groupby("symbol")["pnl"].agg(["count", "sum"]).sort_values(by="sum")
        logging.info("\n📊 الرموز الأكثر خسارة:")
        print(tabulate(by_symbol, headers="keys", tablefmt="grid"))

        # تحليل حسب الأيام
        by_date = losses.groupby("date")["pnl"].sum().sort_values()
        logging.info("\n📅 أسوأ الأيام:")
        print(tabulate(by_date.reset_index(), headers="keys", tablefmt="pipe"))

    except Exception as e:
        logging.error(f"❌ [Error] تحليل الخسائر فشل: {e}")

if __name__ == "__main__":
    analyze_failed_trades()
