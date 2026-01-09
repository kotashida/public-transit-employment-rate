@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Step 1: Downloading Data...
python src/download_data.py

echo.
echo Step 2: Processing Data...
python src/process_data.py

echo.
echo Step 3: Analyzing...
python src/analyze.py

echo.
echo Done! Check the 'outputs' folder.
pause
