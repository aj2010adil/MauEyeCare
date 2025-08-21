<#!
.SYNOPSIS
  Runs the full backend test suite in CI-like mode.
#>
$ErrorActionPreference = 'Stop'

Write-Host "[MauEyeCare] Installing test dependencies..." -ForegroundColor Yellow
& .\.venv\Scripts\pip install -r requirements.txt | Out-Null

Write-Host "[MauEyeCare] Running tests..." -ForegroundColor Yellow
& .\.venv\Scripts\python -m pytest -q

if ($LASTEXITCODE -ne 0) {
  Write-Error "Tests failed with exit code $LASTEXITCODE"
  exit $LASTEXITCODE
}

Write-Host "[MauEyeCare] All tests passed." -ForegroundColor Green
