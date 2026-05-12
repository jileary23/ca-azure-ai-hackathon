---
agent: agent
description: Build and deploy the DCA Professional License Navigator using Microsoft Agent Framework on Azure AI Foundry
tools:
  - AIAgentExpert
---

# 016 — DCA Professional License Navigator

## Microsoft Agent Framework Build & Deploy

You are an expert Azure AI engineer. Build and deploy the **DCA Professional License Navigator** for the California Department of Consumer Affairs using [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) on Azure AI Foundry.

## Accelerator Context

- **Agency:** California Department of Consumer Affairs (DCA)
- **Directory:** `accelerators/016-dca-license-navigator/`
- **Backend Port:** 8016
- **Purpose:** Multi-persona navigator for DCA's 40+ boards and bureaus — guides applicants through licensing requirements, helps licensees manage renewals and CE, enables consumers to verify licenses, and assists enforcement staff with disciplinary process queries

## Step 1 — Scaffold the Project Structure

```
accelerators/016-dca-license-navigator/
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
│   │       ├── license_lookup_tool.py     # DCA BreEZe API license status
│   │       ├── board_directory_tool.py    # Route to specific board/bureau
│   │       ├── ce_requirements_tool.py    # CE hours by profession
│   │       ├── application_status_tool.py # Application processing times
│   │       └── search_tool.py             # Azure AI Search RAG
│   ├── mock_data/dca/
│   └── requirements.txt
├── frontend/src/
├── infra/
└── .env.example
```

## Step 2 — Microsoft Agent Framework Agent Definitions

Create `agent.yaml`:

```yaml
name: dca-professional-license-navigator
description: DCA Professional License Navigator
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
  - CA Business & Professions Code
  - Bagley-Keene Open Meeting Act
```

Create `agents/query_agent.yaml`:

```yaml
name: QueryAgent
model: gpt-4o
instructions: |
  You are the QueryAgent for the DCA Professional License Navigator.
  1. Detect user persona:
     - APPLICANT: applying for a new California professional license
     - LICENSEE: currently licensed; questions about renewal, CE, name change, reinstatement
     - CONSUMER: verifying license status or filing a complaint
     - ENFORCEMENT: disciplinary process, accusation, probation requirements (route to BreEZe only)
  2. Detect profession category (first-level routing):
     HEALTH (medical, dental, pharmacy, nursing, behavioral health, veterinary)
     CONSTRUCTION (contractors, architects, engineers, landscapers)
     REAL_ESTATE_FINANCE (real estate brokers, appraisers, mortgage)
     AUTOMOTIVE (automotive repair, smog check, vehicle dealers)
     PERSONAL_SERVICES (cosmetology, barbering, acupuncture, physical therapy)
     PROFESSIONAL_SERVICES (accountants, attorneys-referral-only, court reporters)
     CANNABIS (Bureau of Cannabis Control — licenses overlap with CDFA/CDPH)
  3. Extract: license number (for verification), profession name, board/bureau name, renewal deadline, CE hours needed.
  4. Apply PII filter — strip SSN/license numbers after extraction.
  5. Flag URGENT for licenses expiring within 30 days or disciplinary deadlines.
  6. If the user's query is incomplete or ambiguous, request clarification before proceeding.
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
  Two-level routing strategy for DCA's 40+ boards and bureaus.

  Level 1 — Profession Category (from QueryAgent):
  HEALTH, CONSTRUCTION, REAL_ESTATE_FINANCE, AUTOMOTIVE, PERSONAL_SERVICES, PROFESSIONAL_SERVICES, CANNABIS

  Level 2 — Specific Board/Bureau:
  HEALTH: Medical Board (physicians) | Dental Board | Pharmacy Board | BRN (nurses) | BBS (LCSW, MFT, LPCC) | Osteopathic Board | Optometry Board | Veterinary Medicine Board | PT Board | Speech-Language Pathology Board
  CONSTRUCTION: CSLB (contractors) | Architects Board | PE Board (engineers) | Landscape Architects Technical Committee
  REAL_ESTATE_FINANCE: DRE (real estate) | BREA (appraisers) | DFPI (mortgage — refer to DFPI)
  AUTOMOTIVE: Bureau of Automotive Repair (BAR) | DMV Dealer (refer to DMV)
  PERSONAL_SERVICES: Board of Barbering & Cosmetology | Acupuncture Board | Cemetery/Funeral Board
  PROFESSIONAL_SERVICES: CBA (CPAs/accountants) | Court Reporters Board
  CANNABIS: Bureau of Cannabis Control (refer to DCC for current active programs)

  Routing actions:
  - NEW_APPLICATION: requirements, eligibility, exam info, application steps, processing times
  - RENEWAL: renewal deadlines, CE requirements, online renewal link (breeze.ca.gov)
  - LICENSE_VERIFICATION: call BreEZe API for public license status
  - COMPLAINT: complaint form, investigation process, what DCA can/cannot do
  - DISCIPLINARY: accusation process, hearing, probation conditions (serve document links)
  - CE_REQUIREMENTS: hours by renewal cycle, approved providers, audit risk
handoff: ActionAgent
```

Create `agents/action_agent.yaml`:

