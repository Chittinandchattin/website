param(
    [switch]$DryRun,
    [switch]$Force,
    [string]$Token = ""
)

# Fetch episode thumbnails, then preview /episodes/ locally
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

$py = "python"
if (Test-Path "$root\.venv-transcribe\Scripts\python.exe") {
    $py = "$root\.venv-transcribe\Scripts\python.exe"
}

Write-Host "Refreshing episode list from RSS..." -ForegroundColor Cyan
& $py scripts/pull-episodes.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$fetchArgs = @("scripts/fetch-episode-images.py")
if ($DryRun) { $fetchArgs += "--dry-run" }
if ($Force) { $fetchArgs += "--force" }
if ($Token) { $fetchArgs += @("--token", $Token) }

Write-Host "Fetching per-episode thumbnails from Spotify..." -ForegroundColor Cyan
if (-not $Token -and -not $env:SPOTIFY_ACCESS_TOKEN) {
    Write-Host "Tip: if auto token fails, set `$env:SPOTIFY_ACCESS_TOKEN from browser DevTools (get_access_token)." -ForegroundColor Yellow
}
& $py @fetchArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($DryRun) {
    Write-Host "Dry run complete. Re-run without -DryRun to download, then preview." -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "Starting local preview — open /episodes/ to check thumbnails." -ForegroundColor Green
& "$PSScriptRoot\preview.ps1"
