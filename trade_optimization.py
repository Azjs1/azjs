import sys
sys.stdout.reconfigure(encoding='utf-8')

import logging
import pandas as pd

def optimize_trade_decision(lstm_signal, xgb_signal, sentiment_score=0, liquidity_score=1.0):
    """
    🧠 تحسين قرار التداول باستخدام خوارزميات متعددة:
    - XGBoost
    - LSTM
    - تحليل المشاعر
    - تحليل السيولة
    """
    try:
        valid_signals = ["BUY", "SELL", "HOLD"]

        # التحقق من صحة الإشارات
        if lstm_signal not in valid_signals:
            logging.warning(f"⚠️ [WARNING] lstm_signal غير صالح: {lstm_signal}")
            lstm_signal = "HOLD"
        if xgb_signal not in valid_signals:
            logging.warning(f"⚠️ [WARNING] xgb_signal غير صالح: {xgb_signal}")
            xgb_signal = "HOLD"

        # تحويل الإشارات إلى قيم عددية
        def to_score(signal):
            return 1 if signal == "BUY" else -1 if signal == "SELL" else 0

        # أوزان ديناميكية
        lstm_weight = 0.35
        xgb_weight = 0.35
        sentiment_weight = 0.15
        liquidity_weight = 0.15

        # حساب الدرجة النهائية
        score = 0
        score += lstm_weight * to_score(lstm_signal)
        score += xgb_weight * to_score(xgb_signal)
        score += sentiment_weight * sentiment_score
        score += liquidity_weight * (liquidity_score - 1)

        # القرار النهائي
        if score > 0.3:
            final = "BUY"
        elif score < -0.3:
            final = "SELL"
        else:
            final = "HOLD"

        logging.info(f"✅ [INFO] Final trade decision: {final} (Score: {score:.2f})")
        return final

    except Exception as e:
        logging.error(f"❌ [ERROR] في تحسين قرار التداول: {e}")
        return "HOLD"


# ✅ تقدير درجة السيولة بناءً على حجم الصفقات والتغير السعري
def estimate_liquidity_score(df: pd.DataFrame):
    """
    حساب درجة السيولة:
    - > 1 يعني ضغط شراء قوي
    - < 1 يعني ضغط بيع قوي
    - 1 يعني توازن
    """
    try:
        if df.empty or len(df) < 10:
            return 1.0

        df['price_change'] = df['close'].pct_change()
        df['volume_change'] = df['volume'].pct_change()
        df.dropna(inplace=True)

        price_vol = df['price_change'].std()
        volume_vol = df['volume_change'].std()

        score = 1.0 + (volume_vol - price_vol)
        score = max(0.5, min(score, 1.5))  # ضمن النطاق
        return round(score, 3)
    except Exception as e:
        logging.error(f"❌ [ERROR] في حساب سيولة السوق: {e}")
        return 1.0
