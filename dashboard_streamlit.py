# dashboard_streamlit.py

import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
import plotly.express as px

load_dotenv()

st.set_page_config(page_title="لوحة تحكم البوت", layout="wide")

# ✅ الاتصال بقاعدة البيانات
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432)
    )

# ✅ تحميل البيانات من الجداول
@st.cache_data(ttl=60)
def load_data():
    with get_connection() as conn:
        decisions = pd.read_sql("SELECT * FROM bot_decisions ORDER BY timestamp DESC", conn)
        trades = pd.read_sql("SELECT * FROM closed_trades ORDER BY timestamp DESC", conn)
        return decisions, trades

# ✅ عرض التقرير الرئيسي
def main():
    st.title("📈 لوحة تحكم البوت الذكي")

    decisions, trades = load_data()

    # التصفيات
    st.sidebar.header("🎛️ الفلاتر")
    symbols = decisions["symbol"].unique()
    selected_symbol = st.sidebar.selectbox("🔍 الرمز", options=["الكل"] + list(symbols))

    if selected_symbol != "الكل":
        decisions = decisions[decisions["symbol"] == selected_symbol]
        trades = trades[trades["symbol"] == selected_symbol]

    st.subheader("📊 قرارات البوت")
    st.dataframe(decisions[[
        "timestamp", "symbol", "decision", "confidence_score", "executed", "decision_result"
    ]].head(50), use_container_width=True)

    st.subheader("💰 أداء الصفقات")
    st.dataframe(trades[[
        "timestamp", "symbol", "entry_price", "exit_price", "quantity", "pnl"
    ]].head(50), use_container_width=True)

    # ✅ إحصائيات عامة
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    total_trades = len(trades)
    total_profit = trades["pnl"].sum()
    win_rate = (trades["pnl"] > 0).mean() * 100 if total_trades > 0 else 0
    avg_confidence = decisions["confidence_score"].mean()

    col1.metric("📦 عدد الصفقات", total_trades)
    col2.metric("💵 إجمالي الربح/الخسارة", f"{total_profit:.2f} USDT")
    col3.metric("🏆 نسبة النجاح", f"{win_rate:.1f}%")
    col4.metric("🧠 متوسط الثقة", f"{avg_confidence:.2f}")

    # ✅ رسم بياني للأداء اليومي
    st.markdown("### 📅 الأداء اليومي")
    if not trades.empty:
        trades["date"] = pd.to_datetime(trades["timestamp"]).dt.date
        daily = trades.groupby("date")["pnl"].sum().reset_index()
        fig = px.bar(daily, x="date", y="pnl", title="📉 الأرباح اليومية", color="pnl")
        st.plotly_chart(fig, use_container_width=True)

    # ✅ تحليل القرارات حسب نوعها
    st.markdown("### 🧠 توزيع قرارات البوت")
    if not decisions.empty:
        decision_counts = decisions["decision"].value_counts().reset_index()
        fig2 = px.pie(decision_counts, names="index", values="decision", title="نسبة قرارات الشراء/البيع/الانتظار")
        st.plotly_chart(fig2, use_container_width=True)

if __name__ == "__main__":
    main()
