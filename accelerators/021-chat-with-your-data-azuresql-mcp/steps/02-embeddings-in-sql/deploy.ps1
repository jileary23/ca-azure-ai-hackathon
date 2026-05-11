<#
.SYNOPSIS
    Step 2 — Embeddings in SQL. Wires Azure SQL to the Foundry embedding
    endpoint (via the UAMI), creates dbo.get_embedding, smoke-tests it,
    and backfills embeddings over dbo.ProductReviews. Optionally installs
    an auto-embed trigger.

.DESCRIPTION
    Reads step 1's outputs.json to discover the SQL FQDN, database name,
    OpenAI endpoint, embedding deployment name, and UAMI name — so you
    don't have to type or copy any of those.

    For each .sql file under sql\, this script substitutes the
    <<UAMI_NAME>>, <<OPENAI_ENDPOINT>>, and <<EMBEDDING_DEPLOYMENT>>
    placeholders with the real values, writes the result to a temp file,
    runs it via "sqlcmd -G", then deletes the temp file.

    The same .sql files can also be opened in your SQL Editor (VS Code
    MSSQL extension, SSMS, Azure Data Studio). Edit the DECLARE lines
    marked EDIT at the top of each script with the same values from
    outputs.json, then run.

.PARAMETER InstallAutoEmbedTrigger
    Default $false. Pass -InstallAutoEmbedTrigger to install the optional
    trigger that auto-embeds rows on INSERT/UPDATE.

.PARAMETER SkipBackfill
    Default $false. Pass -SkipBackfill to create the SP but not embed
    any rows yet.

.EXAMPLE
    .\steps\02-embeddings-in-sql\deploy.ps1

.EXAMPLE
    .\steps\02-embeddings-in-sql\deploy.ps1 -InstallAutoEmbedTrigger
#>

