---
agent: agent
description: Build and deploy the OTSI HHS Integration Intelligence Agent using Microsoft Agent Framework on Azure AI Foundry
tools:
  - AIAgentExpert
---

# 019 — OTSI HHS Integration Intelligence Agent

## Microsoft Agent Framework Build & Deploy

You are an expert Azure AI engineer. Build and deploy the **OTSI HHS Integration Intelligence Agent** for the California Health and Human Services — Office of Technology and Solutions Integration using [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) on Azure AI Foundry.

## Accelerator Context

- **Agency:** California Health and Human Services (CHHS) — Office of Technology and Solutions Integration (OTSI)
- **Directory:** `accelerators/019-otsi-hhs-integration-agent/`
- **Backend Port:** 8019
- **Purpose:** Internal AI assistant for CHHS/OTSI technical staff — navigates the HHS integration platform (CalSAWS, MEDS, CalHEERS, CDW), API catalog, data sharing protocols, and system onboarding procedures. Authenticated access only (Azure Entra ID / internal staff).

## Step 1 — Scaffold the Project Structure

```
accelerators/019-otsi-hhs-integration-agent/
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
│   │       ├── api_catalog_tool.py         # OTSI API catalog search
│   │       ├── system_status_tool.py       # HHS system health/status
│   │       ├── onboarding_checklist_tool.py # Integration onboarding steps
│   │       ├── data_governance_tool.py     # Data sharing agreement lookup
│   │       └── search_tool.py              # Azure AI Search RAG
│   ├── mock_data/otsi/
│   └── requirements.txt
├── frontend/src/
├── infra/
└── .env.example
```

## Step 2 — Microsoft Agent Framework Agent Definitions

Create `agent.yaml`:

```yaml
name: otsi-hhs-integration-intelligence
description: OTSI HHS Integration Intelligence Agent
version: "1.0"
framework: microsoft-agent-framework
pipeline:
  - query_agent
  - router_agent
  - action_agent
constitution: ../../shared/constitution.md
authentication:
  provider: azure_entra_id
  mode: required
  audience: internal_staff_only
compliance:
  - EO N-12-23
  - EO N-5-26
  - HIPAA
  - IRS Pub 1075 (FTI)
  - NIST SP 800-53
  - CCPA/CPRA
```

Create `agents/query_agent.yaml`:

```yaml
name: QueryAgent
model: gpt-4o
instructions: |
  You are the QueryAgent for the OTSI HHS Integration Intelligence system (internal authenticated users only).
  1. Detect user role: DEVELOPER (integration developer, API consumer), BUSINESS_ANALYST (data architect, program analyst), PROJECT_MANAGER (project/program manager, vendor coordinator).
  2. Detect integration intent: api_integration, calsaws_onboarding, meds_query, calhEERS_enrollment, cdw_data_access, data_sharing_agreement, fti_handling, ita_documentation, system_status.
  3. Extract entities: system name (CalSAWS, MEDS, CalHEERS, CDW, Medi-Cal, SAWS), data element requested, county/agency name, project name, API endpoint pattern.
  4. Classify data sensitivity: FTI (Federal Tax Information — IRS Pub 1075 controls apply), PHI (HIPAA), PII (CCPA), or non-sensitive.
  5. For FTI queries: apply IRS Pub 1075 disclosure controls — restrict to authorized use cases and enforce need-to-know.
  6. If the query is incomplete or ambiguous, request clarification before proceeding.
tools:
  - name: phi_fti_filter
    type: builtin
    config:
      detect_fti: true
      detect_phi: true
handoff: RouterAgent
```

Create `agents/router_agent.yaml`:

```yaml
name: RouterAgent
model: gpt-4o
instructions: |
  Route OTSI integration queries to the appropriate HHS system domain:
  - CALSAWS: California Statewide Automated Welfare System — county integration, MCI (master client index), eligibility data exchange, SAWS technical specs
  - MEDS: Medi-Cal Eligibility Data System — enrollment feeds, 834 transactions, eligibility verification, CIN lookup integration
  - CALHERS: California Healthcare Eligibility, Enrollment, and Retention System — Covered California integration, APTC reconciliation, QHP enrollment
  - CDW: CHHS Data Warehouse — data request process, data governance, CDW data dictionary, analytic use cases
  - API_CATALOG: OTSI API catalog — available APIs, API key management via Azure API Management, rate limits, authentication
  - DATA_SHARING: ISA (Interagency Service Agreement), MOU, NACI for new data feeds, PIAs (Privacy Impact Assessments)
  - FTI_CONTROLS: IRS Pub 1075 FTI safeguards, safeguard activity report, allowed access patterns, prohibition on AI model training with FTI
  - SYSTEM_ONBOARDING: new integration checklist, sandbox/test environment access, ITSO intake form, security review process
  - AZURE_APIM: Azure API Management configuration, subscription keys, policy configuration, throttling, OAuth 2.0 flows for HHS APIs
  Note: FTI route applies additional access controls — log all FTI-related queries per IRS Pub 1075 §2.1.
handoff: ActionAgent
```

Create `agents/action_agent.yaml`:

```yaml
name: ActionAgent
model: gpt-4o
instructions: |
  Deliver OTSI integration technical guidance for authenticated CHHS/OTSI staff.
  Use Azure AI Search to query the OTSI RAG index (system technical specs, API catalog, data dictionaries, IRS Pub 1075 safeguard guide, NIST SP 800-53 control references, OTSI onboarding guides, ISA/MOU templates).
  Use the API Catalog tool to retrieve available integration APIs and authentication patterns.
  Use the Onboarding Checklist tool for step-by-step system integration onboarding.
  Use the Data Governance tool for data sharing agreement requirements.
  For FTI-tagged queries: include mandatory IRS Pub 1075 citation, note prohibition on using FTI in AI model training, and confirm need-to-know requirement.
  Always include Azure API Management integration notes for technical API queries.
  Note: Responses are guidance for authorized CHHS/OTSI staff only. Not for external disclosure.
tools:
  - name: azure_ai_search
    type: azure_search
    index: otsi-knowledge-base
  - name: api_catalog
    type: function
    function: search_otsi_api_catalog
  - name: onboarding_checklist
    type: function
    function: get_system_onboarding_steps
  - name: data_governance
    type: function
    function: get_data_sharing_requirements
```

