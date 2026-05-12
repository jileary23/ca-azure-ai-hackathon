---
agent: agent
description: Build and deploy the CCHCS Correctional Health Clinical Support Agent using Microsoft Agent Framework on Azure AI Foundry
tools:
  - AIAgentExpert
---

# 012 — CCHCS Correctional Health Clinical Support Agent

## Microsoft Agent Framework Build & Deploy

You are an expert Azure AI engineer. Build and deploy the **CCHCS Correctional Health Clinical Support Agent** for California Correctional Health Care Services using [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) on Azure AI Foundry.

## Accelerator Context

- **Agency:** California Correctional Health Care Services (CCHCS)
- **Directory:** `accelerators/012-cchcs-clinical-support-agent/`
- **Backend Port:** 8012
- **Purpose:** AI clinical decision support for CCHCS staff — formulary lookups, clinical protocols, CalAIM reentry planning, mental health policy, dental triage. Strictly advisory; no EHR access. HIPAA and CCPA compliant.

## Step 1 — Scaffold the Project Structure

```
accelerators/012-cchcs-clinical-support-agent/
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
│   │       ├── formulary_tool.py        # CCHCS formulary lookup
│   │       ├── clinical_protocol_tool.py
│   │       ├── calaim_resource_tool.py  # Community reentry resources
│   │       └── search_tool.py           # Azure AI Search RAG
│   ├── mock_data/cchcs/
│   └── requirements.txt
├── frontend/src/
├── infra/
└── .env.example
```

## Step 2 — Microsoft Agent Framework Agent Definitions

Create `agent.yaml`:

```yaml
name: cchcs-clinical-support
description: CCHCS Correctional Health Clinical Support Agent
version: "1.0"
framework: microsoft-agent-framework
pipeline:
  - query_agent
  - router_agent
  - action_agent
constitution: ../../shared/constitution.md
compliance:
  - EO N-12-23
  - HIPAA
  - CCPA/CPRA
  - Plata v. Newsom
  - Coleman v. Newsom
```

Create `agents/query_agent.yaml`:

```yaml
name: QueryAgent
model: gpt-4o
instructions: |
  You are the QueryAgent for the CCHCS Clinical Support system serving correctional health clinicians.
  1. Detect clinical intent: formulary_lookup, clinical_protocol, mental_health_policy, dental_triage, calaim_reentry, medication_reconciliation.
  2. Extract clinical entities: medication name, diagnosis code, clinical condition, care setting (reception, general population, MHSDS level), county (for CalAIM ECM resources).
  3. CRITICAL: Strip any patient identifiers (name, CDCR number, DOB, housing location) before processing. These must never be included in queries.
  4. Detect clinician role: physician, RN, mental_health_clinician, dentist, pharmacist.
  5. Flag urgent clinical questions (acute conditions) for priority routing.
  6. If the clinician's query is incomplete or ambiguous, request clarification before proceeding.
  HIPAA/CCPA: Zero tolerance for PHI in the pipeline. Redirect any EHR/EHRS access requests.
tools:
  - name: phi_filter
    type: builtin
    config:
      mode: strict
      zero_tolerance: true
handoff: RouterAgent
```

Create `agents/router_agent.yaml`:

```yaml
name: RouterAgent
model: gpt-4o
instructions: |
  Route CCHCS clinical queries to the correct knowledge domain:
  - FORMULARY: drug tier criteria, prescribing restrictions, non-formulary exception process, drug interactions (general)
  - CLINICAL_PROTOCOL: CCHCS chronic care guidelines, acute care pathways (diabetes, hypertension, asthma, HIV, HCV), STI protocols
  - MENTAL_HEALTH: MHSDS Program Guide, Level of Care placement reviews (CCCMS, EOP, MHCB, PSU), QMH timelines
  - DENTAL: CCHCS dental priority classification, emergent/urgent/routine triage, treatment timelines
  - CALAIM_REENTRY: ECM (Enhanced Care Management) providers by county, Community Supports, post-release Medi-Cal enrollment
  - MEDICATION_RECONCILIATION: non-formulary bridge protocols, inter-facility transfer procedures
  Set URGENT flag for acute conditions requiring immediate clinical attention (these require supervisor consultation warning).
handoff: ActionAgent
```

Create `agents/action_agent.yaml`:

```yaml
name: ActionAgent
model: gpt-4o
instructions: |
  Retrieve and synthesize clinical guidance from the CCHCS knowledge base.
  Use Azure AI Search to query the CCHCS RAG index (Formulary, Policies & Procedures, MHSDS Program Guide, CalAIM ECM/CS guides, Dental Manual).
  Always cite the specific CCHCS policy number, formulary edition date, or Program Guide chapter.
  Include the standard disclaimer: "This is clinical decision support. Individual patient care decisions require clinician judgment and, where appropriate, consultation with a supervising provider."
  For CalAIM ECM resources: filter by county and SMI/SUD/complex need status.
  NEVER suggest treatments for specific patients — responses are general clinical guidance only.
tools:
  - name: azure_ai_search
    type: azure_search
    index: cchcs-clinical-knowledge-base
  - name: formulary_lookup
    type: function
    function: search_formulary
  - name: calaim_resources
    type: function
    function: get_ecm_providers_by_county
```

