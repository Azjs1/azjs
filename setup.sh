#!/bin/bash

echo "🚀 بدء تثبيت بيئة البوت الذكي..."

# 1. تحديث النظام وتثبيت الأساسيات
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git wget unzip build-essential

# 2. تثبيت PostgreSQL
sudo apt install -y postgresql postgresql-contrib libpq-dev

# 3. إنشاء مستخدم وقاعدة بيانات PostgreSQL
sudo -u postgres psql <<EOF
CREATE USER botuser WITH PASSWORD 'botpass';
CREATE DATABASE botdb OWNER botuser;
EOF

# 4. إعداد مجلد المشروع
mkdir -p ~/ai_trading_bot && cd ~/ai_trading_bot

# ملاحظة: هنا يمكن استخدام Git:
# git clone https://github.com/USERNAME/REPO.git .

# أو رفع الملفات يدويًا عبر SCP

# 5. إعداد البيئة الافتراضية
python3 -m venv venv
source venv/bin/activate

# 6. تثبيت المتطلبات
pip install --upgrade pip
pip install -r requirements.txt

# 7. إعداد ملف البيئة .env
cat <<EOF > .env
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
DB_NAME=botdb
DB_USER=botuser
DB_PASSWORD=botpass
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=sk-xxxx
EOF

# 8. تشغيل قاعدة البيانات (إذا لم تكن تعمل)
sudo systemctl enable postgresql
sudo systemctl start postgresql

# 9. إعداد الجدولة لتشغيل البوت كل دقيقة
(crontab -l 2>/dev/null; echo "* * * * * cd ~/ai_trading_bot && source venv/bin/activate && python3 bot.py >> bot.log 2>&1") | crontab -

# 10. تشغيل Streamlit تلقائيًا
cat <<EOF > run_dashboard.sh
#!/bin/bash
cd ~/ai_trading_bot
source venv/bin/activate
streamlit run dashboard_streamlit.py --server.port 8501
EOF
chmod +x run_dashboard.sh

echo "✅ تم إعداد السيرفر بنجاح."
echo "📍 البوت سيعمل كل دقيقة تلقائيًا. الداشبورد على: http://your-server-ip:8501"
