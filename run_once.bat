@echo off
cd /d D:\bot
call venv\Scripts\activate.bat
python -c "from bot import run_bot_once; run_bot_once()"
pause
