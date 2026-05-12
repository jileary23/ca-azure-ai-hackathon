<#
.SYNOPSIS
    Step 4 — Generate a local dab-config.json for Data API Builder.

.DESCRIPTION
    Reads step 1's outputs.json for the SQL FQDN + database name, fills
    those into dab-config.template.json, and writes the result to
    .\steps\04-dab-local\dab-config.json (which is gitignored).

    The generated config uses "Authentication=Active Directory Default"
    on the connection string. When you run "dab start" from this folder,
    DAB picks up YOUR developer identity (whoever's currently logged in
    via "az login") to connect to Azure SQL. The UAMI does NOT come
    into play locally — that switch happens in step 5 on ACA.

    This script does NOT start DAB. Run "dab start" yourself in the
    same folder once it's done — that's a long-running server, not
    something a deploy script should background.

.PARAMETER LaunchDab
    If specified, launches "dab start" in this terminal after generating
    the config. Ctrl-C to stop. Default: $false.

.EXAMPLE
    .\steps\04-dab-local\deploy.ps1
    # then in the same folder:
    dab start

.EXAMPLE
    .\steps\04-dab-local\deploy.ps1 -LaunchDab
#>

[CmdletBinding()]
param(
    [switch] $LaunchDab
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$here     = Split-Path -Parent $MyInvocation.MyCommand.Path
$template = Join-Path $here 'dab-config.template.json'
$config   = Join-Path $here 'dab-config.json'
$step1Out = Join-Path $here '..\01-foundation\outputs.json'

function Write-Section([string]$Title) {
    Write-Host ''
    Write-Host ('=' * 72) -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host ('=' * 72) -ForegroundColor Cyan
}

Write-Section '0/2  Loading step 1 outputs'

if (-not (Test-Path $step1Out)) {
    throw "Step 1 outputs not found at $step1Out. Run step 1 first."
}
$step1 = Get-Content $step1Out -Raw | ConvertFrom-Json

$fqdn = $step1.sqlServerFqdn
$db   = $step1.sqlDatabaseName

Write-Host "SQL FQDN  : $fqdn"
Write-Host "Database  : $db"

# -----------------------------------------------------------------------------
# 1. Tool checks
# -----------------------------------------------------------------------------

Write-Section '1/2  Verifying prerequisites'

$dotnet = Get-Command dotnet -ErrorAction SilentlyContinue
if (-not $dotnet) {
    throw '.NET SDK not found. Install .NET 8 (see root README prerequisites section F).'
}
Write-Host ".NET    : $((dotnet --version).Trim())"

$dab = Get-Command dab -ErrorAction SilentlyContinue
if (-not $dab) {
    throw "DAB CLI not found. Install with: dotnet tool install --global Microsoft.DataApiBuilder"
}
Write-Host "DAB CLI : $((dab --version 2>&1) -join ' ')"

# Confirm the developer is signed in to Azure (the local connection uses their identity)
$account = & az account show --query "{user:user.name, tenant:tenantId}" -o json 2>$null
if (-not $account) {
    throw 'Not signed in to Azure CLI. Run "az login" first.'
}
$acct = $account | ConvertFrom-Json
Write-Host "az login: $($acct.user)"

# -----------------------------------------------------------------------------
# 2. Generate dab-config.json
# -----------------------------------------------------------------------------

Write-Section '2/2  Generating dab-config.json'

$tokenMap = @{
    '<<SQL_FQDN>>' = $fqdn
    '<<SQL_DB>>'   = $db
}

$content = Get-Content -LiteralPath $template -Raw
foreach ($k in $tokenMap.Keys) {
    $content = $content.Replace($k, $tokenMap[$k])
}
Set-Content -LiteralPath $config -Value $content -Encoding utf8
Write-Host "Wrote: $config"

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------

Write-Section 'Done'
Write-Host ''
Write-Host 'Start DAB locally with:' -ForegroundColor Yellow
Write-Host "  cd .\steps\04-dab-local"
Write-Host "  dab start"
Write-Host ''
Write-Host 'Then in another terminal try:' -ForegroundColor Yellow
Write-Host "  curl http://localhost:5000/api/Product"
Write-Host "  curl http://localhost:5000/api/ProductReview"
Write-Host ''

if ($LaunchDab) {
    Write-Section 'Launching dab start (Ctrl-C to stop)'
    Push-Location $here
    try {
        & dab start
    } finally {
        Pop-Location
    }
}