[CmdletBinding()]
param(
    [switch] $InstallAutoEmbedTrigger,
    [switch] $SkipBackfill
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$here       = Split-Path -Parent $MyInvocation.MyCommand.Path
$sqlFolder  = Join-Path $here 'sql'
$step1Out   = Join-Path $here '..\01-foundation\outputs.json'

function Write-Section([string]$Title) {
    Write-Host ''
    Write-Host ('=' * 72) -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host ('=' * 72) -ForegroundColor Cyan
}

# -----------------------------------------------------------------------------
# 0. Read step 1 outputs
# -----------------------------------------------------------------------------

Write-Section '0/6  Loading step 1 outputs'

if (-not (Test-Path $step1Out)) {
    throw "Step 1 outputs not found at $step1Out. Run step 1 first."
}
$step1 = Get-Content $step1Out -Raw | ConvertFrom-Json

$fqdn      = $step1.sqlServerFqdn
$db        = $step1.sqlDatabaseName
$endpoint  = $step1.openAiEndpoint.TrimEnd('/')
$deploy    = $step1.embeddingDeployment
$uamiName  = $step1.uamiName

Write-Host "SQL FQDN              : $fqdn"
Write-Host "Database              : $db"
Write-Host "OpenAI endpoint       : $endpoint"
Write-Host "Embedding deployment  : $deploy"
Write-Host "UAMI name             : $uamiName"

if (-not (Get-Command sqlcmd -ErrorAction SilentlyContinue)) {
    throw 'sqlcmd not found. See the prerequisites in the root README.'
}

# Map each <<TOKEN>> to its replacement value. Files only need to use the
# tokens they actually care about; unused tokens are simply not present.
$tokenMap = @{
    '<<UAMI_NAME>>'            = $uamiName
    '<<OPENAI_ENDPOINT>>'      = $endpoint
    '<<EMBEDDING_DEPLOYMENT>>' = $deploy
}

function Invoke-SqlFile {
    param(
        [Parameter(Mandatory)] [string] $Path
    )
    $name = Split-Path -Leaf $Path
    Write-Host "  -> $name"

    $content = Get-Content -LiteralPath $Path -Raw
    foreach ($k in $tokenMap.Keys) {
        $content = $content.Replace($k, $tokenMap[$k])
    }

    $tmp = New-TemporaryFile
    $tmp = Rename-Item -Path $tmp.FullName -NewName ($tmp.BaseName + '.sql') -PassThru
    try {
        Set-Content -LiteralPath $tmp.FullName -Value $content -Encoding utf8
        & sqlcmd -S $fqdn -d $db -G -i $tmp.FullName -b
        if ($LASTEXITCODE -ne 0) {
            throw "sqlcmd failed for $name (exit $LASTEXITCODE)"
        }
    } finally {
        Remove-Item -LiteralPath $tmp.FullName -ErrorAction SilentlyContinue
    }
}

# -----------------------------------------------------------------------------
# 1. UAMI database user
# -----------------------------------------------------------------------------

Write-Section '1/6  Creating database user for the UAMI'
Invoke-SqlFile (Join-Path $sqlFolder '01-create-uami-db-user.sql')

# -----------------------------------------------------------------------------
# 2. Database scoped credential
# -----------------------------------------------------------------------------

Write-Section '2/6  Creating database master key + DATABASE SCOPED CREDENTIAL'
Invoke-SqlFile (Join-Path $sqlFolder '02-create-credential.sql')

# -----------------------------------------------------------------------------
# 3. dbo.get_embedding SP (no tokens needed)
# -----------------------------------------------------------------------------

Write-Section '3/6  Creating dbo.get_embedding stored procedure'
Invoke-SqlFile (Join-Path $sqlFolder '03-create-get-embedding-sp.sql')

# -----------------------------------------------------------------------------
# 4. Smoke test
# -----------------------------------------------------------------------------

Write-Section '4/6  Smoke-testing dbo.get_embedding on a single string'
Invoke-SqlFile (Join-Path $sqlFolder '04-test-embedding.sql')

# -----------------------------------------------------------------------------
# 5. Backfill
# -----------------------------------------------------------------------------

if ($SkipBackfill) {
    Write-Section '5/6  -SkipBackfill set - leaving ReviewEmbedding NULL'
} else {
    Write-Section '5/6  Backfilling ReviewEmbedding for all NULL rows'
    Invoke-SqlFile (Join-Path $sqlFolder '05-backfill-embeddings.sql')
}

# -----------------------------------------------------------------------------
# 6. Optional trigger
# -----------------------------------------------------------------------------

if ($InstallAutoEmbedTrigger) {
    Write-Section '6/6  Installing optional auto-embed trigger'
    Invoke-SqlFile (Join-Path $sqlFolder '06-create-auto-embed-trigger.sql')
} else {
    Write-Section '6/6  Skipping auto-embed trigger (pass -InstallAutoEmbedTrigger to install)'
}

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------

Write-Section 'Done'
Write-Host ''
Write-Host 'You now have:' -ForegroundColor Green
Write-Host "  Database user        : $uamiName  (db_datareader, db_datawriter, EXEC on dbo)"
Write-Host "  Credential           : $endpoint  (Managed Identity)"
Write-Host "  Stored procedure     : dbo.get_embedding"
if (-not $SkipBackfill) {
    Write-Host "  Embeddings backfilled over dbo.ProductReviews"
}
if ($InstallAutoEmbedTrigger) {
    Write-Host "  Trigger              : dbo.trg_ProductReviews_AutoEmbed"
}
Write-Host ''
Write-Host 'Verify with:' -ForegroundColor Yellow
Write-Host "  sqlcmd -S $fqdn -d $db -G -Q `"SELECT COUNT(*) AS embedded FROM dbo.ProductReviews WHERE ReviewEmbedding IS NOT NULL;`""
Write-Host ''
Write-Host 'Next: open steps/03-hybrid-search-sp/README.md' -ForegroundColor Yellow
