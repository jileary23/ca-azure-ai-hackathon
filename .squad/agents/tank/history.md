# Project Context

- **Owner:** msftsean
- **Project:** 47 Doors — Universal Front Door Support Agent for university student support
- **Stack:** Python 3.11+ / FastAPI 0.109+, TypeScript 5 / React 18, Azure OpenAI, Azure AI Search, Pydantic v2.5+
- **Architecture:** Three-agent pipeline (QueryAgent → RouterAgent → ActionAgent) with voice interaction via Azure OpenAI GPT-4o Realtime API / WebRTC
- **Created:** 2026-03-13

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

### 2026-03-15 — Phone Call-In Feature (ACS Call Automation)

**Architecture decisions**

- ACS Call Automation bridges inbound PSTN calls to Azure OpenAI Realtime API via WebSocket media streaming (`MediaStreamingOptions`). Audio flows: PSTN caller → ACS → WebSocket → Azure OpenAI Realtime. Backend is never in the audio path — same pattern as browser WebRTC.
- Reused the same `gpt-4o-realtime-preview` deployment and 4-tool pipeline as browser voice. PHONE_SYSTEM_PROMPT is phone-specific (terse, no markdown, no scrolling back) but same agent identity.
- `PhoneServiceInterface` added to `backend/app/services/interfaces.py` following same ABC pattern as `RealtimeServiceInterface`. `AzurePhoneService` uses lazy-init `CallAutomationClient` with async double-checked locking — same pattern as `AzureRealtimeService`.
- Mock service (`MockPhoneService`) uses SYNCHRONOUS methods (not async). This is intentional — the service tests call it without `await`. The API layer uses `_call()` helper (`inspect.isawaitable`) to handle both sync mocks and async production services. This is the correct pattern for Pydantic-v2 codebases with mixed sync/async test coverage.
- ACS webhook events use TWO different event type names for subscription validation: `Microsoft.EventGrid.SubscriptionValidationEvent` AND `Microsoft.EventGrid.SubscriptionValidated`. Both must be handled.
- Event Grid delivers callbacks as JSON arrays. Call Automation callbacks use flat dicts with `event_type` and `call_connection_id` as direct top-level keys (not wrapped in `data`). The phone API normalizes both formats.
- ACS `listKeys().primaryConnectionString` provides the connection string for the `CallAutomationClient`. Managed identity is the preferred production auth path.

**Pydantic v2 gotcha — multiple model validators**

- Pydantic v2 only supports ONE `@model_validator(mode="after")` per class. Defining a second one with a different method name OVERRIDES the first silently (with a warning). Fix: combine all after-validators into a single method (`_auto_disable_features`). This affected the voice+phone auto-disable logic in `config.py`.

**Key file paths**

- `backend/app/services/azure/phone.py` — ACS Call Automation production service
- `backend/app/services/mock/phone.py` — Synchronous mock for test isolation
- `backend/app/api/phone.py` — `/api/phone/incoming` (Event Grid) + `/api/phone/callbacks` (Call Automation) + `/api/phone/health`
- `backend/app/models/phone_schemas.py` — `IncomingCallEvent`, `CallEventRequest`, `CallState`, `PhoneHealthResponse`, `EventGridValidationEvent`
- `infra/main.bicep` — ACS resource (always provisioned, not conditional), ACS connection string secret, Contributor role assignment for backend managed identity, `AZURE_ACS_ENDPOINT` env var + output
- `backend/app/core/config.py` — `phone_enabled`, `azure_acs_endpoint`, `azure_acs_connection_string`, `acs_phone_number`, `max_call_duration`

**New SDK dependency**

- Added `azure-communication-callautomation>=1.4.0` to both `requirements.txt` and `pyproject.toml`



### 2026-03-13 — Voice Interaction Phase 0/1 Research & Data Model

**Architecture decisions**

