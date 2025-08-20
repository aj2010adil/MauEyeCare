param(
  [string]$Host = $env:MAU_DB_HOST, 
  [string]$Port = $env:MAU_DB_PORT, 
  [string]$User = $env:MAU_DB_USER, 
  [string]$Password = $env:MAU_DB_PASSWORD, 
  [string]$Database = $env:MAU_DB_NAME
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $Host) { $Host = '127.0.0.1' }
if (-not $Port) { $Port = '5432' }
if (-not $User) { $User = 'maueyecare' }
if (-not $Password) { $Password = 'maueyecare' }
if (-not $Database) { $Database = 'maueyecare' }

function Get-PsqlPath {
  $candidates = @(
    (Join-Path $env:ProgramFiles "PostgreSQL\**\bin\psql.exe"),
    (Join-Path ${env:ProgramFiles(x86)} "PostgreSQL\**\bin\psql.exe")
  )
  foreach ($glob in $candidates) {
    try {
      $files = Get-ChildItem -Path $glob -ErrorAction SilentlyContinue
      if ($files) { return ($files | Sort-Object FullName -Descending | Select-Object -First 1).FullName }
    } catch {}
  }
  $cmd = Get-Command psql -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  return $null
}

$psql = Get-PsqlPath
if (-not $psql) { Write-Error "psql.exe not found. Ensure PostgreSQL is installed."; exit 1 }

try {
  $env:PGPASSWORD = $Password
  Write-Host "[DB] Connecting to $User@$Host:$Port/$Database" -ForegroundColor Yellow
  & $psql -U $User -h $Host -p $Port -d $Database -c "SELECT current_user, current_database();" | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "Connection failed" }
  Write-Host "[DB] Connection OK" -ForegroundColor Green

  Write-Host "[DB] Checking tables..." -ForegroundColor Yellow
  & $psql -U $User -h $Host -p $Port -d $Database -c "\dt" | Out-Null
  Write-Host "[DB] Tables listed." -ForegroundColor Green

  Write-Host "[DB] Checking 'users' table and default doctor..." -ForegroundColor Yellow
  $res = & $psql -U $User -h $Host -p $Port -d $Database -t -A -c "SELECT id,email,is_active FROM users WHERE email='doctor@maueyecare.com'" 2>&1
  if ($LASTEXITCODE -eq 0 -and $res.Trim()) {
    Write-Host "[DB] Default user exists: $res" -ForegroundColor Green
  } else {
    Write-Host "[DB] Default user not found." -ForegroundColor DarkYellow
  }
} finally {
  Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}


