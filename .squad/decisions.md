# Squad Decisions

## Active Decisions

### Model Selection Directive
**Timestamp:** 2026-03-13T13-09-59  
**Authority:** User (msftsean via Copilot)  
**Decision:** 
- Code-writing agents (Tank, Switch, Mouse, Neo): use `claude-sonnet-4.6`
- Non-code agents (Scribe, documentation, evals, Morpheus when not reviewing): use `claude-haiku-4.6`

**Rationale:** Optimize for cost vs. quality based on task type. Code work requires full Sonnet capability; administrative/documentation work can use faster Haiku model.

### Azure Resources Ready for Live Testing
**Timestamp:** 2026-03-13T17:34  
**Authority:** User (msftsean via Copilot)  
**Decision:** Azure resources provisioned and ready for live voice testing.
- **Resource Group:** `rg-47doors-voice` (eastus2)
- **Resource Name:** `oai-47doors-voice`
- **Deployments:** `gpt-4o` + `gpt-4o-realtime`

**Rationale:** User directive to plan for live Azure testing, not just mock mode. Infrastructure is in place and ready for Phase 3+ endpoint validation.

### Azure-First Deployment Strategy
**Timestamp:** 2026-03-13T18:46:00Z  
**Authority:** User (msftsean via Morpheus)  
**Decision:** Spec update to make Azure Container Apps the primary deployment target.

- **VFR-026**: Azure Container Apps via `azd up` is PRIMARY
- **VFR-027**: Local dev as secondary path via `uvicorn`
- **VFR-028**: No code changes needed between deployments
- **VFR-029**: Health checks work identically in both environments

**Rationale:** User directive — production and demo environments should run on Azure, not locally. Mock mode repositioned as development/testing tool.

### Phase 1 Setup — Voice Config, Env, Bicep
**Timestamp:** 2026-03-14  
**Authority:** Tank (Backend Dev)  
**Decision:** Voice configuration strategy for `backend/app/core/config.py`

**Key Decisions:**
- Used Pydantic v2 `model_validator(mode="after")` for voice validation (consistent with codebase v2.5+ usage)
- Voice config fields:
  - `voice_enabled` (default `True`): Kill switch, disabled when `azure_openai_realtime_deployment == ""` AND `mock_mode == False`
  - `azure_openai_realtime_deployment` (default `""`): Empty value auto-disables voice in prod mode
  - `azure_openai_realtime_api_version` (default `"2025-04-01-preview"`): Realtime endpoint version
  - `realtime_voice` (default `"alloy"`): Azure voice selection
  - `realtime_vad_threshold_ms` (default `500`): Voice activity detection threshold
  - `max_voice_session_duration` (default `600`): Session timeout (10 min)

- `.env.example`: Added `AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-realtime-preview` as stub
- `infra/main.bicep`: Added `openAiRealtimeDeployment` resource with:
  - `dependsOn: [openAiDeployment]` to serialize operations (avoid rate-limit throttling)
  - Capacity: 1 TPM-unit (minimal, scale manually as needed)
  - Output: `AZURE_OPENAI_REALTIME_DEPLOYMENT` for azd auto-wiring

**Rationale:** Phase 1 unblocks deployment configuration. Mock mode enables local development; validator logic ensures voice is disabled in production without credentials.

### Voice Data Model Architecture
**Timestamp:** 2026-03-13  
**Authority:** Tank (Backend Dev)  
**Decision:** Additive-only model strategy for voice entities

**Key Decisions:**
1. **File Organization**
   - New voice models in `backend/app/models/voice_schemas.py` and `backend/app/models/voice_enums.py` (not appended to existing files)
   - Reduces merge conflicts with parallel feature work
   - Keeps existing `schemas.py` lean (430+ lines already)

2. **Data Model Integration**
   - `VoiceMessage.input_modality: Literal["voice"]` acts as discriminator (text/voice coexist in shared history)
   - Cheaper than union types or separate history stores
   - Aligns with spec VFR-010 (shared transcript) + Constitution Principle IV (session continuity)
   - `VoiceState.transcript` is append-only with `max_length=100` (matches `Session.conversation_history` cap pattern)

3. **Auth & Persistence**
   - No new auth model — reuse `Session.session_id: UUID` as voice↔text join key
   - Zero schema migration required; UUID index already exists
   - Trivially maps to future persistence layer (Cosmos DB): `WHERE session_id = ?`

4. **Tool Call Models**
   - `ToolCallRequest` / `ToolCallResponse` marked explicitly transient ("never persisted" in docstring)
   - Prevents PII leaks from tool arguments/results into audit logs before PII-filter pass
   - Aligns with Constitution Principle I (pipeline integrity)

