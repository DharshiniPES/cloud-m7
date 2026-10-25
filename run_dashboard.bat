@echo off
echo ==============================================================================
echo   CLOUD-M7: Launching Interactive Forensic Provenance Dashboard
echo ==============================================================================
call .venv\Scripts\activate.bat
streamlit run cloud_m7\dashboard\app.py --server.port 8501
pause
