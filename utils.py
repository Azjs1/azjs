import csv
import logging
from datetime import datetime
import pandas as pd
from predict_lstm_signal import predict_lstm_signal  # ✅ تم تصحيح الاستيراد
from binance.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BOT_DECISIONS_FILE = "bot_decisions.csv"

def log_bot_decision(symbol, decision, lstm_signal, xgb_signal, technical_signal,
                     sentiment_score, liquidity_score, rl_decision, confidence_score=1.0,
                     executed=False, log_file=BOT_DECISIONS_FILE):
    try:
        file_exists = False
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                file_exists = True
        except FileNotFoundError:
            pass

        with open(log_file, "a", newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                "timestamp", "symbol", "decision", "lstm_signal", "xgb_signal",
                "technical_signal", "sentiment_score", "liquidity_score",
                "rl_decision", "confidence_score", "executed"
            ])

            if not file_exists:
                writer.writeheader()

            writer.writerow({
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "decision": decision,
                "lstm_signal": lstm_signal,
                "xgb_signal": xgb_signal,
                "technical_signal": technical_signal,
                "sentiment_score": sentiment_score,
                "liquidity_score": liquidity_score,
                "rl_decision": rl_decision,
                "confidence_score": confidence_score,
                "executed": executed
            })

        logging.info(f"🧠 [LOGGED] Decision logged successfully: {decision} (Executed: {executed})")

    except Exception as e:
        logging.error(f"❌ [ERROR] Failed to log bot decision: {e}")

# ✅ دالة ذكية لجلب البيانات الموحدة من Binance
def fetch_combined_market_data(client, symbol, intervals=["5m", "15m", "1h", "4h"]):
    try:
        all_data = []

        for interval in intervals:
            candles = client.futures_klines(symbol=symbol, interval=interval, limit=100)
            df = pd.DataFrame(candles, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df.astype(float)
            df.columns = [f"{col}_{interval}" for col in df.columns]
            all_data.append(df)

        merged = pd.concat(all_data, axis=1).dropna()
        logging.info("✅ تم دمج البيانات بنجاح.")
        return merged

    except Exception as e:
        logging.error(f"❌ [ERROR] في دمج البيانات: {e}")
        return pd.DataFrame()

# ✅ مثال لاستخراج الإشارات
def extract_all_signals():
    try:
        lstm_signal, confidence = predict_lstm_signal()
        return {
            "lstm_signal": lstm_signal,
            "confidence": confidence
        }
    except Exception as e:
        logging.error(f"❌ [ERROR] Failed to extract signals: {e}")
        return {"lstm_signal": 1, "confidence": 0.5}
