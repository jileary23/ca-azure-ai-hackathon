---
agent: agent
description: Build and deploy the CalPERS Retirement Benefits Navigator using Microsoft Agent Framework on Azure AI Foundry
tools:
  - AIAgentExpert
---

# 010 — CalPERS Retirement Benefits Navigator

## Microsoft Agent Framework Build & Deploy

You are an expert Azure AI engineer. Build and deploy the **CalPERS Retirement Benefits Navigator** for the California Public Employees' Retirement System using [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) on Azure AI Foundry.

## Accelerator Context

- **Agency:** California Public Employees' Retirement System (CalPERS)
- **Directory:** `accelerators/010-calpers-retirement-navigator/`
- **Backend Port:** 8010
- **Purpose:** AI-powered retirement benefits navigator — helps ~2M CalPERS members understand pension options, calculate retirement projections, navigate health plan enrollment, and prepare for key life events

## Step 1 — Scaffold the Project Structure

```
accelerators/010-calpers-retirement-navigator/
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
│   │       ├── benefit_calculator_tool.py  # Retirement projection calculations
│   │       ├── health_plan_tool.py         # Health plan comparison
│   │       └── search_tool.py              # RAG over CalPERS publications
│   ├── mock_data/calpers/
│   └── requirements.txt
├── frontend/src/
├── infra/
└── .env.example
```

## Step 2 — Microsoft Agent Framework Agent Definitions

Create `agent.yaml`:

```yaml
name: calpers-retirement-navigator
description: CalPERS Retirement Benefits Navigator
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
  - CA Government Code §20000+
  - IRS Circular 230
```

Create `agents/query_agent.yaml`:

```yaml
name: QueryAgent
model: gpt-4o
instructions: |
  You are the QueryAgent for the CalPERS Retirement Navigator. Perform these steps in order:
  1. Detect member intent: pension calculation, health plan enrollment, service credit, survivor/beneficiary, life event (divorce, disability, retirement date).
  2. Extract entities: years of service, age, membership tier (PEPRA vs Classic), health plan region, benefit formula.
  3. Filter PII (member ID, SSN, DOB) — NEVER pass identifiable data downstream. If member asks for account-specific data, redirect to myCalPERS portal.
  4. If the member's input is incomplete or ambiguous, respond with a clarifying question to gather the necessary information before proceeding.
  5. Output structured intent: intent, entities, member_tier (classic/pepra), topic_domain.
  Comply with CCPA/CPRA. Scope advisory only — no account access.
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
  Route CalPERS member queries to the correct benefit domain:
  - PENSION: retirement formulas (2%@55, 2%@62, 2.5%@55, 3%@50), service credit, retirement date calculation
  - HEALTH: health plan comparison (PERS Choice, PERS Care, PERS Select), enrollment windows, premiums by region
  - LONG_TERM_CARE: CalPERS LTC program options and enrollment
  - SERVICE_CREDIT: purchase rules, cost calculation, private sector credit, military service
  - SURVIVOR_BENEFICIARY: survivor benefit options, beneficiary designations, DROs
  - LIFE_EVENT: disability retirement, divorce/DRO, death benefits, name changes
  - RETIREE_GENERAL: COLA, taxation of benefits, direct deposit
  Include the following disclaimer at the end of every response: 'This is general guidance only. Verify your specific benefits with myCalPERS at my.calpers.ca.gov.'
handoff: ActionAgent
```

Create `agents/action_agent.yaml`:

```yaml
name: ActionAgent
model: gpt-4o
instructions: |
  Retrieve and synthesize CalPERS benefit guidance from the knowledge base.
  Use Azure AI Search to query the CalPERS RAG index (Member Handbooks, PEPRA/Classic plan documents, Health Plan Comparison guides, Annual Reports).
  Use the benefit calculator tool for retirement projection illustrations (these are estimates only).
  Always cite the source document and publication date.
  Include a standard IRS Circular 230 disclaimer when discussing tax implications.
  Redirect account-specific requests (benefit estimates, election changes, address updates) to the myCalPERS portal: my.calpers.ca.gov
tools:
  - name: azure_ai_search
    type: azure_search
    index: calpers-knowledge-base
  - name: benefit_calculator
    type: function
    function: calculate_retirement_estimate
  - name: health_plan_compare
    type: function
    function: compare_health_plans
```

## Step 3 — Backend Implementation

