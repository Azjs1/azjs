# bot_engine.py

import logging
from datetime import datetime
from decision_engine import make_final_decision
from risk_management import apply_risk_management
from utils import (
    fetch_market_data,
    extract_all_signals,
    log_bot_decision,
    log_trade,
)
from notifier import send_telegram_message
from trade_monitor import monitor_open_positions
from predict_lstm_signal import predict_lstm_signal  # ✅ جديد

# ✅ إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ✅ تنفيذ خطوة واحدة من البوت
def run_bot_once(client, symbol, weights, rl_trader, tracked_trades, last_signal=None):
    try:
        logging.info(f"🚀 بدء تنفيذ البوت لرمز: {symbol}")

        # ✅ جلب البيانات
        df = fetch_market_data(client, symbol)
        if df is None or df.empty:
            logging.warning("⚠️ لا توجد بيانات كافية.")
            return

        # ✅ تحميل إشارات الذكاء
        signals = extract_all_signals(df, symbol, weights, rl_trader)

        # ✅ استدعاء LSTM مباشرة
        lstm_signal, confidence_score = predict_lstm_signal()
        signals["lstm_signal"] = lstm_signal
        signals["confidence_score"] = confidence_score

        # ✅ اتخاذ القرار النهائي
        decision, _ = make_final_decision(signals, weights)

        # ✅ تسجيل القرار
        log_bot_decision({
            "symbol": symbol,
            "decision": decision,
            "lstm_signal": signals.get("lstm_signal"),
            "xgb_signal": signals.get("xgb_signal"),
            "technical_signal": signals.get("technical_signal"),
            "sentiment_score": signals.get("sentiment_score"),
            "liquidity_score": signals.get("liquidity_score"),
            "rl_decision": signals.get("rl_decision"),
            "confidence_score": confidence_score,
            "executed": False
        })

        if decision == "HOLD":
            logging.info("⏸️ إشارة HOLD - لا يوجد تنفيذ.")
            return

        # ✅ إنشاء أمر تداول
        current_price = float(df["close"].iloc[-1])
        base_order = {
            "entry_price": current_price,
            "direction": decision,
            "symbol": symbol
        }

        # ✅ إدارة المخاطر
        order = apply_risk_management(
            base_order,
            {"account_balance": 15000, "risk_percent": 0.02, "stop_loss_distance": 20},
            signals.get("volatility"),
            signals.get("sentiment_score"),
            signals.get("liquidity_score"),
            signals.get("xgb_signal"),
            confidence_score
        )

        if order is None:
            logging.warning("❌ لم يتم إنشاء الأمر - إدارة المخاطر رفضته.")
            return

        # ✅ تنفيذ الصفقة
        side = "BUY" if order["direction"] == "BUY" else "SELL"
        qty = round(order["quantity"], 3)

        client.futures_create_order(
            symbol=symbol,
            side=client.SIDE_BUY if side == "BUY" else client.SIDE_SELL,
            type="MARKET",
            quantity=qty
        )

        # ✅ حفظ الصفقة
        tracked_trades[symbol] = {
            "entry_price": order["entry_price"],
            "take_profit": order["take_profit"],
            "stop_loss": order["stop_loss"],
            "quantity": order["quantity"]
        }

        # ✅ إشعار
        send_telegram_message(
            f"🚀 *تم فتح صفقة {side}*\n\n"
            f"*الرمز:* `{symbol}`\n"
            f"*الكمية:* `{qty}`\n"
            f"*سعر الدخول:* `{order['entry_price']}`\n"
            f"*وقف الخسارة:* `{order['stop_loss']}`\n"
            f"*جني الأرباح:* `{order['take_profit']}`\n"
            f"*نسبة العائد:* `{order['risk_reward_ratio']}`"
        )

        # ✅ سجل الصفقة
        order["final_signal"] = side
        log_trade(order)

        log_bot_decision({
            **signals,
            "symbol": symbol,
            "decision": decision,
            "confidence_score": confidence_score,
            "executed": True
        })

        # ✅ مراقبة الصفقة المفتوحة
        monitor_open_positions(client, symbol, tracked_trades, lstm_signal, signals.get("xgb_signal"))

    except Exception as e:
        logging.error(f"❌ [bot_engine] خطأ أثناء التنفيذ: {e}")
