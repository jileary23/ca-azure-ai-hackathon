---
agent: agent
description: Build and deploy the CDPH Public Health Surveillance Intelligence Agent using Microsoft Agent Framework on Azure AI Foundry
tools:
  - AIAgentExpert
---

# 014 — CDPH Public Health Surveillance Intelligence Agent

## Microsoft Agent Framework Build & Deploy

You are an expert Azure AI engineer. Build and deploy the **CDPH Public Health Surveillance Intelligence Agent** for the California Department of Public Health using [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) on Azure AI Foundry.

## Accelerator Context

- **Agency:** California Department of Public Health (CDPH)
- **Directory:** `accelerators/014-cdph-public-health-agent/`
- **Backend Port:** 8014
- **Purpose:** Role-aware public health intelligence — helps epidemiologists, local health officers, healthcare providers, and community advocates synthesize surveillance data, understand reportable disease regulations, and navigate immunization requirements

## Step 1 — Scaffold the Project Structure

```
accelerators/014-cdph-public-health-agent/
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
│   │       ├── surveillance_tool.py      # Synthetic surveillance data (mock CalREDIE)
│   │       ├── immunization_tool.py      # CAIR2 immunization schedule lookups
│   │       ├── reportable_disease_tool.py
│   │       └── search_tool.py            # Azure AI Search RAG
│   ├── mock_data/cdph/
│   └── requirements.txt
├── frontend/src/
├── infra/
└── .env.example
```

## Step 2 — Microsoft Agent Framework Agent Definitions

Create `agent.yaml`:

```yaml
name: cdph-public-health-intelligence
description: CDPH Public Health Surveillance Intelligence Agent
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
  - Title 17 CCR
  - 42 CFR Part 2
```

Create `agents/query_agent.yaml`:

```yaml
name: QueryAgent
model: gpt-4o
instructions: |
  You are the QueryAgent for the CDPH Public Health Intelligence system.
  1. Detect user role: INVESTIGATOR (epidemiologist, LHO, public health investigator), PROVIDER (physician, clinic, lab), or PUBLIC (community member, advocate).
  2. Detect intent: outbreak_intelligence, reportable_disease_guidance, immunization_requirements, contact_tracing, syndromic_surveillance, lab_reporting, disease_prevention.
  3. Extract entities: disease/condition name, county/jurisdiction, time period, age group (for immunization), school year.
  4. CRITICAL: Strip any patient/case identifiers before processing. Case counts are aggregated only; no individual case data flows through this pipeline.
  5. Apply 42 CFR Part 2 filter for substance use disorder queries — these have additional disclosure restrictions.
  6. Set reading level output: INVESTIGATOR=technical, PROVIDER=clinical, PUBLIC=8th grade plain language (CDPH health equity standard).
  7. If the query is incomplete or ambiguous, request clarification before proceeding.
tools:
  - name: phi_filter
    type: builtin
    config:
      mode: strict
handoff: RouterAgent
```

Create `agents/router_agent.yaml`:

```yaml
name: RouterAgent
model: gpt-4o
instructions: |
  Route CDPH public health queries by domain:
  - COMMUNICABLE_DISEASE: outbreak investigation guidance, case definitions, contact tracing protocols, isolation/quarantine timelines
  - REPORTABLE_DISEASE: Title 17 CCR mandatory reporting timelines, reporting methods, lab vs. physician obligations
  - IMMUNIZATION: school-entry requirements, catch-up schedules, exemptions, CAIR2 guidance
  - SYNDROMIC_SURVEILLANCE: ED visit pattern analysis, unusual cluster identification (serves synthetic mock data in local dev)
  - LAB_REPORTING: specific pathogen reporting requirements, specimen submission, DCLS contacts
  - ENVIRONMENTAL_HEALTH: vector-borne disease prevention (West Nile, plague), environmental hazard advisories
  - SUBSTANCE_USE: apply 42 CFR Part 2 restrictions — route only to approved guidance, no case data
  Apply role-specific response formatting: INVESTIGATOR gets full epidemiologic detail; PUBLIC gets plain-language prevention tips.
handoff: ActionAgent
```

Create `agents/action_agent.yaml`:

