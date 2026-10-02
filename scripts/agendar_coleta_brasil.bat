@echo off
rem Clique duas vezes UMA vez: agenda a coleta no Brasil a cada 3 horas (Agendador de Tarefas do Windows).
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\agendar_coleta_brasil.ps1"
pause