```yaml
name: ActionAgent
model: gpt-4o
instructions: |
  Deliver board-specific licensing guidance with DCA BreEZe integration.
  Use Azure AI Search to query the DCA RAG index (board application checklists, CA BPC sections, CE requirements by board, exam info guides, complaint process guides).
  Use the License Lookup tool to fetch real-time BreEZe license status (public data only).
  Use the CE Requirements tool to retrieve current CE hours and approved provider lists by board.
  Use the Application Status tool for current processing time estimates.
  Always link to the specific board's page at dca.ca.gov/licensees/ and to breeze.ca.gov for online services.
  Note: The DCA serves as an umbrella — responses must specify which board or bureau governs the profession.
tools:
  - name: azure_ai_search
    type: azure_search
    index: dca-knowledge-base
  - name: license_verification
    type: function
    function: lookup_dca_license_status
  - name: ce_requirements
    type: function
    function: get_ce_requirements_by_board
  - name: processing_times
    type: function
    function: get_application_processing_time
```

## Step 3 — Backend Implementation

```python
# backend/app/main.py
from fastapi import FastAPI
from azure.identity import DefaultAzureCredential
import os

app = FastAPI(title="DCA Professional License Navigator")
USE_MOCK = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

@app.post("/api/query")
async def query(request: dict):
    credential = DefaultAzureCredential() if not USE_MOCK else None
    query_result = await QueryAgent(credential).process(request["message"])
    route_result = await RouterAgent(credential).route(query_result)
    response = await ActionAgent(credential, mock=USE_MOCK).act(route_result)
    return {
        "response": response,
        "persona": query_result.persona,
        "board": route_result.specific_board,
        "breeze_portal": "https://breeze.ca.gov"
    }

@app.get("/api/verify-license/{license_number}")
async def verify_license(license_number: str, license_type: str = None):
    """Real-time BreEZe license verification."""
    if USE_MOCK:
        return {"status": "active", "board": "Medical Board of California", "mock": True}
    return await LicenseLookupTool().lookup(license_number, license_type)
```

## Step 4 — Azure Services to Provision

### Azure AI Foundry

```bash
az ml workspace create \
  --name dca-license-hub \
  --resource-group rg-dca-license \
  --kind hub

az ml workspace create \
  --name dca-license-project \
  --resource-group rg-dca-license \
  --kind project \
  --hub-name dca-license-hub
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name dca-openai \
  --resource-group rg-dca-license \
  --kind OpenAI \
  --sku S0 \
  --location westus

az cognitiveservices account deployment create \
  --name dca-openai \
  --resource-group rg-dca-license \
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
  --name dca-ai-search \
  --resource-group rg-dca-license \
  --sku Standard

# Index: dca-knowledge-base
# Source documents:
#   - Application checklists for all 40+ boards/bureaus
#   - CA Business & Professions Code (key licensing sections)
#   - CE requirements and approved provider lists by board
#   - DCA complaint process guides
#   - Exam information guides (USMLE, NCLEX, CBEST, etc. where applicable)
#   - BreEZe user guide
#   - Board of Barbering & Cosmetology guides
#   - CSLB contractor licensing requirements
#   - Real estate exam and CE requirements (DRE)
```

### Azure Container Apps

```bash
az containerapp create \
  --name dca-license-backend \
  --resource-group rg-dca-license \
  --environment dca-env \
  --image ghcr.io/jileary23/dca-license:latest \
  --target-port 8016 \
  --env-vars \
    USE_MOCK_SERVICES=false \
    AZURE_OPENAI_ENDPOINT=secretref:openai-endpoint \
    AZURE_SEARCH_ENDPOINT=secretref:search-endpoint \
    BREEZE_API_URL=https://breeze.ca.gov/api
```

## Step 5 — Bicep Infrastructure

Create `infra/main.bicep` defining:

- Azure AI Foundry Hub + Project (West US)
- Azure OpenAI (GPT-4o, 30K TPM GlobalStandard)
- Azure AI Search (Standard, `dca-knowledge-base`)
- Azure Container Apps (public ingress — consumer and applicant facing)
- Managed Identity with minimal role assignments
- Key Vault for secrets
- Azure Front Door + WAF for DDoS and rate limiting (BreEZe is a high-traffic system)
- Azure Monitor with 90-day retention

## Step 6 — Deploy

```bash
cd accelerators/016-dca-license-navigator
azd up --environment dca-dev

./scripts/azd-deploy.sh 016
```

## Compliance & Guardrails

- **CA BPC**: Responses cite specific BPC sections; licensing decisions made by boards, not AI
- **CCPA/CPRA**: PII filter on license number extraction; public license verification uses public data only
- **No disciplinary advice**: Enforcement/disciplinary queries serve document links and refer to attorney (CA BPC §315+)
- **Two-level routing**: Ensures correct board guidance — a medical RN question must not get Pharmacy Board guidance
- **EO N-12-23**: Source citations mandatory; AI used only for routing and RAG; final licensing decisions are human
- **BreEZe integration**: Only public-facing license status data; no confidential enforcement data

## Validation

```bash
USE_MOCK_SERVICES=true uvicorn backend.app.main:app --reload --port 8016 &
curl -X POST http://localhost:8016/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "I am a licensed LCSW in California. How many CE hours do I need for my upcoming renewal and are live-scan fingerprints required?"}'
```

Run smoke tests: `npm run smoke-test -- --accelerator 016`
