---
agent: agent
description: Build and deploy the Caltrans Transportation Project Intelligence Agent using Microsoft Agent Framework on Azure AI Foundry
tools:
  - AIAgentExpert
---

# 011 — Caltrans Transportation Project Intelligence Agent

## Microsoft Agent Framework Build & Deploy

You are an expert Azure AI engineer. Build and deploy the **Caltrans Transportation Project Intelligence Agent** for the California Department of Transportation using [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) on Azure AI Foundry.

## Accelerator Context

- **Agency:** California Department of Transportation (Caltrans)
- **Directory:** `accelerators/011-caltrans-project-intelligence-agent/`
- **Backend Port:** 8011
- **Purpose:** Accelerate Caltrans project delivery — helps engineers, project managers, and encroachment permit applicants navigate HDM standards, CEQA/NEPA requirements, and permit workflows. Azure Document Intelligence used for submitted drawing analysis.

## Step 1 — Scaffold the Project Structure

```
accelerators/011-caltrans-project-intelligence-agent/
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
│   │       ├── document_intel_tool.py  # Azure Document Intelligence — drawing extraction
│   │       ├── hdm_search_tool.py      # Highway Design Manual RAG
│   │       ├── permit_tool.py          # Encroachment permit workflow
│   │       └── search_tool.py          # Azure AI Search
│   ├── mock_data/caltrans/
│   └── requirements.txt
├── frontend/src/
├── infra/
└── .env.example
```

## Step 2 — Microsoft Agent Framework Agent Definitions

Create `agent.yaml`:

```yaml
name: caltrans-project-intelligence
description: Caltrans Transportation Project Intelligence Agent
version: "1.0"
framework: microsoft-agent-framework
pipeline:
  - query_agent
  - router_agent
  - action_agent
constitution: ../../shared/constitution.md
compliance:
  - EO N-12-23
  - FHWA
  - CEQA
  - NEPA
  - ADA
  - Caltrans Right-of-Way Manual
```

Create `agents/query_agent.yaml`:

```yaml
name: QueryAgent
model: gpt-4o
instructions: |
  You are the QueryAgent for the Caltrans Transportation Project Intelligence system.
  1. Detect intent: encroachment_permit, design_standard, environmental_review, construction_compliance, project_status, ada_compliance.
  2. Extract entities: route number (e.g., SR-101, I-5), project EA number, permit type (utility, structure, access), county/district, work type.
  3. Detect user role: external_applicant (limited guidance) vs. caltrans_staff (full internal guidance).
  4. Flag submitted documents (PDFs, drawings) for Document Intelligence processing.
  5. Filter any project-confidential or pre-decisional CEQA information per FHWA guidance.
  6. If the query is incomplete or ambiguous, request clarification before proceeding.
tools:
  - name: pii_filter
    type: builtin
  - name: document_classifier
    type: function
    function: classify_uploaded_document
handoff: RouterAgent
```

Create `agents/router_agent.yaml`:

```yaml
name: RouterAgent
model: gpt-4o
instructions: |
  Route Caltrans queries to the appropriate knowledge domain:
  - ENCROACHMENT_PERMIT: submittal requirements, plan check checklists, fee schedules, processing timelines
  - DESIGN_STANDARDS: Highway Design Manual (HDM), Standard Plans, Standard Specifications, lane widths, sight distance, ADA curb ramps
  - ENVIRONMENTAL_REVIEW: CEQA/NEPA thresholds, categorical exemptions, IS/MND criteria, air quality conformity
  - CONSTRUCTION_COMPLIANCE: CMS sign requirements, traffic control plans, lane closure restrictions, peak hour rules
  - PROJECT_STATUS: outstanding permits and clearances by EA number (requires Caltrans staff role)
  - ADA_COMPLIANCE: pedestrian access route standards, detour routes during construction
  Enforce role-based access: external_applicant routes only get public-facing guidance.
handoff: ActionAgent
```

Create `agents/action_agent.yaml`:

```yaml
name: ActionAgent
model: gpt-4o
instructions: |
  Retrieve precise, citation-backed Caltrans guidance from the knowledge base.
  Use Azure AI Search to query the Caltrans RAG index (HDM, Standard Plans, Encroachment Permits Manual, CEQA/NEPA guidelines, Standard Specifications).
  For submitted permit drawings, use the Document Intelligence tool to extract dimensions, materials, and locations for pre-screening.
  Always cite the specific HDM chapter/section, Standard Plan sheet number, or permit manual section.
  For CEQA/NEPA questions, always confirm whether the specific project characteristics require further analysis.
  Route project-specific status queries (EA number lookups) only for authenticated Caltrans staff.
tools:
  - name: azure_ai_search
    type: azure_search
    index: caltrans-knowledge-base
  - name: document_intelligence
    type: azure_document_intelligence
    model: prebuilt-document
  - name: permit_workflow
    type: function
    function: get_permit_checklist
```

