@echo off
cd /d D:\bot
call venv\Scripts\activate.bat

:: ✅ تشغيل البوت مرة واحدة
python -c "from bot import run_bot_once; run_bot_once()"

:: ✅ تحسين الأوزان بعد كل تشغيل
python weights_optimizer.py

:: ✅ إرسال إشعار إلى تلغرام (اختياري – لازم تكون مفعل send_telegram_message)
python -c "from notifier import send_telegram_message; send_telegram_message('✅ تم تنفيذ البوت وتحسين الأوزان بنجاح')"
