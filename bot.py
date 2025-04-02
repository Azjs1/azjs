import time
from datetime import datetime
from decision_engine import smart_decision
from sentiment_analysis import analyze_sentiment
from liquidity_analysis import analyze_liquidity
from technical_analysis import get_technical_signal
from reinforcement_learning import get_rl_decision
from predict_lstm_signal import get_lstm_signal
from risk_management import apply_risk_management
from notifier import send_telegram_message
from utils import log_bot_decision, get_xgb_signal
from database import log_bot_decision_to_db
from config import DEFAULT_SYMBOL, CONFIDENCE_THRESHOLD

def run_bot_once(symbol=DEFAULT_SYMBOL):
    try:
        # ⏱️ التوقيت
        timestamp = datetime.utcnow().isoformat()

        # 1️⃣ تحليل السوق
        lstm_signal = get_lstm_signal(symbol)
        xgb_signal = get_xgb_signal(symbol)
        technical_signal = get_technical_signal(symbol)
        sentiment_score = analyze_sentiment(symbol)
        liquidity_score = analyze_liquidity(symbol)
        rl_decision = get_rl_decision(technical_signal, sentiment_score)

        # 2️⃣ اتخاذ القرار الذكي (مع GPT)
        decision_data = smart_decision({
            "lstm_signal": lstm_signal,
            "xgb_signal": xgb_signal,
            "technical_signal": technical_signal,
            "sentiment_score": sentiment_score,
            "liquidity_score": liquidity_score,
            "rl_decision": rl_decision
        })

        final_decision = decision_data["decision"]
        confidence_score = decision_data["confidence"]
        gpt_decision = decision_data.get("gpt_decision")
        gpt_confidence = decision_data.get("gpt_confidence")

        # 3️⃣ تقييم الثقة
        executed = False
        if confidence_score >= CONFIDENCE_THRESHOLD:
            # 4️⃣ إدارة المخاطر وتنفيذ الصفقة
            trade_params = apply_risk_management(symbol, final_decision, confidence_score, sentiment_score, liquidity_score)
            if trade_params:
                executed = True
                send_telegram_message(f"""
🚀 *تم تنفيذ صفقة*
▪️ الزوج: {symbol}
▪️ الإجراء: {final_decision}
▪️ الكمية: {trade_params['quantity']}
▪️ وقف الخسارة: {trade_params['stop_loss']}
▪️ جني الأرباح: {trade_params['take_profit']}
▪️ الثقة: {confidence_score * 100:.1f}%
""")
        else:
            send_telegram_message(f"""
⚠️ *صفقة لم تُنفذ بسبب ضعف الثقة*
▪️ القرار: {final_decision}
▪️ الثقة: {confidence_score * 100:.1f}%
▪️ الحد الأدنى: {CONFIDENCE_THRESHOLD * 100:.1f}%
""")

        # 5️⃣ تسجيل القرار الكامل
        log_data = {
            "timestamp": timestamp,
            "symbol": symbol,
            "decision": final_decision,
            "lstm_signal": lstm_signal,
            "xgb_signal": xgb_signal,
            "technical_signal": technical_signal,
            "sentiment_score": sentiment_score,
            "liquidity_score": liquidity_score,
            "rl_decision": rl_decision,
            "confidence_score": confidence_score,
            "gpt_decision": gpt_decision,
            "gpt_confidence": gpt_confidence,
            "executed": executed
        }
        log_bot_decision(log_data)
        log_bot_decision_to_db(log_data)

    except Exception as e:
        send_telegram_message(f"❌ حدث خطأ في البوت:\n{str(e)}")
        print(f"❌ [BOT ERROR]: {e}")

# ✅ تشغيل البوت عند الاستدعاء
if __name__ == "__main__":
    run_bot_once()