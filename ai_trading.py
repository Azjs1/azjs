# ai_trading.py

import pandas as pd
import xgboost as xgb
import numpy as np
import joblib
import logging
from technical_analysis import extract_features
from binance.client import Client
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MODEL_PATH = "xgb_model.json"
FEATURES_FILE = "model_features.csv"
SYMBOL = "BTCUSDT"

client = Client(api_key=os.getenv("BINANCE_API_KEY"), api_secret=os.getenv("BINANCE_API_SECRET"))

def fetch_latest_market_data(symbol=SYMBOL):
    try:
        klines = client.futures_klines(symbol=symbol, interval="5m", limit=100)
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbbav", "tbqav", "ignore"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df = df.astype(float)
        return df
    except Exception as e:
        logging.error(f"❌ [Fetch Market Error]: {e}")
        return pd.DataFrame()

def predict_trade_direction(symbol=SYMBOL):
    try:
        model = xgb.XGBClassifier()
        model.load_model(MODEL_PATH)

        df = fetch_latest_market_data(symbol)
        if df.empty or len(df) < 50:
            return 0  # HOLD

        features = extract_features(df)
        if features.empty:
            return 0  # HOLD

        model_features = pd.read_csv(FEATURES_FILE).columns.tolist()
        features = features.reindex(columns=model_features, fill_value=0)

        prediction = model.predict(features)[0]
        logging.info(f"🧠 إشارة XGBoost: {prediction}")
        return int(prediction)

    except Exception as e:
        logging.error(f"❌ [XGBoost Prediction Error]: {e}")
        return 0  # HOLD
