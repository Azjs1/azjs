# database.py

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432)
    )

# ✅ إنشاء الجداول
def create_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bot_decisions (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT,
                    decision TEXT,
                    lstm_signal FLOAT,
                    xgb_signal INT,
                    technical_signal TEXT,
                    sentiment_score FLOAT,
                    liquidity_score FLOAT,
                    rl_decision TEXT,
                    confidence_score FLOAT,
                    executed BOOLEAN,
                    decision_result TEXT
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS closed_trades (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT,
                    entry_price FLOAT,
                    exit_price FLOAT,
                    quantity FLOAT,
                    pnl FLOAT,
                    duration_minutes INT
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_trades INT,
                    total_profit FLOAT,
                    total_loss FLOAT,
                    win_rate FLOAT,
                    report_type TEXT
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS backtest_trades (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT,
                    strategy TEXT,
                    signal TEXT,
                    entry_price FLOAT,
                    exit_price FLOAT,
                    quantity FLOAT,
                    pnl FLOAT,
                    test_name TEXT
                );
            """)

            conn.commit()
            print("✅ [Database] تم إنشاء جميع الجداول بنجاح.")

# ✅ تسجيل قرار البوت
def log_bot_decision_to_db(data: dict):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO bot_decisions (
                    symbol, decision, lstm_signal, xgb_signal, technical_signal,
                    sentiment_score, liquidity_score, rl_decision,
                    confidence_score, executed, decision_result
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get("symbol"),
                data.get("decision"),
                data.get("lstm_signal"),
                data.get("xgb_signal"),
                data.get("technical_signal"),
                data.get("sentiment_score"),
                data.get("liquidity_score"),
                data.get("rl_decision"),
                data.get("confidence_score"),
                data.get("executed"),
                data.get("decision_result", None)
            ))
            conn.commit()

# ✅ تسجيل الصفقة المغلقة
def log_closed_trade_to_db(data: dict):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO closed_trades (
                    symbol, entry_price, exit_price, quantity, pnl, duration_minutes
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data.get("symbol"),
                data.get("entry_price"),
                data.get("exit_price"),
                data.get("quantity"),
                data.get("pnl"),
                data.get("duration_minutes")
            ))
            conn.commit()

# ✅ تحديث أداء التداول
def update_performance_metrics(total_trades, total_profit, total_loss, win_rate, report_type):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO performance_metrics (
                    total_trades, total_profit, total_loss, win_rate, report_type
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                total_trades,
                total_profit,
                total_loss,
                win_rate,
                report_type
            ))
            conn.commit()

# ✅ تسجيل صفقة من نتائج باك تست
def log_backtest_trade(data: dict):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO backtest_trades (
                    symbol, strategy, signal, entry_price,
                    exit_price, quantity, pnl, test_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get("symbol"),
                data.get("strategy"),
                data.get("signal"),
                data.get("entry_price"),
                data.get("exit_price"),
                data.get("quantity"),
                data.get("pnl"),
                data.get("test_name")
            ))
            conn.commit()

if __name__ == "__main__":
    create_tables()
