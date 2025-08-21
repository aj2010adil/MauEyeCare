# MauEyeCare Test Runner Script
# This script runs all tests for the MauEyeCare application

param(
    [string]$TestType = "all",  # all, unit, integration, e2e
    [switch]$Coverage,
    [switch]$Watch,
    [switch]$Verbose
)

Write-Host "🔬 MauEyeCare Test Runner" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: package.json not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check dependencies
Write-Host "📋 Checking dependencies..." -ForegroundColor Yellow

$missingDeps = @()

if (-not (Test-Command "node")) {
    $missingDeps += "Node.js"
}

if (-not (Test-Command "npm")) {
    $missingDeps += "npm"
}

if (-not (Test-Command "python")) {
    $missingDeps += "Python"
}

if (-not (Test-Command "pytest")) {
    $missingDeps += "pytest"
}

if ($missingDeps.Count -gt 0) {
    Write-Host "❌ Missing dependencies: $($missingDeps -join ', ')" -ForegroundColor Red
    Write-Host "Please install the missing dependencies and try again." -ForegroundColor Red
    exit 1
}

Write-Host "✅ All dependencies found" -ForegroundColor Green

# Install npm dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing npm dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install npm dependencies" -ForegroundColor Red
        exit 1
    }
}

# Install Python dependencies if needed
if (-not (Test-Path ".venv")) {
    Write-Host "🐍 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment and install dependencies
Write-Host "🐍 Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
if (-not (Test-Path ".venv\Lib\site-packages\fastapi")) {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
        exit 1
    }
}

# Function to run tests
function Run-Tests {
    param(
        [string]$Type,
        [string]$Description
    )
    
    Write-Host "`n🧪 Running $Description tests..." -ForegroundColor Magenta
    Write-Host "----------------------------------------" -ForegroundColor Magenta
    
    $startTime = Get-Date
    
    switch ($Type) {
        "unit" {
            if ($Coverage) {
                npm run test:coverage
            } elseif ($Watch) {
                npm run test -- --watch
            } else {
                npm run test
            }
        }
        "integration" {
            python -m pytest tests/test_integration.py -v
        }
        "e2e" {
            # Run integration tests first
            python -m pytest tests/test_integration.py -v
            if ($LASTEXITCODE -eq 0) {
                # Then run unit tests
                if ($Coverage) {
                    npm run test:coverage
                } else {
                    npm run test
                }
            }
        }
    }
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $Description tests completed successfully in $($duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Green
    } else {
        Write-Host "❌ $Description tests failed after $($duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to start backend server for integration tests
function Start-BackendServer {
    Write-Host "🚀 Starting backend server for integration tests..." -ForegroundColor Yellow
    
    # Check if backend is already running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend server is already running" -ForegroundColor Green
            return $true
        }
    } catch {
        # Server not running, start it
    }
    
    # Start backend server in background
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        & ".\.venv\Scripts\Activate.ps1"
        python -m uvicorn main:app --host 0.0.0.0 --port 8000
    }
    
    # Wait for server to start
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Backend server started successfully" -ForegroundColor Green
                return $true
            }
        } catch {
            $attempt++
            Start-Sleep -Seconds 1
        }
    }
    
    Write-Host "❌ Failed to start backend server" -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    return $false
}

# Function to stop backend server
function Stop-BackendServer {
    Write-Host "🛑 Stopping backend server..." -ForegroundColor Yellow
    Get-Job | Where-Object { $_.Command -like "*uvicorn*" } | Stop-Job -ErrorAction SilentlyContinue
    Get-Job | Where-Object { $_.Command -like "*uvicorn*" } | Remove-Job -ErrorAction SilentlyContinue
}

# Main test execution
$allTestsPassed = $true

try {
    switch ($TestType.ToLower()) {
        "unit" {
            $allTestsPassed = Run-Tests -Type "unit" -Description "Unit"
        }
        "integration" {
            if (Start-BackendServer) {
                $allTestsPassed = Run-Tests -Type "integration" -Description "Integration"
            } else {
                $allTestsPassed = $false
            }
        }
        "e2e" {
            if (Start-BackendServer) {
                $allTestsPassed = Run-Tests -Type "e2e" -Description "End-to-End"
            } else {
                $allTestsPassed = $false
            }
        }
        "all" {
            if (Start-BackendServer) {
                $allTestsPassed = Run-Tests -Type "unit" -Description "Unit"
                if ($allTestsPassed) {
                    $allTestsPassed = Run-Tests -Type "integration" -Description "Integration"
                }
            } else {
                $allTestsPassed = $false
            }
        }
        default {
            Write-Host "❌ Invalid test type: $TestType" -ForegroundColor Red
            Write-Host "Valid options: unit, integration, e2e, all" -ForegroundColor Yellow
            exit 1
        }
    }
} finally {
    # Always stop the backend server
    Stop-BackendServer
}

# Final results
Write-Host "`n📊 Test Results Summary" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan

if ($allTestsPassed) {
    Write-Host "🎉 All tests passed successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "💥 Some tests failed. Please check the output above." -ForegroundColor Red
    exit 1
}