- WebRTC transports audio direct browser → Azure; backend is never in the audio path (no audio storage, no codec pipeline).
- Ephemeral token endpoint `POST /api/realtime/session` issues ≤60 s TTL credentials; Azure API key stays server-side only.
- Tool calls flow over a dedicated WS relay `/api/realtime/ws/{session_id}`; voice pipeline MUST route through the same QueryAgent → RouterAgent → ActionAgent chain (Constitution I).
- Three-layer PII filter: pre-tool, post-tool, pre-speech (Constitution III).
- Mock mode: full `RealtimeService` mock implementing `RealtimeServiceInterface` — activated by existing `settings.use_mock_services`.
- Six-state UI machine: idle → connecting → listening → processing → speaking → idle (+ error from connecting/listening/processing).
- Voice and text share the same `session_id` UUID; voice transcript entries appended with `input_modality = "voice"` discriminator.
- `eastus2` primary region — only region with `gpt-4o-realtime-preview` availability matching existing infra region.

**Key file paths**

- `backend/app/models/schemas.py` — Pydantic v2 model patterns; `@field_validator` + `@classmethod`; `Optional[T]` with `default=None`
- `backend/app/models/enums.py` — `str, Enum` pattern for all enumerations
- `backend/app/services/interfaces.py` — ABC interface pattern for all service integrations (voice service will follow same structure)
- `backend/app/core/config.py` — `mock_mode` / `use_mock_services` pattern; `SettingsConfigDict` with `.env` loading
- `specs/002-voice-interaction/research.md` — Phase 0 decision log (10 decisions)
- `specs/002-voice-interaction/data-model.md` — Phase 1 entity definitions (7 backend models, 3 frontend types)

**Patterns to replicate for Phase 1 implementation**

- New voice models go in `backend/app/models/voice_schemas.py` and `backend/app/models/voice_enums.py`
- Service interface goes in `backend/app/services/interfaces.py` (extend existing file, same ABC pattern)
- Config additions go in `backend/app/core/config.py` under a new `# Voice / Realtime Settings` section
- Frontend types go in `frontend/src/types/voice.ts`

### 2026-03-14 — Phase 1 Setup (T001, T002, T003)

**Config changes (T001)**

- Added 6 voice fields to `Settings` in `backend/app/core/config.py` under a `# Voice / Realtime API Settings` section.
- Used `model_validator(mode="after")` (Pydantic v2) to auto-set `voice_enabled=False` when `azure_openai_realtime_deployment` is empty AND `mock_mode=False`. Validator confirmed working: mock_mode=True keeps voice_enabled=True, mock_mode=False with empty deployment flips it to False.
- `max_voice_session_duration` added (600 s default) as requested in the task brief; tasks.md did not list it but the spec and user instructions both required it.

**Env stubs (T002)**

- Appended 6 voice vars to `backend/.env.example` with a `# Voice / Realtime API Configuration` comment block.
- Used `gpt-4o-realtime-preview` as the deployment stub value (matches tasks.md; user task brief used `gpt-4o-realtime` — tasks.md value preferred as canonical).

**Bicep (T003)**

- Added `openAiRealtimeDeployment` resource inside the Azure OpenAI resource block in `infra/main.bicep`, model `gpt-4o-realtime-preview`, version `2025-04-01`, sku Standard, capacity 1.
- Added `dependsOn: [openAiDeployment]` to sequence deployments and avoid throttle conflicts during provisioning.
- Added output `AZURE_OPENAI_REALTIME_DEPLOYMENT` so azd wires the deployment name into app settings automatically.

### 2026-03-14 — Live Azure Deployment (azd up)

**Deployment verified and documented**

- `azd up` completed successfully. All services running live on Azure (MOCK_MODE=false).
- **Container App URL**: `https://frontdoor-6wfum6gndxawy-backend.blackflower-446b9850.eastus2.azurecontainerapps.io`
- **Resource Group**: `rg-vvoice`
- **Azure OpenAI Endpoint**: `https://frontdoor-6wfum6gndxawy-openai.openai.azure.com/`
- **OpenAI Deployments**: `gpt-4o` (text) + `gpt-4o-realtime-preview` (voice/WebRTC)
- **Cosmos DB**: `https://frontdoor-zfyhb6f72odyg-cosmos.documents.azure.com:443/`
- **AI Search**: `https://frontdoor-6wfum6gndxawy-search.search.windows.net`
- **Container Registry**: `frontdoor6wfum6gndxawyacr.azurecr.io`
- **Region**: `eastus2`
- **Subscription**: `ME-MngEnvMCAP262307-segayle-1`
- Health checks verified: `/api/health` → LLM connecting (ticketing, knowledge_base, session_store up); `/api/realtime/health` → realtime_available: true, mock_mode: false, voice_enabled: true
- Updated DEMO_RUNBOOK.md and docs/index.html: replaced all placeholder `${AZURE_CONTAINERAPP_URL}` and old resource group/subscription references with live values. Runbook is now Azure-first throughout.

