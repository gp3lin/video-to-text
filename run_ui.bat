@echo off
echo ================================================
echo             B-LEXIS - Web UI
echo      Lexical Intelligence System
echo ================================================
echo.
echo [B-LEXIS] Initializing lexical engine...
echo [B-LEXIS] Loading AI models...
echo.
echo Browser: http://localhost:8501
echo Stop: CTRL+C
echo.
echo ================================================
echo.

cd /d "%~dp0"
call venv\Scripts\activate
streamlit run app_ui.py
pause
