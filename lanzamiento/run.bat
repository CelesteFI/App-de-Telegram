@echo off
REM run.bat — alternativa sin problemas de ExecutionPolicy.
REM Hace exactamente lo mismo que ".\run.ps1", pero no pide nada
REM ni hay que desbloquear nada: llama con Bypass solo para este proceso.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
