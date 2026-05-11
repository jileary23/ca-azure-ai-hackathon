<#
.SYNOPSIS
    Step 3 — Optional upgrade. Switches the embedding path from
    sp_invoke_external_rest_endpoint + dbo.get_embedding to the
    native CREATE EXTERNAL MODEL + AI_GENERATE_EMBEDDINGS primitives.

.DESCRIPTION
    Reads steps/01-foundation/outputs.json. Substitutes
    <<OPENAI_ENDPOINT>>, <<EMBEDDING_DEPLOYMENT>>, and <<UAMI_NAME>>
    in the SQL files at runtime and pipes each through "sqlcmd -G".

    Order of scripts:
      01-create-external-model.sql       -- registers EmbeddingModel,
                                            grants EXECUTE to the UAMI,
                                            smoke-tests the model.
      02-create-hybrid-search-sp-v2.sql  -- replaces find_similar_reviews_hybrid
                                            with a (queryText, top) signature.
      03-test-hybrid-search-v2.sql       -- runs three demo queries.

    Step 2 (DSC + master key + UAMI grants) and step 3's full-text index
    must already be in place. This script does NOT re-run them.

.EXAMPLE
    .\steps\03-hybrid-search-sp\upgrade-external-model\deploy.ps1
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$here       = Split-Path -Parent $MyInvocation.MyCommand.Path
$sqlFolder  = Join-Path $here 'sql'
$step1Out   = Join-Path $here '..\..\01-foundation\outputs.json'

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
$uamiName  = $step1.uamiName

Write-Host "SQL FQDN              : $fqdn"
Write-Host "Database              : $db"
Write-Host "OpenAI endpoint       : $endpoint"
Write-Host "Embedding deployment  : $deploy"
Write-Host "UAMI                  : $uamiName"

if (-not (Get-Command sqlcmd -ErrorAction SilentlyContinue)) {
    throw 'sqlcmd not found. See the prerequisites in the root README.'
}

$tokenMap = @{
    '<<OPENAI_ENDPOINT>>'      = $endpoint
    '<<EMBEDDING_DEPLOYMENT>>' = $deploy
    '<<UAMI_NAME>>'            = $uamiName
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

Write-Section '1/3  Registering EXTERNAL MODEL EmbeddingModel'
Invoke-SqlFile (Join-Path $sqlFolder '01-create-external-model.sql')

Write-Section '2/3  Replacing dbo.find_similar_reviews_hybrid (v2 signature)'
Invoke-SqlFile (Join-Path $sqlFolder '02-create-hybrid-search-sp-v2.sql')

Write-Section '3/3  Smoke-testing the v2 signature'
Invoke-SqlFile (Join-Path $sqlFolder '03-test-hybrid-search-v2.sql')

Write-Section 'Done'
Write-Host ''
Write-Host 'New call shape:' -ForegroundColor Green
Write-Host "  EXEC dbo.find_similar_reviews_hybrid @queryText = N'...', @top = 5;"
Write-Host ''
Write-Host 'MCP / DAB shape becomes:' -ForegroundColor Green
Write-Host '  execute_entity({ entity: "FindSimilarReviewsHybrid", parameters: { queryText, top } })'
Write-Host ''
Write-Host 'No DAB redeploy needed — DAB reflects the new signature on next request.' -ForegroundColor Yellow