## Step 3 — Backend Implementation

```python
# backend/app/main.py
from fastapi import FastAPI, UploadFile, File
from azure.identity import DefaultAzureCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
import os

app = FastAPI(title="Caltrans Project Intelligence Agent")
USE_MOCK = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

@app.post("/api/query")
async def query(request: dict):
    credential = DefaultAzureCredential() if not USE_MOCK else None
    query_result = await QueryAgent(credential).process(request["message"])
    route_result = await RouterAgent(credential).route(query_result)
    response = await ActionAgent(credential, mock=USE_MOCK).act(route_result)
    return {"response": response}

@app.post("/api/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    """Analyze submitted encroachment permit drawings with Document Intelligence."""
    if USE_MOCK:
        return {"extracted": {"dimensions": "mock-data", "material": "conduit"}}
    client = DocumentIntelligenceClient(
        endpoint=os.getenv("AZURE_DOCUMENT_INTEL_ENDPOINT"),
        credential=DefaultAzureCredential()
    )
    result = await client.begin_analyze_document("prebuilt-document", file.file.read())
    return {"extracted": result.content}
```

## Step 4 — Azure Services to Provision

### Azure AI Foundry

```bash
az ml workspace create \
  --name caltrans-intel-hub \
  --resource-group rg-caltrans-intel \
  --kind hub

az ml workspace create \
  --name caltrans-intel-project \
  --resource-group rg-caltrans-intel \
  --kind project \
  --hub-name caltrans-intel-hub
```

### Azure OpenAI

```bash
az cognitiveservices account create \
  --name caltrans-openai \
  --resource-group rg-caltrans-intel \
  --kind OpenAI \
  --sku S0 \
  --location westus

az cognitiveservices account deployment create \
  --name caltrans-openai \
  --resource-group rg-caltrans-intel \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-11-20" \
  --model-format OpenAI \
  --sku-capacity 30 \
  --sku-name GlobalStandard
```

### Azure AI Search (RAG — Caltrans Manuals)

```bash
az search service create \
  --name caltrans-ai-search \
  --resource-group rg-caltrans-intel \
  --sku Standard

# Index: caltrans-knowledge-base
# Source documents:
#   - Caltrans Highway Design Manual (HDM) chapters
#   - Standard Plans (current edition)
#   - Encroachment Permits Manual
#   - CEQA/NEPA guidance documents
#   - Standard Specifications for Construction
#   - ADA Transition Plan and pedestrian access guidance
```

### Azure Document Intelligence

```bash
az cognitiveservices account create \
  --name caltrans-doc-intel \
  --resource-group rg-caltrans-intel \
  --kind FormRecognizer \
  --sku S0 \
  --location westus
```

### Azure Container Apps

```bash
az containerapp create \
  --name caltrans-intel-backend \
  --resource-group rg-caltrans-intel \
  --environment caltrans-env \
  --image ghcr.io/jileary23/caltrans-intel:latest \
  --target-port 8011 \
  --env-vars \
    USE_MOCK_SERVICES=false \
    AZURE_OPENAI_ENDPOINT=secretref:openai-endpoint \
    AZURE_SEARCH_ENDPOINT=secretref:search-endpoint \
    AZURE_DOCUMENT_INTEL_ENDPOINT=secretref:doc-intel-endpoint
```

## Step 5 — Bicep Infrastructure

Create `infra/main.bicep` defining:

- Azure AI Foundry Hub + Project (West US)
- Azure OpenAI (GPT-4o, 30K TPM GlobalStandard)
- Azure AI Search (Standard tier, `caltrans-knowledge-base` index)
- Azure Document Intelligence (Standard S0)
- Azure Container Apps Environment
- Container Apps for backend (8011) and frontend (3011)
- Managed Identity with role assignments: `Cognitive Services OpenAI User`, `Search Index Data Reader`, `Cognitive Services User` (Document Intelligence)
- Azure Entra ID app registration for role-based access (Caltrans staff vs. external applicant)

## Step 6 — Deploy

```bash
cd accelerators/011-caltrans-project-intelligence-agent
azd up --environment caltrans-dev

# Or project-level
./scripts/azd-deploy.sh 011
```

## Compliance & Guardrails

- **EO N-12-23**: All responses cite specific HDM/Standard Plan sections
- **FHWA**: Agent scoped to FHWA-compliant project delivery guidance only
- **CEQA/NEPA**: Responses recommend professional environmental review for project-specific determinations
- **ADA**: Pedestrian access route responses comply with ADA Title II standards
- **Role-based access**: External applicants see only public guidance; Caltrans staff access internal project context via Entra ID

## Validation

```bash
USE_MOCK_SERVICES=true uvicorn backend.app.main:app --reload --port 8011 &
curl -X POST http://localhost:8011/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What documentation is needed for a fiber optic conduit in Caltrans right-of-way on Route 101?"}'
```

Run smoke tests: `npm run smoke-test -- --accelerator 011`
