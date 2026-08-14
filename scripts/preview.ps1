# Start local preview server for chittinandchattin.com
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

if (-not (Test-Path "$root\index.html")) {
    Write-Error "index.html not found in $root"
    exit 1
}

function Test-PortInUse([int]$Port) {
    $matches = netstat -ano | Select-String "LISTENING" | Select-String ":$Port\s"
    return [bool]$matches
}

$port = 8780
while (Test-PortInUse $port) {
    $port++
    if ($port -gt 8799) {
        Write-Error "No free preview port found between 8780-8799"
        exit 1
    }
}

if (Test-PortInUse 8080) {
    Write-Host "Note: port 8080 is already in use by another app — not this site." -ForegroundColor Yellow
    Write-Host "      Use the URL below instead of localhost:8080." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Chittin' and Chattin preview: http://localhost:$port/" -ForegroundColor Green
Write-Host "Puzzle:                       http://localhost:$port/puzzle/" -ForegroundColor Green
Write-Host "Ctrl+C to stop"
python -m http.server $port
