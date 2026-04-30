<#
.SYNOPSIS
Builds and packages the MauEyeCare Clinical Suite into a single standalone deployment folder.

.DESCRIPTION
This script publishes the WPF Desktop Client (as a self-contained executable) and the ASP.NET Core API,
then copies the Python AI Microservice into a 'Dist' folder. The result is a folder that can be zipped
and distributed to the doctor's PC.
#>

$DistDir = ".\Dist\MauEyeCare_ClinicalSuite"
$BackupDir = ".\Dist\Build_Backup"
if (Test-Path $DistDir) {
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
    if (Test-Path "$DistDir\maueyecare.db") {
        Copy-Item -Path "$DistDir\maueyecare.db" -Destination "$BackupDir\maueyecare.db" -Force
    }
    if (Test-Path "$DistDir\MauEyeCare.AI\models") {
        Copy-Item -Path "$DistDir\MauEyeCare.AI\models" -Destination "$BackupDir" -Recurse -Force
    }

    Get-ChildItem -Path $DistDir -Exclude "*.db", "*.txt", "*.log" | Remove-Item -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $DistDir | Out-Null

Write-Host "1. Building API..." -ForegroundColor Cyan
dotnet publish .\MauEyeCare.API\MauEyeCare.API.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o "$DistDir\API_Temp"

Write-Host "2. Building Desktop Application..." -ForegroundColor Cyan
dotnet publish .\MauEyeCare.Desktop\MauEyeCare.Desktop.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o "$DistDir"

Write-Host "3. Merging Components..." -ForegroundColor Cyan
# Move API executable to the same directory as Desktop
Move-Item -Path "$DistDir\API_Temp\MauEyeCare.API.exe" -Destination "$DistDir\MauEyeCare.API.exe" -Force

# Copy the API's appsettings.json so it has its JWT Key and ConnectionStrings
if (Test-Path "$DistDir\API_Temp\appsettings.json") {
    Copy-Item -Path "$DistDir\API_Temp\appsettings.json" -Destination "$DistDir\appsettings.json" -Force
}

Remove-Item -Recurse -Force "$DistDir\API_Temp"

# Copy AI Directory
$AiDest = "$DistDir\MauEyeCare.AI"
New-Item -ItemType Directory -Force -Path $AiDest | Out-Null
Copy-Item -Path ".\MauEyeCare.AI\app.py" -Destination $AiDest -Force
Copy-Item -Path ".\MauEyeCare.AI\requirements.txt" -Destination $AiDest -Force
Copy-Item -Path ".\MauEyeCare.AI\train_model.py" -Destination $AiDest -Force

# Restore or deploy AI models
if (Test-Path "$BackupDir\models") {
    Write-Host "Restoring AI Models from backup..." -ForegroundColor Yellow
    Copy-Item -Path "$BackupDir\models" -Destination $AiDest -Recurse -Force
} elseif (Test-Path ".\MauEyeCare.AI\models") {
    Copy-Item -Path ".\MauEyeCare.AI\models" -Destination $AiDest -Recurse -Force
}

# Restore DB if needed
if (Test-Path "$BackupDir\maueyecare.db") {
    Write-Host "Restoring Database from backup..." -ForegroundColor Yellow
    Copy-Item -Path "$BackupDir\maueyecare.db" -Destination "$DistDir\maueyecare.db" -Force
}

# Provide an easy runner shortcut or bat file
$LaunchBat = "$DistDir\Launch_MauEyeCare.bat"
"@echo off
echo Starting MauEyeCare Clinical Suite...
start MauEyeCare.Desktop.exe
" | Out-File -FilePath $LaunchBat -Encoding ASCII

Write-Host "=========================================================" -ForegroundColor Green
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "Deployment folder is ready at: $DistDir" -ForegroundColor White
Write-Host "The Desktop application will automatically launch the API and AI silently." -ForegroundColor White
Write-Host "Make sure Python 3.11+ is installed on the target machine." -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Green
