# train_lstm_model.py

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import os
import joblib
from binance.client import Client
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from datetime import datetime, timedelta
import logging
from notifier import send_telegram_message

# ✅ الإعدادات
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")
client = Client(API_KEY, API_SECRET)

symbol = "BTCUSDT"
intervals = ["5m", "15m", "1h", "4h"]
look_back = 50

model_output = "models/lstm_model.h5"
scaler_output = "models/lstm_scaler.pkl"
performance_log = "lstm_training_log.csv"

def fetch_data(symbol, interval, lookback_days=10):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=lookback_days)
    klines = client.get_historical_klines(
        symbol=symbol,
        interval=interval,
        start_str=start_time.strftime("%d %b %Y %H:%M:%S"),
        end_str=end_time.strftime("%d %b %Y %H:%M:%S")
    )
    if not klines:
        return pd.DataFrame()
    
    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df.set_index("timestamp", inplace=True)
    df = df[["close"]].astype(float)
    df.columns = [f"close_{interval}"]
    return df

def merge_timeframes(symbol, intervals):
    merged = None
    for interval in intervals:
        df = fetch_data(symbol, interval)
        if df.empty:
            continue
        if merged is None:
            merged = df
        else:
            merged = merged.join(df, how='outer')
    return merged.dropna()

def create_dataset(data, look_back=50, threshold=0.002):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)

    X, y = [], []
    for i in range(look_back, len(scaled)):
        X.append(scaled[i - look_back:i, 0])
        change = (scaled[i, 0] - scaled[i - 1, 0]) / scaled[i - 1, 0]
        y.append(1 if change > threshold else 0)

    X = np.array(X)
    y = np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X, y, scaler

def train_lstm_model():
    try:
        logging.info("🚀 تحميل البيانات من Binance...")
        df = merge_timeframes(symbol, intervals)

        if df.empty or len(df) <= look_back:
            raise ValueError("❌ البيانات غير كافية.")

        logging.info("✅ تم دمج البيانات بنجاح.")
        df["avg_close"] = df.mean(axis=1)

        X, y, scaler = create_dataset(df[["avg_close"]], look_back=look_back)

        model = Sequential()
        model.add(LSTM(64, return_sequences=True, input_shape=(X.shape[1], 1)))
        model.add(Dropout(0.25))
        model.add(LSTM(64))
        model.add(Dropout(0.25))
        model.add(Dense(1, activation="sigmoid"))

        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

        checkpoint = ModelCheckpoint(model_output, monitor="val_loss", save_best_only=True, verbose=1)
        early_stop = EarlyStopping(monitor="val_loss", patience=5)

        history = model.fit(
            X, y,
            epochs=25,
            batch_size=32,
            validation_split=0.1,
            callbacks=[checkpoint, early_stop],
            verbose=1
        )

        joblib.dump(scaler, scaler_output)

        logging.info(f"✅ النموذج محفوظ في: {model_output}")
        logging.info(f"✅ Scaler محفوظ في: {scaler_output}")

        # سجل الأداء
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "samples": len(X),
            "train_acc": history.history["accuracy"][-1],
            "val_acc": history.history["val_accuracy"][-1],
            "train_loss": history.history["loss"][-1],
            "val_loss": history.history["val_loss"][-1],
        }
        log_df = pd.DataFrame([log_entry])
        if os.path.exists(performance_log):
            log_df.to_csv(performance_log, mode='a', header=False, index=False)
        else:
            log_df.to_csv(performance_log, index=False)

        logging.info("📊 تقرير الأداء محفوظ.")
        send_telegram_message(f"🤖 تم تدريب LSTM بنجاح - Val Acc: {log_entry['val_acc']:.2f}")

    except Exception as e:
        logging.error(f"❌ فشل تدريب LSTM: {e}")
        send_telegram_message(f"❌ خطأ في تدريب LSTM: {e}")

train_lstm_model()
