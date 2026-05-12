---
agent: agent
description: Build and deploy the CDI Insurance Consumer Protection Agent using Microsoft Agent Framework on Azure AI Foundry
tools:
  - AIAgentExpert
---

# 013 — CDI Insurance Consumer Protection Agent

## Microsoft Agent Framework Build & Deploy

You are an expert Azure AI engineer. Build and deploy the **CDI Insurance Consumer Protection Agent** for the California Department of Insurance using [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) on Azure AI Foundry.

## Accelerator Context

- **Agency:** California Department of Insurance (CDI)
- **Directory:** `accelerators/013-cdi-insurance-consumer-agent/`
- **Backend Port:** 8013
- **Purpose:** Dual-persona AI assistant — helps California consumers understand insurance rights, navigate complaint processes, and verify licenses; helps licensed producers (agents/brokers) track CE requirements and regulatory updates

## Step 1 — Scaffold the Project Structure

```
accelerators/013-cdi-insurance-consumer-agent/
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
│   │       ├── license_lookup_tool.py     # CDI License Lookup API integration
│   │       ├── complaint_intake_tool.py   # Complaint process guidance
│   │       ├── bulletin_search_tool.py    # CDI regulatory bulletin search
│   │       └── search_tool.py             # Azure AI Search RAG
│   ├── mock_data/cdi/
│   └── requirements.txt
├── frontend/src/
├── infra/
└── .env.example
```

## Step 2 — Microsoft Agent Framework Agent Definitions

Create `agent.yaml`:

```yaml
name: cdi-insurance-consumer
description: CDI Insurance Consumer Protection Agent
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
  - California Insurance Code
  - Proposition 103
```

Create `agents/query_agent.yaml`:

```yaml
name: QueryAgent
model: gpt-4o
instructions: |
  You are the QueryAgent for the CDI Insurance Consumer Protection system.
  1. Detect user persona: CONSUMER (general public with insurance question) or PRODUCER (licensed insurance agent/broker).
  2. Detect intent:
     Consumer: claim_denial, rate_increase_challenge, fair_plan_guidance, complaint_filing, license_verification, coverage_question, fraud_reporting
     Producer: license_renewal, ce_requirements, regulatory_bulletin, disciplinary_action_inquiry, market_conduct
  3. Extract entities: insurance type (auto, home, health, life), insurer name, policy number (anonymize), CDI complaint number, license number (anonymize), county, coverage type.
  4. Apply PII filter — policy numbers and license numbers are extracted for routing but not stored.
  5. If the user's query is incomplete or ambiguous, request clarification before proceeding.
  6. Output: persona, intent, entities, urgency (HIGH for imminent deadlines or active disasters).
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
  Route CDI queries based on persona and intent:

  CONSUMER routes:
  - CLAIM_RIGHTS: claim denial appeals, bad faith handling, Unfair Claims Settlement Practices
  - RATE_REVIEW: Proposition 103 rate review process, requesting rate hearing, rate increase challenges
  - FAIR_PLAN: FAIR Plan eligibility, application process, coverage limits, wildfire non-renewal rights
  - COMPLAINT_PROCESS: how to file CDI complaint, CDI complaint portal, what CDI can/cannot do
  - LICENSE_VERIFICATION: license lookup, company authorization status, agent background
  - FRAUD_REPORTING: insurance fraud hotline, CDI Fraud Division, fraud form guidance
  - COVERAGE_EXPLANATION: plain-language policy explanation, exclusion interpretation

  PRODUCER routes:
  - CE_REQUIREMENTS: CE hours by license type, approved courses, renewal deadline calculation
  - LICENSE_RENEWAL: renewal process, lapsed license reinstatement, fingerprint re-requirements
  - REGULATORY_BULLETIN: CDI bulletin search, new compliance requirements, market conduct
  - MARKET_CONDUCT: examination preparation, record retention requirements

  Flag DISASTER_RELIEF when query involves wildfire/flood/earthquake claim handling (CDI emergency orders apply).
handoff: ActionAgent
```

Create `agents/action_agent.yaml`:

