@echo off
REM Serves this folder over local HTTP and opens the Election Simulator demo in your browser.
REM
REM A real server (not just double-clicking index.html) is required for the "Compile Video"
REM feature to work - browsers block fetch() of local files under a file:// page, which the
REM video export needs to inline the stylesheet/images into each frame.
cd /d "%~dp0"

echo Starting local server for the Election Simulator demo on http://localhost:8781 ...
start "CMHoC Election Simulator Server (close this window to stop)" cmd /k python -m http.server 8781

timeout /t 2 /nobreak >nul

start "" http://localhost:8781/index.html

echo.
echo Demo server is running in the other window - close it when you're done.
echo On the setup screen, upload:
echo   Party Data:  demo\parties-demo.csv
echo   Riding Data: demo\ridings-demo.csv
echo Try Primary/Secondary set to 5 sec for a quick run-through.
