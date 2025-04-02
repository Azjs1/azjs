@echo off
cd /d D:\bot
call venv\Scripts\activate.bat
streamlit run dashboard_streamlit.py --server.port 8501
pause
