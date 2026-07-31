param(
  [switch]$Force,
  [int]$LimitMb = 1024,
  [int]$WarnPercent = 80,
  [int]$CriticalPercent = 95
)

$ErrorActionPreference = "Stop"
$SiteRoot = Split-Path $PSScriptRoot -Parent

function Get-SiteSizeReport {
  param([string]$Root)

  $folderSizes = @{}
  $total = 0L

  Get-ChildItem -Path $Root -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.FullName -match "\\\.git\\") { return }
    $total += $_.Length
    $relative = $_.FullName.Substring($Root.Length).TrimStart("\")
    $top = ($relative -split "\\", 2)[0]
    if (-not $folderSizes.ContainsKey($top)) {
      $folderSizes[$top] = 0L
    }
    $folderSizes[$top] += $_.Length
  }

  return [PSCustomObject]@{
    TotalBytes = $total
    FolderSizes = $folderSizes
  }
}

$report = Get-SiteSizeReport -Root $SiteRoot
$totalMb = [math]::Round($report.TotalBytes / 1MB, 2)
$limitBytes = [int64]$LimitMb * 1MB
$warnBytes = [int64][math]::Floor($limitBytes * ($WarnPercent / 100.0))
$criticalBytes = [int64][math]::Floor($limitBytes * ($CriticalPercent / 100.0))
$percentUsed = if ($limitBytes -gt 0) { [math]::Round(($report.TotalBytes / $limitBytes) * 100, 1) } else { 0 }

Write-Host "Site size (excluding .git): $totalMb MB ($($report.TotalBytes) bytes)"
Write-Host "Limit: $LimitMb MB | Used: $percentUsed% | Warn at $WarnPercent% | Critical at $CriticalPercent%"

Write-Host ""
Write-Host "Largest top-level folders:"
$report.FolderSizes.GetEnumerator() |
  Sort-Object Value -Descending |
  Select-Object -First 5 |
  ForEach-Object {
    $mb = [math]::Round($_.Value / 1MB, 2)
    Write-Host ("  {0,-24} {1,8} MB" -f $_.Key, $mb)
  }

if ($report.TotalBytes -ge $criticalBytes -and -not $Force) {
  Write-Host ""
  Write-Host "CRITICAL: Site is at or above $CriticalPercent% of the $LimitMb MB budget. Push blocked. Re-run with -Force after review." -ForegroundColor Red
  exit 2
}

if ($report.TotalBytes -ge $warnBytes) {
  Write-Host ""
  Write-Host "WARNING: Site is at or above $WarnPercent% of the $LimitMb MB budget." -ForegroundColor Yellow
  if (-not $Force) {
    Write-Host "Proceeding is allowed. Use -Force to skip this warning on future pushes."
  }
  exit 1
}

Write-Host ""
Write-Host "OK: Under $WarnPercent% of site size budget."
exit 0
