@echo off
rem Doble clic: revisa si esta PC tiene todo lo necesario y ofrece instalar lo que falte.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0verificar.ps1" %*
pause
