import logging
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from gpt_utils import analyze_news_with_gpt
from train_news_model import predict_news_sentiment_lstm
import requests
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

vader_analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment_textblob(text: str) -> float:
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except Exception as e:
        logging.error(f"❌ [TextBlob] فشل تحليل المشاعر: {e}")
        return 0

def analyze_sentiment_vader(text: str) -> float:
    try:
        return vader_analyzer.polarity_scores(text)['compound']
    except Exception as e:
        logging.error(f"❌ [VADER] فشل تحليل المشاعر: {e}")
        return 0

def analyze_sentiment_lstm(text: str) -> float:
    try:
        return predict_news_sentiment_lstm(text)
    except Exception as e:
        logging.error(f"❌ [LSTM] فشل تحليل المشاعر: {e}")
        return 0

def analyze_sentiment_gpt_only(text: str) -> float:
    try:
        return analyze_news_with_gpt(text)
    except Exception as e:
        logging.error(f"❌ [GPT] فشل تحليل المشاعر عبر GPT: {e}")
        return 0

def aggregate_sentiment_analysis(text: str) -> float:
    try:
        scores = [
            analyze_sentiment_textblob(text),
            analyze_sentiment_vader(text),
            analyze_sentiment_lstm(text),
            analyze_sentiment_gpt_only(text)
        ]
        average = sum(scores) / len(scores)
        logging.info(f"🧠 [Sentiment] متوسط المشاعر: {average:.2f}")
        return round(average, 3)
    except Exception as e:
        logging.error(f"❌ [Sentiment] فشل دمج تحليلات المشاعر: {e}")
        return 0

# ✅ للاستخدام في bot.py
def analyze_sentiment_gpt(text="Bitcoin is rising fast today!") -> float:
    return aggregate_sentiment_analysis(text)

# ✅ جلب الأخبار من NewsAPI
def fetch_bitcoin_news(api_key: str, query="bitcoin", page_size=5) -> list:
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "apiKey": api_key,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data["status"] == "ok":
            return [article["title"] + ". " + article.get("description", "") for article in data["articles"]]
        else:
            print("❌ [NewsAPI] فشل في جلب الأخبار:", data)
            return []
    except Exception as e:
        print(f"❌ [NewsAPI ERROR] {e}")
        return []
