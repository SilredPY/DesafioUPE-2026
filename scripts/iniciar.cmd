@echo off
rem Para quienes usan CMD: reenvía a iniciar.ps1. Ejemplos:
rem   scripts\iniciar.cmd
rem   scripts\iniciar.cmd -Demo -Publico
rem   scripts\iniciar.cmd -Detener
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0iniciar.ps1" %*
rem Con doble clic la ventana se cerraría antes de poder leer el link.
echo %cmdcmdline% | "%SystemRoot%\System32\find.exe" /i "%~0" >nul && pause