**Rationale:** Additive strategy reduces friction with parallel work. Discriminator pattern is simpler and aligns with existing session model. Explicit transience markers document the PII-safety constraint for future implementers.

### Azure Static Web Apps Auth for Runbook Site
**Timestamp:** 2026-03-14  
**Authority:** Switch (Frontend Dev)  
**Decision:** Use Azure Static Web Apps (SWA) with Azure AD (Microsoft Entra ID) authentication for docs runbook site

**Key Decisions:**
- **Identity provider:** Azure AD only (Microsoft login)
- **Auth enforcement:** All routes require `authenticated` role; 401 auto-redirects to `/.auth/login/aad`
- **User display:** `/.auth/me` endpoint surfaced in nav bar; degrades gracefully on local dev
- **Blocked providers:** GitHub, Twitter (return 404)

**Affected Files:**
- `docs/staticwebapp.config.json` — SWA route rules and auth config
- `docs/index.html` — `.nav-auth` bar + `/.auth/me` JS
- `.github/workflows/deploy-docs-swa.yml` — CI/CD deployment
- `docs/AZURE_SWA_SETUP.md` — Operator setup guide

**Rationale:** EDU/Microsoft audience context. SWA built-in auth requires no app-level middleware. Restricts runbook access (internal tooling, demo sequences) to authenticated Microsoft accounts. Local dev parity via graceful `/.auth/me` fallback.

### Azure OpenAI Managed Identity Authentication
**Timestamp:** 2026-03-13T23:00Z  
**Authority:** Anvil (Production Fix)  
**Decision:** Use system-assigned managed identity for Azure OpenAI authentication instead of API keys

**Key Decisions:**
- **Backend Authentication:**
  - `AzureRealtimeService` uses `DefaultAzureCredential` from `azure-identity` for token-based auth
  - API key support retained as fallback for local development (optional parameter)
  - Token auto-refresh before expiration (checks `expires_on` timestamp)
  
- **Infrastructure Changes (`infra/main.bicep`):**
  - Set `disableLocalAuth: true` on Azure OpenAI resource (enforce managed identity)
  - Removed `azure-openai-api-key` secret from backend container app
  - Added `identity: { type: 'SystemAssigned' }` to backend container app
  - Created role assignment: `Cognitive Services OpenAI User` role for backend managed identity
  - Removed `AZURE_OPENAI_API_KEY` environment variable injection

- **Error Handling:**
  - Status-code-specific error messages (401: auth failed, 403: missing role, 404: deployment not found, 5xx: service unavailable)
  - Network errors surfaced with endpoint URL for debugging
  - All errors wrapped in `VoiceUnavailableError` with detailed context

- **Configuration:**
  - `azure_openai_api_key` now optional in `config.py` (description updated)
  - `dependencies.py` passes `api_key=None` when unset, triggering managed identity path
  - Mock mode unaffected (no Azure credentials required)

**Affected Files:**
- `backend/app/services/azure/realtime.py` — Token-based auth with credential refresh
- `backend/app/core/config.py` — Made API key optional
- `backend/app/core/dependencies.py` — Pass None for API key when unset
- `infra/main.bicep` — System-assigned identity + RBAC role assignment

**Rationale:** Deployed frontend was hitting 503 errors because Azure OpenAI had `disableLocalAuth: true` (API key auth rejected with 403). Managed identity is Azure best practice for container apps — no secrets in config, auto-rotated tokens, and RBAC-controlled access. API key fallback preserves local dev workflow without Azure credentials.

### Realtime API Authentication Fix — RESOLVED
**Timestamp:** 2026-03-14  
**Authority:** Anvil (Production Fix)  
**Status:** ✅ Complete  
**Decision:** Re-enabled API key auth + implemented async DefaultAzureCredential with fallback