## Step 3 — Backend Implementation

```python
# backend/app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from azure.identity import DefaultAzureCredential
import os
import logging

app = FastAPI(title="CCHCS Clinical Support Agent")
# Disable request body logging — HIPAA compliance
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
USE_MOCK = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

@app.post("/api/query")
async def query(request: dict):
    """Clinical query endpoint — PHI-safe pipeline."""
    credential = DefaultAzureCredential() if not USE_MOCK else None
    # PHI filter is the first gate — throws 400 if PHI detected
    query_result = await QueryAgent(credential).process(request["message"])
    route_result = await RouterAgent(credential).route(query_result)
    response = await ActionAgent(credential, mock=USE_MOCK).act(route_result)
    return {
        "response": response,
        "disclaimer": "Clinical decision support only. Individual patient care requires clinician judgment."
    }
```

## Step 4 — Azure Services to Provision

### Azure AI Foundry

```bash
az ml workspace create \
  --name cchcs-clinical-hub \
  --resource-group rg-cchcs-clinical \
  --kind hub

az ml workspace create \
  --name cchcs-clinical-project \
  --resource-group rg-cchcs-clinical \
  --kind project \
  --hub-name cchcs-clinical-hub
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name cchcs-openai \
  --resource-group rg-cchcs-clinical \
  --kind OpenAI \
  --sku S0 \
  --location usgovvirginia  # Prefer sovereign cloud for HIPAA
  # Alt: use standard region with HIPAA BAA in place: eastus

az cognitiveservices account deployment create \
  --name cchcs-openai \
  --resource-group rg-cchcs-clinical \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-11-20" \
  --model-format OpenAI \
  --sku-capacity 30 \
  --sku-name GlobalStandard
```

### Azure AI Search (RAG — CCHCS Clinical Knowledge)

```bash
az search service create \
  --name cchcs-ai-search \
  --resource-group rg-cchcs-clinical \
  --sku Standard

# Index: cchcs-clinical-knowledge-base
# Source documents:
#   - CCHCS Formulary (current edition, ~650 medications)
#   - CCHCS Policies & Procedures (medical, dental, mental health)
#   - MHSDS Program Guide (Coleman stipulations)
#   - CalAIM ECM/Community Supports guides by county
#   - Dental Priority Classification Manual
#   - Plata Remedial Plan clinical guidelines
```

### Azure Container Apps (with HIPAA controls)

```bash
az containerapp create \
  --name cchcs-clinical-backend \
  --resource-group rg-cchcs-clinical \
  --environment cchcs-env \
  --image ghcr.io/jileary23/cchcs-clinical:latest \
  --target-port 8012 \
  --ingress internal \  # Internal only — Caltrans VPN or CDCR network access
  --env-vars \
    USE_MOCK_SERVICES=false \
    AZURE_OPENAI_ENDPOINT=secretref:openai-endpoint \
    AZURE_SEARCH_ENDPOINT=secretref:search-endpoint \
    HIPAA_MODE=true
```

## Step 5 — Bicep Infrastructure

Create `infra/main.bicep` defining:

- Azure AI Foundry Hub + Project
- Azure OpenAI (GPT-4o, 30K TPM — consider US Government region for HIPAA BAA)
- Azure AI Search (Standard, `cchcs-clinical-knowledge-base`)
- Azure Container Apps with internal ingress (VPN/CDCR network only)
- Managed Identity with minimal role assignments
- Key Vault (RBAC, not access policies) for all secrets
- Azure Monitor with 180-day retention (HIPAA minimum) and diagnostic settings
- Azure Policy assignment: deny public network access to all services
- Private endpoints for all PaaS services

## Step 6 — Deploy

```bash
cd accelerators/012-cchcs-clinical-support-agent
azd up --environment cchcs-dev

./scripts/azd-deploy.sh 012
```

## Compliance & Guardrails

- **HIPAA**: PHI filter in QueryAgent (zero tolerance); no patient data in request/response logs; HIPAA BAA required for Azure services; internal ingress only
- **EO N-12-23**: Confidence indicators on clinical guidance; citations mandatory
- **Plata/Coleman**: Responses aligned with court-ordered remedial plans; MHSDS Program Guide authoritative
- **CCPA/CPRA**: No personal information collected or stored
- **Advisory only**: Always includes clinician consultation disclaimer
- **Audit logging**: Query intent category and timestamp only (no content); 180-day retention

## Validation

```bash
USE_MOCK_SERVICES=true uvicorn backend.app.main:app --reload --port 8012 &
curl -X POST http://localhost:8012/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the prescribing restrictions for gabapentin in the CCHCS formulary?"}'
```

Run smoke tests: `npm run smoke-test -- --accelerator 012`
