# Project Context

- **Owner:** msftsean
- **Project:** California State AI Hackathon Accelerators — 8 AI accelerators for California state government agencies
- **Stack:** Python 3.11+ / FastAPI 0.109+, TypeScript 5 / React 18, Azure OpenAI, Azure AI Search, Semantic Kernel, Azure Document Intelligence, Pydantic v2.5+
- **Architecture:** Three-agent pipeline (QueryAgent → RouterAgent → ActionAgent) deployed across 8 accelerators for CDSS, CAL FIRE, DHCS, OPR, CDT, GovOps, EDD, Cal OES
- **Governance:** EO N-12-23, EO N-5-26, SB 53, CCPA/CPRA compliance
- **Created:** 2026-03-13

## Learnings

- **2026-04-03 (Morpheus):** Phase B task generation for all 8 accelerators (commit d44b89c) provided actionable, dependency-ordered tasks that enabled Tank's 4-wave concurrent implementation to reach 100% test pass rate (503 tests). Task structure enforced by speckit-tasks.agent aligned teams on acceptance criteria, enabling parallelization. Constitution governance across all 8 accelerators proved effective — zero agency boundary conflicts, consistent CCPA/CPRA consent flows, EO N-12-23 compliance checks, emergency escalation rules. Key learning: spec-driven development from specs/ → tasks.md → concurrent implementation reduced rework and eliminated regressions.

- **2026-04-02 (Morpheus):** Rebranded CLAUDE.md and .github/copilot-instructions.md from 47 Doors university context to California State AI Hackathon Accelerators. Updated all project references, added 8 accelerator IDs with agency mappings, added CA governance context (EO N-12-23, N-5-26, SB 53, CCPA/CPRA), clarified architecture pattern and project structure for CA state deployments.

- **2026-04-03 (Morpheus):** Created deployment infrastructure for all 8 accelerators: docker-compose.accelerators.yml enables local multi-accelerator development with clean port mapping (8001-8008 backend, 3001-3008 frontend); scripts/azd-deploy.sh provides selective deployment to Azure Container Apps (all/platform/specific accelerator); documentation updates in CLAUDE.md and copilot-instructions.md give developers clear deployment paths. Key learning: Accelerator 005 (GenAI Procurement Compliance) is backend-only — deployment tooling must handle mixed frontend/backend-only patterns across accelerators.

## Work Log

### 2026-03-13T18:46:00Z — Azure-First Spec Update (Morpheus)
Updated `specs/002-voice-interaction/spec.md` to prioritize Azure Container Apps as primary deployment target.

**Changes:**
- MVP scope: Added "Azure Container Apps deployment"
- VFR-026–029: Deployment requirements (Azure primary, local dev secondary, parity)
- Updated assumptions and dependencies to reflect Azure-first strategy
- Mock mode clarified as dev/test tool, not demo default

**Commit:** `71a91d6`

**Cross-agent impact:** Tank's Phase 1 deployment config must align with these requirements.

### 2026-04-03 — Phase D Deployment Orchestration (Morpheus, Tank, Switch)

**Orchestration session: 2026-04-03T16:38:41Z**

**Context:** Tank delivered infrastructure loop pattern + 8 accelerator service definitions. Switch delivered 22 containerized Dockerfiles. Morpheus orchestrated tooling and documentation.

**Morpheus's Deliverables:**

1. **docker-compose.accelerators.yml** (15 services)
   - Backend services (8): accel-001 through accel-008, ports 8001-8008 mapped to internal 8000
   - Frontend services (7): accel-001-fe through accel-008-fe, ports 3001-3008 mapped to internal 80
   - Shared network: `cahack-network` for cross-service communication
   - Environment: USE_MOCK_SERVICES=true (default), each backend gets accelerator-specific env vars
   - Health checks: `curl -f http://localhost:8000/health` for backends (30s timeout, 5s interval)
   - Dependency gating: Frontend depends_on backend with `service_healthy` condition
   - Resilience: `restart: unless-stopped` for all services

2. **scripts/azd-deploy.sh** (deployment automation)
   - `./azd-deploy.sh all` — azd deploy (platform + all accelerators via acceleratorIds parameter)
   - `./azd-deploy.sh platform` — azd deploy platform only
   - `./azd-deploy.sh 001-008` — azd deploy specific accelerator(s)
   - Input validation: Case pattern for `00[1-8]` IDs, fallback to `all` if unrecognized
   - Mixed pattern support: Script knows accelerator 005 has no frontend (no error on deploy)

3. **CLAUDE.md — Azure Deployment section added**
   - Full deployment: `azd up` (provision + deploy all resources)
   - Selective deployment: `azd up --parameters acceleratorIds='["001","002","003"]'`
   - Local development: `docker-compose -f docker-compose.accelerators.yml up`
   - Port mapping table: Clear reference for all 8 accelerators (backend 800X, frontend 300X)
   - Environment variable guide for mock mode vs. Azure credentials
   - Deployment examples (first-time, selective update, local dev)

4. **.github/copilot-instructions.md — Deployment Commands reference added**
   - Quick reference section for AI agent consumption
   - Deployment command patterns
   - Environment variable setup instructions

**Cross-Agent Dependencies:**
- **Consumed Tank's infrastructure:** azure.yaml service names (accel-001 → accel-008-fe), acceleratorIds parameter pattern
- **Consumed Switch's Dockerfiles:** Health check endpoints (/health), port assumptions (8000 internal), security patterns

**Design Decisions:**
- Port scheme: 8001-8008 for backend (matches accelerator IDs), 3001-3008 for frontend (visual consistency)
- Mock mode default: Enables local development without Azure credentials, seamless transition to production
- Health check dependency: Frontend startup blocked until backend passes health check (prevents cascading failures)
- Script design: Case pattern ensures invalid IDs fail safely with fallback to `all` (defensive programming)

**Key Learning:** Multi-accelerator orchestration requires THREE integration points: (1) docker-compose for local dev, (2) azd script for selective cloud deployment, (3) documentation for operator clarity. Missing any one creates friction for developers and operators.

**Result:** Developers can now:
- Local dev: `docker-compose up` (all 8 accelerators in mock mode, ~30s startup)
- Azure deployment: `./azd-deploy.sh 001` (single accelerator), `./azd-deploy.sh all` (full platform)
- Documentation: Clear port mapping, environment setup, deployment patterns

**Decisions merged:** `morpheus-deploy-tooling.md` → `.squad/decisions.md`

**Next Phase:** CI/CD workflows for ACR image builds + GitHub Actions for `azd deploy` triggers
