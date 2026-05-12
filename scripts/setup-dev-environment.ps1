#!/usr/bin/env pwsh
# =============================================================================
# CA Hackathon Accelerators — Developer Environment Setup Script (Windows)
# =============================================================================
# Installs all tools, runtimes, VS Code extensions, and project dependencies
# needed to run the accelerators locally or deploy them to Azure.
#
# Usage:
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#   .\scripts\setup-dev-environment.ps1
#
# Options:
#   -SkipToolInstall   Skip system-level tool installation (if already done)
#   -SkipExtensions    Skip VS Code extension installation
#   -MockOnly          Only install dependencies needed for mock mode (Labs 00-03)
# =============================================================================

param(
    [switch]$SkipToolInstall,
    [switch]$SkipExtensions,
    [switch]$MockOnly
)

$ErrorActionPreference = "Stop"

# ── Helpers ──────────────────────────────────────────────────────────────────

function Write-Header($msg) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  $msg" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
}

function Write-Step($msg) {
    Write-Host ""
    Write-Host ">>> $msg" -ForegroundColor Yellow
}

function Write-OK($msg) {
    Write-Host "  [OK] $msg" -ForegroundColor Green
}

function Write-Warn($msg) {
    Write-Host "  [WARN] $msg" -ForegroundColor DarkYellow
}

function Write-Fail($msg) {
    Write-Host "  [FAIL] $msg" -ForegroundColor Red
}

