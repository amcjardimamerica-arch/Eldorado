# AGENDA A COLETA NO BRASIL NO COMPUTADOR DO TITULAR (Windows) — uma vez só.
# Roda scripts\coleta_brasil.py a cada 3 horas, das 06:10 às 22:10, enquanto o computador estiver ligado e com o
# usuário conectado (precisa do login do GitHub já gravado no Git deste computador, o mesmo da coleta_brasil.bat).
# Lê, com o IP brasileiro de casa, os portais que recusam IP estrangeiro e os motores indexadores da rota "ponte".
# Para remover: Unregister-ScheduledTask -TaskName "Eldorado - coleta Brasil" -Confirm:$false
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $python) { Write-Host "Python não encontrado. Instale o Python 3 (python.org) e rode de novo."; exit 1 }
$acao = New-ScheduledTaskAction -Execute $python -Argument "scripts\coleta_brasil.py" -WorkingDirectory $repo
$gatilho = New-ScheduledTaskTrigger -Daily -At 06:10
$gatilho.Repetition = (New-ScheduledTaskTrigger -Once -At 06:10 -RepetitionInterval (New-TimeSpan -Hours 3) -RepetitionDuration (New-TimeSpan -Hours 16)).Repetition
$cfg = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 1) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "Eldorado - coleta Brasil" -Action $acao -Trigger $gatilho -Settings $cfg `
  -Description "Eldorado: lê com o IP do Brasil os portais que recusam IP estrangeiro e envia ao GitHub" -Force | Out-Null
Write-Host "Pronto: a coleta no Brasil roda sozinha a cada 3 horas (06:10 a 22:10) com o computador ligado."
