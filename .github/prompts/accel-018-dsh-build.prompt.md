---
agent: agent
description: Build and deploy the DSH Forensic Mental Health Placement Agent using Microsoft Agent Framework on Azure AI Foundry
tools:
  - AIAgentExpert
---

# 018 — DSH Forensic Mental Health Placement Agent

## Microsoft Agent Framework Build & Deploy

You are an expert Azure AI engineer. Build and deploy the **DSH Forensic Mental Health Placement Agent** for the California Department of State Hospitals using [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) on Azure AI Foundry.

## Accelerator Context

- **Agency:** California Department of State Hospitals (DSH)
- **Directory:** `accelerators/018-dsh-forensic-placement-agent/`
- **Backend Port:** 8018
- **Purpose:** Advisory AI assistant for navigating DSH forensic mental health placement pathways — IST restoration, NGI acquittee placement, LPS conservatorship, SVP commitment, and CONREP conditional release. Strictly advisory; no individual placement decisions are made by the AI.

> **CRITICAL SAFETY CONSTRAINT:** This system must never render individual placement recommendations or predict clinical outcomes. All outputs are procedural/educational guidance only. All placement and discharge decisions are exclusively made by DSH clinical staff and the courts.

## Step 1 — Scaffold the Project Structure

```
accelerators/018-dsh-forensic-placement-agent/
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
│   │       ├── program_directory_tool.py    # DSH facility/program lookup
│   │       ├── legal_timeline_tool.py       # Penal/W&I code deadline calculator
│   │       ├── conrep_lookup_tool.py        # CONREP county office directory
│   │       └── search_tool.py               # Azure AI Search RAG
│   ├── mock_data/dsh/
│   └── requirements.txt
├── frontend/src/
├── infra/
└── .env.example
```

## Step 2 — Microsoft Agent Framework Agent Definitions

Create `agent.yaml`:

```yaml
name: dsh-forensic-placement-advisor
description: DSH Forensic Mental Health Placement Agent
version: "1.0"
framework: microsoft-agent-framework
pipeline:
  - query_agent
  - router_agent
  - action_agent
constitution: ../../shared/constitution.md
compliance:
  - HIPAA
  - CCPA/CPRA
  - CA Penal Code §1370 et seq.
  - Welfare & Institutions Code §5000 et seq.
  - Coleman v. Brown stipulations
  - EO N-12-23
guardrails:
  no_individual_placement_decisions: true
  no_clinical_outcome_predictions: true
  phi_zero_tolerance: true
```

Create `agents/query_agent.yaml`:

```yaml
name: QueryAgent
model: gpt-4o
instructions: |
  You are the QueryAgent for the DSH Forensic Mental Health Placement Advisory system.
  1. Detect user role: COURT_REFERRAL (public defender, DA, court staff, judge's clerk), DSH_CLINICAL (DSH clinician, facility administrator), COMMUNITY_PARTNER (county mental health, CONREP provider, probation).
  2. Detect pathway: IST (incompetent to stand trial, PC §1370), NGI (not guilty by reason of insanity, PC §1026), LPS (Lanterman-Petris-Short conservatorship), SVP (sexually violent predator, WI §6600), CONREP (conditional release program), GENERAL_INFO.
  3. Extract procedural entities: charge type, court county, referral stage (pre-commitment, active commitment, restoration review), CONREP program region.
  4. STRICT PII FILTER: Strip all patient names, dates of birth, case numbers, and any identifying information. The system works with procedural questions only — never individual case information.
  5. If query contains apparent individual case details (name + diagnosis + court date), reject and redirect to secure DSH case management channels.
  6. Flag COURT_DEADLINE for queries involving PC §1370 90-day deadlines or commitment extensions.
  7. If the query is incomplete or ambiguous (and does not contain individual case information), request clarification before proceeding.
tools:
  - name: phi_filter
    type: builtin
    config:
      mode: strict
      reject_individual_case_queries: true
handoff: RouterAgent
```

Create `agents/router_agent.yaml`:

```yaml
name: RouterAgent
model: gpt-4o
instructions: |
  Route DSH forensic placement queries by commitment pathway:
  - IST_RESTORATION: PC §1370 commitment procedures, MDO evaluation timeline, restoration programs by DSH facility, 90-day review requirements, transport coordination, competency restoration curriculum
  - NGI_PLACEMENT: PC §1026 acquittee commitment, conditional release criteria, annual review process, placement levels at DSH facilities
  - LPS_PLACEMENT: WI §5000+ conservatorship, LPS referral to DSH, level of care determination framework, annual conservatorship review
  - SVP_COMMITMENT: WI §6600 Sexually Violent Predator commitment process, DSH SVP program information, annual SVPAP review, conditional release criteria
  - CONREP: Conditional release program overview, county CONREP office directory, revocation procedures, discharge criteria, CONREP referral process
  - DISCHARGE_PLANNING: community re-entry planning resources, county mental health linkage, CONREP transition
  - POLICY_LEGAL: Coleman stipulations compliance, PC/WI code section interpretation guidance, DSH policy documents
  Include the following disclaimer at the end of every response: 'Responses are procedural guidance only. Individual placement decisions are made by DSH clinicians and the courts.'
handoff: ActionAgent
```

Create `agents/action_agent.yaml`:

