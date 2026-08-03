param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$Message,
  [switch]$Force
)

Set-Location (Split-Path $PSScriptRoot -Parent)
. (Join-Path $PSScriptRoot "git-author.ps1")

$sizeArgs = @()
if ($Force) { $sizeArgs += "-Force" }
& (Join-Path $PSScriptRoot "check-site-size.ps1") @sizeArgs
$sizeExit = $LASTEXITCODE
if ($sizeExit -eq 2 -and -not $Force) {
  Write-Host "Push aborted due to site size critical threshold."
  exit 2
}

git add .
git status

if (-not (git diff --cached --quiet)) {
  $commitExit = Invoke-GitCommitWithAuthor -Message $Message
  if ($commitExit -ne 0) { exit $commitExit }
  git push origin main
  Write-Host "Pushed to main. Cloudflare Pages will redeploy in 1-3 minutes."
} else {
  Write-Host "Nothing to commit."
}
