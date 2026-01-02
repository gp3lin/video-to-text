@echo off
echo ================================================
echo     Video Mulakat Transkripsiyon - Web UI
echo ================================================
echo.
echo Starting Streamlit UI...
echo.
echo Browser otomatik acilacak: http://localhost:8501
echo Kapatmak icin: CTRL+C
echo.
echo ================================================
echo.

cd /d "%~dp0"
call venv\Scripts\activate
streamlit run app_ui.py
pause
