---
agent: agent
description: Build and deploy the DGS Procurement Intelligence Agent using Microsoft Agent Framework on Azure AI Foundry
tools:
  - AIAgentExpert
---

# 017 — DGS Procurement Intelligence Agent

## Microsoft Agent Framework Build & Deploy

You are an expert Azure AI engineer. Build and deploy the **DGS Procurement Intelligence Agent** for the California Department of General Services using [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) on Azure AI Foundry.

## Accelerator Context

- **Agency:** California Department of General Services (DGS)
- **Directory:** `accelerators/017-dgs-procurement-agent/`
- **Backend Port:** 8017
- **Purpose:** AI procurement compliance assistant for California state agencies and vendors — CMAS, SLP, master agreements, SB/DVBE requirements, IT procurement, and non-competitive justification guidance. Also implements EO N-5-26 AI procurement compliance checks (meta-applicable: AI purchasing must comply with EO N-5-26).

## Step 1 — Scaffold the Project Structure

```
accelerators/017-dgs-procurement-agent/
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
│   │       ├── cmas_lookup_tool.py         # CMAS contract availability
│   │       ├── dvbe_requirement_tool.py    # SB/DVBE threshold calculator
│   │       ├── ncb_guidance_tool.py        # Non-competitive bid guidance
│   │       ├── ai_procurement_tool.py      # EO N-5-26 compliance checker
│   │       └── search_tool.py              # Azure AI Search RAG
│   ├── mock_data/dgs/
│   └── requirements.txt
├── frontend/src/
├── infra/
└── .env.example
```

## Step 2 — Microsoft Agent Framework Agent Definitions

Create `agent.yaml`:

```yaml
name: dgs-procurement-intelligence
description: DGS Procurement Intelligence Agent
version: "1.0"
framework: microsoft-agent-framework
pipeline:
  - query_agent
  - router_agent
  - action_agent
constitution: ../../shared/constitution.md
compliance:
  - EO N-12-23
  - EO N-5-26
  - CA Public Contract Code
  - SB 53
  - CCPA/CPRA
```

Create `agents/query_agent.yaml`:

```yaml
name: QueryAgent
model: gpt-4o
instructions: |
  You are the QueryAgent for the DGS Procurement Intelligence system.
  1. Detect user persona: AGENCY_BUYER (state agency purchasing staff), VENDOR (business seeking state contracts), AUDITOR (CalSAWS, SCO, DGS auditor reviewing procurement).
  2. Detect procurement intent: find_contract_vehicle, bid_threshold_rules, dvbe_requirement, non_competitive_justification, it_procurement_stoa, ai_procurement_compliance, protest_process, small_business_certification.
  3. Extract entities: commodity/service type, estimated contract value, IT vs. non-IT, ITHC sensitivity (for IT procurements), prior contract number.
  4. Classify purchase amount relative to thresholds: <$10K (informal), <$249,999 (informal competitive), >$249,999 (formal competitive, SCPRS required).
  5. Flag AI_PROCUREMENT if procurement involves AI/GenAI tools, models, or services — triggers EO N-5-26 compliance branch.
  6. If the query is incomplete or ambiguous, request clarification before proceeding.
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
  Route DGS procurement queries by method and program:
  - CMAS: California Multiple Award Schedules — who can use, category search, ordering procedures, SB certification on CMAS
  - SLP: Statewide Leveraged Procurement Agreements — WSCA, CALNET 3, Dept. of Tech agreements
  - MASTER_AGREEMENTS: MA creation, piggybacking rules, inter-agency use, IT Master Contracts
  - SB_DVBE: Small Business certification, DVBE 3% requirement, Incentive Award, SB preference (5%), calculating thresholds
  - IT_PROCUREMENT: STOA, IPPP, Innovative Projects Program, GIS/data standards, DGS/CDT dual-approval path
  - NON_COMPETITIVE: NCB justification thresholds, sole-source documentation requirements, approval levels, STD 66 form
  - AI_PROCUREMENT: EO N-5-26 requirements — vendor AI attestation, risk tier classification, bias testing documentation, ongoing monitoring plan, DGS AI Procurement Checklist
  - SURPLUS_PROPERTY: DGS surplus disposal, state agency donations program
  - PROTEST_PROCESS: protest grounds, timelines, informal vs. formal process, BIDS public portal
  Always distinguish between IT (CDT oversight) and non-IT (DGS oversight) procurement paths.
handoff: ActionAgent
```

Create `agents/action_agent.yaml`:

