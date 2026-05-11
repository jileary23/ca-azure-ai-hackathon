<#
.SYNOPSIS
    Step 5 — Build the DAB image, push to ACR, deploy DAB on Azure
    Container Apps using the step 1 User-Assigned Managed Identity.

.DESCRIPTION
    1. Reads step 1 outputs.json for: resource group, namePrefix,
       environmentName, location, UAMI ids, SQL FQDN, SQL DB name.
    2. Verifies az login + the containerapp extension.
    3. Creates the Azure Container Registry (idempotent — runs
       "az acr create" so deploy.ps1 doesn't fight Bicep over image
       ordering).
    4. "az acr build" — submits the steps/05-dab-on-aca/docker folder
       (Dockerfile + dab-config.json) to ACR Tasks, which builds and
       tags the image inside Azure. No local Docker required.
    5. Builds the SQL connection string from step 1 outputs, using
       "Authentication=Active Directory Managed Identity;User Id=<clientId>".
    6. Deploys steps/05-dab-on-aca/bicep/main.bicep — creates the
       AcrPull role assignment, Log Analytics, ACA environment, and
       the ACA app referencing the freshly-built image.
    7. Prints the public https FQDN and writes outputs.json next to
       this script.

    No SQL changes are needed: step 2's 01-create-uami-db-user.sql
    already mapped the UAMI to a DB user and gave it db_datareader +
    db_datawriter + EXECUTE on schema::dbo.

.PARAMETER ImageTag
    Docker tag to apply to the built image. Default: "latest".

.PARAMETER SkipBuild
    Skip the "az acr build" step. Useful when iterating on the Bicep
    template only.

.EXAMPLE
    .\steps\05-dab-on-aca\deploy.ps1

.EXAMPLE
    .\steps\05-dab-on-aca\deploy.ps1 -ImageTag v2 -Verbose
#>

