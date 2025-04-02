import json
import os
import logging
from gpt_utils import get_gpt_trade_recommendation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ✅ الأوزان الافتراضية
DEFAULT_WEIGHTS = {
    "lstm_weight": 1.0,
    "xgb_weight": 1.0,
    "technical_weight": 1.0,
    "sentiment_weight": 1.0,
    "liquidity_weight": 1.0,
    "rl_weight": 1.0,
    "gpt_weight": 1.0,
    "use_gpt": True
}

WEIGHTS_FILE = "weights_config.json"

# ✅ تحميل الأوزان من ملف JSON
def load_weights():
    if os.path.exists(WEIGHTS_FILE):
        try:
            with open(WEIGHTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"⚠️ فشل تحميل أوزان الذكاء من JSON: {e}")
    return DEFAULT_WEIGHTS

# ✅ الدالة الرئيسية لاتخاذ القرار الذكي
def smart_decision(signals, weights=None):
    try:
        if weights is None:
            weights = load_weights()

        decision_scores = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0}

        def apply_vote(signal_value, weight, buy_value="BUY", sell_value="SELL"):
            if signal_value == buy_value:
                decision_scores["BUY"] += weight
            elif signal_value == sell_value:
                decision_scores["SELL"] += weight
            else:
                decision_scores["HOLD"] += weight * 0.5

        # ✅ تطبيق الإشارات الأساسية
        apply_vote(signals.get("lstm_signal"), weights.get("lstm_weight", 1))
        apply_vote(signals.get("xgb_signal"), weights.get("xgb_weight", 1))
        apply_vote(signals.get("technical_signal"), weights.get("technical_weight", 1))
        apply_vote("BUY" if signals.get("sentiment_score", 0) > 0 else "SELL", weights.get("sentiment_weight", 1))
        apply_vote("BUY" if signals.get("liquidity_score", 1) > 1 else "SELL", weights.get("liquidity_weight", 1))
        apply_vote(signals.get("rl_decision"), weights.get("rl_weight", 1))

        # ✅ توصية GPT (اختياري)
        gpt_decision = None
        gpt_confidence = 0.0
        if weights.get("use_gpt", True):
            try:
                gpt_result = get_gpt_trade_recommendation(signals)
                gpt_decision = gpt_result["decision"]
                gpt_confidence = gpt_result["confidence"]
                if gpt_decision in decision_scores:
                    decision_scores[gpt_decision] += weights.get("gpt_weight", 1) * gpt_confidence
            except Exception as e:
                logging.warning(f"⚠️ فشل استخدام GPT في القرار: {e}")

        # ✅ تحديد القرار النهائي والثقة
        final_decision = max(decision_scores, key=decision_scores.get)
        total_score = sum(decision_scores.values())
        confidence_score = round((decision_scores[final_decision] / total_score) if total_score > 0 else 0, 3)

        return {
            "decision": final_decision,
            "confidence": confidence_score,
            "scores": decision_scores,
            "gpt_decision": gpt_decision,
            "gpt_confidence": gpt_confidence
        }

    except Exception as e:
        logging.error(f"❌ [Decision Error] فشل اتخاذ القرار الذكي: {e}")
        return {
            "decision": "HOLD",
            "confidence": 0,
            "scores": {"BUY": 0, "SELL": 0, "HOLD": 1},
            "gpt_decision": None,
            "gpt_confidence": 0
        }
