# Shared git author for Laughing Dragons repos (no permanent git config required).
$script:GitAuthorName = "Brandon Sparks"
$script:GitAuthorEmail = "laughingdragonsproductions@gmail.com"

function Set-GitAuthorEnv {
  $env:GIT_AUTHOR_NAME = $script:GitAuthorName
  $env:GIT_AUTHOR_EMAIL = $script:GitAuthorEmail
  $env:GIT_COMMITTER_NAME = $script:GitAuthorName
  $env:GIT_COMMITTER_EMAIL = $script:GitAuthorEmail
}

function Invoke-GitCommitWithAuthor {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Message
  )
  Set-GitAuthorEnv
  git commit -m $Message | Out-Null
  return $LASTEXITCODE
}
