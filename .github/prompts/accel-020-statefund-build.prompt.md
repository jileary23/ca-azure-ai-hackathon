---
agent: agent
description: Build and deploy the CA State Fund Workers' Comp Navigator using Microsoft Agent Framework on Azure AI Foundry
tools:
  - AIAgentExpert
---

# 020 — CA State Fund Workers' Compensation Navigator

## Microsoft Agent Framework Build & Deploy

You are an expert Azure AI engineer. Build and deploy the **CA State Fund Workers' Compensation Navigator** for the State Compensation Insurance Fund using [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) on Azure AI Foundry.

## Accelerator Context

- **Agency:** State Compensation Insurance Fund (CA State Fund)
- **Directory:** `accelerators/020-statefund-workers-comp-navigator/`
- **Backend Port:** 8020
- **Purpose:** Multi-persona workers' compensation guide for California — helps injured workers understand their rights and benefits, assists employers with policy and audit management, and guides medical providers through billing authorization and MTUS compliance

## Step 1 — Scaffold the Project Structure

```
accelerators/020-statefund-workers-comp-navigator/
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
│   │       ├── xmod_calculator_tool.py     # Experience Modification (X-MOD) explanation
│   │       ├── mtus_lookup_tool.py         # DWC Medical Treatment Utilization Schedule
│   │       ├── benefit_calculator_tool.py  # TD/PD benefit estimate by wage
│   │       ├── imr_guidance_tool.py        # Independent Medical Review process
│   │       └── search_tool.py              # Azure AI Search RAG
│   ├── mock_data/statefund/
│   └── requirements.txt
├── frontend/src/
├── infra/
└── .env.example
```

## Step 2 — Microsoft Agent Framework Agent Definitions

Create `agent.yaml`:

```yaml
name: statefund-workers-comp-navigator
description: CA State Fund Workers' Compensation Navigator
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
  - CA Labor Code §3200 et seq.
  - DWC regulations (8 CCR §9700 et seq.)
  - HIPAA (medical information)
```

Create `agents/query_agent.yaml`:

```yaml
name: QueryAgent
model: gpt-4o
instructions: |
  You are the QueryAgent for the CA State Fund Workers' Compensation Navigator.
  1. Detect user persona:
     - INJURED_WORKER: employee with a workplace injury; may be represented by attorney
     - EMPLOYER: policyholder or HR manager managing claims or policy
     - MEDICAL_PROVIDER: physician, clinic, physical therapist, pharmacist billing State Fund
  2. Detect intent:
     Injured Worker: report_injury, td_benefits, pd_rating, medical_treatment, mmi_status, vocational_rehab, imr_appeal, return_to_work
     Employer: claim_status, policy_management, xmod_explanation, audit_prep, return_to_work_program, injury_prevention
     Medical Provider: billing_authorization, rfa_submission, mtus_compliance, imr_process, lien_resolution, fee_schedule
  3. Extract entities: injury type/body part, claim number (anonymize), policy number (anonymize), injury date, wage information (for benefit estimates), WCAB case number.
  4. Apply PII filter — strip claim/policy numbers, SSNs, medical record details before routing.
  5. Flag URGENT for: denied claims requiring IMR within 30 days, disputes at WCAB, return-to-work deadlines.
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
  Route CA workers' compensation queries by persona and topic:

  INJURED_WORKER routes:
  - MEDICAL_TREATMENT: MPN (Medical Provider Network) selection, RFA process, treatment approval timelines, MTUS standards, UR denial rights
  - DISABILITY_BENEFITS: TD (temporary disability — 2/3 wage replacement), PD (permanent disability rating process, AMA Guides), TTD dates
  - IMR_APPEAL: Independent Medical Review — grounds, 30-day deadline, DWC IMR application, stay of treatment denial
  - RETURN_TO_WORK: modified duty offers, vocational rehabilitation (SJDB voucher), work restrictions
  - CLAIM_DISPUTE: WCAB process, DWC Information & Assistance Unit (free, non-attorney), attorney referral information

  EMPLOYER routes:
  - XMOD: Experience Modification Rate explanation — how calculated, impact on premium, improvement strategies
  - AUDIT: premium audit process, classification of employees, payroll records required
  - POLICY: policy endorsements, coverage questions, certificate of insurance
  - INJURY_PREVENTION: Cal/OSHA IIPP requirements, ergonomic programs, State Fund safety programs

  MEDICAL_PROVIDER routes:
  - BILLING_AUTHORIZATION: prior authorization requirements, RFA submission via State Fund portal
  - MTUS: DWC Medical Treatment Utilization Schedule lookup by body part/diagnosis (8 CCR §9792.20 et seq.)
  - FEE_SCHEDULE: California Workers' Comp Official Medical Fee Schedule (OMFS), billing codes
  - LIEN: lien filing process, WCAB lien conference, IBR (Independent Bill Review)
handoff: ActionAgent
```

Create `agents/action_agent.yaml`:

```yaml
name: ActionAgent
model: gpt-4o
instructions: |
  Deliver plain-language California workers' compensation guidance backed by State Fund knowledge and CA Labor Code.
  Use Azure AI Search to query the State Fund RAG index (DWC MTUS, CA Labor Code §3200+, 8 CCR workers' comp regulations, State Fund claim guides, WCAB procedures, IMR process guide, SJDB guide).
  Use the X-MOD Calculator tool to explain experience modification rate calculation (mock data in local dev).
  Use the MTUS Lookup tool to retrieve treatment guidelines for specific diagnoses (8 CCR §9792.20 et seq.).
  Use the Benefit Calculator tool to estimate TD/PD benefits based on average weekly wage.
  Use the IMR Guidance tool for step-by-step IMR appeal procedures.
  Injured worker responses: plain language, rights-forward, include DWC Information & Assistance Unit referral (800-736-7401) for disputes.
  Medical provider responses: include OMFS fee schedule reference and State Fund portal link for RFAs.
  Always note: responses are general guidance; individual claim decisions are made by State Fund claims adjusters and DWC adjudicators.
tools:
  - name: azure_ai_search
    type: azure_search
    index: statefund-knowledge-base
  - name: xmod_explainer
    type: function
    function: explain_experience_modification
  - name: mtus_lookup
    type: function
    function: get_mtus_guidelines
  - name: benefit_calculator
    type: function
    function: estimate_td_pd_benefits
  - name: imr_guidance
    type: function
    function: get_imr_process_steps
```