## Step 3 — Backend Implementation

```python
# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from azure.identity import DefaultAzureCredential
import os

app = FastAPI(title="OTSI HHS Integration Intelligence Agent")
USE_MOCK = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "true").lower() == "true"

async def verify_entra_token(authorization: str = None):
    """Validate Azure Entra ID (AAD) token — internal staff only."""
    if USE_MOCK or not REQUIRE_AUTH:
        return {"oid": "mock-user", "roles": ["HHS.Staff"]}
    # Validate bearer token against CHHS Entra tenant
    return await EntraTokenValidator(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        audience=os.getenv("AZURE_APP_CLIENT_ID")
    ).validate(authorization)

@app.post("/api/query")
async def query(request: dict, user: dict = Depends(verify_entra_token)):
    credential = DefaultAzureCredential() if not USE_MOCK else None
    query_result = await QueryAgent(credential).process(request["message"])
    route_result = await RouterAgent(credential).route(query_result)
    response = await ActionAgent(credential, mock=USE_MOCK).act(route_result)
    return {
        "response": response,
        "user_role": query_result.user_role,
        "system": route_result.route,
        "internal_only": True
    }
```

## Step 4 — Azure Services to Provision

### Azure AI Foundry

```bash
az ml workspace create \
  --name otsi-integration-hub \
  --resource-group rg-otsi-integration \
  --kind hub

az ml workspace create \
  --name otsi-integration-project \
  --resource-group rg-otsi-integration \
  --kind project \
  --hub-name otsi-integration-hub
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name otsi-openai \
  --resource-group rg-otsi-integration \
  --kind OpenAI \
  --sku S0 \
  --location eastus2

az cognitiveservices account deployment create \
  --name otsi-openai \
  --resource-group rg-otsi-integration \
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
  --name otsi-ai-search \
  --resource-group rg-otsi-integration \
  --sku Standard

# Index: otsi-knowledge-base
# Source documents (internal):
#   - OTSI API catalog documentation
#   - CalSAWS technical integration guide
#   - MEDS interface specifications
#   - CalHEERS enrollment data exchange guide
#   - CDW data dictionary and request process
#   - IRS Publication 1075 (FTI safeguards)
#   - NIST SP 800-53 control references (CHHS applicability)
#   - Azure API Management configuration guide for HHS
#   - ISA/MOU templates and data sharing checklist
```

### Azure API Management

```bash
# Configure Azure APIM as the gateway for HHS integration APIs
az apim create \
  --name otsi-apim \
  --resource-group rg-otsi-integration \
  --location eastus2 \
  --sku-name Developer \
  --publisher-name "CHHS OTSI" \
  --publisher-email otsi@chhs.ca.gov
```

### Azure Container Apps

```bash
az containerapp create \
  --name otsi-integration-backend \
  --resource-group rg-otsi-integration \
  --environment otsi-env \
  --image ghcr.io/jileary23/otsi-integration:latest \
  --target-port 8019 \
  --ingress internal \
  --env-vars \
    USE_MOCK_SERVICES=false \
    REQUIRE_AUTH=true \
    AZURE_TENANT_ID=secretref:tenant-id \
    AZURE_APP_CLIENT_ID=secretref:client-id \
    AZURE_OPENAI_ENDPOINT=secretref:openai-endpoint \
    AZURE_SEARCH_ENDPOINT=secretref:search-endpoint
```

## Step 5 — Bicep Infrastructure

Create `infra/main.bicep` defining:

- Azure AI Foundry Hub + Project (East US 2)
- Azure OpenAI (GPT-4o, 30K TPM GlobalStandard)
- Azure AI Search (Standard, `otsi-knowledge-base`, restricted access)
- Azure Container Apps with **internal ingress only** + Azure Entra ID authentication
- Azure API Management (Developer tier — internal HHS APIs)
- Azure Virtual Network integration
- Managed Identity with minimal RBAC
- Key Vault for all secrets (Entra credentials, API keys)
- Azure Monitor with 1-year retention (NIST SP 800-53 AU controls)

## Step 6 — Deploy

```bash
cd accelerators/019-otsi-hhs-integration-agent
azd up --environment otsi-dev

./scripts/azd-deploy.sh 019
```

## Compliance & Guardrails

- **IRS Pub 1075 (FTI)**: FTI queries logged per §2.1; prohibition on AI model training with FTI enforced at tool level; need-to-know enforced via Entra role claims
- **HIPAA**: PHI filter active; no beneficiary data in query logs; 180-day health data retention
- **NIST SP 800-53**: System follows MODERATE impact controls; Azure Monitor audit logging fulfills AU family
- **EO N-5-26**: This system is itself an AI tool in state service — EO N-5-26 compliance documented in procurement
- **Azure Entra ID**: All access requires authenticated CHHS staff token; no anonymous queries
- **EO N-12-23**: Source citations mandatory in all technical guidance

## Validation

```bash
USE_MOCK_SERVICES=true REQUIRE_AUTH=false uvicorn backend.app.main:app --reload --port 8019 &
curl -X POST http://localhost:8019/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I set up a new county integration with CalSAWS to receive eligibility determination updates via API?"}'
```

Run smoke tests: `npm run smoke-test -- --accelerator 019`