```python
# backend/app/main.py
from fastapi import FastAPI
from azure.identity import DefaultAzureCredential
import os

app = FastAPI(title="CalPERS Retirement Navigator")
USE_MOCK = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

@app.post("/api/query")
async def query(request: dict):
    credential = DefaultAzureCredential() if not USE_MOCK else None
    # PII warning — never log request content
    query_result = await QueryAgent(credential).process(request["message"])
    route_result = await RouterAgent(credential).route(query_result)
    response = await ActionAgent(credential, mock=USE_MOCK).act(route_result)
    return {"response": response, "disclaimer": "General guidance only. Verify at my.calpers.ca.gov"}
```

## Step 4 — Azure Services to Provision

### Azure AI Foundry

```bash
az ml workspace create \
  --name calpers-retirement-hub \
  --resource-group rg-calpers-retirement \
  --kind hub

az ml workspace create \
  --name calpers-retirement-project \
  --resource-group rg-calpers-retirement \
  --kind project \
  --hub-name calpers-retirement-hub
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name calpers-openai \
  --resource-group rg-calpers-retirement \
  --kind OpenAI \
  --sku S0 \
  --location eastus2

az cognitiveservices account deployment create \
  --name calpers-openai \
  --resource-group rg-calpers-retirement \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-11-20" \
  --model-format OpenAI \
  --sku-capacity 30 \
  --sku-name GlobalStandard
```

### Azure AI Search (RAG — CalPERS Publications)

```bash
az search service create \
  --name calpers-ai-search \
  --resource-group rg-calpers-retirement \
  --sku Standard

# Index: calpers-knowledge-base
# Source documents:
#   - CalPERS Member Handbook (Classic and PEPRA)
#   - Health Plan Comparison guides by region
#   - PEPRA statutory framework (CA Gov Code §7522+)
#   - Service Credit Purchase guides
#   - Survivor Benefit guides
#   - Annual Valuation Report excerpts
```

### Azure Container Apps

```bash
az containerapp create \
  --name calpers-retirement-backend \
  --resource-group rg-calpers-retirement \
  --environment calpers-env \
  --image ghcr.io/jileary23/calpers-retirement:latest \
  --target-port 8010 \
  --env-vars \
    USE_MOCK_SERVICES=false \
    AZURE_OPENAI_ENDPOINT=secretref:openai-endpoint \
    AZURE_SEARCH_ENDPOINT=secretref:search-endpoint
```

## Step 5 — Bicep Infrastructure

Create `infra/main.bicep` defining:

- Azure AI Foundry Hub + Project (East US 2)
- Azure OpenAI (GPT-4o, 30K TPM GlobalStandard)
- Azure AI Search (Standard tier, `calpers-knowledge-base` index)
- Azure Container Apps Environment with private networking
- Managed Identity with role assignments: `Cognitive Services OpenAI User`, `Search Index Data Reader`
- Key Vault with secrets for all service endpoints
- Azure Monitor workspace with 90-day retention (compliance requirement)

## Step 6 — Deploy via Azure Developer CLI

```bash
cd accelerators/010-calpers-retirement-navigator
azd up --environment calpers-dev

# Or project-level
cd ../..
./scripts/azd-deploy.sh 010
```

## Step 7 — Foundry Agent Registration

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint="https://calpers-retirement-project.eastus2.api.azureml.ms",
    credential=DefaultAzureCredential()
)

for agent_name, yaml_path in [
    ("calpers-query-agent", "agents/query_agent.yaml"),
    ("calpers-router-agent", "agents/router_agent.yaml"),
    ("calpers-action-agent", "agents/action_agent.yaml"),
]:
    client.agents.create_agent(
        model="gpt-4o",
        name=agent_name,
        instructions=open(yaml_path).read()
    )
```

## Compliance & Guardrails

- **EO N-12-23**: Confidence scores on all benefit calculations; source citations mandatory
- **CCPA/CPRA**: PII filter in QueryAgent; no member account data accessed or stored
- **IRS Circular 230**: Disclaimer on all tax-related responses
- **CA Government Code §20000+**: Responses scoped to plan documents; no account-specific benefit elections
- **Advisory only**: All responses include myCalPERS portal redirect for account actions
- **Audit logging**: Query intents logged (no PII) to Azure Monitor, 90-day retention

## Validation

```bash
USE_MOCK_SERVICES=true uvicorn backend.app.main:app --reload --port 8010 &
curl -X POST http://localhost:8010/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "I have 25 years of Classic service. What is my 2% at 55 monthly pension estimate?"}'
```

Run smoke tests: `npm run smoke-test -- --accelerator 010`
