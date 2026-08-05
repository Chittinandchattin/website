# Start local preview server for chittinandchattin.com
Set-Location (Split-Path $PSScriptRoot -Parent)
Write-Host "Preview at http://localhost:8080/ (Ctrl+C to stop)"
python -m http.server 8080