### 2026-03-14 — Frontend Container App Deployment

**Architecture decisions**

- Frontend deployed as a separate Container App alongside the backend, both in the same Container App Environment.
- nginx reverse-proxies `/api/` requests to the backend, making all API calls same-origin from the browser's perspective — eliminates CORS issues entirely.
- `BACKEND_URL` is injected via env var and resolved at container startup using `envsubst` (only `${BACKEND_URL}` is substituted; nginx variables like `$host`, `$uri` are preserved).
- Dockerfile default `BACKEND_URL=http://backend:8000` preserves docker-compose backward compatibility.
- Added WebSocket upgrade headers (`Upgrade`, `Connection`) and long read timeout (86400s) to nginx `/api/` location for voice relay WebSocket support.
- Frontend Container App: 0.25 vCPU, 0.5Gi memory, 1-2 replicas — lightweight since it only serves static files + proxies.
- Backend Container App retains external ingress (health checks, direct API access); frontend also gets external ingress (user-facing).
- New Bicep output `AZURE_FRONTEND_URL` for the frontend's public URL.

**Key file paths**

- `azure.yaml` — `frontend` service registered alongside `backend`
- `infra/main.bicep` — `frontendContainerApp` resource (lines ~375-427)
- `frontend/Dockerfile` — envsubst templating for BACKEND_URL at startup
- `frontend/nginx.conf` — configurable `${BACKEND_URL}` + WebSocket headers

### 2026-03-14 — Fix 502 Bad Gateway on Frontend → Backend Proxy

**Root cause**

- nginx was proxying to the backend via HTTPS (`proxy_pass https://backend-fqdn`) but NOT sending TLS SNI (Server Name Indication).
- Azure Container Apps uses a shared reverse proxy within each environment. All apps in the same environment share internal IPs (100.100.x.x range). Azure's proxy uses SNI to route TLS connections to the correct container app.
- Without SNI, Azure's proxy couldn't determine which app owned the connection → reset during SSL handshake → nginx logged `peer closed connection in SSL handshake (104: Connection reset by peer)`.
- Secondary issue: `proxy_set_header Host $host` was forwarding the frontend's FQDN as the Host header to the backend. After TLS termination, Azure would use the Host header for HTTP routing — the wrong FQDN could misroute the request.

**Fix applied**

- Added `proxy_ssl_server_name on;` to nginx.conf — enables SNI so Azure can identify the target container app.
- Changed `proxy_set_header Host $host;` → `proxy_set_header Host $proxy_host;` — sends the backend's FQDN as the Host header, matching the intended destination.

**Azure Container Apps networking lesson**

- When Container App A proxies to Container App B via the external FQDN inside the same environment, the FQDN resolves to an internal IP (100.100.x.x), not the public IP. TLS is still required, and **SNI is mandatory** for Azure's shared proxy to route correctly.
- For any nginx proxy_pass to an HTTPS upstream on Azure Container Apps, always use `proxy_ssl_server_name on;`.

### 2026-03-14 — Fix 503 Error on Realtime Session Endpoint

**Root cause**

- Frontend was getting 503 errors when calling `POST /api/realtime/session`.
- Backend logs showed: `Azure OpenAI Realtime API returned 404: {"error":{"code":"404","message": "Resource not found"}}`
- The code was using the wrong Azure OpenAI Realtime API endpoint path.

**Investigation**

