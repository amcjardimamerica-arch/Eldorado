@echo off
rem Clique duas vezes UMA vez: os pilotos passam a voar pelo seu computador de hora em hora (Agendador de Tarefas).
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\agendar_pilotos_brasil.ps1"
pause
