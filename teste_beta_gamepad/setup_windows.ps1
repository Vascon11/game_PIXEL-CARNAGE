# setup_windows.ps1
$ErrorActionPreference = "Stop"

Write-Host "Overclock Arena setup"

# 1) Escolha do Python
# Tenta achar Python 3.12 via py launcher
$py = $null
try {
  $ver = & py -3.12 --version 2>$null
  if ($LASTEXITCODE -eq 0) { $py = "py -3.12" }
} catch {}

if (-not $py) {
  Write-Host "Python 3.12 nao encontrado via 'py -3.12'." -ForegroundColor Yellow
  Write-Host "Instale Python 3.12 (x64) e tente novamente." -ForegroundColor Yellow
  Write-Host "Ou rode com seu python atual, mas pode falhar por dependencias nativas." -ForegroundColor Yellow
  exit 1
}

# 2) Criar venv
if (-not (Test-Path ".\.venv")) {
  Write-Host "Criando venv (.venv)..."
  & $py -m venv .venv
}

# 3) Ativar venv
Write-Host "Ativando venv..."
& .\.venv\Scripts\Activate.ps1

# 4) Atualizar pip
python -m pip install --upgrade pip setuptools wheel

# 5) Instalar deps
if (Test-Path ".\requirements.txt") {
  pip install -r requirements.txt
} elseif (Test-Path ".\pyproject.toml") {
  pip install .
} else {
  Write-Host "Nao achei requirements.txt nem pyproject.toml" -ForegroundColor Red
  exit 1
}

Write-Host "Setup concluido. Para rodar:"
Write-Host ".\.venv\Scripts\Activate.ps1"
Write-Host "python run.py"