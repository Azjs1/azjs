import os
import numpy as np
import pandas as pd
import joblib
from binance.client import Client
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from datetime import datetime
import logging

# ✅ إعداد السجلات
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ تحميل المفاتيح
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

# ✅ تحميل البيانات من Binance
def get_klines(symbol="BTCUSDT", interval="1h", limit=1000):
    raw = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(raw, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df

# ✅ توليد الميزات
def add_features(df):
    df["return"] = df["close"].pct_change().shift(-1)
    df["target"] = np.where(df["return"] > 0, 1, 0)

    df["sma_10"] = df["close"].rolling(window=10).mean()
    df["ema_10"] = df["close"].ewm(span=10).mean()
    df["volatility"] = df["close"].rolling(window=10).std()
    df["price_vs_sma"] = df["close"] / df["sma_10"]
    df["high_low_range"] = df["high"] - df["low"]
    df["body_size"] = abs(df["close"] - df["open"])

    df.dropna(inplace=True)
    return df

# ✅ تدريب النموذج
def train_xgb_model():
    try:
        logging.info("🚀 بدء تحميل البيانات وتوليد الميزات...")
        df = get_klines()
        df = add_features(df)

        feature_cols = ["open", "high", "low", "close", "volume",
                        "sma_10", "ema_10", "volatility", "price_vs_sma",
                        "high_low_range", "body_size"]
        X = df[feature_cols]
        y = df["target"]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        model = XGBClassifier()
        model.fit(X_train, y_train)

        model.save_model("xgb_model.json")
        joblib.dump(scaler, "xgb_scaler.pkl")

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        logging.info(f"✅ تم حفظ نموذج XGBoost بنجاح.")
        logging.info(f"📊 دقة النموذج: {accuracy:.4f} | عينات: {len(X)}")

        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "samples": len(X),
            "accuracy": accuracy
        }
        pd.DataFrame([log_entry]).to_csv("xgb_training_log.csv", mode="a", header=not os.path.exists("xgb_training_log.csv"), index=False)

    except Exception as e:
        logging.error(f"❌ خطأ أثناء تدريب النموذج: {e}")

# ✅ توقع إشارة XGBoost من بيانات جديدة
def predict_xgb_signal(df_latest):
    try:
        if df_latest.empty or len(df_latest) < 10:
            logging.warning("⚠️ بيانات غير كافية لتوقع XGB.")
            return None

        model = XGBClassifier()
        model.load_model("xgb_model.json")
        scaler = joblib.load("xgb_scaler.pkl")

        df_latest = add_features(df_latest)
        feature_cols = ["open", "high", "low", "close", "volume",
                        "sma_10", "ema_10", "volatility", "price_vs_sma",
                        "high_low_range", "body_size"]
        X = df_latest[feature_cols].tail(1)
        X_scaled = scaler.transform(X)

        prediction = model.predict(X_scaled)[0]
        logging.info(f"🤖 توقع XGB للإشارة: {prediction}")
        return int(prediction)

    except Exception as e:
        logging.error(f"❌ فشل في توقع إشارة XGB: {e}")
        return None

if __name__ == "__main__":
    train_xgb_model()
