@echo off
echo Batch file started.

REM Set project root (adjust if needed)
set "ROOT=C:\Users\mcagr\Desktop\SafePDF\SafePDF"
echo ROOT is set to: %ROOT%

REM Check for pyinstaller (but don't exit if not found)
echo Checking for PyInstaller...
where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Warning: PyInstaller not found in PATH.
    echo You may need to activate your Python environment or install pyinstaller (pip install pyinstaller)
    echo Continuing anyway...
) else (
    echo PyInstaller found.
)

echo About to call pyinstaller...
pyinstaller --noconfirm --onefile --windowed --icon "%ROOT%\assets\icon.ico" --version-file "%ROOT%\version.txt" --add-data "%ROOT%\assets;assets/" --add-data "%ROOT%\ui;ui/" --add-data "%ROOT%\pdf_operations.py;." --add-data "%ROOT%\safe_pdf_controller.py;." --add-data "%ROOT%\welcome_content.html;." --add-data "%ROOT%\welcome_content.txt;." "%ROOT%\safe_pdf_app.py"
pause

if errorlevel 1 (
    echo PyInstaller failed to run.
) else (
    echo PyInstaller command finished successfully.
)
echo Done. Check the "dist" folder for the generated executable.
pause
    --icon "%ROOT%\assets\icon.ico" ^
    --version-file "%ROOT%\version.txt" ^
    --add-data "%ROOT%\assets;assets/" ^
    --add-data "%ROOT%\ui;ui/" ^
    --add-data "%ROOT%\pdf_operations.py;." ^
    --add-data "%ROOT%\safe_pdf_controller.py;." ^
    --add-data "%ROOT%\welcome_content.html;." ^
    --add-data "%ROOT%\welcome_content.txt;." ^
    "%ROOT%\safe_pdf_app.py"

if errorlevel 1 (
    echo PyInstaller failed to run.
) else (
    echo PyInstaller command finished successfully.
)
echo Done. Check the "dist" folder for the generated executable.
pause
cmd /k
