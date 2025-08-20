param(
  [string]$DbHost = $env:MAU_DB_HOST, 
  [string]$DbPort = $env:MAU_DB_PORT, 
  [string]$DbUser = $env:MAU_DB_USER, 
  [string]$DbPassword = $env:MAU_DB_PASSWORD, 
  [string]$DbName = $env:MAU_DB_NAME
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $DbHost) { $DbHost = '127.0.0.1' }
if (-not $DbPort) { $DbPort = '5432' }
if (-not $DbUser) { $DbUser = 'maueyecare' }
if (-not $DbPassword) { $DbPassword = 'maueyecare' }
if (-not $DbName) { $DbName = 'maueyecare' }

function Get-PsqlPath {
  try {
    $pf = Join-Path $env:ProgramFiles "PostgreSQL\*\bin\psql.exe"
    $x86 = Join-Path ${env:ProgramFiles(x86)} "PostgreSQL\*\bin\psql.exe"
    $candidates = @()
    $candidates += Get-ChildItem -Path $pf -ErrorAction SilentlyContinue
    $candidates += Get-ChildItem -Path $x86 -ErrorAction SilentlyContinue
    if ($candidates -and $candidates.Count -gt 0) {
      return ($candidates | Sort-Object FullName -Descending | Select-Object -First 1).FullName
    }
  } catch {}
  $cmd = Get-Command psql -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  return $null
}

$psql = Get-PsqlPath
if (-not $psql) { Write-Error "psql.exe not found. Ensure PostgreSQL is installed and psql is available."; exit 1 }

try {
  $env:PGPASSWORD = $DbPassword
  Write-Host "[DB] Connecting to ${DbUser}@${DbHost}:${DbPort}/${DbName}" -ForegroundColor Yellow
  & $psql -U $DbUser -h $DbHost -p $DbPort -d $DbName -c "SELECT current_user, current_database();"
  if ($LASTEXITCODE -ne 0) { throw "Connection failed" }
  Write-Host "[DB] Connection OK" -ForegroundColor Green

  Write-Host "[DB] Checking tables..." -ForegroundColor Yellow
  & $psql -U $DbUser -h $DbHost -p $DbPort -d $DbName -c "\dt"
  Write-Host "[DB] Tables listed." -ForegroundColor Green

  Write-Host "[DB] Checking 'users' table and default doctor..." -ForegroundColor Yellow
  $res = & $psql -U $DbUser -h $DbHost -p $DbPort -d $DbName -t -A -c "SELECT id,email,is_active FROM users WHERE email='doctor@maueyecare.com'"
  if ($LASTEXITCODE -eq 0 -and $res.Trim()) {
    Write-Host "[DB] Default user exists: $res" -ForegroundColor Green
  } else {
    Write-Host "[DB] Default user not found." -ForegroundColor DarkYellow
  }
} finally {
  Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}


