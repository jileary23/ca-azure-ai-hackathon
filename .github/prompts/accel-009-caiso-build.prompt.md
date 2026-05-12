---
agent: agent
description: Build and deploy the CAISO Grid Operations Intelligence Agent using Microsoft Agent Framework on Azure AI Foundry
tools:
  - AIAgentExpert
---

# 009 — CAISO Grid Operations Intelligence Agent

## Microsoft Agent Framework Build & Deploy

You are an expert Azure AI engineer. Build and deploy the **CAISO Grid Operations Intelligence Agent** for the California Independent System Operator using [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) on Azure AI Foundry.

## Accelerator Context

- **Agency:** California Independent System Operator (CAISO)
- **Directory:** `accelerators/009-caiso-grid-operations-agent/`
- **Backend Port:** 8009
- **Purpose:** Real-time grid operations intelligence — aggregates OASIS market data, weather forecasts, and operational alerts to support CAISO operators

## Step 1 — Scaffold the Project Structure

Create the following directory layout:

```
accelerators/009-caiso-grid-operations-agent/
├── agent.yaml                    # Microsoft Agent Framework root definition
├── agents/
│   ├── query_agent.yaml          # QueryAgent definition
│   ├── router_agent.yaml         # RouterAgent definition
│   └── action_agent.yaml         # ActionAgent definition
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint
│   │   ├── agents/
│   │   │   ├── query_agent.py    # QueryAgent implementation
│   │   │   ├── router_agent.py   # RouterAgent implementation
│   │   │   └── action_agent.py   # ActionAgent implementation
│   │   └── tools/
│   │       ├── oasis_tool.py     # CAISO OASIS data feed tool
│   │       ├── flex_alert_tool.py
│   │       └── search_tool.py    # Azure AI Search RAG tool
│   ├── mock_data/caiso/          # Synthetic grid/market data
│   └── requirements.txt
├── frontend/
│   └── src/
├── infra/
│   ├── main.bicep
│   └── main.parameters.json
└── .env.example
```

## Step 2 — Microsoft Agent Framework Agent Definitions

Create `agent.yaml` at the accelerator root:

```yaml
# agent.yaml — Microsoft Agent Framework
name: caiso-grid-ops-agent
description: CAISO Grid Operations Intelligence Agent
version: "1.0"
framework: microsoft-agent-framework
pipeline:
  - query_agent
  - router_agent
  - action_agent
constitution: ../../shared/constitution.md
compliance:
  - EO N-12-23
  - NERC CIP
  - CAISO Tariff
```

Create `agents/query_agent.yaml`:

```yaml
name: QueryAgent
model: gpt-4o
instructions: |
  You are the QueryAgent for the CAISO Grid Operations system. Execute steps in order:
  1. Detect the operator's intent: real-time operations, day-ahead market, transmission planning, demand response, or outage coordination.
  2. Extract entities: time windows, grid nodes, LMP zones, demand response programs, transmission corridors.
  3. Filter any PII before passing to the RouterAgent.
  4. If the operator's query is invalid or incomplete, request clarification before proceeding.
  5. Output a structured intent object with: intent, entities, priority, and operator_role (internal_operator, market_participant, analyst).
  Comply with EO N-12-23 and NERC CIP cybersecurity standards. The QueryAgent must never emit dispatch commands or market submissions.
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
  You are the RouterAgent for CAISO Grid Operations. Route the query to the correct domain:
  - REALTIME_OPS: current grid status, renewable curtailment, net imports/exports
  - DAY_AHEAD_MARKET: LMP spreads, congestion nodes, day-ahead schedules
  - DEMAND_RESPONSE: Flex Alert capacity, DR program availability
  - RENEWABLE_INTEGRATION: solar/wind over-generation risk, curtailment forecasts
  - OUTAGE_COORDINATION: planned transmission outages, maintenance windows
  Set priority (CRITICAL, HIGH, NORMAL) based on time sensitivity.
  Escalate CRITICAL grid reliability events immediately.
handoff: ActionAgent
```

Create `agents/action_agent.yaml`:

```yaml
name: ActionAgent
model: gpt-4o
instructions: |
  You are the ActionAgent for CAISO Grid Operations. Retrieve and synthesize data from the routed domain.
  Use Azure AI Search to query the CAISO knowledge base (OASIS feeds, operational reports, tariff documents).
  Use the OASIS tool for real-time market data (mock when USE_MOCK_SERVICES=true).
  Use the Flex Alert tool for demand response capacity.
  Always cite the data source and timestamp. The agent is READ-ONLY — never issue dispatch commands or market submissions.
  Format responses for control room operators: concise, actionable, status-first.
tools:
  - name: azure_ai_search
    type: azure_search
    index: caiso-knowledge-base
  - name: oasis_feed
    type: function
    function: get_oasis_data
  - name: flex_alert
    type: function
    function: get_flex_alert_status
```