```yaml
name: ActionAgent
model: gpt-4o
instructions: |
  Deliver DSH forensic pathway guidance — procedural, educational, and regulatory only.
  Use Azure AI Search to query the DSH RAG index (DSH policy guides, PC §1370/1026/1026.5, WI §5000/6600, CONREP program guide, Coleman compliance reports, DSH facility program descriptions).
  Use the Program Directory tool for facility-specific program information (commitment type, program capacity, location).
  Use the Legal Timeline tool for procedure deadline calculations (PC §1370 90-day, commitment extension periods).
  Use the CONREP Lookup tool for county CONREP office contacts and referral procedures.
  Every response must include: "This is procedural guidance only. Clinical and legal placement decisions are made exclusively by DSH clinicians and the courts."
  For any query touching individual patient information: refuse and direct to DSH secure case management system.
tools:
  - name: azure_ai_search
    type: azure_search
    index: dsh-knowledge-base
  - name: program_directory
    type: function
    function: lookup_dsh_programs
  - name: legal_timeline
    type: function
    function: calculate_commitment_deadlines
  - name: conrep_directory
    type: function
    function: get_conrep_county_contacts
```

## Step 3 — Backend Implementation

```python
# backend/app/main.py
from fastapi import FastAPI, HTTPException
from azure.identity import DefaultAzureCredential
import os
import logging

app = FastAPI(title="DSH Forensic Mental Health Placement Agent")
# HIPAA: minimal access logging — no query content in logs
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
USE_MOCK = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

@app.post("/api/query")
async def query(request: dict):
    message = request.get("message", "")
    # Reject any query that appears to contain individual case details
    if await PHIDetector.contains_individual_case_data(message):
        raise HTTPException(
            status_code=422,
            detail="Individual case queries must use secure DSH case management channels."
        )
    credential = DefaultAzureCredential() if not USE_MOCK else None
    query_result = await QueryAgent(credential).process(message)
    route_result = await RouterAgent(credential).route(query_result)
    response = await ActionAgent(credential, mock=USE_MOCK).act(route_result)
    return {
        "response": response,
        "pathway": route_result.pathway,
        "disclaimer": "Procedural guidance only. Clinical and legal placement decisions are made exclusively by DSH clinicians and the courts.",
        "dsh_contact": "dsh.ca.gov | 916-654-2390"
    }
```

## Step 4 — Azure Services to Provision

### Azure AI Foundry

```bash
az ml workspace create \
  --name dsh-forensic-hub \
  --resource-group rg-dsh-forensic \
  --kind hub

az ml workspace create \
  --name dsh-forensic-project \
  --resource-group rg-dsh-forensic \
  --kind project \
  --hub-name dsh-forensic-hub
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name dsh-openai \
  --resource-group rg-dsh-forensic \
  --kind OpenAI \
  --sku S0 \
  --location eastus2

az cognitiveservices account deployment create \
  --name dsh-openai \
  --resource-group rg-dsh-forensic \
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
  --name dsh-ai-search \
  --resource-group rg-dsh-forensic \
  --sku Standard

# Index: dsh-knowledge-base
# Source documents:
#   - DSH Forensic Admissions policy guides
#   - CA Penal Code §1370, §1026, §1026.5 (competency/NGI)
#   - Welfare & Institutions Code §5000–5120 (LPS), §6600–6609.3 (SVP)
#   - CONREP program guide and county directory
#   - Coleman v. Brown compliance documents
#   - DSH facility program descriptions (Atascadero, Coalinga, Metropolitan, Napa, Patton, Vacaville)
#   - IST restoration program curricula overview
#   - Community re-entry and CONREP referral processes
```

### Azure Container Apps

```bash
az containerapp create \
  --name dsh-forensic-backend \
  --resource-group rg-dsh-forensic \
  --environment dsh-env \
  --image ghcr.io/jileary23/dsh-forensic:latest \
  --target-port 8018 \
  --ingress internal \
  --env-vars \
    USE_MOCK_SERVICES=false \
    AZURE_OPENAI_ENDPOINT=secretref:openai-endpoint \
    AZURE_SEARCH_ENDPOINT=secretref:search-endpoint
```

## Step 5 — Bicep Infrastructure

Create `infra/main.bicep` defining:

- Azure AI Foundry Hub + Project (East US 2 — HIPAA-aligned region)
- Azure OpenAI (GPT-4o, 30K TPM GlobalStandard)
- Azure AI Search (Standard, `dsh-knowledge-base`)
- Azure Container Apps with **internal ingress only** (DSH intranet/VPN access)
- Azure Virtual Network integration for Container Apps
- Managed Identity with minimal RBAC
- Key Vault for all secrets
- Azure Monitor with 180-day retention (HIPAA requirement)
- Azure Content Safety to block PHI re-generation in responses

## Step 6 — Deploy

```bash
cd accelerators/018-dsh-forensic-placement-agent
azd up --environment dsh-dev

./scripts/azd-deploy.sh 018
```

## Compliance & Guardrails

- **HIPAA PHI zero tolerance**: PHI filter rejects individual case data; PHI never logged; 180-day log retention
- **No individual decisions**: Hard-coded rejection of placement recommendations; every response includes mandatory procedural-only disclaimer
- **Penal Code / W&I Code**: All procedural guidance cites specific code section and subsection
- **Coleman compliance**: Coleman stipulation documents included in RAG index; routing aware of Coleman requirements
- **CCPA/CPRA**: No personal data stored; minimal logging (query content not logged)
- **EO N-12-23**: Citations mandatory; AI role is advisory support for procedural navigation only
- **Internal-only deployment**: Container Apps internal ingress; accessible only via DSH network/VPN

## Validation

```bash
USE_MOCK_SERVICES=true uvicorn backend.app.main:app --reload --port 8018 &
curl -X POST http://localhost:8018/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the process and timeline for IST restoration under PC 1370 for a misdemeanor charge? When must the court be notified of restoration?"}'
```

Run smoke tests: `npm run smoke-test -- --accelerator 018`