[CmdletBinding()]
param(
    [string] $ImageTag = 'latest',
    [switch] $SkipBuild
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$here       = Split-Path -Parent $MyInvocation.MyCommand.Path
$bicepFile  = Join-Path $here 'bicep\main.bicep'
$dockerDir  = Join-Path $here 'docker'
$step1Out   = Join-Path $here '..\01-foundation\outputs.json'
$outFile    = Join-Path $here 'outputs.json'

function Write-Section([string]$Title) {
    Write-Host ''
    Write-Host ('=' * 72) -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host ('=' * 72) -ForegroundColor Cyan
}

# -----------------------------------------------------------------------------
# 1. Load step 1 outputs
# -----------------------------------------------------------------------------

Write-Section '1/6  Loading step 1 outputs'

if (-not (Test-Path $step1Out)) {
    throw "Step 1 outputs not found at $step1Out. Run step 1 first."
}
$step1 = Get-Content $step1Out -Raw | ConvertFrom-Json

$resourceGroup    = $step1.resourceGroup
$location         = $step1.location
$namePrefix       = $step1.namePrefix
$environmentName  = $step1.environmentName
$uamiResourceId   = $step1.uamiResourceId
$uamiClientId     = $step1.uamiClientId
$uamiPrincipalId  = $step1.uamiPrincipalId
$sqlServerFqdn    = $step1.sqlServerFqdn
$sqlDatabaseName  = $step1.sqlDatabaseName

Write-Host "Resource group : $resourceGroup"
Write-Host "Location       : $location"
Write-Host "Name prefix    : $namePrefix"
Write-Host "Env            : $environmentName"
Write-Host "UAMI client id : $uamiClientId"
Write-Host "SQL FQDN       : $sqlServerFqdn"
Write-Host "Database       : $sqlDatabaseName"

# The ACR name has to be reproducible across re-runs (the Bicep references
# it by name), and it must be globally unique. The cleanest way to satisfy
# both constraints is to reuse the same per-RG suffix step 1 already baked
# into its SQL server name: "{namePrefix}-sql-{env}-{uniq}".
$sqlSrvName = $step1.sqlServerName
$uniqSuffix = $sqlSrvName.Substring($sqlSrvName.LastIndexOf('-') + 1)
if (-not $uniqSuffix) {
    throw "Could not derive uniq suffix from sqlServerName '$sqlSrvName'."
}
$acrName = ("{0}acr{1}{2}" -f $namePrefix, $environmentName, $uniqSuffix).ToLower()
Write-Host "ACR name       : $acrName"

# -----------------------------------------------------------------------------
# 2. Verify az + extensions
# -----------------------------------------------------------------------------

Write-Section '2/6  Verifying az + containerapp extension'

$account = az account show -o json 2>$null | ConvertFrom-Json
if (-not $account) {
    throw 'Not logged in. Run "az login".'
}
Write-Host "az subscription: $($account.name)"

# Ensure containerapp extension is present (silently install if not)
$ext = az extension list --query "[?name=='containerapp'].name" -o tsv
if (-not $ext) {
    Write-Host 'Installing az containerapp extension...'
    az extension add --name containerapp --yes | Out-Null
} else {
    Write-Host 'az containerapp extension already installed'
}

# Required providers
Write-Host 'Ensuring resource providers are registered (App, ContainerRegistry, OperationalInsights)...'
az provider register -n Microsoft.App --wait | Out-Null
az provider register -n Microsoft.ContainerRegistry --wait | Out-Null
az provider register -n Microsoft.OperationalInsights --wait | Out-Null

# -----------------------------------------------------------------------------
# 3. Create ACR (idempotent)
# -----------------------------------------------------------------------------

Write-Section '3/6  Ensuring Azure Container Registry exists'

$acrExists = az acr show -n $acrName -g $resourceGroup --query name -o tsv 2>$null
if (-not $acrExists) {
    Write-Host "Creating ACR $acrName..."
    az acr create `
        --resource-group $resourceGroup `
        --name $acrName `
        --sku Basic `
        --location $location `
        --admin-enabled false `
        -o none
} else {
    Write-Host "ACR $acrName already exists"
}

$acrLoginServer = az acr show -n $acrName -g $resourceGroup --query loginServer -o tsv

# -----------------------------------------------------------------------------
# 4. Build + push the DAB image
# -----------------------------------------------------------------------------

$dabImage = "$acrLoginServer/dab:$ImageTag"

if ($SkipBuild) {
    Write-Section '4/6  Skipping image build (-SkipBuild)'
    Write-Host "Will use existing image: $dabImage"
} else {
    Write-Section "4/6  Building image via ACR Tasks: $dabImage"
    az acr build `
        --registry $acrName `
        --resource-group $resourceGroup `
        --image "dab:$ImageTag" `
        --file (Join-Path $dockerDir 'Dockerfile') `
        $dockerDir
}

# -----------------------------------------------------------------------------
# 5. Build connection string
# -----------------------------------------------------------------------------

Write-Section '5/6  Building SQL connection string'

# Authentication=Active Directory Managed Identity + User Id=<UAMI clientId>
# tells the Microsoft.Data.SqlClient driver to acquire a token using that
# specific UAMI from IMDS (available inside the ACA container).
$sqlConn = "Server=tcp:$sqlServerFqdn,1433;Database=$sqlDatabaseName;Authentication=Active Directory Managed Identity;User Id=$uamiClientId;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
Write-Host "Connection string built (UAMI auth, no secrets)."

# -----------------------------------------------------------------------------
# 6. Deploy main Bicep (LAW + ACA env + ACA app + AcrPull role)
# -----------------------------------------------------------------------------

Write-Section '6/6  Deploying ACA infrastructure'

$deploymentName = "step5-$(Get-Date -Format yyyyMMddHHmmss)"

az deployment group create `
    --resource-group $resourceGroup `
    --name $deploymentName `
    --template-file $bicepFile `
    --parameters `
        namePrefix=$namePrefix `
        environmentName=$environmentName `
        location=$location `
        uamiResourceId=$uamiResourceId `
        uamiClientId=$uamiClientId `
        uamiPrincipalId=$uamiPrincipalId `
        acrName=$acrName `
        sqlConnectionString="$sqlConn" `
        dabImage="$dabImage" `
    -o none

$deployment = az deployment group show `
    --resource-group $resourceGroup `
    --name $deploymentName `
    -o json | ConvertFrom-Json

$outputs = $deployment.properties.outputs
$acaFqdn = $outputs.acaAppFqdn.value
$acaUrl  = $outputs.acaAppUrl.value
$acaApp  = $outputs.acaAppName.value

# -----------------------------------------------------------------------------
# Persist outputs and print summary
# -----------------------------------------------------------------------------

Write-Section 'Done'

$result = [ordered]@{
    deployedAtUtc   = (Get-Date).ToUniversalTime().ToString('o')
    resourceGroup   = $resourceGroup
    acrName         = $acrName
    acrLoginServer  = $acrLoginServer
    dabImage        = $dabImage
    acaAppName      = $acaApp
    acaAppFqdn      = $acaFqdn
    acaAppUrl       = $acaUrl
}
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $outFile -Encoding utf8
Write-Host "Wrote $outFile"
Write-Host ''
Write-Host "DAB is live at: $acaUrl" -ForegroundColor Yellow
Write-Host ''
Write-Host 'Quick smoke test:' -ForegroundColor Yellow
Write-Host "  curl $acaUrl/api/Product"
Write-Host ''
Write-Host 'Tail logs:' -ForegroundColor Yellow
Write-Host "  az containerapp logs show -g $resourceGroup -n $acaApp --follow"
Write-Host ''
