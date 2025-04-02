import numpy as np
import pandas as pd
import logging
import os
import joblib

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

Q_TABLE_PATH = "q_table.pkl"
ACTIONS = ["BUY", "SELL", "HOLD"]

class ReinforcementLearningTrader:
    def __init__(self, learning_rate=0.1, discount_factor=0.95, exploration_rate=0.2):
        self.q_table = self.load_q_table()
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate

    def load_q_table(self):
        if os.path.exists(Q_TABLE_PATH):
            try:
                return joblib.load(Q_TABLE_PATH)
            except Exception as e:
                logging.warning(f"⚠️ فشل تحميل Q-Table: {e}")
        return {}

    def save_q_table(self):
        try:
            joblib.dump(self.q_table, Q_TABLE_PATH)
            logging.info("✅ تم حفظ Q-Table بنجاح.")
        except Exception as e:
            logging.error(f"❌ فشل حفظ Q-Table: {e}")

    def get_state(self, row):
        """
        توليد حالة Q-State من بيانات السوق
        """
        try:
            if "technical_signal" in row and "sentiment_score" in row:
                return f"{row['technical_signal']}_{int(row['sentiment_score'] * 10)}"
            return "default_state"
        except Exception as e:
            logging.warning(f"⚠️ فشل توليد الحالة: {e}")
            return "default_state"

    def choose_action(self, state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in ACTIONS}
        if np.random.rand() < self.epsilon:
            return np.random.choice(ACTIONS)
        return max(self.q_table[state], key=self.q_table[state].get)

    def update_q_value(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in ACTIONS}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0 for a in ACTIONS}
        max_future_q = max(self.q_table[next_state].values())
        old_value = self.q_table[state][action]
        new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * max_future_q)
        self.q_table[state][action] = new_value

    def train(self, df):
        for i in range(len(df) - 1):
            row = df.iloc[i]
            next_row = df.iloc[i + 1]
            state = self.get_state(row)
            next_state = self.get_state(next_row)
            action = self.choose_action(state)

            reward = row.get("pnl", 0)
            self.update_q_value(state, action, reward, next_state)

        self.save_q_table()

    def predict_rl_decision(self, row):
        state = self.get_state(row if row is not None else {})
        if state in self.q_table:
            return max(self.q_table[state], key=self.q_table[state].get)
        return "HOLD"

# ✅ تدريب النموذج من CSV
def train_rl_model(file_path="bot_decisions.csv"):
    if not os.path.exists(file_path):
        logging.warning("⚠️ ملف التدريب غير موجود.")
        return

    df = pd.read_csv(file_path)
    if "technical_signal" not in df or "sentiment_score" not in df:
        logging.warning("⚠️ تنسيق البيانات غير كافٍ للتدريب.")
        return

    rl = ReinforcementLearningTrader()
    rl.train(df)

# ✅ دالة جاهزة لـ bot.py
def get_rl_decision(symbol="BTCUSDT"):
    try:
        rl_trader = ReinforcementLearningTrader()
        dummy_df = {"technical_signal": "BUY", "sentiment_score": 0.2}
        return rl_trader.predict_rl_decision(dummy_df)
    except Exception as e:
        logging.error(f"❌ [RL] خطأ في get_rl_decision: {e}")
        return "HOLD"

# ✅ تدريب يدوي
if __name__ == "__main__":
    train_rl_model()
    
def get_rl_decision(symbol="BTCUSDT"):
    try:
        rl_trader = ReinforcementLearningTrader()
        dummy_df = {"technical_signal": "BUY", "sentiment_score": 0.2}
        return rl_trader.predict_rl_decision(dummy_df)
    except Exception as e:
        logging.error(f"❌ [RL] خطأ في get_rl_decision: {e}")
        return "HOLD"
