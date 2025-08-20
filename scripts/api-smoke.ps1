param(
  [string]$ApiBase = "http://127.0.0.1:8000",
  [string]$Email = $env:MAU_ADMIN_EMAIL,
  [string]$Password = $env:MAU_ADMIN_PASSWORD
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $Email) { $Email = 'doctor@maueyecare.com' }
if (-not $Password) { $Password = 'MauEyeCareAdmin@2024' }

Write-Host "[API] Health check $ApiBase/api/health" -ForegroundColor Yellow
$health = Invoke-RestMethod -Method GET -Uri "$ApiBase/api/health"
if ($health.status -ne 'ok') { throw "Health check failed: $($health | ConvertTo-Json -Compress)" }
Write-Host "[API] Health OK" -ForegroundColor Green

Write-Host "[API] Login as $Email" -ForegroundColor Yellow
$form = @{
  username = $Email
  password = $Password
  grant_type = 'password'
}
$token = Invoke-RestMethod -Method POST -Uri "$ApiBase/api/auth/login" -ContentType "application/x-www-form-urlencoded" -Body $form
if (-not $token.access_token) { throw "Login did not return access_token" }
Write-Host "[API] Login OK; token acquired" -ForegroundColor Green

Write-Host "[API] Token refresh" -ForegroundColor Yellow
$refresh = @{ refresh_token = $token.refresh_token } | ConvertTo-Json
$newAccess = Invoke-RestMethod -Method POST -Uri "$ApiBase/api/auth/refresh" -ContentType 'application/json' -Body $refresh
if (-not $newAccess.access_token) { throw "Refresh did not return access_token" }
Write-Host "[API] Refresh OK" -ForegroundColor Green


