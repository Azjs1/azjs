# liquidity_analysis.py

import numpy as np
import pandas as pd
import logging

# ✅ إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_liquidity(df):
    try:
        if df is None or df.empty or len(df) < 20:
            logging.warning("⚠️ [Liquidity] لا توجد بيانات كافية لتحليل السيولة.")
            return 1.0

        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

        price_changes = df["close"].pct_change().dropna()
        volume_changes = df["volume"].pct_change().dropna()

        price_std = price_changes.std()
        volume_std = volume_changes.std()

        # ✅ اكتشاف تلاعب سعري إذا كانت التغيرات عالية جداً
        manipulation_score = 0
        if price_std > 0.04:
            manipulation_score += 1
        if volume_std > 0.6:
            manipulation_score += 1

        if manipulation_score == 2:
            logging.warning("🚨 [Liquidity] احتمال تلاعب في السوق.")
            return 0.5  # سيولة غير موثوقة
        elif volume_std > 0.3:
            logging.info("📈 [Liquidity] سيولة مرتفعة.")
            return 1.5
        else:
            return 1.0

    except Exception as e:
        logging.error(f"❌ [Liquidity Error] فشل في تحليل السيولة: {e}")
        return 1.0
