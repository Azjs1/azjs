import numpy as np
import pandas as pd
from utils import get_price_data, get_current_price

# سجل الأداء للتعلم الذاتي
trade_history = {
    "win_rate": 0.6,
    "recent_profits": [],
    "max_drawdown": 0.0,
    "last_signals": []
}

# ✅ تحديث سجل الأداء بعد كل صفقة
def update_trade_history(pnl):
    trade_history["recent_profits"].append(pnl)
    if len(trade_history["recent_profits"]) > 100:
        trade_history["recent_profits"] = trade_history["recent_profits"][-100:]

    wins = [1 for p in trade_history["recent_profits"] if p > 0]
    losses = [1 for p in trade_history["recent_profits"] if p <= 0]
    total = len(wins) + len(losses)
    trade_history["win_rate"] = round(len(wins) / total, 2) if total > 0 else 0.5
    trade_history["max_drawdown"] = round(min(trade_history["recent_profits"]), 2) if trade_history["recent_profits"] else 0.0

# ✅ حساب التذبذب الحالي للسوق
def measure_volatility(symbol, window=20):
    try:
        df = get_price_data(symbol, interval="1h", limit=window + 1)
        df["returns"] = df["close"].pct_change()
        return round(df["returns"].std(), 4)
    except:
        return 0.01  # قيمة افتراضية عند الفشل

# ✅ كشف التلاعب السعري أو السيولة المنخفضة
def detect_manipulation(symbol):
    vol = measure_volatility(symbol)
    return vol > 0.05

# ✅ تحسين وقف الخسارة ديناميكيًا
def improve_stop_loss(base_sl, direction, sentiment_score=0.0, volatility=0.01):
    adjustment = (sentiment_score * 0.5) + (volatility * 1.5)
    if direction == "BUY":
        return round(base_sl - adjustment, 2)
    else:
        return round(base_sl + adjustment, 2)

# ✅ حساب حجم الصفقة الذكي
def calculate_position_size(base_qty, confidence_score=0.5, sentiment_score=0.0, liquidity_score=1.0):
    multiplier = 1.0 + (confidence_score * 0.5) + (sentiment_score * 0.2) + ((liquidity_score - 1) * 0.3)
    return round(base_qty * multiplier, 4)

# ✅ الدالة الأساسية لإدارة المخاطر
def apply_risk_management(symbol, decision, confidence_score=0.5, sentiment_score=0.0, liquidity_score=1.0):
    try:
        base_qty = 0.01
        price = get_current_price(symbol)
        volatility = measure_volatility(symbol)
        position_size = calculate_position_size(base_qty, confidence_score, sentiment_score, liquidity_score)

        stop_loss_distance = round(volatility * 2, 4)
        take_profit_distance = round(stop_loss_distance * (1.5 + confidence_score), 4)

        if decision == "BUY":
            stop_loss = improve_stop_loss(price - stop_loss_distance, "BUY", sentiment_score, volatility)
            take_profit = round(price + take_profit_distance, 2)
        elif decision == "SELL":
            stop_loss = improve_stop_loss(price + stop_loss_distance, "SELL", sentiment_score, volatility)
            take_profit = round(price - take_profit_distance, 2)
        else:
            return None

        return {
            "quantity": position_size,
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2)
        }

    except Exception as e:
        print(f"❌ [Risk Management Error]: {e}")
        return None
