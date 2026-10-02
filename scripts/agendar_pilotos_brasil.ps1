# AGENDA OS PILOTOS NO COMPUTADOR DO TITULAR (Windows) — uma vez só.
# Roda scripts\pilotos_brasil.py de hora em hora (55 minutos de voo), enquanto o computador estiver ligado e com o usuário
# conectado: o Espião e o Interceptador voam com o IP de casa e a nuvem fica em terra; desligou, a nuvem reassume sozinha.
# Precisa: Git com o login do GitHub gravado (o mesmo da coleta) e a IA local (python scripts\ia_local_instalar.py).
# Para remover: Unregister-ScheduledTask -TaskName "Eldorado - pilotos no Brasil" -Confirm:$false
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $python) { Write-Host "Python não encontrado. Instale o Python 3 (python.org) e rode de novo."; exit 1 }
if (-not (Test-Path "$repo\ia_local\modelos\Qwen3-8B-Q4_K_M.gguf")) {
  Write-Host "Instalando a IA local (llama.cpp + Qwen3-8B, cerca de 5 GB) — só desta vez..."
  & $python "$repo\scripts\ia_local_instalar.py"
}
$acao = New-ScheduledTaskAction -Execute $python -Argument "scripts\pilotos_brasil.py --minutos 55 --maquina computador" -WorkingDirectory $repo
$gatilho = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) -RepetitionInterval (New-TimeSpan -Hours 1)
$cfg = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 58) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "Eldorado - pilotos no Brasil" -Action $acao -Trigger $gatilho -Settings $cfg `
  -Description "Eldorado: Espião e Interceptador com o IP do Brasil; a nuvem reassume quando o computador desliga" -Force | Out-Null
Write-Host "Pronto: os pilotos voam pelo seu computador de hora em hora, enquanto ele estiver ligado."