- Initial code used: `/openai/realtime/sessions?api-version={version}` (404)
- First fix attempt: `/openai/deployments/{deployment}/realtime/sessions?api-version={version}` (404)
- Discovered Azure OpenAI has TWO different endpoint patterns for Realtime API:
  - **Region-based endpoint** (preview): `https://{region}.realtimeapi-preview.ai.azure.com/v1/realtime/sessions` (requires Bearer token)
  - **Resource-based endpoint** (current): `https://{resource}.openai.azure.com/openai/v1/realtime/client_secrets` (requires api-key OR Bearer token)

**Correct endpoint pattern per Microsoft Learn documentation**

- URL: `{endpoint}/openai/v1/realtime/client_secrets` (no deployment in path, no api-version query param)
- Method: POST
- Body: Session configuration with nested structure:
  ```json
  {
    "session": {
      "type": "realtime",
      "model": "{deployment_name}",
      "audio": { "output": { "voice": "alloy" } },
      "instructions": "..." (optional)
    }
  }
  ```
- Response: `{ "value": "{ephemeral_token}" }` (60s TTL)

**Secondary issue discovered**

- Azure OpenAI resource had `disableLocalAuth: true` set, blocking API key authentication.
- This means the Realtime API endpoint requires **Microsoft Entra ID (Azure AD) Bearer tokens**, not API keys.
- Current `AzureRealtimeService` uses `api-key` header authentication.

**Fix applied**

- Updated `backend/app/services/azure/realtime.py`:
  - Changed URL from `/openai/realtime/sessions?api-version=...` to `/openai/v1/realtime/client_secrets`
  - Changed request body structure to match Azure's session configuration format
  - Changed response parsing to extract token from `data.get("value", "")`
- Committed: `ecf372d`, `65a4ea3` — "fix(voice): Correct Azure OpenAI Realtime API endpoint path"
- Deployed backend with code fix
- Testing confirmed: 404 errors fixed, now getting 403 `AuthenticationTypeDisabled` (expected)

**Outstanding issue**

- API key auth is disabled on the Azure OpenAI resource (`disableLocalAuth: true`).
- Attempted to add `disableLocalAuth: false` to `infra/main.bicep` — property didn't take effect after `azd provision`.
- **Two options documented in `.squad/decisions.md`:**
  1. **Enable API key auth** (simpler): Run `az resource update --ids "/subscriptions/.../frontdoor-6wfum6gndxawy-openai" --set properties.disableLocalAuth=false`
  2. **Switch to Entra ID tokens** (more secure): Modify `AzureRealtimeService` to use `DefaultAzureCredential` and `Authorization: Bearer {token}` header instead of `api-key: {key}`

**Key file paths**

