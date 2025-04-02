# technical_analysis.py

import pandas as pd
import ta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def perform_technical_analysis(df: pd.DataFrame) -> dict:
    """
    تحليل فني متقدم باستخدام مؤشرات مكتبة TA
    """
    try:
        if df is None or df.empty:
            logging.warning("❌ [TA] بيانات غير صالحة للتحليل الفني.")
            return {"trading_signal": "HOLD"}

        df = df.copy()

        # تحويل الأعمدة إلى أرقام
        for col in ['close', 'high', 'low', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # ✅ مؤشرات فنية
        df["ema10"] = ta.trend.ema_indicator(df["close"], window=10)
        df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)
        df["rsi"] = ta.momentum.rsi(df["close"], window=14)
        df["macd"] = ta.trend.macd(df["close"])
        df["macd_signal"] = ta.trend.macd_signal(df["close"])
        df["adx"] = ta.trend.adx(df["high"], df["low"], df["close"])
        df["stoch_k"] = ta.momentum.stoch(df["high"], df["low"], df["close"])
        df["stoch_d"] = ta.momentum.stoch_signal(df["high"], df["low"], df["close"])

        # ✅ إشارات مبنية على التقاطع والتحركات
        last = df.iloc[-1]

        ema_cross = "BUY" if last["ema10"] > last["ema50"] else "SELL"
        macd_cross = "BUY" if last["macd"] > last["macd_signal"] else "SELL"
        rsi_signal = "BUY" if last["rsi"] < 30 else "SELL" if last["rsi"] > 70 else "HOLD"
        stoch_signal = "BUY" if last["stoch_k"] > last["stoch_d"] else "SELL"

        # ✅ نظام تصويت بسيط من المؤشرات
        signals = [ema_cross, macd_cross, rsi_signal, stoch_signal]
        signal_counts = {s: signals.count(s) for s in set(signals)}
        final = max(signal_counts, key=signal_counts.get)

        return {"trading_signal": final}

    except Exception as e:
        logging.error(f"❌ [TA ERROR] فشل التحليل الفني: {e}")
        return {"trading_signal": "HOLD"}
