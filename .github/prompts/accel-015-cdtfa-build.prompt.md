---
agent: agent
description: Build and deploy the CDTFA Tax Compliance Navigator using Microsoft Agent Framework on Azure AI Foundry
tools:
  - AIAgentExpert
---

# 015 — CDTFA Tax Compliance Navigator

## Microsoft Agent Framework Build & Deploy

You are an expert Azure AI engineer. Build and deploy the **CDTFA Tax Compliance Navigator** for the California Department of Tax and Fee Administration using [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) on Azure AI Foundry.

## Accelerator Context

- **Agency:** California Department of Tax and Fee Administration (CDTFA)
- **Directory:** `accelerators/015-cdtfa-tax-compliance-navigator/`
- **Backend Port:** 8015
- **Purpose:** AI tax compliance navigator for California businesses — jurisdiction-specific tax rates, registration requirements, nexus rules, exemption certificates, cannabis taxes, and audit preparation. General guidance only; not legal/professional tax advice.

## Step 1 — Scaffold the Project Structure

```
accelerators/015-cdtfa-tax-compliance-navigator/
├── agent.yaml
├── agents/
│   ├── query_agent.yaml
│   ├── router_agent.yaml
│   └── action_agent.yaml
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── agents/
│   │   └── tools/
│   │       ├── tax_rate_tool.py        # CDTFA Tax Rate API (500+ CA jurisdictions)
│   │       ├── nexus_analyzer_tool.py  # Economic nexus threshold analysis
│   │       ├── exemption_tool.py       # Exemption certificate lookup
│   │       ├── filing_deadline_tool.py # Filing schedule calculator
│   │       └── search_tool.py          # Azure AI Search RAG
│   ├── mock_data/cdtfa/
│   └── requirements.txt
├── frontend/src/
├── infra/
└── .env.example
```

## Step 2 — Microsoft Agent Framework Agent Definitions

Create `agent.yaml`:

```yaml
name: cdtfa-tax-compliance-navigator
description: CDTFA Tax Compliance Navigator
version: "1.0"
framework: microsoft-agent-framework
pipeline:
  - query_agent
  - router_agent
  - action_agent
constitution: ../../shared/constitution.md
compliance:
  - EO N-12-23
  - CCPA/CPRA
  - CA Revenue & Taxation Code
  - CA Business & Professions Code §22250+
```

Create `agents/query_agent.yaml`:

```yaml
name: QueryAgent
model: gpt-4o
instructions: |
  You are the QueryAgent for the CDTFA Tax Compliance Navigator.
  1. Detect intent: tax_rate_lookup, business_registration, exemption_certificate, nexus_analysis, cannabis_tax, fuel_tax, filing_deadline, audit_rights, special_tax_program.
  2. Extract entities: business type (retail, manufacturer, online seller, cannabis dispensary, fuel distributor), transaction type, city/county (for rate lookup), filing frequency (monthly/quarterly/annual), EIN status.
  3. Detect if the query is account-specific (penalty waiver, payment plan, audit notice) — these must be redirected to CDTFA authenticated portal.
  4. Apply PII filter — strip EIN/SSN, account numbers before routing.
  5. Set complexity: SIMPLE (rate lookup) vs. COMPLEX (nexus analysis, audit prep) — complex queries include an advisory disclaimer.
  6. If the query is incomplete or ambiguous, request clarification before proceeding.
  Scope to general guidance only per CA Business & Professions Code §22250+ (unauthorized practice of tax advice).
tools:
  - name: pii_filter
    type: builtin
handoff: RouterAgent
```

Create `agents/router_agent.yaml`:

```yaml
name: RouterAgent
model: gpt-4o
instructions: |
  Route CDTFA queries to the correct tax program domain:
  - SALES_USE_TAX: rate lookups (500+ CA jurisdictions), nexus rules for online sellers, use tax obligations, drop shipping
  - EXEMPTIONS: manufacturing exemption, resale certificate, agricultural exemption, partial exemptions, CDTFA-230 series forms
  - BUSINESS_REGISTRATION: seller's permit, use tax account, when registration is required, economic nexus thresholds ($500K CA sales)
  - CANNABIS_TAX: cultivation tax, excise tax (retail, distributor), reporting timelines, track-and-trace integration
  - FUEL_TAX: motor vehicle fuel tax, diesel fuel tax, underground storage tank fee, IFTA
  - SPECIAL_TAXES: cigarette/tobacco, alcohol, hazardous waste, tire fee, lumber products assessment
  - FILING_COMPLIANCE: filing frequency, due dates, prepayment requirements, penalty calculation
  - AUDIT_RIGHTS: audit notification process, records to gather, Taxpayer Rights Advocate referral, statute of limitations
  - PORTAL_REDIRECT: account-specific actions (penalty waiver, payment plan, return amendment) → cdtfa.ca.gov/services/
handoff: ActionAgent
```

Create `agents/action_agent.yaml`:

