#!/bin/bash

echo "================================================"
echo "            B-LEXIS - Web UI"
echo "      Lexical Intelligence System"
echo "================================================"
echo ""
echo "[B-LEXIS] Initializing lexical engine..."
echo "[B-LEXIS] Loading AI models..."
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