```yaml
name: ActionAgent
model: gpt-4o
instructions: |
  Deliver accurate, plain-language CDI guidance backed by the knowledge base.
  Use Azure AI Search to query the CDI RAG index (Consumer Guides, CA Insurance Code, CDI Bulletins, FAIR Plan docs, Producer licensing guides).
  Use the License Lookup tool for real-time license verification (GET https://interactive.web.insurance.ca.gov/api).
  For DISASTER_RELIEF queries: apply the most recent CDI emergency order provisions.
  Consumer responses: use plain language (8th grade reading level); include CDI contact info (800-927-4357) and complaint portal link (insurance.ca.gov/0100-consumers/0300-solving-problems/0200-filing-complaint/).
  Producer responses: include specific CE course categories, hours, and renewal timeline.
  Always note that specific policy interpretation requires review of the actual policy document.
tools:
  - name: azure_ai_search
    type: azure_search
    index: cdi-knowledge-base
  - name: license_lookup
    type: function
    function: lookup_insurance_license
  - name: bulletin_search
    type: function
    function: search_cdi_bulletins
```

## Step 3 — Backend Implementation

```python
# backend/app/main.py
from fastapi import FastAPI
from azure.identity import DefaultAzureCredential
import os

app = FastAPI(title="CDI Insurance Consumer Protection Agent")
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
        "cdi_contact": "800-927-4357 | insurance.ca.gov"
    }

@app.get("/api/verify-license/{license_number}")
async def verify_license(license_number: str):
    """Direct license verification endpoint."""
    if USE_MOCK:
        return {"status": "active", "name": "Mock Insurer Inc.", "mock": True}
    # Call CDI public License Lookup API
    return await LicenseLookupTool().lookup(license_number)
```

## Step 4 — Azure Services to Provision

### Azure AI Foundry

```bash
az ml workspace create \
  --name cdi-insurance-hub \
  --resource-group rg-cdi-insurance \
  --kind hub

az ml workspace create \
  --name cdi-insurance-project \
  --resource-group rg-cdi-insurance \
  --kind project \
  --hub-name cdi-insurance-hub
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name cdi-openai \
  --resource-group rg-cdi-insurance \
  --kind OpenAI \
  --sku S0 \
  --location westus

az cognitiveservices account deployment create \
  --name cdi-openai \
  --resource-group rg-cdi-insurance \
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
  --name cdi-ai-search \
  --resource-group rg-cdi-insurance \
  --sku Standard

# Index: cdi-knowledge-base
# Source documents:
#   - CDI Consumer Guides (auto, home, health, life)
#   - California Insurance Code (key consumer protection sections)
#   - CDI Bulletins (2020–present)
#   - FAIR Plan documentation
#   - Producer licensing guides (CE requirements by license type)
#   - Proposition 103 rate review procedures
#   - CDI Emergency Order library (disaster-related)
```

### Azure Container Apps

```bash
az containerapp create \
  --name cdi-insurance-backend \
  --resource-group rg-cdi-insurance \
  --environment cdi-env \
  --image ghcr.io/jileary23/cdi-insurance:latest \
  --target-port 8013 \
  --env-vars \
    USE_MOCK_SERVICES=false \
    AZURE_OPENAI_ENDPOINT=secretref:openai-endpoint \
    AZURE_SEARCH_ENDPOINT=secretref:search-endpoint \
    CDI_LICENSE_API_URL=https://interactive.web.insurance.ca.gov/api
```

## Step 5 — Bicep Infrastructure

Create `infra/main.bicep` defining:

- Azure AI Foundry Hub + Project (West US)
- Azure OpenAI (GPT-4o, 30K TPM GlobalStandard)
- Azure AI Search (Standard, `cdi-knowledge-base`)
- Azure Container Apps (public ingress — consumer-facing)
- Managed Identity with role assignments
- Key Vault for API secrets
- Azure Front Door + WAF policy (consumer-facing public endpoint protection)

## Step 6 — Deploy

```bash
cd accelerators/013-cdi-insurance-consumer-agent
azd up --environment cdi-dev

./scripts/azd-deploy.sh 013
```

## Compliance & Guardrails

- **CCPA/CPRA**: PII filter on all consumer inputs; no personal data stored; privacy policy linked in UI
- **CA Insurance Code**: Responses cite specific code sections; no legal advice disclaimer
- **Prop 103**: Rate review guidance aligned with CDI Prop 103 procedures
- **EO N-12-23**: Source citations mandatory; confidence indicator on regulatory guidance
- **FAIR Plan**: Wildfire non-renewal guidance follows AB 2756 and current CDI emergency orders
- **Disaster relief**: Dynamic routing to current emergency order provisions during declared disasters

## Validation

```bash
USE_MOCK_SERVICES=true uvicorn backend.app.main:app --reload --port 8013 &
curl -X POST http://localhost:8013/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "My homeowner insurance was cancelled due to wildfire risk. How do I get FAIR Plan coverage?"}'
```

Run smoke tests: `npm run smoke-test -- --accelerator 013`
