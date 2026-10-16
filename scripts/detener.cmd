@echo off
rem Doble clic: apaga todo (los datos se conservan).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0iniciar.ps1" -Detener
pause