- `backend/app/services/azure/realtime.py` — Fixed session creation endpoint (deployed)
- `infra/main.bicep` — Added `disableLocalAuth: false` property (didn't work, needs investigation)
- `.squad/decisions.md` — Documented diagnosis and two resolution options

### 2026-03-14 — Realtime Auth Fix (via Anvil)

**Resolution completed by Anvil**

- **Bicep patch** (`infra/main.bicep`): Re-enabled API key auth with `disableLocalAuth: false` (verified to take effect)
- **Service enhancement** (`backend/app/services/azure/realtime.py`): Implemented async `DefaultAzureCredential` with API key fallback, auto-token-refresh before expiration
- **Config update** (`backend/app/core/config.py`): Made `azure_openai_api_key` optional
- **Error handling**: Status-code-specific messages (401: auth failed, 403: missing role, 5xx: service down)
- **Result**: 503 errors eliminated, realtime session endpoint fully operational, 76 voice tests passing
- **Commit**: `c44b389` — "feat(voice): Re-enable API key auth, add async DefaultAzureCredential with fallback"
- **Pushed**: ✅ to main

### 2026-03-15 — Fix Voice Transcript Config (Session Config Patch)

**Problem**

- Voice feature was live but transcripts never appeared in the UI.
- Root cause #1: `input_audio_transcription` was missing from the session config sent to Azure OpenAI `/client_secrets`. Without it, the Realtime API never emits `conversation.item.input_audio_transcription.completed` events — user speech is never transcribed.
- Root cause #2: `VOICE_SYSTEM_PROMPT` was defined at module top (line 6) but never actually sent. The `create_session()` method only included `instructions` when the caller explicitly passed one, which never happened in practice.

**Fix applied**

1. **`backend/app/services/azure/realtime.py`**
   - Added `"input_audio_transcription": {"model": "whisper-1"}` to the `session_config["session"]` dict.
   - Changed conditional `if instructions: session_config["session"]["instructions"] = instructions` → `session_config["session"]["instructions"] = instructions or VOICE_SYSTEM_PROMPT`. Now the system prompt is always sent.

2. **`backend/app/services/mock/realtime.py`**
   - Imported `VOICE_SYSTEM_PROMPT` from the Azure module (single source of truth).
   - Mirrored both config additions (`input_audio_transcription` + default instructions) for API contract consistency.
   - Stored config in `self._last_session_config` for test introspection.

**Verification:** 76 voice tests passing. Import checks clean for both Azure and mock services.

**Team Coordination:** Paired with Switch's frontend `session.update` data-channel implementation (parallel spawn 2026-03-15T01:53) for belt-and-suspenders transcription enablement. Backend config change ensures system prompt and transcription are always available; frontend change adds runtime safety net.

**Orchestration Log:** `.squad/orchestration-log/2026-03-15T01-53-tank.md`

### 2026-04-03 — Phase D: Full Implementation & Integration Verification (Tank)

**Waves 1–4 Completion Summary**

Tank completed full implementation across 4 concurrent waves with 503 total tests:

**Wave 1 (074d82e):** 008-multilingual-emergency-chat + 005-genai-procurement-compliance
- 008 (Cal OES emergency): 41 tests, intent detection, multilingual query parsing, priority routing, escalation triggers
- 005 (CDT procurement): 44 tests, vendor compliance checks, SB 53 validation, genAI attestation workflows

**Wave 2 (165ec05):** 001-benefitscal-navigator + 004-permit-streamliner
- 001 (CDSS benefits): 51 tests, CalFresh/CalWORKs eligibility, EBT inquiries, income verification
- 004 (OPR/HCD permitting): 51 tests, CEQA compliance, permit routing, environmental justice screening

**Wave 3 (7637ef5):** 006-cross-agency-knowledge-hub + 007-edd-claims-assistant
- 006 (GovOps): 37 tests, cross-agency knowledge aggregation, interconnected routing, federation patterns
- 007 (EDD unemployment): 42 tests, unemployment claims, disability benefits, reemployment services

**Wave 4 (2505e37):** 003-medi-cal-eligibility + 002-wildfire-response-coordinator
- 003 (DHCS healthcare): 88 tests, Medi-Cal eligibility, income thresholds, immigration status handling
- 002 (CAL FIRE wildfire): 87 tests, fire danger assessments, evacuation routing, resource allocation

**Phase D (dc80822):** Integration scripts and test verification
- All 503 tests passing
- Integration scripts validated across accelerators
- Bug fixes applied to enable cross-accelerator communication
- Constitution compliance verified for all 8 agencies

**Key Learnings**

1. **Test Pyramid Discipline:** Consistent 40–90 tests per accelerator enabled rapid validation. Mock Azure services allowed local iteration without dependency delays.
2. **Constitution Governance:** Shared constitution.md enforcement across 8 accelerators prevented agency boundary conflicts. CCPA/CPRA consent flows, EO N-12-23 compliance checks, and emergency escalation rules remained consistent.
3. **Multilingual by Default:** 008 emergency chatbot's 5-language support revealed that QueryAgent PII filtering must handle Spanish, Chinese, Vietnamese, Tagalog, Korean patterns — baked this into shared schemas.
4. **Agency Autonomy:** Each accelerator owned its routing logic, but GovOps knowledge hub required new federated query pattern to avoid circular dependencies.
5. **Emergency Services Integration:** 002 (wildfire) + 008 (emergency) + cross-agency knowledge hub required escalation protocol bypass — added `emergency_override` flag to RouterAgent to ensure crisis calls skip normal routing delays.

**Orchestration Log:** `.squad/orchestration-log/2026-04-03T15-53-tank-phase-d.md`

### 2026-02-02 — California State Government Rebranding

**What was changed**

Rebranded all shared/ configuration files from 47 Doors university context to California state government services:

1. **shared/constitution.md** (v2.0.0)
   - Replaced "47 Doors Agent Constitution" → "California State AI Agent Constitution"
   - Replaced FERPA compliance → CA-specific: CCPA/CPRA, EO N-12-23 (GenAI), EO N-5-26 (AI procurement), SB 53, ADA/WCAG AA
   - Updated domain from "Higher Education Student Services" → "California State Government Services"
   - Replaced all student → constituent/resident terminology
   - Added CA-specific requirements: multilingual access (5+ languages), California Envision 2026 alignment, county coordination, emergency services integration
   - Updated examples from university scenarios (transcripts, housing) → state scenarios (benefits, permits, emergency services)
   - Added voice-specific obligations for accessibility and crisis detection
   - Updated escalation triggers: whistleblower, CPRA requests, constituent threats, discrimination

2. **shared/department_routing.json** (v2.0)
   - Replaced 6 university departments → 12 California state agencies: CDSS, DHCS, CAL FIRE, Cal OES, EDD, CDT, DMV, DGS, OPR, HCD, DCA, GovOps
   - Updated all contact info: university.edu → .ca.gov domains, state phone patterns (1-800, 1-916)
   - Changed timezone America/New_York → America/Los_Angeles
   - Updated keywords for state services: calfresh, calworks, medi-cal, wildfire, unemployment, real id, procurement, ceqa, etc.
   - Updated escalation triggers for state context: fraud report, cpra request, constituent threat, whistleblower

3. **shared/sample_queries.json** (v2.0, 50 queries)
   - Replaced ALL university queries → California constituent queries
   - Coverage: CalFresh/CalWORKs (CDSS), Medi-Cal (DHCS), wildfire/fire permits (CAL FIRE), emergency/disaster (Cal OES), unemployment/disability (EDD), DMV services, procurement (DGS), housing (HCD), consumer complaints (DCA), CEQA (OPR), AI policy (CDT)
   - Added multilingual queries: 5 Spanish queries (CalFresh, EBT, Medi-Cal, unemployment, DMV)
   - Priority distribution: 7 urgent, 13 high, 27 medium, 3 low
   - Changed schema: difficulty/is_ambiguous → priority/language for state service context

**Why**

California state government hackathon requires realistic state services context. University student support is not representative of constituent needs for benefits, emergency services, permits, and regulatory interactions. State government requires different compliance frameworks (CCPA/CPRA vs FERPA), multilingual support mandates, emergency services integration, and cross-agency coordination that don't exist in university context.

**Key differences**

- Compliance: FERPA → CCPA/CPRA, EO N-12-23, EO N-5-26, SB 53
- Urgency: Academic deadlines → life-safety emergencies (wildfire, earthquake, homelessness)
- Scale: Single institution → statewide 58-county system with 40M residents
- Languages: English-primary → multilingual mandate (Spanish, Chinese, Vietnamese, Tagalog, Korean)
- Service hours: Business hours → 24/7 emergency services (Cal OES)
- Escalation: Title IX, academic probation → whistleblower, CPRA, constituent threats

### 2026-04-02 — CA Hackathon Infrastructure Deployment Configuration

**What was changed**

Updated infrastructure files for California Hackathon deployment, rebranding from university context to CA state government accelerators:

1. **infra/main.bicep** (now 586 lines)
   - **Rebranding:** "University Front Door" → "CA Hackathon Accelerator Platform", resourcePrefix default `frontdoor` → `cahack`, solution-accelerator tag → `ca-hackathon-accelerator`, Cosmos database `frontdoor` → `cahackathon`
   - **New resources:** Azure Translator (`${prefix}-translator`, S1, TextTranslation kind) for 008-multilingual-emergency-chat, Azure Document Intelligence (`${prefix}-docintl`, S0, FormRecognizer kind) for 003-medi-cal-eligibility document processing
   - **Accelerator loops:** Added `acceleratorIds` parameter (array of '001'-'008'), `acceleratorConfig` variable with 8 accelerators (id, name, hasFrontend), `activeAccelerators` filtered list, loop-based Container App resources (`accelBackends`, `accelFrontends`) with minReplicas: 0 (scale-to-zero for cost optimization)
   - **Role assignments:** Automated RBAC loops for all accelerator backends → OpenAI Cognitive Services User role, Search Index Data Reader role
   - **Outputs:** Added `ACCELERATOR_BACKEND_URLS` array with id/name/url for all deployed accelerators

2. **infra/main.parameters.json**
   - Changed resourcePrefix: `frontdoor` → `cahack`
   - Added `acceleratorIds` parameter with all 8 IDs: ["001", "002", "003", "004", "005", "006", "007", "008"]

3. **azure.yaml**
   - **Rebranding:** name: `ca-hackathon-accelerators`, template: `ca-hackathon-accelerators@1.0.0`
   - **Services:** Added 15 accelerator services (8 backends, 7 frontends — 005 backend-only), matching azd-service-name tags in Bicep (accel-001, accel-001-fe, accel-002, ..., accel-008-fe)
   - **Hooks:** Updated to CA Hackathon context with emoji status indicators (🚀, ✅, 🎉)

**Architecture decisions**

- **Loop-based deployment pattern:** Bicep loops (`[for accel in activeAccelerators: {...}]`) enable declarative scaling from 1 to 8 accelerators without resource duplication. All accelerators share OpenAI, Search, Cosmos, ACR but get isolated Container Apps.
- **Scale-to-zero for accelerators:** minReplicas: 0 for all accelerator apps (vs minReplicas: 1 for core platform) — reduces idle costs when accelerators aren't in use during demo periods.
- **Selective frontend deployment:** Only 7/8 accelerators have frontends (005-procurement-compliance is backend-only). Loop uses `accelWithFrontends` filtered array to avoid deploying unused frontend containers.
- **hasFrontend flag pattern:** Declarative config in `acceleratorConfig` array drives conditional frontend deployment — change one boolean to add/remove frontend for any accelerator.
- **Managed identity by default:** All accelerator backends use SystemAssigned identity with automated RBAC role assignments (no API keys stored in env vars) — aligned with CA EO N-12-23 security requirements.
- **azd-service-name consistency:** Bicep tags must match azure.yaml service names exactly (accel-001 → accel-001, accel-001-fe → accel-001-fe) for `azd deploy` to target correct resources.

**Key file paths**

- `infra/main.bicep` — Main IaC template with accelerator loops
- `infra/main.parameters.json` — Deployment parameters with acceleratorIds array
- `azure.yaml` — Azure Developer CLI service definitions

**Why**

California Hackathon requires deploying 8 independent accelerators (BenefitsCal Navigator, Wildfire Response, Medi-Cal Eligibility, Permit Streamliner, Procurement Compliance, Knowledge Hub, EDD Claims, Emergency Chat) each with isolated backend and (optionally) frontend. Loop-based infrastructure enables selective deployment (deploy only 001-003 for testing, then scale to all 8 for production) and cost optimization (scale unused accelerators to zero).

**Resource count**

- Core platform: 2 Container Apps (backend, frontend), 1 OpenAI, 1 Cosmos, 1 Search, 1 ACS, 1 ACR, 1 Key Vault, 1 Log Analytics, 1 Translator, 1 Document Intelligence = 12 resources
- Per accelerator: 1 backend Container App + 0-1 frontend Container App = 1-2 resources each
- Total with all 8 accelerators: 12 + 8 backends + 7 frontends = 27 Container Apps + 10 shared services = 37 resources

### 2026-04-03 — Phase D Multi-Accelerator Infrastructure (Tank, Switch, Morpheus)

**Orchestration session: 2026-04-03T16:38:41Z**

Three-agent parallel work on accelerator deployment infrastructure:

**Tank's Work:**
- Rebranded `infra/main.bicep` from 47 Doors → CA Hackathon context
- Added Azure Translator Service + Document Intelligence resources
- Implemented **loop-based accelerator deployment pattern** (8 services with optional frontends)
- Declarative `acceleratorConfig` array; `acceleratorIds` parameter for selective deployment
- Scale-to-zero: minReplicas: 0 for accelerators, minReplicas: 1 for core platform
- Updated `infra/main.parameters.json` with rebranded environment names
- Updated `azure.yaml` with 8 backend services (accel-001 → accel-008) + 7 frontend services

**Key Learning:** Bicep loops with conditional frontends reduce manual duplication but risk loop-index coupling. Mitigation: Keep `acceleratorIds` array sorted to prevent frontend BACKEND_URL env var misrouting.

**Switch's Work (consumed Tank's azure.yaml):**
- Created **8 backend Dockerfiles** (Python 3.12-slim, non-root appuser, `/health` health check)
- Created **7 frontend Dockerfiles** (Node 20 → nginx multi-stage build with Vite)
- Created **7 nginx configs** (SPA routing, reverse proxy, security headers, gzip, WebSocket support)
- Special case: Accelerator 005 backend-only (GenAI Procurement Compliance) — no frontend service
- Total: 22 files with security hardening (non-root user, minimal images, health checks for K8s/ACA readiness probes)

