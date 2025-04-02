import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ دالة تحليل المشاعر بالأخبار باستخدام GPT
def analyze_sentiment_gpt(news_text):
    prompt = f"""
قم بتحليل المشاعر في هذا الخبر المتعلق بالبيتكوين، وقيّمه بين -1 (سلبي) و +1 (إيجابي):

النص: """ + news_text + """

أجب فقط برقم عشري بين -1 و +1 بدون شرح.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        score = float(response.choices[0].message.content.strip())
        return round(score, 3)
    except Exception as e:
        print(f"❌ [GPT Sentiment Error] {e}")
        return 0.0

# ✅ دالة توصية تداول ذكية باستخدام GPT
def get_gpt_trade_recommendation(signals):
    """
    signals = {
        "lstm_signal": "BUY",
        "xgb_signal": "BUY",
        "technical_signal": "BUY",
        "sentiment_score": 0.7,
        "liquidity_score": 1.2,
        "rl_decision": "BUY"
    }
    """
    prompt = f"""
أنت محلل تداول ذكي. لديك الإشارات التالية:
- LSTM: {signals.get("lstm_signal")}
- XGBoost: {signals.get("xgb_signal")}
- التحليل الفني: {signals.get("technical_signal")}
- مؤشر المشاعر: {signals.get("sentiment_score")}
- مؤشر السيولة: {signals.get("liquidity_score")}
- تعلم التعزيز: {signals.get("rl_decision")}

بناءً على هذه الإشارات، ما هي التوصية الأفضل؟
- BUY (شراء)
- SELL (بيع)
- HOLD (انتظار)

أجب بالتنسيق التالي فقط:
Decision: <BUY/SELL/HOLD>
Confidence: <رقم بين 0 و 1>
Reason: <شرح منطقي>
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        content = response.choices[0].message.content.strip()
        lines = content.splitlines()
        decision = ""
        confidence = 0.0
        reason = ""

        for line in lines:
            if "Decision:" in line:
                decision = line.split("Decision:")[1].strip().upper()
            elif "Confidence:" in line:
                confidence = float(line.split("Confidence:")[1].strip())
            elif "Reason:" in line:
                reason = line.split("Reason:")[1].strip()

        return {
            "decision": decision,
            "confidence": round(confidence, 3),
            "reason": reason
        }

    except Exception as e:
        print(f"❌ [GPT Trade Recommendation Error] {e}")
        return {
            "decision": "HOLD",
            "confidence": 0.0,
            "reason": "حدث خطأ أثناء تحليل GPT."
        }