```yaml
name: ActionAgent
model: gpt-4o
instructions: |
  Retrieve and synthesize public health guidance from the CDPH knowledge base.
  Use Azure AI Search to query the CDPH RAG index (Disease Investigation Guides, Title 17 CCR, CAIR immunization registry guides, CDPH MMWR-style reports, CalREDIE references).
  Use the Surveillance tool for aggregated case counts and cluster summaries (mock CalREDIE data in local dev — never real patient data).
  Use the Immunization tool for school-entry and catch-up schedule lookups (CAIR2 schedule data).
  For INVESTIGATOR queries: include case definition, investigation timeline, regulatory citation.
  For PUBLIC queries: plain language, prevention-focused, include CDPH hotline (916-558-1784) and local LHO referral.
  Always note that public health orders and individual case management are handled by local health departments.
tools:
  - name: azure_ai_search
    type: azure_search
    index: cdph-public-health-knowledge-base
  - name: surveillance_data
    type: function
    function: get_surveillance_summary
  - name: immunization_schedule
    type: function
    function: get_immunization_requirements
  - name: reportable_disease_lookup
    type: function
    function: get_reporting_requirements
```

## Step 3 — Backend Implementation

```python
# backend/app/main.py
from fastapi import FastAPI
from azure.identity import DefaultAzureCredential
import os
import logging

app = FastAPI(title="CDPH Public Health Intelligence Agent")
# HIPAA: suppress detailed access logs
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
USE_MOCK = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

@app.post("/api/query")
async def query(request: dict):
    credential = DefaultAzureCredential() if not USE_MOCK else None
    query_result = await QueryAgent(credential).process(request["message"])
    route_result = await RouterAgent(credential).route(query_result)
    response = await ActionAgent(credential, mock=USE_MOCK).act(route_result)
    return {
        "response": response,
        "role": query_result.user_role,
        "reading_level": query_result.reading_level,
        "disclaimer": "Public health guidance only. Contact your local health department for case management."
    }
```

## Step 4 — Azure Services to Provision

### Azure AI Foundry

```bash
az ml workspace create \
  --name cdph-public-health-hub \
  --resource-group rg-cdph-public-health \
  --kind hub

az ml workspace create \
  --name cdph-public-health-project \
  --resource-group rg-cdph-public-health \
  --kind project \
  --hub-name cdph-public-health-hub
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name cdph-openai \
  --resource-group rg-cdph-public-health \
  --kind OpenAI \
  --sku S0 \
  --location westus

az cognitiveservices account deployment create \
  --name cdph-openai \
  --resource-group rg-cdph-public-health \
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
  --name cdph-ai-search \
  --resource-group rg-cdph-public-health \
  --sku Standard

# Index: cdph-public-health-knowledge-base
# Source documents:
#   - CDPH Disease Investigation Guides (all reportable conditions)
#   - Title 17 CCR (communicable disease reporting regulations)
#   - CDPH CAIR2 immunization registry user guides
#   - School immunization requirements by school year
#   - CalREDIE field investigator guides
#   - Vector-borne disease seasonal advisories
#   - CDPH Health Equity Framework documents
```

### Azure Container Apps

```bash
az containerapp create \
  --name cdph-public-health-backend \
  --resource-group rg-cdph-public-health \
  --environment cdph-env \
  --image ghcr.io/jileary23/cdph-public-health:latest \
  --target-port 8014 \
  --env-vars \
    USE_MOCK_SERVICES=false \
    AZURE_OPENAI_ENDPOINT=secretref:openai-endpoint \
    AZURE_SEARCH_ENDPOINT=secretref:search-endpoint
```

## Step 5 — Bicep Infrastructure

Create `infra/main.bicep` defining:

- Azure AI Foundry Hub + Project (West US)
- Azure OpenAI (GPT-4o, 30K TPM)
- Azure AI Search (Standard, `cdph-public-health-knowledge-base`)
- Azure Container Apps with split ingress: internal for investigator endpoints, public for community portal
- Managed Identity with role assignments
- Key Vault for all secrets
- Azure Monitor with 180-day retention (HIPAA)
- Content Safety filter configured to block health misinformation

## Step 6 — Deploy

```bash
cd accelerators/014-cdph-public-health-agent
azd up --environment cdph-dev

./scripts/azd-deploy.sh 014
```

## Compliance & Guardrails

- **HIPAA**: PHI filter (zero tolerance); aggregated surveillance data only; no individual case data
- **Title 17 CCR**: Reporting timelines and methods sourced directly from current regulations
- **42 CFR Part 2**: Substance use disorder queries routed only to approved guidance, additional disclosure restrictions enforced
- **CCPA/CPRA**: No PII collection; community queries are anonymous
- **Health equity**: PUBLIC role responses at 8th grade reading level; multilingual support via Azure Cognitive Services (Spanish, Hmong, Tagalog, Chinese)
- **EO N-12-23**: Citations mandatory; confidence indicators on surveillance data summaries

## Validation

```bash
USE_MOCK_SERVICES=true uvicorn backend.app.main:app --reload --port 8014 &
curl -X POST http://localhost:8014/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the mandatory reporting timelines for a confirmed measles case in a Los Angeles County clinic?"}'
```

Run smoke tests: `npm run smoke-test -- --accelerator 014`
