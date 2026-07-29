@echo off
title SafePDF Automated Installer Builder
echo ==================================================
echo Starting automated build pipeline for SafePDF...
echo This will compile the python scripts to an executable 
echo and package it into a Windows Setup Installer.
echo ==================================================
echo.

REM Execute build script
python "%~dp0build_installer.py"

echo.
echo Press any key to exit.
pause >nul
