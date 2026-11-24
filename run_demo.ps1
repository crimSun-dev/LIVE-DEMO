<#
  One-command demo start (Windows PowerShell). Docker-free.

    .\run_demo.ps1              # uses backend\.env (Neon if DATABASE_URL is set, else SQLite)
    .\run_demo.ps1 -Offline     # venue wifi dead: SQLite + mock BMKG
    .\run_demo.ps1 -Live        # real BMKG
    .\run_demo.ps1 -Reset       # fresh demo data before starting
#>
param(
    [switch]$Offline,
    [switch]$Live,
    [switch]$Reset,
    [int]$Port = 8000
)
$ErrorActionPreference = "Stop"
# The project path contains spaces and an apostrophe: always quote, always use $PSScriptRoot.
$backend = Join-Path $PSScriptRoot "backend"
Set-Location -LiteralPath $backend

$py = Join-Path $backend ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $py)) {
    Write-Host "Creating virtual environment..."
    py -3.11 -m venv .venv
    & $py -m pip install --quiet --upgrade pip
    & $py -m pip install --quiet -r requirements-dev.txt
}

if ($Offline) {
    $env:DATABASE_URL = "sqlite:///demo.db"
    $env:WEATHER_MODE = "mock"
} elseif ($Live) {
    $env:WEATHER_MODE = "live"
}

$seedArgs = @()
if ($Reset) { $seedArgs += "--reset" }
& $py seed.py @seedArgs   # also pre-warms Neon (first query wakes a scaled-to-zero compute)
if ($LASTEXITCODE -ne 0) { throw "seed failed - check DATABASE_URL in backend\.env, or use -Offline" }

Start-Process "http://127.0.0.1:$Port/"
& $py -m uvicorn app.main:app --host 127.0.0.1 --port $Port
