<#
.SYNOPSIS
    Step 3 — Hybrid (vector + full-text) search. Adds the full-text
    index on dbo.ProductReviews(ReviewText), creates the hybrid search
    stored procedure, and smoke-tests it with three demo queries.

.DESCRIPTION
    Reads step 1's outputs.json for SQL FQDN + database + OpenAI endpoint
    + embedding deployment. Substitutes the <<OPENAI_ENDPOINT>> and
    <<EMBEDDING_DEPLOYMENT>> placeholders in the SQL files at runtime
    and pipes each through "sqlcmd -G".

    Step 2 must already be complete (dbo.get_embedding must exist and
    ReviewEmbedding must be populated). This script does NOT re-run
    step 2.

.EXAMPLE
    .\steps\03-hybrid-search-sp\deploy.ps1
#>

[CmdletBinding()]
param()

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

Write-Section '0/3  Loading step 1 outputs'

if (-not (Test-Path $step1Out)) {
    throw "Step 1 outputs not found at $step1Out. Run step 1 first."
}
$step1 = Get-Content $step1Out -Raw | ConvertFrom-Json

$fqdn      = $step1.sqlServerFqdn
$db        = $step1.sqlDatabaseName
$endpoint  = $step1.openAiEndpoint.TrimEnd('/')
$deploy    = $step1.embeddingDeployment

Write-Host "SQL FQDN              : $fqdn"
Write-Host "Database              : $db"
Write-Host "OpenAI endpoint       : $endpoint"
Write-Host "Embedding deployment  : $deploy"

if (-not (Get-Command sqlcmd -ErrorAction SilentlyContinue)) {
    throw 'sqlcmd not found. See the prerequisites in the root README.'
}

$tokenMap = @{
    '<<OPENAI_ENDPOINT>>'      = $endpoint
    '<<EMBEDDING_DEPLOYMENT>>' = $deploy
}

function Invoke-SqlFile {
    param([Parameter(Mandatory)] [string] $Path)
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

Write-Section '1/3  Creating full-text catalog + index on dbo.ProductReviews'
Invoke-SqlFile (Join-Path $sqlFolder '01-create-fulltext-index.sql')

Write-Section '2/3  Creating dbo.find_similar_reviews_hybrid stored procedure'
Invoke-SqlFile (Join-Path $sqlFolder '02-create-hybrid-search-sp.sql')

Write-Section '3/3  Smoke-testing with three demo queries'
Invoke-SqlFile (Join-Path $sqlFolder '03-test-hybrid-search.sql')

Write-Section 'Done'
Write-Host ''
Write-Host 'You now have:' -ForegroundColor Green
Write-Host "  Full-text catalog    : ftCatalog"
Write-Host "  Full-text index      : dbo.ProductReviews(ReviewText)"
Write-Host "  Stored procedure     : dbo.find_similar_reviews_hybrid"
Write-Host ''
Write-Host 'Try your own query:' -ForegroundColor Yellow
Write-Host "  sqlcmd -S $fqdn -d $db -G -Q `"EXEC dbo.find_similar_reviews_hybrid @openAiEndpoint=N'$endpoint', @embeddingDeployment=N'$deploy', @queryText=N'your query here', @top=5;`""
Write-Host ''
Write-Host 'Next: open steps/04-dab-local/README.md' -ForegroundColor Yellow
