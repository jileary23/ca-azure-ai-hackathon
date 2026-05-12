<#
.SYNOPSIS
    Step 1 — Foundation. Deploys the resource group, UAMI, Azure SQL,
    Azure AI Foundry account + project, and an embedding model deployment.
    Optionally seeds the demo Products + ProductReviews data.

.DESCRIPTION
    What this script does, in order:

      1. Verifies you are logged in to az and on the right subscription.
      2. Resolves your AAD object id + UPN (used as the SQL AAD admin).
      3. Resolves your current public IPv4 (added to the SQL firewall).
      4. Creates the resource group if missing.
      5. Deploys steps/01-foundation/bicep/main.bicep.
      6. Runs sql/00-create-schema.sql to create dbo.Products and
         dbo.ProductReviews (the ReviewEmbedding VECTOR(1536) column is
         created here but stays NULL until step 2).
      7. If -SeedSampleData (default), runs 01-seed-products.sql and
         02-seed-reviews.sql.
      8. Prints a "what you got" summary and the values you'll need
         later (also written to .\steps\01-foundation\outputs.json).

.PARAMETER ResourceGroupName
    Resource group to deploy into. Created if it does not exist.

.PARAMETER Location
    Azure region. Default: eastus2.

.PARAMETER NamePrefix
    Lowercase alphanumeric prefix used in resource names.
    3-12 chars. Example: "sqlrag".

.PARAMETER EnvironmentName
    Short env name appended to resource names. 2-6 chars. Default: dev.

.PARAMETER SubscriptionId
    Optional. If set, switches az to this subscription before deploying.

.PARAMETER SeedSampleData
    Default $true. Pass -SeedSampleData:$false to skip the demo data.

.PARAMETER SkipSqlScripts
    Default $false. If set, only the Bicep deploys; no SQL is run.
    Useful if your client cannot reach Azure SQL on port 1433.

.EXAMPLE
    .\steps\01-foundation\deploy.ps1 -ResourceGroupName rg-sqlrag-dev -NamePrefix sqlrag

.EXAMPLE
    # Skip the demo data — bring your own table later (see step 2 BYO appendix)
    .\steps\01-foundation\deploy.ps1 -ResourceGroupName rg-sqlrag-dev -NamePrefix sqlrag -SeedSampleData:$false
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $ResourceGroupName,

    [string] $Location = 'eastus2',

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z][a-z0-9]{2,11}$')]
    [string] $NamePrefix,

    [ValidatePattern('^[a-z][a-z0-9]{1,5}$')]
    [string] $EnvironmentName = 'dev',

    [string] $SubscriptionId,

    [bool] $SeedSampleData = $true,

    [switch] $SkipSqlScripts
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$here       = Split-Path -Parent $MyInvocation.MyCommand.Path
$bicepFile  = Join-Path $here 'bicep\main.bicep'
$sqlFolder  = Join-Path $here 'sql'
$outFile    = Join-Path $here 'outputs.json'

function Write-Section([string]$Title) {
    Write-Host ''
    Write-Host ('=' * 72) -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host ('=' * 72) -ForegroundColor Cyan
}

# -----------------------------------------------------------------------------
# 1. az login + subscription
# -----------------------------------------------------------------------------

Write-Section '1/8  Verifying az login'

$account = az account show -o json 2>$null | ConvertFrom-Json
if (-not $account) {
    throw 'Not logged in. Run "az login" first.'
}
if ($SubscriptionId -and $account.id -ne $SubscriptionId) {
    Write-Host "Switching to subscription $SubscriptionId"
    az account set --subscription $SubscriptionId | Out-Null
    $account = az account show -o json | ConvertFrom-Json
}
Write-Host "Subscription: $($account.name) ($($account.id))"
Write-Host "Tenant:       $($account.tenantId)"

# -----------------------------------------------------------------------------
# 2. Resolve signed-in user (SQL AAD admin)
# -----------------------------------------------------------------------------

Write-Section '2/8  Resolving signed-in user (will become SQL AAD admin)'

$me = az ad signed-in-user show -o json | ConvertFrom-Json
$adminObjectId = $me.id
$adminLogin    = if ($me.userPrincipalName) { $me.userPrincipalName } else { $me.displayName }
Write-Host "AAD admin login:    $adminLogin"
Write-Host "AAD admin objectId: $adminObjectId"

# -----------------------------------------------------------------------------
# 3. Resolve developer IP for SQL firewall
# -----------------------------------------------------------------------------

Write-Section '3/8  Resolving your public IPv4 for SQL firewall'

$myIp = '0.0.0.0'
try {
    $myIp = (Invoke-RestMethod -Uri 'https://api.ipify.org?format=json' -TimeoutSec 10).ip
    Write-Host "Detected IP: $myIp"
} catch {
    Write-Warning "Could not detect public IP. Skipping developer firewall rule. You can add one later in the portal or via 'az sql server firewall-rule create'."
}

# -----------------------------------------------------------------------------
# 4. Create resource group if missing
# -----------------------------------------------------------------------------

Write-Section "4/8  Ensuring resource group $ResourceGroupName exists in $Location"