function Test-CommandExists($cmd) {
    return $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

function Install-WingetPackage($id, $name) {
    if (-not (Test-CommandExists "winget")) {
        Write-Warn "winget not available — install $name manually from the URL shown above."
        return
    }
    Write-Host "  Installing $name via winget..." -ForegroundColor Gray
    winget install --id $id --silent --accept-package-agreements --accept-source-agreements 2>&1 | Out-Null
    Write-OK "$name installed"
}

# ── Banner ────────────────────────────────────────────────────────────────────

Write-Header "CA Hackathon Accelerators — Dev Environment Setup"
Write-Host "  This script installs all required tools, extensions, and"
Write-Host "  project dependencies for the CA State AI Hackathon repo."
Write-Host ""
Write-Host "  Estimated time: 5–15 minutes depending on network speed."
Write-Host ""

# ── 1. System Tools ───────────────────────────────────────────────────────────

if (-not $SkipToolInstall) {
    Write-Header "1. System Tools"

    # ── Git ──────────────────────────────────────────────────────────────────
    Write-Step "Git"
    if (Test-CommandExists "git") {
        $gitVersion = git --version
        Write-OK "Already installed: $gitVersion"
    }
    else {
        Write-Host "  Download: https://git-scm.com/download/win"
        Install-WingetPackage "Git.Git" "Git"
    }

    # ── Python 3.11+ ─────────────────────────────────────────────────────────
    Write-Step "Python 3.11+"
    $pythonOk = $false
    foreach ($cmd in @("python", "python3")) {
        if (Test-CommandExists $cmd) {
            $ver = & $cmd --version 2>&1
            if ($ver -match "3\.(1[1-9]|[2-9]\d)") {
                Write-OK "Already installed: $ver"
                $pythonOk = $true
                break
            }
        }
    }
    if (-not $pythonOk) {
        Write-Host "  Download: https://www.python.org/downloads/  (3.11 or newer)"
        Install-WingetPackage "Python.Python.3.11" "Python 3.11"
        Write-Warn "Restart your terminal after Python installs to refresh PATH."
    }

    # ── Node.js 18+ ──────────────────────────────────────────────────────────
    Write-Step "Node.js 18+ (LTS)"
    if (Test-CommandExists "node") {
        $nodeVer = node --version
        $nodeMajor = [int]($nodeVer -replace "v(\d+).*", '$1')
        if ($nodeMajor -ge 18) {
            Write-OK "Already installed: $nodeVer"
        }
        else {
            Write-Warn "Node $nodeVer found but 18+ required. Upgrading..."
            Install-WingetPackage "OpenJS.NodeJS.LTS" "Node.js LTS"
        }
    }
    else {
        Write-Host "  Download: https://nodejs.org/en/download/"
        Install-WingetPackage "OpenJS.NodeJS.LTS" "Node.js LTS"
    }

    # ── Docker Desktop ────────────────────────────────────────────────────────
    Write-Step "Docker Desktop"
    if (Test-CommandExists "docker") {
        $dockerVer = docker --version
        Write-OK "Already installed: $dockerVer"
    }
    else {
        Write-Host "  Download: https://www.docker.com/products/docker-desktop/"
        Install-WingetPackage "Docker.DockerDesktop" "Docker Desktop"
        Write-Warn "Start Docker Desktop and complete the initial setup before running containers."
    }

    # ── Azure CLI ─────────────────────────────────────────────────────────────
    Write-Step "Azure CLI (az)"
    if (Test-CommandExists "az") {
        $azVer = az version --query '"azure-cli"' -o tsv 2>&1
        Write-OK "Already installed: $azVer"
    }
    else {
        Write-Host "  Download: https://aka.ms/installazurecliwindows"
        Install-WingetPackage "Microsoft.AzureCLI" "Azure CLI"
    }

    # ── Azure Developer CLI (azd) ─────────────────────────────────────────────
    Write-Step "Azure Developer CLI (azd)"
    if (Test-CommandExists "azd") {
        $azdVer = azd version 2>&1
        Write-OK "Already installed: $azdVer"
    }
    else {
        Write-Host "  Install docs: https://aka.ms/azd-install"
        if (Test-CommandExists "winget") {
            winget install --id Microsoft.Azd --silent --accept-package-agreements --accept-source-agreements 2>&1 | Out-Null
            Write-OK "Azure Developer CLI (azd) installed"
        }
        else {
            # Fallback: PowerShell installer
            Write-Host "  Running azd installer script..."
            Invoke-RestMethod "https://aka.ms/install-azd.ps1" | Invoke-Expression
            Write-OK "Azure Developer CLI (azd) installed"
        }
    }

    Write-Step "Refreshing PATH for this session..."
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
    [System.Environment]::GetEnvironmentVariable("Path", "User")

}
else {
    Write-Host ""
    Write-Host "  Skipping system tool installation (-SkipToolInstall)" -ForegroundColor Gray
}

# ── 2. VS Code Extensions ─────────────────────────────────────────────────────

if (-not $SkipExtensions) {
    Write-Header "2. VS Code Extensions"

    if (-not (Test-CommandExists "code")) {
        Write-Warn "'code' CLI not found. Open VS Code, press Ctrl+Shift+P, then run:"
        Write-Host "         'Shell Command: Install code command in PATH'" -ForegroundColor Gray
        Write-Host "  Then re-run this script with the -SkipToolInstall flag."
    }
    else {
        $extensions = @(
            # Python
            @{ id = "ms-python.python"; name = "Python" },
            @{ id = "ms-python.vscode-pylance"; name = "Pylance" },
            @{ id = "ms-python.black-formatter"; name = "Black Formatter" },
            @{ id = "charliermarsh.ruff"; name = "Ruff (Python linter)" },

            # TypeScript / Frontend
            @{ id = "dbaeumer.vscode-eslint"; name = "ESLint" },
            @{ id = "esbenp.prettier-vscode"; name = "Prettier" },
            @{ id = "bradlc.vscode-tailwindcss"; name = "Tailwind CSS IntelliSense" },

            # Azure
            @{ id = "ms-azuretools.vscode-docker"; name = "Docker" },
            @{ id = "ms-azuretools.vscode-azurefunctions"; name = "Azure Functions" },
            @{ id = "ms-azuretools.vscode-bicep"; name = "Bicep" },
            @{ id = "ms-azuretools.azure-dev"; name = "Azure Developer CLI (azd)" },

            # Testing
            @{ id = "ms-playwright.playwright"; name = "Playwright Test" },

            # Utilities
            @{ id = "redhat.vscode-yaml"; name = "YAML" },
            @{ id = "github.copilot"; name = "GitHub Copilot" },
            @{ id = "github.copilot-chat"; name = "GitHub Copilot Chat" },
            @{ id = "eamodio.gitlens"; name = "GitLens" }
        )

        foreach ($ext in $extensions) {
            Write-Host "  Installing: $($ext.name)..." -ForegroundColor Gray
            code --install-extension $ext.id --force 2>&1 | Out-Null
            Write-OK $ext.name
        }
    }
}
else {
    Write-Host ""
    Write-Host "  Skipping VS Code extension installation (-SkipExtensions)" -ForegroundColor Gray
}

# ── 3. Project Root Dependencies ──────────────────────────────────────────────

Write-Header "3. Project Root (npm)"

if (Test-CommandExists "npm") {
    Write-Step "Installing root npm devDependencies (concurrently, etc.)"
    npm install --silent
    Write-OK "Root npm packages installed"
}
else {
    Write-Fail "npm not found. Install Node.js first, then re-run."
}

# ── 4. Backend Python Dependencies ────────────────────────────────────────────

Write-Header "4. Backend Python Dependencies"

$pythonCmd = if (Test-CommandExists "python3") { "python3" } else { "python" }

Write-Step "Upgrading pip"
& $pythonCmd -m pip install --upgrade pip --quiet
Write-OK "pip upgraded"

Write-Step "Installing backend/requirements.txt"
Push-Location backend
& $pythonCmd -m pip install -r requirements.txt --quiet
Pop-Location
Write-OK "Backend dependencies installed"

# ── 5. Frontend Dependencies ──────────────────────────────────────────────────

Write-Header "5. Frontend Dependencies"

Write-Step "Installing frontend/package.json dependencies"
Push-Location frontend
npm install --silent
Pop-Location
Write-OK "Frontend dependencies installed"

# ── 6. Accelerator Dependencies ───────────────────────────────────────────────

Write-Header "6. Accelerator Dependencies"

$accelDirs = Get-ChildItem -Path "accelerators" -Directory | Sort-Object Name

foreach ($accel in $accelDirs) {
    $backendReq = Join-Path $accel.FullName "backend\requirements.txt"
    $frontendPkg = Join-Path $accel.FullName "frontend\package.json"

    if (Test-Path $backendReq) {
        Write-Step "$($accel.Name) — Python backend"
        & $pythonCmd -m pip install -r $backendReq --quiet
        Write-OK "$($accel.Name) backend"
    }

    if (Test-Path $frontendPkg) {
        Write-Step "$($accel.Name) — Node frontend"
        Push-Location (Join-Path $accel.FullName "frontend")
        npm install --silent
        Pop-Location
        Write-OK "$($accel.Name) frontend"
    }
}

# ── 7. Playwright Browsers ────────────────────────────────────────────────────

Write-Header "7. Playwright Browsers (E2E Testing)"

if (Test-CommandExists "npx") {
    Write-Step "Installing Chromium browser for Playwright"
    Push-Location frontend
    npx playwright install chromium --with-deps 2>&1 | Out-Null
    Pop-Location
    Write-OK "Playwright Chromium installed"
}
else {
    Write-Warn "npx not found — skipping Playwright browser install"
}

# ── 8. Environment Files ──────────────────────────────────────────────────────

Write-Header "8. Environment Files"

Write-Step "Creating .env files for mock-mode local development"

# Backend .env
$backendEnv = "backend\.env"
if (-not (Test-Path $backendEnv)) {
    @"
# Backend environment — mock mode (no Azure credentials required for Labs 00-03)
USE_MOCK_SERVICES=true
ENVIRONMENT=development

# Uncomment and fill in for Labs 04+ (real Azure services)
# AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
# AZURE_OPENAI_DEPLOYMENT=gpt-4.1
# AZURE_OPENAI_API_VERSION=2025-04-01-preview
# AZURE_COSMOS_ENDPOINT=https://<your-account>.documents.azure.com:443/
# AZURE_SEARCH_ENDPOINT=https://<your-service>.search.windows.net
# AZURE_KEY_VAULT_URL=https://<your-vault>.vault.azure.net/
"@ | Set-Content $backendEnv
    Write-OK "Created backend/.env (mock mode)"
}
else {
    Write-Warn "backend/.env already exists — skipping"
}

# Frontend .env
$frontendEnv = "frontend\.env"
if (-not (Test-Path $frontendEnv)) {
    @"
# Frontend environment
VITE_API_URL=http://localhost:8000
"@ | Set-Content $frontendEnv
    Write-OK "Created frontend/.env"
}
else {
    Write-Warn "frontend/.env already exists — skipping"
}

# ── 9. Azure CLI Login (Optional) ────────────────────────────────────────────

if (-not $MockOnly) {
    Write-Header "9. Azure Login (Labs 04+ / Deployment)"
    Write-Host ""
    Write-Host "  To deploy to Azure or run Labs 04+, you need to log in:" -ForegroundColor White
    Write-Host ""
    Write-Host "    az login                    # Interactive browser login" -ForegroundColor Cyan
    Write-Host "    azd auth login              # azd-specific login" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Then set your subscription:" -ForegroundColor White
    Write-Host ""
    Write-Host "    az account set --subscription <subscription-id>" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  See AZURE-RBAC-REQUIREMENTS.md for required role assignments." -ForegroundColor Gray
}
else {
    Write-Host ""
    Write-Host "  Mock-only mode — Azure login not required for Labs 00-03." -ForegroundColor Gray
}

# ── 10. Verification ──────────────────────────────────────────────────────────

Write-Header "10. Verification"

Write-Step "Checking installed tools..."

$checks = @(
    @{ cmd = "python"; args = "--version"; label = "Python" },
    @{ cmd = "node"; args = "--version"; label = "Node.js" },
    @{ cmd = "npm"; args = "--version"; label = "npm" },
    @{ cmd = "docker"; args = "--version"; label = "Docker" },
    @{ cmd = "az"; args = "version --query '\"azure-cli\"' -o tsv"; label = "Azure CLI" },
    @{ cmd = "azd"; args = "version"; label = "Azure Dev CLI" }
)

$allOk = $true
foreach ($check in $checks) {
    if (Test-CommandExists $check.cmd) {
        try {
            $ver = Invoke-Expression "$($check.cmd) $($check.args)" 2>&1
            Write-OK "$($check.label): $ver"
        }
        catch {
            Write-OK "$($check.label): installed"
        }
    }
    else {
        Write-Fail "$($check.label): NOT FOUND"
        $allOk = $false
    }
}

# ── Summary ───────────────────────────────────────────────────────────────────

Write-Header "Setup Complete!"
Write-Host ""

if ($allOk) {
    Write-Host "  All tools verified. You're ready to go!" -ForegroundColor Green
}
else {
    Write-Host "  Some tools were not found. Restart your terminal and re-run" -ForegroundColor Yellow
    Write-Host "  this script, or install the missing tools manually." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Quick Start (mock mode — no Azure needed):" -ForegroundColor White
Write-Host ""
Write-Host "    npm run smoke-test          # Verify environment" -ForegroundColor Cyan
Write-Host "    npm start                   # Run backend + frontend" -ForegroundColor Cyan
Write-Host "    docker-compose up           # Run via Docker" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Accelerator quick-start:" -ForegroundColor White
Write-Host ""
Write-Host "    npm run accel:001           # BenefitsCal Navigator (mock)" -ForegroundColor Cyan
Write-Host "    npm run accel:002           # Wildfire Response (mock)" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Azure deployment (Labs 04+):" -ForegroundColor White
Write-Host ""
Write-Host "    az login && azd auth login  # Authenticate" -ForegroundColor Cyan
Write-Host "    azd up                      # Provision + deploy all services" -ForegroundColor Cyan
Write-Host "    azd deploy accel-001        # Deploy single accelerator" -ForegroundColor Cyan
Write-Host ""
Write-Host "  See README.md and docs/ for full documentation." -ForegroundColor Gray
Write-Host ""
