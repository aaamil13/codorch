# Start Frontend Dev Server
$ErrorActionPreference = "Stop"

Set-Location "D:\Dev\codorch\frontend"

Write-Host "Starting Codorch Frontend..." -ForegroundColor Green
Write-Host "Frontend will be available at: http://localhost:9000" -ForegroundColor Cyan

npm run dev
