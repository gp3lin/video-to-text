#!/bin/bash

echo "================================================"
echo "    Video Mülakat Transkripsiyon - Web UI"
echo "================================================"
echo ""
echo "Starting Streamlit UI..."
echo ""
echo "Browser otomatik açılacak: http://localhost:8501"
echo "Kapatmak için: CTRL+C"
echo ""
echo "================================================"
echo ""

# Activate venv
source venv/bin/activate

# Run Streamlit
streamlit run app_ui.py