**Problem (Tank's Initial Diagnosis):**
- Frontend getting 503 when calling `POST /api/realtime/session`
- Root cause: Wrong Azure OpenAI Realtime API endpoint URL → 404 (fixed by Tank)
- Secondary issue: Azure OpenAI resource has `disableLocalAuth: true` → 403 (blocking token acquisition)

**Anvil's Solution:**

1. **Bicep (infra/main.bicep)**
   - Set `disableLocalAuth: false` on Azure OpenAI resource to re-enable API key authentication
   - Verified property takes effect with `azd provision`

2. **Backend Service (backend/app/services/azure/realtime.py)**
   - Integrated `DefaultAzureCredential` from `azure-identity` library
   - Implemented async-aware credential refresh (checks `expires_on` before use)
   - API key remains as fallback for local development (optional parameter)
   - Enhanced error handling with status-code-specific messages:
     - 401: Authentication failed
     - 403: Missing Cognitive Services OpenAI User role
     - 404: Deployment not found
     - 5xx: Service unavailable

3. **Configuration (backend/app/core/config.py)**
   - Made `azure_openai_api_key` optional in Settings
   - `dependencies.py` passes `api_key=None` when unset, triggering managed identity path

**Result:**
- ✅ 503 errors eliminated
- ✅ Realtime session endpoint fully operational
- ✅ 76 voice tests passing
- ✅ Commit: `c44b389` ("feat(voice): Re-enable API key auth, add async DefaultAzureCredential with fallback")
- ✅ Pushed to main

**Affected Files:**
- `infra/main.bicep` — Re-enabled API key auth
- `backend/app/services/azure/realtime.py` — Added DefaultAzureCredential + fallback
- `backend/app/core/config.py` — Made API key optional
- `backend/app/core/dependencies.py` — Pass None when unset
- `tests/voice/*.py` — 76 tests green

### Voice Transcript Session Config
**Timestamp:** 2026-03-15  
**Authority:** Tank (Backend Dev)  
**Status:** ✅ Applied

**Problem:** Voice transcripts never appeared in the UI despite deployment. Two configuration gaps in Realtime API session config prevented transcription.

**Decision:**

1. **Enable `input_audio_transcription` in session config**
   - Added `"input_audio_transcription": {"model": "whisper-1"}` to the session config sent to Azure OpenAI's `/client_secrets` endpoint
   - Without this field, Azure's Realtime API does not emit `conversation.item.input_audio_transcription.completed` events — user speech is never converted to text

2. **Default instructions to `VOICE_SYSTEM_PROMPT`**
   - Changed `create_session()` to always include instructions, defaulting to `VOICE_SYSTEM_PROMPT` when not explicitly provided
   - The prompt was defined at module top but never wired in; without it, voice model operates with no PII redaction rules, ticket conventions, or conversational guidance

3. **Mock service parity**
   - Mirrored both changes in `MockRealtimeService` for API contract consistency
   - Mock imports `VOICE_SYSTEM_PROMPT` from Azure module (single source of truth)

**Affected Files:**
- `backend/app/services/azure/realtime.py` — Session config + instructions default
- `backend/app/services/mock/realtime.py` — Matching config for test parity

**Verification:** 76 voice tests passing. Import validation clean for both services.

### Frontend session.update for Transcription Enablement
**Timestamp:** 2026-03-15  
**Authority:** Switch (Frontend Dev)  
**Status:** ✅ Applied

**Problem:** Azure OpenAI Realtime API requires `input_audio_transcription` to be explicitly enabled. Without it, API produces responses but never emits transcription events.

**Decision:** Send a `session.update` event via WebRTC data channel (`dc.onopen`) immediately after it opens, enabling `input_audio_transcription` with `whisper-1`.

**Belt-and-Suspenders Approach:**
- **Backend (Tank):** Includes `input_audio_transcription` in initial session config
- **Frontend (Switch):** Sends `session.update` through data channel as safety net
- Both paths are idempotent — redundant messages cause no errors

**Side Effect:** Moved `dispatch({ type: 'LISTENING' })` from `pc.onconnectionstatechange` into `dc.onopen`. Data channel being open is the actual prerequisite for event exchange — semantically more correct.

**Affected Files:**
- `frontend/src/hooks/useVoice.ts` — Added `dc.onopen` handler

**Verification:** TypeScript compiles cleanly. Code review passed.

### California State Government Rebranding
**Timestamp:** 2026-02-02  
**Authority:** Tank (Backend Dev)  
**Status:** ✅ Implemented

**Context:** Project rebranded from 47 Doors university student support system to California state government services across 12 agencies (CDSS, DHCS, HCD, CDT, EDD, CAL FIRE, Cal OES, DMV, DGS, OPR, DCA, GovOps).

**Key Decisions:**
- Constitution v1.0 → v2.0.0: FERPA → CCPA/CPRA, university → constituent/resident terminology
- Department routing: 6 university departments → 12 CA state agencies
- Sample queries: 100+ university queries → 50 CA queries with multilingual support (Spanish)
- Timezone: America/New_York → America/Los_Angeles
- Compliance: Added EO N-12-23, EO N-5-26, SB 53, CCPA/CPRA, Envision 2026

**Affected Files:**
- `shared/constitution.md` (1.0 → 2.0.0, 13KB)
- `shared/department_routing.json` (1.0 → 2.0, 13KB)
- `shared/sample_queries.json` (1.0 → 2.0, 17KB, 50 queries)

**Rationale:** Complete context rewrite necessary — life-safety requirements (emergency services), incompatible compliance frameworks (FERPA vs. CCPA/CPRA), mandated multilingual access, and 40M-resident scale make gradual migration infeasible. Quality over quantity: 50 realistic queries better serve state services than 100 academic queries.

### CA Hackathon Infrastructure Loop Pattern
**Timestamp:** 2026-04-02  
**Authority:** Tank (Backend Dev)  
**Status:** ✅ Implemented

**Context:** Deploying 8 independent accelerators with optional frontends and shared Azure services requires cost-optimized, declarative architecture.

**Key Decisions:**
1. **Loop-based Bicep resources** — Avoids manual duplication of 15 Container App definitions
2. **Selective deployment** — `acceleratorIds` parameter controls which accelerators deploy
3. **Scale-to-zero** — minReplicas: 0 for accelerators, minReplicas: 1 for platform (cost optimization)
4. **Conditional frontends** — `accelWithFrontends` filters out accelerator 005 (backend-only)
5. **Automated RBAC** — Loop-based role assignments grant managed identity access

**Implications:**
- **For Switch:** Each accelerator gets isolated `BACKEND_URL` env var — no shared state
- **For deployment:** Selective targeting via `azd up --parameters acceleratorIds='["001","002","003"]'`
- **For scaling:** Add new entry to `acceleratorConfig` array for future accelerators (009+)

**Affected Files:**
- `infra/main.bicep` (rebranded, loop pattern, Translator + Document Intelligence)
- `infra/main.parameters.json` (rebranded environment names)
- `azure.yaml` (8 backend + 7 frontend services, azd-service-name tags)

**Risks Mitigated:**
- Loop index coupling: Keep `acceleratorIds` array sorted to prevent frontend BACKEND_URL misrouting
- Cold start: minReplicas: 0 acceptable for demo/dev; production may need minReplicas: 1

### Standardized Docker Configuration for All Accelerators
**Timestamp:** 2026-04-02  
**Authority:** Switch (Frontend Dev)  
**Status:** ✅ Implemented

**Context:** 8 accelerators needed consistent containerization with security hardening and multi-stage optimization.

**Key Decisions:**
1. **Backend Dockerfiles (8):** Python 3.12-slim, non-root `appuser`, `/health` health check, minified
2. **Frontend Dockerfiles (7):** Multi-stage (Node 20 builder → nginx alpine runtime), Vite build, `BACKEND_URL` envsubst
3. **Nginx configs (7):** SPA routing, reverse proxy, security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection), gzip, 1y asset caching, WebSocket support
4. **Accelerator 005 exception:** Backend-only (GenAI Procurement Compliance) — no frontend service

