@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py artnet_bridge.py
  goto fin
)
where python >nul 2>nul
if %errorlevel%==0 (
  python artnet_bridge.py
  goto fin
)
echo Python n'est pas installe.
echo Installe-le depuis https://www.python.org/downloads/
echo (coche "Add python.exe to PATH" pendant l'installation)
:fin
pause
