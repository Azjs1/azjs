import pandas as pd
import numpy as np
import json
from sklearn.linear_model import LinearRegression
from notifier import send_telegram_message

# 🔁 تحميل البيانات
def load_data():
    decisions = pd.read_csv("bot_decisions.csv")
    trades = pd.read_csv("closed_trades.csv")

    # دمج القرارات مع الصفقات بناءً على الرمز والتاريخ الأقرب
    decisions['timestamp'] = pd.to_datetime(decisions['timestamp'])
    trades['timestamp'] = pd.to_datetime(trades['timestamp'])

    merged = []
    for _, trade in trades.iterrows():
        symbol = trade['symbol']
        trade_time = trade['timestamp']
        decision = decisions[(decisions['symbol'] == symbol) &
                             (decisions['timestamp'] <= trade_time)].sort_values(by='timestamp', ascending=False).head(1)
        if not decision.empty:
            row = decision.iloc[0].to_dict()
            row['pnl'] = trade['pnl']
            merged.append(row)

    return pd.DataFrame(merged)

# 🧠 تحويل الإشارات إلى أرقام
def encode_signals(df):
    signal_map = {"BUY": 1, "SELL": -1, "HOLD": 0}
    df["lstm_encoded"] = df["lstm_signal"].map(signal_map)
    df["xgb_encoded"] = df["xgb_signal"].map(signal_map)
    df["ta_encoded"] = df["technical_signal"].map(signal_map)
    df["rl_encoded"] = df["rl_decision"].map(signal_map)
    return df

# ⚖️ تحسين الأوزان
def optimize_weights(df):
    features = df[["lstm_encoded", "xgb_encoded", "ta_encoded", "sentiment_score", "liquidity_score", "rl_encoded"]]
    target = df["pnl"]

    model = LinearRegression()
    model.fit(features, target)

    weights = {
        "lstm_weight": round(model.coef_[0], 2),
        "xgb_weight": round(model.coef_[1], 2),
        "technical_weight": round(model.coef_[2], 2),
        "sentiment_weight": round(model.coef_[3], 2),
        "liquidity_weight": round(model.coef_[4], 2),
        "rl_weight": round(model.coef_[5], 2),
        "use_gpt": True  # لتفعيل gpt كاستشاري
    }

    return weights

# 💾 حفظ الأوزان
def save_weights(weights, path="weights_config.json"):
    with open(path, "w") as f:
        json.dump(weights, f, indent=4)

# 📩 إشعار تلغرام
def notify_weights(weights):
    msg = "*⚖️ تم تحسين أوزان الذكاء:*\n"
    for k, v in weights.items():
        if k != "use_gpt":
            name = k.replace("_weight", "").upper()
            msg += f"▪️ {name}: `{v}`\n"
    send_telegram_message(msg)

# 🚀 التشغيل
def main():
    df = load_data()
    if df.empty:
        print("❌ لا توجد بيانات كافية لتحسين الأوزان.")
        return

    df = encode_signals(df)
    weights = optimize_weights(df)
    save_weights(weights)
    notify_weights(weights)
    print("✅ تم تحسين الأوزان وتحديث weights_config.json بنجاح.")

if __name__ == "__main__":
    main()