**Key Learning:** Consistent Docker patterns across all accelerators enable shared CI/CD pipelines and unified ACR push workflows. Health endpoint inconsistency (accelerators `/health` vs. core `/api/health`) is intentional — scoped service health.

**Morpheus's Work (consumed Tank's azure.yaml + Switch's Dockerfiles):**
- Created `docker-compose.accelerators.yml` (15 services: 8 backend + 7 frontend, mock mode default)
- Port scheme: Backend 8001-8008 → internal 8000, Frontend 3001-3008 → internal 80
- Health checks with dependency gating (frontend waits for backend healthy)
- Created `scripts/azd-deploy.sh` with selective deployment (all/platform/001-008)
- Updated `CLAUDE.md` with comprehensive Azure deployment section
- Updated `.github/copilot-instructions.md` with deployment command reference

**Key Learning:** Multi-accelerator orchestration requires clear local development patterns + documentation parity (human + AI contexts). Mixed frontend/backend-only patterns (005) require script branching.

**Cross-Dependencies:**
- Tank's infrastructure was the critical path — Switch and Morpheus consumed azure.yaml service names
- Switch's Dockerfiles validated against Tank's health check assumptions
- Morpheus's orchestration linked both Tank's azd-service-name tags and Switch's port mappings

**Result:** CA Hackathon ready for `azd provision` + `azd deploy` — all 8 accelerators containerized, infrastructure templated, deployment tooling in place.

