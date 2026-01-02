#!/bin/bash

echo "================================================"
echo "         JARVIS INTERVIEW - Web UI"
echo "   AI-Powered Interview Transcription System"
echo "================================================"
echo ""
echo "[JARVIS] Initializing system..."
echo "[JARVIS] Loading AI models..."
echo ""
echo "Browser: http://localhost:8501"
echo "Stop: CTRL+C"
echo ""
echo "================================================"
echo ""

# Activate venv
source venv/bin/activate

# Run Streamlit
streamlit run app_ui.py