**Files Created (22 total):**
```
accelerators/00[1-8]/backend/Dockerfile (8)
accelerators/00[1-4,6-8]/frontend/Dockerfile (7)
accelerators/00[1-4,6-8]/frontend/nginx.conf (7)
```

**Rationale:** Consistency enables shared CI/CD, unified maintenance, portability across Docker/K8s/ACA. Non-root users and minimal base images improve security posture. Health checks enable K8s/ACA readiness probes.

**Key Difference from Core Platform:** Accelerators use `/health` endpoint; core platform uses `/api/health` for distinct scope.

### Multi-Accelerator Deployment Tooling
**Timestamp:** 2026-04-03  
**Authority:** Morpheus (Lead)  
**Status:** ✅ Implemented

**Context:** Multi-accelerator deployments require orchestration tooling, clear local development patterns, and comprehensive documentation.

**Key Decisions:**
1. **docker-compose.accelerators.yml:** 15 services (8 backend, 7 frontend), ports 8001-8008 → 8000 / 3001-3008 → 80, mock mode default, health checks with dependency gating
2. **scripts/azd-deploy.sh:** Selective deployment helper (all, platform, 001-008 IDs) with mixed patterns (skip 005 frontend)
3. **Documentation:** Enhanced `CLAUDE.md` with Azure deployment section + `copilot-instructions.md` with deployment reference

**Affected Files:**
- **Created:** `docker-compose.accelerators.yml`, `scripts/azd-deploy.sh`
- **Updated:** `CLAUDE.md` (Azure Deployment section), `.github/copilot-instructions.md` (Deployment Commands reference)

**Rationale:** Single command spins up all accelerators locally (`docker-compose up`). Selective deployment supports production updates without full redeployment. Predictable port scheme (800X/300X) maps to accelerator IDs for operator convenience.

**Implementation Notes:**
- Health check: `curl -f http://localhost:8000/health`
- Frontend dependency gate: `depends_on: { <backend>: { condition: service_healthy } }`
- All services: `restart: unless-stopped` for resilience

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
