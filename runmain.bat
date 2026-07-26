@echo off
setlocal

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed. Installing Python...
    start https://www.python.org/downloads/
    pause
    goto :checkpython
) else (
    echo Python is already installed.
)

:checkpython
:: Check if Python is installed again
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Please install Python manually and rerun this script.
    exit /b 1
)

:: Install dependencies from requirements.txt
echo Installing dependencies...
pip install -r requirements.txt

:: Check if PRAW was installed successfully
pip show praw >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies. Please check your Python and pip installations.
    exit /b 1
) else (
    echo Dependencies installed successfully.
)

:: Run Main.py
echo Running Main.py...
python Main.py

:: Pause the script to keep the window open
pause