## Step 3 — Backend Implementation

```python
# backend/app/main.py
from fastapi import FastAPI
from azure.identity import DefaultAzureCredential
import os

app = FastAPI(title="CA State Fund Workers' Compensation Navigator")
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
        "disclaimer": "General workers' comp guidance. Individual claim decisions are made by State Fund adjusters.",
        "dwc_info": "DWC Information & Assistance: 800-736-7401 | statefundca.com"
    }

@app.get("/api/mtus/{body_part}")
async def mtus_lookup(body_part: str, icd10_code: str = None):
    """Direct MTUS treatment guideline lookup."""
    if USE_MOCK:
        return {"body_part": body_part, "guideline": "Mock MTUS guideline", "mock": True}
    return await MTUSLookupTool().get_guidelines(body_part=body_part, icd10=icd10_code)

@app.post("/api/benefit-estimate")
async def benefit_estimate(request: dict):
    """Estimate TD/PD benefits (informational only)."""
    avg_weekly_wage = request.get("avg_weekly_wage", 0)
    td_weekly = min(avg_weekly_wage * 2/3, 1540)  # 2024 TD max
    return {
        "td_weekly_estimate": round(td_weekly, 2),
        "disclaimer": "Estimate only. Actual benefits determined by State Fund claims adjuster."
    }
```

## Step 4 — Azure Services to Provision

### Azure AI Foundry

```bash
az ml workspace create \
  --name statefund-wc-hub \
  --resource-group rg-statefund-wc \
  --kind hub

az ml workspace create \
  --name statefund-wc-project \
  --resource-group rg-statefund-wc \
  --kind project \
  --hub-name statefund-wc-hub
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name statefund-openai \
  --resource-group rg-statefund-wc \
  --kind OpenAI \
  --sku S0 \
  --location westus

az cognitiveservices account deployment create \
  --name statefund-openai \
  --resource-group rg-statefund-wc \
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
  --name statefund-ai-search \
  --resource-group rg-statefund-wc \
  --sku Standard

# Index: statefund-knowledge-base
# Source documents:
#   - DWC Medical Treatment Utilization Schedule (all body part chapters)
#   - CA Labor Code §3200–6002 (key workers' comp provisions)
#   - 8 CCR §9700–9999 (DWC regulations including MTUS, OMFS, UR, IMR)
#   - State Fund Injured Worker Guide
#   - State Fund Employer Guide
#   - DWC IMR Application and process guide
#   - SJDB (Supplemental Job Displacement Benefit) voucher guide
#   - WCAB procedural guide
#   - Experience Modification Rate calculation guide
#   - Official Medical Fee Schedule (OMFS) reference
```

### Azure Container Apps

```bash
az containerapp create \
  --name statefund-wc-backend \
  --resource-group rg-statefund-wc \
  --environment statefund-env \
  --image ghcr.io/jileary23/statefund-wc:latest \
  --target-port 8020 \
  --env-vars \
    USE_MOCK_SERVICES=false \
    AZURE_OPENAI_ENDPOINT=secretref:openai-endpoint \
    AZURE_SEARCH_ENDPOINT=secretref:search-endpoint
```

## Step 5 — Bicep Infrastructure

Create `infra/main.bicep` defining:

- Azure AI Foundry Hub + Project (West US)
- Azure OpenAI (GPT-4o, 30K TPM GlobalStandard)
- Azure AI Search (Standard, `statefund-knowledge-base`)
- Azure Container Apps (public ingress — injured workers and employers are external)
- Managed Identity with minimal RBAC
- Key Vault for all secrets
- Azure Front Door + WAF (HIPAA medical information protection)
- Azure Monitor with 180-day retention (HIPAA — medical information)
- Content Safety filter on medical information outputs

## Step 6 — Deploy

```bash
cd accelerators/020-statefund-workers-comp-navigator
azd up --environment statefund-dev

./scripts/azd-deploy.sh 020
```

## Compliance & Guardrails

- **CA Labor Code §3200+**: All benefit and procedure guidance cites specific Labor Code sections
- **HIPAA**: Medical treatment information protected; PHI filter; 180-day log retention
- **DWC MTUS (8 CCR §9792.20)**: Treatment guidelines sourced directly from DWC MTUS; no deviation
- **CCPA/CPRA**: PII filter on claim/policy numbers and medical record references
- **No claim decisions**: AI provides guidance only; all claim acceptance/denial is by licensed adjusters
- **IMR deadline enforcement**: URGENT flag for queries with 30-day IMR deadline approaching
- **EO N-12-23**: Source citations mandatory; benefit estimates include statutory disclaimer

## Validation

```bash
USE_MOCK_SERVICES=true uvicorn backend.app.main:app --reload --port 8020 &
curl -X POST http://localhost:8020/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "My workers comp doctor recommended physical therapy but State Fund denied it. What is the IMR appeal process and how long do I have to file?"}'
```

Run smoke tests: `npm run smoke-test -- --accelerator 020`
