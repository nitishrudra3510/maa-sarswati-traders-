# Video Recommendation Engine - Complete Setup Script
# This script will set up everything and run the API

Write-Host "=== Video Recommendation Engine Setup ===" -ForegroundColor Green

# Move to project directory
Set-Location "C:\Users\ACER\OneDrive\Documents\AI VIDEO RECOMMENDATION ENGINE"

# 1. Locate Python
Write-Host "1. Locating Python..." -ForegroundColor Yellow
$pythonPath = $null

# Try common installation paths
$possiblePaths = @(
    "C:\Users\ACER\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files (x86)\Python312\python.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $pythonPath = $path
        break
    }
}

# Try PATH
if (-not $pythonPath) {
    try {
        $pythonCmd = Get-Command python.exe -ErrorAction Stop
        $pythonPath = $pythonCmd.Path
    } catch {
        Write-Host "Python not found in PATH" -ForegroundColor Red
    }
}

# Install Python if not found
if (-not $pythonPath) {
    Write-Host "Installing Python 3.12..." -ForegroundColor Yellow
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    Start-Sleep -Seconds 10
    
    # Try again after installation
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $pythonPath = $path
            break
        }
    }
}

if (-not $pythonPath) {
    Write-Error "Python installation failed. Please install Python 3.12 manually and restart PowerShell."
    exit 1
}

Write-Host "Using Python: $pythonPath" -ForegroundColor Green

# 2. Create virtual environment
Write-Host "2. Creating virtual environment..." -ForegroundColor Yellow
& $pythonPath -m venv .venv

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Error "Failed to create virtual environment"
    exit 1
}

# 3. Install dependencies
Write-Host "3. Installing dependencies..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install fastapi "uvicorn[standard]" sqlalchemy alembic pydantic requests python-dotenv redis httpx pytest aiosqlite

# 4. Create .env file if it doesn't exist
Write-Host "4. Setting up environment..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    @"
FLIC_TOKEN=flic_11d3da28e403d182c36a3530453e290add87d0b4a40ee50f17611f180d47956f
API_BASE_URL=https://api.socialverseapp.com
DATABASE_URL=sqlite+aiosqlite:///./app.db
REDIS_URL=redis://localhost:6379/0
APP_NAME=video-recommendation-engine
DEBUG=true
"@ | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "Created .env file with default values" -ForegroundColor Green
}

# 5. Run database migrations
Write-Host "5. Running database migrations..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m alembic upgrade head

# 6. Start the server
Write-Host "6. Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API docs at: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start server in foreground so you can see logs
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload