@echo off
chcp 65001 > nul
title Sincronización FAL Benchmark - GitHub a Local
cls
echo =================================================================
echo   SINCRONIZADOR LOCAL DEL BENCHMARK FAL CON GITHUB
echo =================================================================
echo Conectando con https://github.com/GenesisFinal/benchmark-fal ...
echo.
python "%~dp0scripts\sync_from_github.py"
echo.
echo Presione cualquier tecla para salir...
pause > nul