$rg = az group show -n $ResourceGroupName -o json 2>$null | ConvertFrom-Json
if (-not $rg) {
    az group create -n $ResourceGroupName -l $Location -o none
    Write-Host 'Created.'
} else {
    Write-Host 'Already exists.'
}

# -----------------------------------------------------------------------------
# 5. Deploy Bicep
# -----------------------------------------------------------------------------

Write-Section '5/8  Deploying Bicep (this is the slow step ~3-6 minutes)'

$deployName = "step01-{0:yyyyMMddHHmmss}" -f (Get-Date)

$deployOut = az deployment group create `
    --resource-group $ResourceGroupName `
    --name $deployName `
    --template-file $bicepFile `
    --parameters `
        namePrefix=$NamePrefix `
        environmentName=$EnvironmentName `
        location=$Location `
        sqlAadAdminObjectId=$adminObjectId `
        sqlAadAdminLogin=$adminLogin `
        developerIpAddress=$myIp `
    --output json | ConvertFrom-Json

if ($LASTEXITCODE -ne 0 -or -not $deployOut) {
    throw 'Bicep deployment failed. See az output above.'
}

$o = $deployOut.properties.outputs

# Persist outputs for later steps
$summary = [ordered]@{
    deployedAtUtc        = (Get-Date).ToUniversalTime().ToString('o')
    resourceGroup        = $ResourceGroupName
    location             = $Location
    namePrefix           = $NamePrefix
    environmentName      = $EnvironmentName
    uamiName             = $o.uamiName.value
    uamiResourceId       = $o.uamiResourceId.value
    uamiClientId         = $o.uamiClientId.value
    uamiPrincipalId      = $o.uamiPrincipalId.value
    sqlServerName        = $o.sqlServerName.value
    sqlServerFqdn        = $o.sqlServerFqdn.value
    sqlDatabaseName      = $o.sqlDatabaseName.value
    foundryAccountName   = $o.foundryAccountName.value
    foundryProjectName   = $o.foundryProjectName.value
    foundryEndpoint      = $o.foundryEndpoint.value
    openAiEndpoint       = $o.openAiEndpoint.value
    embeddingDeployment  = $o.embeddingDeployment.value
}
$summary | ConvertTo-Json -Depth 4 | Set-Content -Path $outFile -Encoding utf8
Write-Host "Bicep outputs saved to: $outFile"

# -----------------------------------------------------------------------------
# 6 + 7. Run SQL scripts
# -----------------------------------------------------------------------------

if ($SkipSqlScripts) {
    Write-Section '6-7/8  -SkipSqlScripts set — skipping all SQL'
} else {
    Write-Section '6/8  Creating schema (dbo.Products, dbo.ProductReviews)'

    $sqlServerFqdn = $summary.sqlServerFqdn
    $sqlDb         = $summary.sqlDatabaseName

    if (-not (Get-Command sqlcmd -ErrorAction SilentlyContinue)) {
        throw "sqlcmd not found. Install it: https://learn.microsoft.com/sql/tools/sqlcmd/sqlcmd-utility"
    }

    function Invoke-SqlFile([string]$Path) {
        Write-Host "  -> $(Split-Path -Leaf $Path)"
        & sqlcmd -S $sqlServerFqdn -d $sqlDb -G -i $Path -b
        if ($LASTEXITCODE -ne 0) { throw "sqlcmd failed for $Path (exit $LASTEXITCODE)" }
    }

    Invoke-SqlFile (Join-Path $sqlFolder '00-create-schema.sql')

    if ($SeedSampleData) {
        Write-Section '7/8  Seeding sample data (10 products, 18 reviews)'
        Invoke-SqlFile (Join-Path $sqlFolder '01-seed-products.sql')
        Invoke-SqlFile (Join-Path $sqlFolder '02-seed-reviews.sql')
    } else {
        Write-Section '7/8  -SeedSampleData:$false — skipping sample inserts'
        Write-Host 'Tables exist but are empty. You can:'
        Write-Host '  - Run the seed files later: sqlcmd -S <fqdn> -d ProductsDB -G -i 01-seed-products.sql'
        Write-Host '  - Or bring your own table; see step 2 BYO appendix.'
    }
}

# -----------------------------------------------------------------------------
# 8. Summary
# -----------------------------------------------------------------------------

Write-Section '8/8  Done'

Write-Host ''
Write-Host 'You now have:' -ForegroundColor Green
Write-Host "  Resource group     : $ResourceGroupName"
Write-Host "  UAMI               : $($summary.uamiName)"
Write-Host "  SQL server (FQDN)  : $($summary.sqlServerFqdn)"
Write-Host "  SQL database       : $($summary.sqlDatabaseName)"
Write-Host "  Foundry account    : $($summary.foundryAccountName)"
Write-Host "  Foundry project    : $($summary.foundryProjectName)"
Write-Host "  OpenAI endpoint    : $($summary.openAiEndpoint)"
Write-Host "  Embedding deploy   : $($summary.embeddingDeployment)"
Write-Host ''
Write-Host 'Next: open steps/02-embeddings-in-sql/README.md' -ForegroundColor Yellow
