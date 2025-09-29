# Start Backend Server
$ErrorActionPreference = "Stop"

Set-Location "D:\Dev\codorch"

$env:DATABASE_URL = "postgresql://usr_codorch:lebaro13@localhost:5432/codorch_dev"
$env:OPENAI_BASE_URL = "http://localhost:3000/v1"
$env:OPENAI_API_KEY = "b09805ca3e309fcb98cf790e08b6ce422450c405e13f18f5476561b513034381"
$env:DEFAULT_MODEL = "gemini-2.5-flash"
$env:ADVANCED_MODEL = "gemini-2.5-pro"
$env:SECRET_KEY = "dev-secret-key-change-in-production-32-chars-min"
$env:PYTHONPATH = "D:\Dev\codorch"

Write-Host "Starting Codorch Backend..." -ForegroundColor Green
Write-Host "Database: $env:DATABASE_URL" -ForegroundColor Cyan
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan

Set-Location "backend"
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