```yaml
name: ActionAgent
model: gpt-4o
instructions: |
  Deliver procurement guidance backed by current DGS policy and CA Public Contract Code.
  Use Azure AI Search to query the DGS RAG index (Procurement Division policy memos, PCC guide, NCB templates, DVBE program guide, CMAS ordering guide, EO N-5-26 implementation guidance, STD forms).
  Use the CMAS Lookup tool to check contract vehicle availability for the commodity.
  Use the DVBE Requirement tool to calculate applicable small business requirements by purchase value.
  For AI_PROCUREMENT route: invoke the AI Procurement Compliance tool to generate an EO N-5-26 checklist — vendor attestation, risk classification (Tier 1/2/3), bias evaluation, privacy impact, transparency to end-users.
  Always cite the CA Public Contract Code section or DGS policy memo.
  Note that AI guidance does not substitute for official competitive procurement review by DGS Procurement Division.
tools:
  - name: azure_ai_search
    type: azure_search
    index: dgs-knowledge-base
  - name: cmas_lookup
    type: function
    function: check_cmas_availability
  - name: dvbe_threshold
    type: function
    function: calculate_dvbe_requirements
  - name: ai_procurement_compliance
    type: function
    function: generate_eo_n526_checklist
```

## Step 3 — Backend Implementation

```python
# backend/app/main.py
from fastapi import FastAPI
from azure.identity import DefaultAzureCredential
import os

app = FastAPI(title="DGS Procurement Intelligence Agent")
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
        "procurement_path": route_result.route,
        "dgs_contact": "dgs.ca.gov/PD | 916-375-4400"
    }

@app.post("/api/ai-procurement-check")
async def ai_procurement_check(request: dict):
    """Generate EO N-5-26 compliance checklist for AI procurement."""
    return await AIProcurementTool().generate_checklist(
        vendor_name=request.get("vendor_name"),
        tool_type=request.get("tool_type"),
        use_case=request.get("use_case"),
        estimated_value=request.get("estimated_value")
    )
```

## Step 4 — Azure Services to Provision

### Azure AI Foundry

```bash
az ml workspace create \
  --name dgs-procurement-hub \
  --resource-group rg-dgs-procurement \
  --kind hub

az ml workspace create \
  --name dgs-procurement-project \
  --resource-group rg-dgs-procurement \
  --kind project \
  --hub-name dgs-procurement-hub
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name dgs-openai \
  --resource-group rg-dgs-procurement \
  --kind OpenAI \
  --sku S0 \
  --location westus

az cognitiveservices account deployment create \
  --name dgs-openai \
  --resource-group rg-dgs-procurement \
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
  --name dgs-ai-search \
  --resource-group rg-dgs-procurement \
  --sku Standard

# Index: dgs-knowledge-base
# Source documents:
#   - DGS Procurement Division policy memos and FAQs
#   - CA Public Contract Code (key procurement sections)
#   - CMAS Program Guide and ordering procedures
#   - Small Business and DVBE Program handbook
#   - Non-Competitive Bid guide and STD 66 instructions
#   - STOA and IT procurement procedures
#   - EO N-5-26 implementation guidance and AI procurement checklist
#   - SB 53 compliance guidance for AI procurement
#   - Protest procedures guide
```

### Azure Container Apps

```bash
az containerapp create \
  --name dgs-procurement-backend \
  --resource-group rg-dgs-procurement \
  --environment dgs-env \
  --image ghcr.io/jileary23/dgs-procurement:latest \
  --target-port 8017 \
  --env-vars \
    USE_MOCK_SERVICES=false \
    AZURE_OPENAI_ENDPOINT=secretref:openai-endpoint \
    AZURE_SEARCH_ENDPOINT=secretref:search-endpoint
```

## Step 5 — Bicep Infrastructure

Create `infra/main.bicep` defining:

- Azure AI Foundry Hub + Project (West US)
- Azure OpenAI (GPT-4o, 30K TPM GlobalStandard)
- Azure AI Search (Standard, `dgs-knowledge-base`)
- Azure Container Apps (internal ingress + Azure AD authentication for auditor persona)
- Managed Identity with minimum required RBAC
- Key Vault for secrets
- Azure Monitor with 1-year retention (procurement audit trail)

## Step 6 — Deploy

```bash
cd accelerators/017-dgs-procurement-agent
azd up --environment dgs-dev

./scripts/azd-deploy.sh 017
```

## Compliance & Guardrails

- **EO N-5-26**: AI procurement route generates mandatory vendor attestation checklist; AI tools procured using this system must themselves comply with EO N-5-26 (meta-compliance)
- **CA PCC**: All procurement thresholds and procedures cite specific PCC sections
- **SB 53**: AI deployment and procurement guidance incorporates SB 53 safety requirements
- **CCPA/CPRA**: PII filter prevents disclosure of vendor or agency personal data
- **EO N-12-23**: Source citations mandatory; procurement decisions remain with authorized procurement officers
- **Audit trail**: All AI procurement compliance checks logged for 1 year per procurement records retention

## Validation

```bash
USE_MOCK_SERVICES=true uvicorn backend.app.main:app --reload --port 8017 &
curl -X POST http://localhost:8017/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "My agency wants to purchase an AI writing assistant for $85,000. What procurement method do I use and what EO N-5-26 requirements apply?"}'
```

Run smoke tests: `npm run smoke-test -- --accelerator 017`
