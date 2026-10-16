@echo off
rem Para quienes usan CMD: reenvía a iniciar.ps1. Ejemplos:
rem   scripts\iniciar.cmd
rem   scripts\iniciar.cmd -Demo -Publico
rem   scripts\iniciar.cmd -Detener
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0iniciar.ps1" %*
