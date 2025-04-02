import os
import pandas as pd
import numpy as np
import logging
import joblib
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# إعداد المسارات
MODEL_PATH = "news_model.h5"
TOKENIZER_PATH = "tokenizer.pkl"
MAX_SEQUENCE_LENGTH = 100
VOCAB_SIZE = 5000

def load_news_dataset(filepath="news_dataset.csv"):
    if not os.path.exists(filepath):
        logging.error("❌ [DATA] ملف الأخبار غير موجود.")
        return None
    df = pd.read_csv(filepath)
    if "text" not in df.columns or "label" not in df.columns:
        logging.error("❌ [DATA] يجب أن يحتوي الملف على عمودي 'text' و 'label'")
        return None
    return df

def train_news_sentiment_model():
    df = load_news_dataset()
    if df is None:
        return

    texts = df["text"].astype(str).tolist()
    labels = pd.get_dummies(df["label"]).values  # تحويل التصنيفات إلى one-hot

    tokenizer = Tokenizer(num_words=VOCAB_SIZE)
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    padded = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)

    X_train, X_test, y_train, y_test = train_test_split(padded, labels, test_size=0.2, random_state=42)

    model = Sequential()
    model.add(Embedding(VOCAB_SIZE, 64, input_length=MAX_SEQUENCE_LENGTH))
    model.add(LSTM(64, return_sequences=False))
    model.add(Dropout(0.5))
    model.add(Dense(3, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    logging.info("🚀 بدء تدريب نموذج تحليل مشاعر الأخبار...")
    model.fit(X_train, y_train, epochs=5, batch_size=32, validation_data=(X_test, y_test))

    model.save(MODEL_PATH)
    joblib.dump(tokenizer, TOKENIZER_PATH)

    logging.info("✅ تم حفظ النموذج والتوكنيزر بنجاح.")

# ✅ دالة التنبؤ باستخدام النموذج المدرّب
def predict_news_sentiment_lstm(text: str) -> float:
    try:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(TOKENIZER_PATH):
            logging.error("❌ النموذج أو التوكنيزر غير موجود.")
            return 0.0

        tokenizer = joblib.load(TOKENIZER_PATH)
        model = load_model(MODEL_PATH)

        sequence = tokenizer.texts_to_sequences([text])
        padded = pad_sequences(sequence, maxlen=MAX_SEQUENCE_LENGTH)
        prediction = model.predict(padded)[0]

        # نعيد الفارق بين الإيجابي والسلبي كمؤشر مشاعر
        sentiment_score = prediction[2] - prediction[0]  # pos - neg
        return round(float(sentiment_score), 3)

    except Exception as e:
        logging.error(f"❌ [PREDICT] فشل في تحليل المشاعر بالنموذج: {e}")
        return 0.0

# ✅ تدريب مباشر إذا تم تشغيل السكربت
if __name__ == "__main__":
    train_news_sentiment_model()