## Step 3 — Backend Implementation

Create `backend/app/main.py` using FastAPI with the 3-agent pipeline:

```python
from fastapi import FastAPI
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from agents.query_agent import QueryAgent
from agents.router_agent import RouterAgent
from agents.action_agent import ActionAgent
import os

app = FastAPI(title="CAISO Grid Operations Agent")

USE_MOCK = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

@app.post("/api/query")
async def query(request: dict):
    credential = DefaultAzureCredential() if not USE_MOCK else None
    query_result = await QueryAgent(credential).process(request["message"])
    route_result = await RouterAgent(credential).route(query_result)
    response = await ActionAgent(credential, mock=USE_MOCK).act(route_result)
    return {"response": response}
```

## Step 4 — Azure Services to Provision

Provision the following Azure and Foundry services:

### Azure AI Foundry

```bash
# Create Azure AI Foundry Hub and Project
az ml workspace create \
  --name caiso-grid-ops-hub \
  --resource-group rg-caiso-grid-ops \
  --kind hub

az ml workspace create \
  --name caiso-grid-ops-project \
  --resource-group rg-caiso-grid-ops \
  --kind project \
  --hub-name caiso-grid-ops-hub
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name caiso-openai \
  --resource-group rg-caiso-grid-ops \
  --kind OpenAI \
  --sku S0 \
  --location eastus2

# Deploy GPT-4o
az cognitiveservices account deployment create \
  --name caiso-openai \
  --resource-group rg-caiso-grid-ops \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-11-20" \
  --model-format OpenAI \
  --sku-capacity 30 \
  --sku-name GlobalStandard
```

### Azure AI Search (RAG Knowledge Base)

```bash
az search service create \
  --name caiso-ai-search \
  --resource-group rg-caiso-grid-ops \
  --sku Standard \
  --partition-count 1 \
  --replica-count 1

# Create index for CAISO knowledge base
# Index: caiso-knowledge-base
# Documents: OASIS operational reports, CAISO Tariff, Flex Alert guides, NERC reliability standards
```

### Azure Container Apps (Deployment)

```bash
az containerapp create \
  --name caiso-grid-ops-backend \
  --resource-group rg-caiso-grid-ops \
  --environment caiso-env \
  --image ghcr.io/jileary23/caiso-grid-ops:latest \
  --target-port 8009 \
  --env-vars \
    USE_MOCK_SERVICES=false \
    AZURE_OPENAI_ENDPOINT=secretref:openai-endpoint \
    AZURE_SEARCH_ENDPOINT=secretref:search-endpoint \
    AZURE_FOUNDRY_PROJECT=secretref:foundry-project
```

## Step 5 — Bicep Infrastructure

Create `infra/main.bicep` defining:

- Azure AI Foundry Hub + Project
- Azure OpenAI (GPT-4o deployment)
- Azure AI Search (Standard tier, `caiso-knowledge-base` index)
- Azure Container Apps Environment
- Container Apps for backend (port 8009) and frontend (port 3009)
- Managed Identity with role assignments: `Cognitive Services OpenAI User`, `Search Index Data Reader`
- Key Vault for secrets

## Step 6 — Deploy via Azure Developer CLI

```bash
# Initialize azd for this accelerator
cd accelerators/009-caiso-grid-operations-agent
azd init --template minimal

# Provision and deploy
azd up --environment caiso-dev

# Or use the project-level script
cd ../..
./scripts/azd-deploy.sh 009
```

## Step 7 — Foundry Agent Registration

Register the 3-agent pipeline in Azure AI Foundry:

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentDefinition
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint="https://caiso-grid-ops-project.eastus2.api.azureml.ms",
    credential=DefaultAzureCredential()
)

# Register QueryAgent
query_agent = client.agents.create_agent(
    model="gpt-4o",
    name="caiso-query-agent",
    instructions=open("agents/query_agent.yaml").read()
)

# Register RouterAgent and ActionAgent similarly
```

## Compliance & Guardrails

- **EO N-12-23**: All AI outputs include confidence scores and source citations
- **NERC CIP**: Agent is READ-ONLY — never issues dispatch commands or market submissions
- **CAISO Tariff**: Responses scoped to publicly available OASIS data; no confidential market data
- **PII**: QueryAgent filters operator PII before pipeline processing
- **Audit logging**: All queries and responses logged to Azure Monitor with 90-day retention

## Validation

```bash
cd accelerators/009-caiso-grid-operations-agent
USE_MOCK_SERVICES=true uvicorn backend.app.main:app --reload --port 8009 &
curl -X POST http://localhost:8009/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the current renewable curtailment level?"}'
```

Run smoke tests: `npm run smoke-test -- --accelerator 009`
