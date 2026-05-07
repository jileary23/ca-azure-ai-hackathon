# LA County Public Defender — Evidence AI Demo

**Powered by Azure Video Indexer + Azure OpenAI GPT-4o**

This demo shows how the LA County Public Defender's Office can use Microsoft Azure
to analyze body cam footage — comparable to tools like Harvey.ai and FileVine, but
deployed entirely **within the County's own secure Azure Government tenant**.
No evidence data leaves the County's environment.

---

## What This Demo Shows

| Capability                  | Description                                                                            |
| --------------------------- | -------------------------------------------------------------------------------------- |
| **Transcript Generation**   | Azure Video Indexer extracts a full timestamped transcript via speech-to-text          |
| **Speaker Diarization**     | Automatically labels and separates officer vs. subject voices                          |
| **Key Moment Detection**    | Flags legally significant events: Miranda rights, consent, use of force, scene changes |
| **GPT-4o Evidence Summary** | Produces a structured narrative, timeline, discrepancies, and defense considerations   |
| **Natural Language Q&A**    | Attorneys ask plain-English questions; GPT-4o answers citing specific timestamps       |

---

## Architecture

```
Body Cam Video (MP4/MOV)
        │
        ▼
┌─────────────────────────┐
│  Azure Video Indexer    │  ← Speaker diarization, transcript
│  (Azure Gov Cloud)      │     key moments, scene analysis
└────────────┬────────────┘
             │  Structured JSON
             ▼
┌─────────────────────────┐
│  Azure OpenAI GPT-4o    │  ← Evidence summary, defense flags,
│  (Azure Gov Cloud)      │     Q&A grounded in transcript only
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  FastAPI Backend        │  ← REST API (Python 3.11)
│  React Frontend         │  ← Attorney-facing UI
└─────────────────────────┘
```

**Security & Compliance:**
- All services run in the County's Azure Government subscription
- CJIS Security Policy compliant
- FedRAMP High authorized
- No data sent to Harvey.ai, FileVine, or any third-party SaaS
- Managed Identity authentication (no secrets in code)

---

## Quick Start (Mock Mode — No Azure Credentials Needed)

### Option 1: Docker

```bash
cd demos/lacounty-pubdef-evidence-ai
docker-compose up --build
```

- Backend: http://localhost:8009
- Frontend: http://localhost:3009

### Option 2: Manual

**Backend:**
```bash
cd demos/lacounty-pubdef-evidence-ai/backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --port 8009 --reload
```

**Frontend (new terminal):**
```bash
cd demos/lacounty-pubdef-evidence-ai/frontend
npm install
npm run dev
```

Visit http://localhost:3009 and click **Load Demo Case** to analyze the pre-built body cam scenario.

---

## Demo Scenario

The demo includes a realistic body cam transcript for **Case LA-2024-CR-087421**:

- Officer Chen stops Marcus Davis on Crenshaw Blvd for a broken tail light
- Officer surfaces a 5-year-old prior charge and begins questioning **without Miranda**
- Ambiguous consent obtained: *"I mean... I guess"*
- Subject attempts to revoke consent mid-search — officer refuses
- Contraband found; Miranda read **at point of arrest** (not pre-questioning)
- Subject clearly invokes right to attorney

**Defense issues automatically flagged:**
1. Consent validity (People v. Zamudio)
2. Consent withdrawal ignored
3. Pre-arrest custodial questioning without Miranda
4. Possible pretext stop

---

## Production Setup (Azure Video Indexer)

1. Create an Azure Video Indexer account in your Azure Government subscription
2. Enable Managed Identity on the backend App Service / Container App
3. Assign the Video Indexer Contributor role to the Managed Identity
4. Copy `.env.example` to `.env` and fill in your values
5. Set `USE_MOCK_SERVICES=false`

```bash
# Provision Video Indexer via Azure CLI
az videoindexer account create \
  --name "lacounty-pubdef-vi" \
  --resource-group "lacounty-pubdef-rg" \
  --location westus2 \
  --sku-name Standard
```

Refer to [Azure Video Indexer documentation](https://learn.microsoft.com/en-us/azure/azure-video-indexer/) for full setup.

---

## API Reference

| Endpoint                 | Method | Description                                |
| ------------------------ | ------ | ------------------------------------------ |
| `/health`                | GET    | Health check                               |
| `/api/analyze`           | POST   | Submit video URL for analysis              |
| `/api/analysis/{job_id}` | GET    | Get full analysis result                   |
| `/api/query`             | POST   | Ask a Q&A question about analyzed evidence |
| `/api/cases`             | GET    | List all analyzed cases                    |

Interactive docs available at http://localhost:8009/docs

---

## Why Microsoft vs. Harvey.ai / FileVine

|                                  | Harvey.ai             | FileVine AI | **Microsoft Azure**           |
| -------------------------------- | --------------------- | ----------- | ----------------------------- |
| Data residency                   | SaaS (OpenAI backend) | SaaS        | Your tenant, your region      |
| CJIS Compliance                  | No                    | No          | **Yes**                       |
| FedRAMP High                     | No                    | No          | **Yes**                       |
| Video analysis                   | Limited               | Limited     | **Azure Video Indexer**       |
| Custom legal workflows           | No                    | Limited     | **Copilot Studio + Azure AI** |
| Existing County M365 integration | No                    | No          | **Native**                    |

---

## File Structure

```
demos/lacounty-pubdef-evidence-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI application
│   │   ├── config.py                    # Settings (pydantic-settings)
│   │   ├── pipeline.py                  # Video Indexer → GPT-4o pipeline
│   │   ├── models/
│   │   │   └── schemas.py               # Pydantic request/response models
│   │   └── services/
│   │       ├── video_indexer_client.py  # Azure Video Indexer REST client
│   │       ├── evidence_analyzer.py     # GPT-4o summarization + Q&A
│   │       └── mock_service.py          # Pre-processed mock data
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   └── src/
│       ├── App.tsx                      # Root app + state machine
│       ├── api/client.ts                # API calls
│       ├── types.ts                     # TypeScript types
│       └── components/
│           ├── SubmitPanel.tsx          # Case submission form
│           ├── AnalysisView.tsx         # Tabbed results view
│           ├── SummaryPanel.tsx         # Narrative + timeline + defense flags
│           ├── KeyMomentsPanel.tsx      # Timestamped event list
│           ├── TranscriptPanel.tsx      # Full scrollable transcript
│           └── QueryPanel.tsx           # GPT-4o Q&A interface
├── mock_data/
│   └── bodycam_incident_03122024.json   # Realistic demo transcript + analysis
├── docker-compose.yml
└── README.md
```