```yaml
name: ActionAgent
model: gpt-4o
instructions: |
  Deliver jurisdiction-aware, citation-backed CDTFA tax guidance.
  Use Azure AI Search to query the CDTFA RAG index (Publications 73, 31, 45, 51, 61, CA Revenue & Taxation Code, tax rate schedules, exemption guides).
  Use the Tax Rate tool for real-time jurisdiction-specific rate lookups (CDTFA public API, mock in local dev).
  Use the Filing Deadline tool to calculate next due date based on business filing frequency.
  Always cite the specific CDTFA publication number and section, or CA R&TC section.
  Include standard disclaimer: "This is general guidance. For account-specific tax advice, consult a licensed CPA or tax attorney, or contact CDTFA at 1-800-400-7115."
  For cannabis tax queries: note that CDTFA coordinates with CDFA and DCC for track-and-trace requirements.
tools:
  - name: azure_ai_search
    type: azure_search
    index: cdtfa-knowledge-base
  - name: tax_rate_lookup
    type: function
    function: get_sales_tax_rate_by_location
  - name: filing_deadline
    type: function
    function: calculate_next_filing_deadline
  - name: exemption_lookup
    type: function
    function: get_exemption_certificate_info
```

## Step 3 — Backend Implementation

```python
# backend/app/main.py
from fastapi import FastAPI
from azure.identity import DefaultAzureCredential
import os

app = FastAPI(title="CDTFA Tax Compliance Navigator")
USE_MOCK = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

@app.post("/api/query")
async def query(request: dict):
    credential = DefaultAzureCredential() if not USE_MOCK else None
    query_result = await QueryAgent(credential).process(request["message"])
    route_result = await RouterAgent(credential).route(query_result)
    response = await ActionAgent(credential, mock=USE_MOCK).act(route_result)
    return {
        "response": response,
        "cdtfa_contact": "1-800-400-7115 | cdtfa.ca.gov",
        "disclaimer": "General guidance only. Consult a licensed tax professional for account-specific advice."
    }

@app.get("/api/tax-rate")
async def tax_rate(city: str, county: str, transaction_type: str = "retail"):
    """Direct tax rate lookup endpoint."""
    if USE_MOCK:
        return {"rate": 9.5, "jurisdiction": f"{city}, {county}", "mock": True}
    return await TaxRateTool().lookup(city=city, county=county, transaction_type=transaction_type)
```

## Step 4 — Azure Services to Provision

### Azure AI Foundry

```bash
az ml workspace create \
  --name cdtfa-tax-hub \
  --resource-group rg-cdtfa-tax \
  --kind hub

az ml workspace create \
  --name cdtfa-tax-project \
  --resource-group rg-cdtfa-tax \
  --kind project \
  --hub-name cdtfa-tax-hub
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name cdtfa-openai \
  --resource-group rg-cdtfa-tax \
  --kind OpenAI \
  --sku S0 \
  --location westus

az cognitiveservices account deployment create \
  --name cdtfa-openai \
  --resource-group rg-cdtfa-tax \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-11-20" \
  --model-format OpenAI \
  --sku-capacity 30 \
  --sku-name GlobalStandard
```

### Azure AI Search

```bash
az search service create \
  --name cdtfa-ai-search \
  --resource-group rg-cdtfa-tax \
  --sku Standard

# Index: cdtfa-knowledge-base
# Source documents:
#   - CDTFA Publication 73 (Your California Seller's Permit)
#   - CDTFA Publication 31 (Sales of Vehicles)
#   - CDTFA Publication 45 (A Guide to Sales and Use Tax)
#   - CDTFA Publication 51 (District Taxes and Delivered Sales)
#   - Cannabis Tax Guide
#   - Fuel Tax Guides
#   - Tax Rate Schedules by jurisdiction
#   - Exemption Certificate guides (CDTFA-230 series)
#   - CA Revenue & Taxation Code (key sections)
```

### Azure Container Apps

```bash
az containerapp create \
  --name cdtfa-tax-backend \
  --resource-group rg-cdtfa-tax \
  --environment cdtfa-env \
  --image ghcr.io/jileary23/cdtfa-tax:latest \
  --target-port 8015 \
  --env-vars \
    USE_MOCK_SERVICES=false \
    AZURE_OPENAI_ENDPOINT=secretref:openai-endpoint \
    AZURE_SEARCH_ENDPOINT=secretref:search-endpoint \
    CDTFA_TAX_RATE_API=https://api.cdtfa.ca.gov/taxrate/v1
```

## Step 5 — Bicep Infrastructure

Create `infra/main.bicep` defining:

- Azure AI Foundry Hub + Project (West US)
- Azure OpenAI (GPT-4o, 30K TPM GlobalStandard)
- Azure AI Search (Standard, `cdtfa-knowledge-base`)
- Azure Container Apps (public ingress — business-facing)
- Managed Identity with minimal role assignments
- Key Vault for all secrets
- Azure Front Door with rate limiting (prevent bulk tax rate scraping)
- Azure Monitor with 90-day log retention

## Step 6 — Deploy

```bash
cd accelerators/015-cdtfa-tax-compliance-navigator
azd up --environment cdtfa-dev

./scripts/azd-deploy.sh 015
```

## Compliance & Guardrails

- **CA B&P Code §22250+**: Advisory disclaimer on all responses; no account-specific tax advice
- **CCPA/CPRA**: PII filter removes EIN/SSN; no personal data stored
- **CA R&TC**: All rate and rule citations link to current CDTFA publications
- **EO N-12-23**: Source citations mandatory; confidence indicator on complex nexus analyses
- **Cannabis compliance**: CDTFA cannabis guidance coordinated with DCC track-and-trace references
- **Portal redirect**: Account-specific actions (penalties, payment plans, audits) always redirect to authenticated cdtfa.ca.gov

## Validation

```bash
USE_MOCK_SERVICES=true uvicorn backend.app.main:app --reload --port 8015 &
curl -X POST http://localhost:8015/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the sales tax rate for a retail transaction in Culver City, California?"}'
```

Run smoke tests: `npm run smoke-test -- --accelerator 015`
