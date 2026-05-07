# 🏛️ California State Azure AI Hackathon Accelerators

**Accelerating AI innovation for California state government — powered by the 3-agent pipeline pattern**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Azure](https://img.shields.io/badge/Azure-Ready-0078D4?style=flat&logo=microsoft-azure)](https://azure.microsoft.com)
[![CA Envision 2026](https://img.shields.io/badge/CA-Envision%202026-FDB515?style=flat)](https://innovation.ca.gov)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Overview

This repository contains **20 AI accelerators** built for California state agencies participating in the **California State Hackathon**. Each accelerator demonstrates practical AI solutions to improve public service delivery across diverse policy domains — from benefits navigation to emergency response.

**Key Features:**

- 🏗️ **3-Agent Pipeline Pattern**: QueryAgent → RouterAgent → ActionAgent architecture for reliable, governable AI
- 🎯 **Agency-Specific**: Each accelerator addresses real challenges for California state departments
- 📜 **Constitution-Driven**: All agent behavior governed by declarative policy in `constitution.md`
- 🔐 **Compliance-First**: Built to align with EO N-12-23, EO N-5-26, SB 53, and Envision 2026 strategy
- 🚀 **Standalone Projects**: Each accelerator can be developed and deployed independently
- 🛠️ **Shared Platform**: Common tech stack, governance framework, and deployment patterns

This work supports California's **Envision 2026** strategy, Executive Orders **N-12-23** (GenAI guidelines) and **N-5-26** (AI procurement), and the **Breakthrough Project** initiative for permitting modernization.

---

## 🎯 The 20 Accelerators

### Original 8 Accelerators

| #   | Accelerator                                                                      | Agency             | Description                                                           | Complexity | Key Tech                      |
| --- | -------------------------------------------------------------------------------- | ------------------ | --------------------------------------------------------------------- | ---------- | ----------------------------- |
| 001 | [BenefitsCal Navigator](accelerators/001-benefitscal-navigator/)                 | CDSS               | Natural language benefits eligibility Q&A with multi-language support | ⭐⭐⭐        | Azure AI Search, Realtime API |
| 002 | [Wildfire Response Coordinator](accelerators/002-wildfire-response-coordinator/) | CAL FIRE / Cal OES | Multi-agency wildfire incident coordination and evacuation planning   | ⭐⭐⭐⭐       | Azure Maps, MCP Tools         |
| 003 | [Medi-Cal Eligibility Agent](accelerators/003-medi-cal-eligibility/)             | DHCS               | Automated document extraction and eligibility pre-determination       | ⭐⭐⭐⭐       | Document Intelligence         |
| 004 | [Permit Streamliner](accelerators/004-permit-streamliner/)                       | OPR / HCD / DCA    | AI-powered permit intake, routing, and SLA tracking                   | ⭐⭐⭐        | Azure AI Search               |
| 005 | [GenAI Procurement Compliance](accelerators/005-genai-procurement-compliance/)   | CDT / DGS          | Vendor AI attestation review against EO N-5-26                        | ⭐⭐         | Semantic Kernel               |
| 006 | [Cross-Agency Knowledge Hub](accelerators/006-cross-agency-knowledge-hub/)       | GovOps             | Permission-aware federated search across 200+ agencies                | ⭐⭐⭐        | Hybrid Search, Entra ID       |
| 007 | [EDD Claims Assistant](accelerators/007-edd-claims-assistant/)                   | EDD                | Voice-enabled claims status and eligibility screening                 | ⭐⭐⭐        | Realtime API, WebRTC          |
| 008 | [Multilingual Emergency Chatbot](accelerators/008-multilingual-emergency-chat/)  | Cal OES            | 70+ language emergency info with SMS support                          | ⭐⭐         | Azure Translator              |

### New Accelerators — Hackathon Attendee Agencies

| #   | Accelerator                                                                                  | Agency        | Description                                                                   | Complexity | Key Tech                                       |
| --- | -------------------------------------------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------- | ---------- | ---------------------------------------------- |
| 009 | [CAISO Grid Operations Agent](accelerators/009-caiso-grid-operations-agent/)                 | CAISO         | Real-time grid intelligence, Flex Alert guidance, and energy market Q&A       | ⭐⭐⭐⭐       | Azure OpenAI, OASIS API, Event Hubs            |
| 010 | [CalPERS Retirement Navigator](accelerators/010-calpers-retirement-navigator/)               | CalPERS       | Pension formula, health plan, and retirement benefit guidance for 2M members  | ⭐⭐⭐        | Azure OpenAI, AI Search RAG                    |
| 011 | [Caltrans Project Intelligence Agent](accelerators/011-caltrans-project-intelligence-agent/) | Caltrans      | Encroachment permit guidance, HDM standards Q&A, and CEQA/NEPA intake         | ⭐⭐⭐        | Azure OpenAI, AI Search, Document Intelligence |
| 012 | [CCHCS Clinical Support Agent](accelerators/012-cchcs-clinical-support-agent/)               | CCHCS         | Clinical policy navigation and formulary lookup for correctional health staff | ⭐⭐⭐        | Azure OpenAI, HCSPP RAG                        |
| 013 | [CDI Insurance Consumer Agent](accelerators/013-cdi-insurance-consumer-agent/)               | CDI           | Consumer insurance rights, claim dispute guidance, and license verification   | ⭐⭐⭐        | Azure OpenAI, AI Search                        |
| 014 | [CDPH Public Health Agent](accelerators/014-cdph-public-health-agent/)                       | CDPH          | Disease reporting, immunization guidance, and vital statistics support        | ⭐⭐⭐        | Azure OpenAI, AI Search                        |
| 015 | [CDTFA Tax Compliance Navigator](accelerators/015-cdtfa-tax-compliance-navigator/)           | CDTFA         | Sales tax, cannabis tax, and audit guidance for California businesses         | ⭐⭐⭐        | Azure OpenAI, R&TC RAG                         |
| 016 | [DCA License Navigator](accelerators/016-dca-license-navigator/)                             | DCA           | Professional licensing guidance across 200+ license types and 37 boards       | ⭐⭐⭐        | Azure OpenAI, AI Search, BreEZe API            |
| 017 | [DGS Procurement Agent](accelerators/017-dgs-procurement-agent/)                             | DGS           | CMAS, SB/DVBE, and State Contracting Manual guidance                          | ⭐⭐⭐        | Azure OpenAI, SCM RAG                          |
| 018 | [DSH Forensic Placement Agent](accelerators/018-dsh-forensic-placement-agent/)               | DSH           | IST/NGI/LPS commitment timelines and CONREP placement guidance                | ⭐⭐⭐⭐       | Azure OpenAI, Penal Code RAG                   |
| 019 | [OTSI HHS Integration Agent](accelerators/019-otsi-hhs-integration-agent/)                   | OTSI/CHHS     | CHHS system integration guidance, API catalog, and SIMM compliance            | ⭐⭐⭐⭐       | Azure OpenAI, AI Search                        |
| 020 | [CA State Fund Workers' Comp Navigator](accelerators/020-statefund-workers-comp-navigator/)  | CA State Fund | Workers' comp claims, employer policy, and IMR/WCAB guidance                  | ⭐⭐⭐        | Azure OpenAI, Labor Code RAG                   |

Each accelerator has a full specification in `specs/` and an implementation project in `accelerators/`.

---

## 🏗️ Architecture: The 3-Agent Pipeline Pattern

All accelerators follow a consistent three-agent architecture:

```
┌──────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                (React + TypeScript + Tailwind)                   │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   QueryAgent     │  ← Intent detection
                    │   (GPT-4o)       │    Entity extraction
                    └────────┬─────────┘    PII filtering
                             │
                             ▼
                    ┌──────────────────┐
                    │   RouterAgent    │  ← Agency routing
                    │   (Semantic      │    Priority setting
                    │    Kernel)       │    Escalation triggers
                    └────────┬─────────┘
                             │
                 ┌───────────┼──────────────┐
                 ▼           ▼              ▼
          ┌──────────┐ ┌──────────┐  ┌──────────┐
          │ RAG KB   │ │ API Call │  │ Escalate │  ← Knowledge retrieval
          │ Search   │ │ (SNOW,   │  │ to Human │    Ticket creation
          │ (AI      │ │  CRM)    │  │          │    Response formatting
          │  Search) │ │          │  │          │
          └──────────┘ └──────────┘  └──────────┘
```

### Agent Responsibilities

| Agent           | Role                   | Key Capabilities                                                                          |
| --------------- | ---------------------- | ----------------------------------------------------------------------------------------- |
| **QueryAgent**  | Understands user input | Intent detection, entity extraction, PII filtering, input validation against constitution |
| **RouterAgent** | Determines action path | Agency routing, priority setting, escalation triggers, session context management         |
| **ActionAgent** | Executes the action    | Knowledge retrieval (RAG), ticket creation, API calls, response formatting, audit logging |

### Why Three Agents?

1. **Separation of Concerns** — Each agent has a single, well-defined responsibility
2. **Governability** — Easier to audit, test, and control behavior at each stage
3. **Reusability** — Router logic and action handlers can be shared across accelerators
4. **Transparency** — Clear decision trails for compliance and debugging

---

## 🧩 Platform vs. Accelerators

This repository separates **shared platform infrastructure** from **individual accelerator projects**, allowing teams to work independently while sharing a common foundation.

| Layer                 | Location                | Purpose                                                                                           |
| --------------------- | ----------------------- | ------------------------------------------------------------------------------------------------- |
| **Core Platform**     | `backend/`, `frontend/` | Reference implementation of the 3-agent pipeline (FastAPI + React)                                |
| **Shared Governance** | `shared/`               | Constitution templates, routing schemas, and cross-accelerator policies ensuring CA compliance    |
| **Accelerators**      | `accelerators/`         | Self-contained projects — each can be developed, tested, and deployed independently               |
| **Specifications**    | `specs/`                | Spec-driven definitions for each accelerator: `spec.md`, `plan.md`, `tasks.md`, `constitution.md` |
| **Workshop Labs**     | `labs/`                 | Hands-on learning curriculum (8 labs) teaching the 3-agent pattern step by step                   |
| **Infrastructure**    | `infra/`                | Reusable Bicep IaC modules for Azure deployment                                                   |

**Spec-driven development**: Every accelerator starts with a specification before any code is written. Specs live in `specs/<accelerator-id>/` and define requirements, architecture decisions, task breakdowns, and governance rules.

---

## 🛠️ Tech Stack

| Layer              | Technology                                             |
| ------------------ | ------------------------------------------------------ |
| **Backend**        | Python 3.11+ / FastAPI / Pydantic v2 / Semantic Kernel |
| **Frontend**       | React 18 / TypeScript 5 / Vite / Tailwind CSS          |
| **AI/LLM**         | Azure OpenAI (GPT-4o) + Azure AI Search (hybrid RAG)   |
| **Voice**          | Azure OpenAI Realtime API (WebRTC)                     |
| **Document AI**    | Azure Document Intelligence                            |
| **Auth**           | Azure Entra ID / MSAL                                  |
| **Infrastructure** | Docker + docker-compose / Azure Developer CLI (azd)    |
| **IaC**            | Bicep                                                  |
| **Testing**        | pytest + vitest + Playwright                           |
| **CI/CD**          | GitHub Actions                                         |
| **Governance**     | Constitution-driven, EO N-12-23 / N-5-26 compliant     |

---

## 🏁 Getting Started

### Quick Start (Mock Mode)

```bash
# 1. Open in GitHub Codespaces (recommended) or clone locally

# 2. Install dependencies
npm run setup

# 3. Start in mock mode (no Azure credentials needed)
npm start

# 4. Run smoke tests
npm run smoke-test
```

> **Mock mode** lets you develop and demo without Azure credentials. Labs 00–03 work entirely in mock mode — perfect for prototyping and testing the 3-agent pipeline locally.

### Running a Specific Accelerator

Each accelerator in `accelerators/` is a self-contained project. To work on one:

```bash
# Navigate to the accelerator
cd accelerators/001-benefitscal-navigator

# Follow its local README for setup and run instructions
```

### Viewing Specs

Specifications define each accelerator's requirements before code is written:

```bash
# Browse all specs
ls specs/

# View a specific accelerator's spec
cat specs/001-benefitscal-navigator/spec.md
```

Each spec directory contains:
- `spec.md` — Feature specification and requirements
- `plan.md` — Implementation plan and architecture decisions
- `tasks.md` — Dependency-ordered task breakdown
- `constitution.md` — Governance rules for agent behavior

### Codespaces Configuration

When running in GitHub Codespaces:

1. **Make port 8000 public** for external access:
   ```bash
   gh codespace ports visibility 8000:public -c $CODESPACE_NAME
   ```

2. **Get your Codespaces URLs** from the Ports tab, or construct them:
   - Frontend: `https://<codespace-name>-5173.app.github.dev`
   - Backend: `https://<codespace-name>-8000.app.github.dev`

3. **Update CORS configuration** in [backend/.env](backend/.env):
   ```bash
   CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","https://<your-codespace-name>-5173.app.github.dev"]
   ```

4. **Do NOT set `VITE_API_BASE_URL`** to `http://localhost:8000` — in Codespaces the browser runs outside the container and cannot reach `localhost`.

5. **Restart the backend** after updating CORS settings.

---

## 🏛️ California Governance & Compliance

This project is designed to align with California's AI governance framework:

### 📜 Executive Orders & Legislation

| Policy                   | What It Covers                                                                      | Relevant Accelerator(s)                  |
| ------------------------ | ----------------------------------------------------------------------------------- | ---------------------------------------- |
| **EO N-12-23**           | GenAI guidelines for state agencies — transparency, accountability, bias mitigation | All — codified in each `constitution.md` |
| **EO N-5-26**            | AI procurement & vendor attestation for safety, security, explainability            | #005 GenAI Procurement Compliance        |
| **SB 53**                | AI safety — risk assessment and safeguards for state AI systems                     | All — risk assessments in specs          |
| **CCPA/CPRA**            | California consumer privacy — PII handling, data minimization                       | All — PII filtering in QueryAgent        |
| **Envision 2026**        | CDT's digital transformation strategy for California government                     | All — strategic alignment                |
| **Breakthrough Project** | Governor's initiative to modernize permitting processes                             | #004 Permit Streamliner                  |

### 🔐 Constitution-Driven Governance

Every accelerator includes a `constitution.md` file that defines:

- **Scope Boundaries**: What the agent can and cannot do
- **Safety Guardrails**: Red lines for sensitive topics (legal advice, medical diagnosis, etc.)
- **Equity Requirements**: Multilingual support, accessibility, plain language
- **Audit & Transparency**: All decisions logged with reasoning chains
- **Escalation Rules**: When to route to human staff

The constitution is **executable** — it's referenced in agent prompts and enforced at runtime, not just documentation.

**Example from BenefitsCal Navigator:**

```markdown
## Scope
- ✅ Provide eligibility criteria for CalFresh, CalWORKs, Medi-Cal
- ✅ Explain application processes and required documents
- ❌ Provide legal advice or represent applicants
- ❌ Make eligibility determinations (route to county staff)
```

---

## 📚 Workshop Labs

The `labs/` directory contains an **8-lab curriculum** that teaches the 3-agent pipeline pattern step by step:

| Lab | Topic                    | Azure Required? |
| --- | ------------------------ | --------------- |
| 00  | Environment Setup        | No              |
| 01  | Understanding Agents     | No              |
| 02  | Building a QueryAgent    | No              |
| 03  | Adding a RouterAgent     | No              |
| 04  | Connecting Azure OpenAI  | Yes             |
| 05  | RAG with Azure AI Search | Yes             |
| 06  | Voice with Realtime API  | Yes             |
| 07  | End-to-End Accelerator   | Yes             |

Labs 00–03 run entirely in **mock mode** — no Azure credentials needed. Labs 04+ require an Azure subscription with the appropriate services provisioned.

See the [Coach Guide](coach-guide/) for facilitation tips and workshop logistics.

---

## 📂 Project Structure

```
ca-hackathon/
├── specs/                          # Accelerator specifications
│   ├── 001-benefitscal-navigator/
│   │   ├── spec.md                 # Feature specification
│   │   ├── plan.md                 # Implementation plan
│   │   ├── tasks.md                # Task breakdown
│   │   └── constitution.md         # Governance rules
│   ├── 002-wildfire-coordinator/
│   └── ...
├── accelerators/                   # Implemented accelerators
│   ├── 001-benefitscal-navigator/
│   ├── 002-wildfire-response-coordinator/
│   └── ...
├── shared/                         # Shared platform code
│   ├── constitution.md             # Root governance document
│   ├── platform/                   # Core 3-agent engine
│   ├── ui-components/              # React component library
│   ├── templates/                  # Spec & constitution templates
│   └── infra/                      # Reusable Bicep modules
├── labs/                           # 8-lab workshop curriculum
│   ├── 00-setup/
│   ├── 01-understanding-agents/
│   └── ...
├── backend/                        # FastAPI backend (reference impl)
│   ├── app/
│   │   ├── agents/                 # QueryAgent, RouterAgent, ActionAgent
│   │   ├── integrations/           # Azure OpenAI, AI Search, etc.
│   │   └── main.py
│   └── tests/
├── frontend/                       # React frontend (reference impl)
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.tsx
│   └── tests/
├── infra/                          # Bicep IaC for Azure deployment
├── docs/                           # Architecture diagrams, guides
└── coach-guide/                    # Workshop facilitation guide
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend && python -m pytest -x

# Frontend tests
cd frontend && npm run test

# Lint Python code
ruff check .

# E2E tests
npm run test:e2e

# Smoke test (validates 3-agent pipeline in mock mode)
npm run smoke-test
```

---

## 🚀 Deployment

Each accelerator can be deployed independently using Azure Developer CLI:

```bash
# Login to Azure
azd auth login

# Provision infrastructure + deploy code
azd up

# Update existing deployment
azd deploy
```

**What gets deployed:**
- Azure Container Apps (backend API)
- Azure Static Web Apps (frontend)
- Azure OpenAI (GPT-4o)
- Azure AI Search (knowledge base)
- Azure Cosmos DB (session storage)
- Azure Application Insights (monitoring)
- Azure Key Vault (secrets)

**Cost estimate**: ~$50–200/month per accelerator depending on usage (development tier)

---

## 🤝 Contributing

We welcome contributions from California state agency staff, vendors, and civic tech partners!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-accelerator`)
3. Follow the spec-driven workflow:
   - Write `spec.md` for your accelerator
   - Generate `plan.md` and `tasks.md` using the spec-kit
   - Implement following the plan
4. Run tests and linting
5. Submit a pull request

**Contribution Guidelines:**
- All code must align with EO N-12-23 principles
- Include a `constitution.md` for any new accelerator
- Add tests for new features
- Update documentation
- Use conventional commits

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

**Note**: This is open-source reference architecture. Agencies are responsible for compliance with state procurement, security, and privacy requirements when deploying to production.


---

**🏛️ Built for California. By Californians. For all Californians.**
