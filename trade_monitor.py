import time
from datetime import datetime
from utils import get_current_price
from predict_lstm_signal import get_lstm_signal
from utils import get_xgb_signal
from notifier import send_telegram_message
from database import log_closed_trade_to_db
from risk_management import update_trade_history

def monitor_and_close_trade(symbol, entry_price, quantity, direction, stop_loss, take_profit):
    """
    مراقبة الصفقة المفتوحة والخروج الذكي بناءً على تحقق الهدف أو الإشارة العكسية.
    """
    start_time = datetime.utcnow()
    trade_closed = False
    exit_reason = ""
    pnl = 0

    while not trade_closed:
        try:
            time.sleep(5)
            current_price = get_current_price(symbol)

            # 1️⃣ تحقق من وقف الخسارة أو جني الأرباح
            if direction == "BUY":
                if current_price >= take_profit:
                    exit_reason = "Take Profit"
                    trade_closed = True
                elif current_price <= stop_loss:
                    exit_reason = "Stop Loss"
                    trade_closed = True
            elif direction == "SELL":
                if current_price <= take_profit:
                    exit_reason = "Take Profit"
                    trade_closed = True
                elif current_price >= stop_loss:
                    exit_reason = "Stop Loss"
                    trade_closed = True

            # 2️⃣ تحقق من انعكاس الإشارات (LSTM/XGB)
            lstm_signal = get_lstm_signal(symbol)
            xgb_signal = get_xgb_signal(symbol)

            if direction == "BUY" and (lstm_signal == "SELL" or xgb_signal == "SELL"):
                exit_reason = "Signal Reversal"
                trade_closed = True
            elif direction == "SELL" and (lstm_signal == "BUY" or xgb_signal == "BUY"):
                exit_reason = "Signal Reversal"
                trade_closed = True

        except Exception as e:
            send_telegram_message(f"❌ [Monitoring Error] {e}")
            break

    # 📉 حساب الربح/الخسارة
    exit_price = get_current_price(symbol)
    if direction == "BUY":
        pnl = (exit_price - entry_price) * quantity
    elif direction == "SELL":
        pnl = (entry_price - exit_price) * quantity

    duration = (datetime.utcnow() - start_time).total_seconds()

    # 📨 إشعار تلغرام
    send_telegram_message(f"""
📤 *صفقة مغلقة*
▪️ الرمز: {symbol}
▪️ الاتجاه: {direction}
▪️ الدخول: {entry_price}
▪️ الإغلاق: {exit_price}
▪️ الربح/الخسارة: {pnl:.2f} USDT
▪️ السبب: {exit_reason}
▪️ المدة: {int(duration)} ثانية
""")

    # 🗂️ تسجيل في قاعدة البيانات
    log_closed_trade_to_db({
        "symbol": symbol,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "quantity": quantity,
        "direction": direction,
        "pnl": pnl,
        "duration": duration,
        "exit_reason": exit_reason,
        "timestamp": datetime.utcnow().isoformat()
    })

    # 📈 تحديث الأداء
    update_trade_history(pnl)
