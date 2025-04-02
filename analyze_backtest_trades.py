# analyze_backtest_trades.py

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

def analyze_backtest_trades():
    try:
        with get_connection() as conn:
            df = pd.read_sql("SELECT * FROM backtest_trades", conn)

        if df.empty:
            logging.warning("⚠️ لا توجد صفقات باك تست لتحليلها.")
            return

        # ✅ تحليل حسب الاستراتيجية
        strategy_summary = df.groupby("strategy").agg(
            total_trades=('id', 'count'),
            avg_pnl=('pnl', 'mean'),
            total_pnl=('pnl', 'sum'),
            win_rate=('pnl', lambda x: (x > 0).mean() * 100)
        ).reset_index()

        logging.info("\n📊 تحليل حسب الاستراتيجية:")
        print(tabulate(strategy_summary, headers='keys', tablefmt='psql'))

        # ✅ تحليل حسب نوع الإشارة
        signal_summary = df.groupby("signal").agg(
            total_trades=('id', 'count'),
            avg_pnl=('pnl', 'mean'),
            win_rate=('pnl', lambda x: (x > 0).mean() * 100)
        ).reset_index()

        logging.info("\n📈 تحليل حسب نوع الإشارة:")
        print(tabulate(signal_summary, headers='keys', tablefmt='psql'))

        # ✅ تحليل حسب اسم الاختبار (Test Name)
        test_summary = df.groupby("test_name").agg(
            total_trades=('id', 'count'),
            avg_pnl=('pnl', 'mean'),
            total_pnl=('pnl', 'sum'),
            win_rate=('pnl', lambda x: (x > 0).mean() * 100),
            strategies=('strategy', lambda x: ', '.join(sorted(set(x))))
        ).reset_index()

        logging.info("\n🧪 تحليل حسب اسم الاختبار (test_name):")
        print(tabulate(test_summary, headers='keys', tablefmt='psql'))

    except Exception as e:
        logging.error(f"❌ [ERROR] فشل في تحليل صفقات الباك تست: {e}")

if __name__ == "__main__":
    analyze_backtest_trades()
