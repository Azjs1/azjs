# predict_lstm_signal.py (نسخة محسّنة)

import os
import numpy as np
import pandas as pd
import logging
import joblib
from tensorflow.keras.models import load_model
from binance.client import Client
from datetime import datetime

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# إعداد Binance API
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

# مسارات النموذج والمحولات
MODEL_PATH = "models/lstm_model.h5"
SCALER_PATH = "models/lstm_scaler.pkl"
LOOK_BACK = 50
INTERVALS = ["5m", "15m", "1h", "4h"]

# ✅ جلب البيانات الحية من Binance ودمجها عبر الفريمات الزمنية
def fetch_recent_data(symbol="BTCUSDT"):
    try:
        def fetch(symbol, interval):
            klines = client.get_klines(symbol=symbol, interval=interval, limit=100)
            df = pd.DataFrame(klines, columns=[
                "timestamp", "open", "high", "low", "close", "volume",
                "close_time", "qav", "trades", "tbbav", "tbqav", "ignore"
            ])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            df = df[["close"]].astype(float)
            df.columns = [f"close_{interval}"]
            return df

        final_df = None
        for interval in INTERVALS:
            df = fetch(symbol, interval)
            if final_df is None:
                final_df = df
            else:
                final_df = final_df.join(df, how="outer")

        final_df["avg_close"] = final_df.mean(axis=1)
        final_df.dropna(inplace=True)
        return final_df

    except Exception as e:
        logging.error(f"❌ [Data Fetch Error] فشل في جلب البيانات من Binance: {e}")
        return pd.DataFrame()

# ✅ توقع إشارة LSTM من البيانات الحالية
def predict_lstm_signal():
    try:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
            logging.warning("⚠️ لم يتم العثور على ملفات النموذج أو المحول.")
            return {
                "signal": 0,
                "confidence": 0.5,
                "prediction": 0.5,
                "timestamp": None,
                "volatility": 0.0
            }

        model = load_model(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        df = fetch_recent_data()

        if df.empty or len(df) < LOOK_BACK:
            logging.warning("⚠️ بيانات غير كافية لإشارة LSTM.")
            return {
                "signal": 0,
                "confidence": 0.5,
                "prediction": 0.5,
                "timestamp": None,
                "volatility": 0.0
            }

        data = df[["avg_close"]].values
        data_scaled = scaler.transform(data)
        last_seq = data_scaled[-LOOK_BACK:]
        X = np.reshape(last_seq, (1, LOOK_BACK, 1))

        prediction = model.predict(X)[0][0]
        signal = 1 if prediction > 0.5 else 0
        confidence = float(prediction)
        volatility = float(np.std(df["avg_close"].pct_change().dropna()))

        logging.info(f"📈 إشارة LSTM: {signal} | الثقة: {confidence:.4f} | التذبذب: {volatility:.4f}")

        return {
            "signal": signal,
            "confidence": confidence,
            "prediction": prediction,
            "timestamp": df.index[-1],
            "volatility": volatility
        }

    except Exception as e:
        logging.error(f"❌ [LSTM Prediction Error] {e}")
        return {
            "signal": 0,
            "confidence": 0.5,
            "prediction": 0.5,
            "timestamp": None,
            "volatility": 0.0
        }