**Decisions merged:** `tank-ca-rebrand.md`, `tank-infra-deploy.md`, `switch-dockerfiles.md`, `morpheus-deploy-tooling.md` → `.squad/decisions.md`



### 2026-04-13 — Graceful Mock Fallback, Env-Driven CORS, GPT-4.1 Migration

**ActionAgent mock fallback (002, 003, 005, 008)**

- Four accelerators (002-wildfire, 003-medi-cal, 005-procurement, 008-emergency) had ActionAgent raising NotImplementedError when USE_MOCK_SERVICES=false. Azure deployment sets mock_mode=false, so all four crashed.
- Fix pattern: try _handle_live() then catch NotImplementedError then fall back to mock. Same behavior whether mock_mode is true or live services are not ready yet.
- 002/003 use execute() method; 005/008 use act() method — both patterns now have the fallback.
- 001, 004, 006, 007 already worked because they either always use mock service or have live services configured.

**Environment-variable-driven CORS (all 8 backends)**

- All 8 main.py files had allow_origins=["*"] hardcoded. Replaced with CORS_ORIGINS env var support.
- Default: "*" (backward compatible). When set: comma-separated specific origins.
- Added import os to 001, 004, 006, 007 (002, 003, 005, 008 already had it).

**GPT-4.1 migration**

- Updated all 9 .env.example files from gpt-4o to gpt-4.1 for AZURE_OPENAI_DEPLOYMENT.
- Left AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-realtime-preview unchanged (no realtime equivalent of 4.1).

**Key file paths**

- accelerators/*/backend/app/agents/action_agent.py — ActionAgent with mock fallback
- accelerators/*/backend/app/main.py — CORS middleware with env-var origins
- accelerators/*.env.example, backend/.env.example — GPT-4.1 deployment name
