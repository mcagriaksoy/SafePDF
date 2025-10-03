@echo off
REM Set project root (adjust if needed)
set "ROOT=C:\Users\mcagr\Desktop\SafePDF\SafePDF"

REM Check for pyinstaller
where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found in PATH.
    echo Activate your Python environment or install pyinstaller (pip install pyinstaller).
    pause
    exit /b 1
)

echo Building executable with PyInstaller...
pyinstaller --noconfirm --onefile --windowed ^
    --icon "%ROOT%\assets\icon.ico" ^
    --version-file "%ROOT%\version.txt" ^
    --add-data "%ROOT%\assets;assets/" ^
    --add-data "%ROOT%\ui;ui/" ^
    --add-data "%ROOT%\pdf_operations.py;." ^
    --add-data "%ROOT%\safe_pdf_controller.py;." ^
    --add-data "%ROOT%\welcome_content.html;." ^
    --add-data "%ROOT%\welcome_content.txt;." ^
    "%ROOT%\safe_pdf_app.py"

echo Done. Check the "dist" folder for the generated executable.
pause
