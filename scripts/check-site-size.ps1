param(
  [switch]$Force,
  [int]$LimitMb = 1024,
  [int]$WarnPercent = 80,
  [int]$CriticalPercent = 95,
  [double]$FileWarnMiB = 20,
  [double]$FileCriticalMiB = 24
)

$ErrorActionPreference = "Stop"
$SiteRoot = Split-Path $PSScriptRoot -Parent

function Get-GitIgnorePatterns {
  param([string]$Root)
  $patterns = @()
  $ignorePath = Join-Path $Root ".gitignore"
  if (-not (Test-Path $ignorePath)) { return $patterns }
  foreach ($line in Get-Content $ignorePath) {
    $line = $line.Trim()
    if (-not $line -or $line.StartsWith("#")) { continue }
    $patterns += $line
  }
  return $patterns
}

function Test-GitIgnoredPath {
  param(
    [string]$RelativePath,
    [string[]]$Patterns
  )
  $normalized = ($RelativePath -replace "\\", "/").TrimStart("/")
  foreach ($pattern in $Patterns) {
    $p = ($pattern -replace "\\", "/").TrimStart("/")
    if ($p.EndsWith("/")) {
      if ($normalized.StartsWith($p) -or ($normalized + "/").StartsWith($p)) { return $true }
      continue
    }
    if ($p.Contains("*")) {
      $regex = "^" + ($p -replace "\.", "\." -replace "\*", ".*") + "$"
      if ($normalized -match $regex) { return $true }
      continue
    }
    if ($normalized -eq $p -or $normalized.StartsWith("$p/")) { return $true }
  }
  return $false
}

function Get-SiteSizeReport {
  param(
    [string]$Root,
    [string[]]$IgnorePatterns
  )

  $folderSizes = @{}
  $total = 0L
  $fileCount = 0
  $largestFile = $null
  $largestBytes = 0L

  Get-ChildItem -Path $Root -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.FullName -match "\\\.git\\") { return }
    $relative = $_.FullName.Substring($Root.Length).TrimStart("\")
    if (Test-GitIgnoredPath -RelativePath $relative -Patterns $IgnorePatterns) { return }

    $fileCount++
    $total += $_.Length
    if ($_.Length -gt $largestBytes) {
      $largestBytes = $_.Length
      $largestFile = $relative
    }

    $top = ($relative -split "\\", 2)[0]
    if (-not $folderSizes.ContainsKey($top)) {
      $folderSizes[$top] = 0L
    }
    $folderSizes[$top] += $_.Length
  }

  return [PSCustomObject]@{
    TotalBytes = $total
    FolderSizes = $folderSizes
    FileCount = $fileCount
    LargestFile = $largestFile
    LargestBytes = $largestBytes
  }
}

$ignorePatterns = Get-GitIgnorePatterns -Root $SiteRoot
$report = Get-SiteSizeReport -Root $SiteRoot -IgnorePatterns $ignorePatterns
$totalMb = [math]::Round($report.TotalBytes / 1MB, 2)
$limitBytes = [int64]$LimitMb * 1MB
$warnBytes = [int64][math]::Floor($limitBytes * ($WarnPercent / 100.0))
$criticalBytes = [int64][math]::Floor($limitBytes * ($CriticalPercent / 100.0))
$percentUsed = if ($limitBytes -gt 0) { [math]::Round(($report.TotalBytes / $limitBytes) * 100, 1) } else { 0 }
$largestMiB = [math]::Round($report.LargestBytes / 1MB, 2)

Write-Host "Deployable site size (respects .gitignore): $totalMb MB ($($report.TotalBytes) bytes)"
Write-Host "Files: $($report.FileCount) | Limit: $LimitMb MB | Used: $percentUsed% | Warn at $WarnPercent% | Critical at $CriticalPercent%"

if ($report.LargestFile) {
  Write-Host "Largest file: $($report.LargestFile) ($largestMiB MiB)"
}

Write-Host ""
Write-Host "Largest top-level folders:"
$report.FolderSizes.GetEnumerator() |
  Sort-Object Value -Descending |
  Select-Object -First 5 |
  ForEach-Object {
    $mb = [math]::Round($_.Value / 1MB, 2)
    Write-Host ("  {0,-24} {1,8} MB" -f $_.Key, $mb)
  }

$exitCode = 0

if ($largestMiB -ge $FileCriticalMiB) {
  Write-Host ""
  Write-Host "CRITICAL: Largest file is $largestMiB MiB (Cloudflare hard limit 25 MiB)." -ForegroundColor Red
  if (-not $Force) { $exitCode = 2 }
}

if ($largestMiB -ge $FileWarnMiB -and $largestMiB -lt $FileCriticalMiB) {
  Write-Host ""
  Write-Host "WARNING: Largest file is $largestMiB MiB (approaching Cloudflare 25 MiB limit)." -ForegroundColor Yellow
  if ($exitCode -eq 0) { $exitCode = 1 }
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
  if ($exitCode -eq 0) { $exitCode = 1 }
}

if ($exitCode -eq 0) {
  Write-Host ""
  Write-Host "OK: Under $WarnPercent% of site size budget and file size limits."
}

exit $exitCode
