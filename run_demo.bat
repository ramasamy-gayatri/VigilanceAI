@echo off
echo ==========================================
echo       VIGILANCE.AI DEMO LAUNCHER
echo ==========================================
echo.
echo NOTE: Ensure you have added your OPENAI_API_KEY to the .env file!
echo.

echo [1/3] Starting Data Generator...
start "Data Feed" cmd /k "python mock_stream.py"

echo [2/3] Starting Pathway Backend (RAG + Analytics)...
echo Please wait for "Chatbot API listening" message...
start "Pathway Backend" cmd /k "python backend.py"

echo [3/3] Starting Streamlit UI...
start "Vigilance App" cmd /k "python -m streamlit run app.py"

echo.
echo Demo is running!
pause
