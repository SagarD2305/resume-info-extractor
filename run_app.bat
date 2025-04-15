@echo off
cd /d "%~dp0"
call .\venv\Scripts\activate.bat
.\venv\Scripts\python.exe -m streamlit run app.py --server.port 8502 --server.address 127.0.0.1
