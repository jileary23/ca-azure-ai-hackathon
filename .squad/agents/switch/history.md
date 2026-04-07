# Project Context

- **Owner:** msftsean
- **Project:** 47 Doors — Universal Front Door Support Agent for university student support
- **Stack:** Python 3.11+ / FastAPI 0.109+, TypeScript 5 / React 18, Azure OpenAI, Azure AI Search, Pydantic v2.5+
- **Architecture:** Three-agent pipeline (QueryAgent → RouterAgent → ActionAgent) with voice interaction via Azure OpenAI GPT-4o Realtime API / WebRTC
- **Created:** 2026-03-13

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

### 2026-03-19 — Workshop Companion Site Build

**Architecture decisions:**
- Built standalone React + TypeScript + Tailwind CSS site at `workshop-site/` as executive briefing tool for "Trustworthy Agentic AI in Higher Education" workshop
- Microsoft Fluent 2 visual language: generous whitespace, calm typography, restrained color palette
- Primary colors: Microsoft blue (#0078D4), neutral gray (#F3F2F1), dark text (#323130)
- IU crimson (#990000) used SPARINGLY for callout borders — accent color, not primary
- 10 tab-based sections covering full 47 Doors narrative: Problem → Architecture → Trust → Voice → Demo → Governance

**Component architecture:**
- Tab navigation with keyboard accessibility (arrow keys, Tab/Shift+Tab, Enter/Space)
- Reusable components: TabNavigation, CollapsibleNotes, CalloutCard, DiagramSVG
- Each tab is standalone React component in `src/tabs/` — deep-linkable design
- SVG diagrams with semantic markup (figure/figcaption, aria-labels, title/desc elements)
- No external component libraries — lightweight, Heroicons only

**Key file paths:**
- Site root: `workshop-site/`
- Main app: `workshop-site/src/App.tsx` (tab state management)
- Tab components: `workshop-site/src/tabs/*.tsx` (10 total: Overview, TheProblem, ChatbotsToAgents, TrustBoundaries, Architecture, VoiceAccessibility, DemoWalkthrough, ResponsibleAI, ReuseAcrossCampus, YourFirstAgent)
- Reusable UI: `workshop-site/src/components/*.tsx`
- README: `workshop-site/README.md` (install/run instructions)

**User preferences observed:**
- Calm, academic tone — NO flashy marketing energy
- Text-light, visually rich — icons, diagrams, callout cards over dense paragraphs
- Speaker notes as collapsible sections (preserve presentation context without cluttering UI)
- Interactive "Your First Agent" exercise (client-side only, no backend) with live-updating agent card
- High contrast text (WCAG AA 4.5:1 minimum), semantic HTML, keyboard navigation
- Design principle: "This should feel like a confident executive briefing, not a product pitch"

**Content patterns:**
- Each tab has: headline, visual elements (diagrams/cards), callout cards for key insights, collapsible presenter notes
- Diagrams use inline SVG with DiagramSVG wrapper for accessibility
- "What to Notice" callouts highlight architectural insights
- Demo walkthrough uses numbered step cards with visual labels and notes
- "Your First Agent" tab uses controlled inputs with example chips for quick selection

**Build verification:**
- TypeScript typechecks clean (`npm run typecheck` passes)
- Production build succeeds: 222.94 kB JS (63.50 kB gzipped), 16.28 kB CSS (3.58 kB gzipped)
- 371 modules transformed, built in 2.15s
- Local dev: `npm run dev` (Vite dev server on port 5173)

### 2026-03-14 — Azure Static Web Apps Auth Migration (docs runbook)

**Architecture decisions:**
- Runbook site migrated from GitHub Pages → Azure Static Web Apps for built-in authentication.
- Auth provider: Azure AD (Microsoft Entra ID) only — GitHub/Twitter providers explicitly blocked with 404.
- `staticwebapp.config.json` route rules: `/.auth/login/aad` + `/.auth/logout` are `anonymous`; all other routes require `authenticated` role; 401 redirects to AAD login.
- Auth bar integrated into existing sticky nav (right-aligned `.nav-auth` div) — uses `/.auth/me` fetch to show username; hidden on local dev when endpoint unavailable (silent catch).

**Key file paths:**
- SWA config: `docs/staticwebapp.config.json`
- Setup guide: `docs/AZURE_SWA_SETUP.md`
- GitHub Actions workflow: `.github/workflows/deploy-docs-swa.yml`
- Deployment secret expected: `AZURE_STATIC_WEB_APPS_API_TOKEN` (user adds after SWA resource creation)

**User preferences observed:**
- Auth UI must be minimal — user said "don't distract from runbook content"
- Dark theme, purple accent, Inter font — all auth elements use existing CSS variables
- Setup docs use bash (not PowerShell) with emojis for readability
- Local dev graceful degradation is a hard requirement (auth bar hides if `/.auth/me` unavailable)

**Architecture decisions:**
- Audio never transits the backend — WebRTC connects browser → Azure OpenAI directly. Backend only relays tool call results via `/api/realtime/ws`.
- Ephemeral token TTL ≤ 60 s is a hard constitutional constraint (Voice Channel Security); tokens are single-use and non-renewable.
- `session_id` is shared between text chat and voice sessions — voice attaches to the existing `Session` entity so modality switching preserves context.

**Key file paths:**
- OpenAPI contract: `specs/002-voice-interaction/contracts/voice-api.yaml`
- Quickstart guide: `specs/002-voice-interaction/quickstart.md`
- Planned backend router: `backend/app/api/realtime.py` (not yet created)
- Planned frontend hook: `frontend/src/hooks/useVoice.ts` (not yet created)
- Existing router pattern: `backend/app/api/routes.py` (FastAPI `APIRouter`, mounted at `settings.api_prefix` = `/api`)
- Vite proxy config: `frontend/vite.config.ts` — `/api` → `http://127.0.0.1:8000`; WebSocket proxy is handled automatically.
- Env example: `backend/.env.example` — `MODE=mock` is the default; voice adds `AZURE_OPENAI_REALTIME_DEPLOYMENT`.

**Patterns to follow:**
- Router uses `APIRouter()` with full `responses={}` dicts for all non-200 status codes.
- All response models use Pydantic v2 schemas defined in `backend/app/models/`.
- Health check pattern: always returns HTTP 200; use field values (`realtime_available`) for capability detection, not HTTP status.
- WebSocket close code conventions: 4001 = invalid token, 4002 = session expired (custom range above 4000 for app-level errors).

### 2026-03-14 — session.update via Data Channel for Transcription

**What:** Added `dc.onopen` handler in `useVoice.ts` that sends a `session.update` event through the WebRTC data channel to enable `input_audio_transcription` (whisper-1 model). Without this, the Azure OpenAI Realtime API never emits `conversation.item.input_audio_transcription.completed` events — meaning user speech is never transcribed.

**Why belt-and-suspenders:** The backend (Tank) is also being updated to include `input_audio_transcription` in the initial session config. The frontend `session.update` is a safety net — if the backend config is ever missing or the API ignores the initial config, the data-channel message ensures transcription is active before we start listening.

**Side benefit:** Moved the `LISTENING` dispatch into `dc.onopen` instead of relying on `pc.onconnectionstatechange`. The data channel being open is the actual prerequisite for sending/receiving events — more semantically correct than peer connection state alone.

**Key files:**
- `frontend/src/hooks/useVoice.ts` — added `dc.onopen` handler (lines 106–116)

**Team Coordination:** Coordinated with Tank's parallel backend session config changes (spawn 2026-03-15T01:53). Both changes are idempotent and reinforce each other. Frontend ensures transcription is active; backend ensures system prompt is sent.

**Verification:** TypeScript compiles clean. Code review passed (Morpheus).

**Orchestration Log:** `.squad/orchestration-log/2026-03-15T01-53-switch.md`

### 2026-03-19 — README Rebrand for California State AI Hackathon

**What:** Complete rewrite of root `README.md` to rebrand from "47 Doors" university student support to California state government AI accelerators. Replaced ALL university and 47 Doors references with California context.

**Why:** Project pivot to focus on California State Hackathon — 8 AI accelerators for state agencies (CDSS, CAL FIRE, DHCS, EDD, Cal OES, etc.) aligned with CA governance framework (EO N-12-23, EO N-5-26, SB 53, Envision 2026).

**Key changes:**
- Header: "🏛️ California State AI Hackathon Accelerators" with CA Envision 2026 badge
- Overview: 8 accelerators for CA agencies, constitution-driven governance, 3-agent pipeline pattern
- Accelerator table: 001-008 with agency assignments (CDSS, CAL FIRE/Cal OES, DHCS, OPR/HCD/DCA, CDT/DGS, GovOps, EDD, Cal OES)
- Architecture: Text-based 3-agent pipeline diagram (QueryAgent → RouterAgent → ActionAgent)
- Tech stack: Table format with governance layer (EO N-12-23/N-5-26 compliant)
- California Governance section: Executive orders, legislation (SB 53), Breakthrough Project, Envision 2026, constitution.md explanation
- Project structure: specs/, accelerators/, shared/, labs/, backend/, frontend/
- Removed: All 47 Doors branding, university student support use cases, boot camp curriculum details, deployment field notes

**Files changed:**
- `/workspaces/ca-hackathon/README.md` — 576 lines → 348 lines (complete rewrite)

**Content patterns:**
- All references to "47 Doors", "university", "student support" removed
- New focus: California state agencies, public service delivery, governance compliance
- Constitution-driven approach emphasized as executable policy (not just docs)
- Each accelerator standalone but shares platform code (shared/)
- Quick Start section streamlined (npm run setup → npm start → npm run smoke-test)

**Preservation:**
- Tech stack badges and versions maintained (Python, FastAPI, React, TypeScript, Azure)
- Quick start commands unchanged (npm run setup, npm start, smoke-test)
- Architecture diagrams and deployment patterns referenced (actual lab content unchanged)
- License (MIT) and contributing guidelines maintained

**Key file paths:**
- README: `/workspaces/ca-hackathon/README.md`
- Specs: `specs/001-benefitscal-navigator/`, `specs/002-wildfire-coordinator/`, etc.
- Shared platform: `shared/platform/`, `shared/ui-components/`, `shared/templates/`, `shared/infra/`

**Learnings for future:**
- Constitution.md is central to CA governance narrative — it's executable policy, not documentation
- All 8 accelerators share 3-agent pattern but serve different agencies/domains
- EO N-12-23, N-5-26, SB 53 are key compliance touchpoints for CA state AI
- Envision 2026 is the strategic umbrella for digital transformation
- Mock mode is critical for prototyping without Azure credentials

### 2026-04-02 — Docker Configuration for All Accelerators

**What:** Created standardized Dockerfiles and nginx configs for all 8 accelerators to enable containerized deployment.

**Files created (22 total):**
- Backend Dockerfiles: `accelerators/*/backend/Dockerfile` (8 files)
- Frontend Dockerfiles: `accelerators/*/frontend/Dockerfile` (7 files — skip 005 which has no frontend)
- Nginx configs: `accelerators/*/frontend/nginx.conf` (7 files)

**Key patterns:**
- Backend Dockerfiles: Python 3.12-slim base, uvicorn server on port 8000, non-root appuser, health check at `/health` (NOT `/api/health` like core platform)
- Frontend Dockerfiles: Node 20-alpine builder stage → nginx alpine runtime, multi-stage build, envsubst for BACKEND_URL injection
- Nginx configs: Identical across all accelerators — SPA routing (try_files), /api/ proxy to backend, gzip compression, security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection), static asset caching (1y expires for /assets/)
- All Dockerfiles use health checks: `curl -f` for backend, `wget --spider` for frontend

**Architecture decisions:**
- Consistent containerization across all accelerators for Kubernetes/ACA deployment
- Health check paths differ: core platform `/api/health`, accelerators `/health`
- Frontend-backend communication via nginx reverse proxy (location /api/)
- Environment-based backend URL injection (ENV BACKEND_URL in Dockerfile + envsubst in CMD)

**Files structure:**
```
accelerators/
  001-benefitscal-navigator/
    backend/Dockerfile
    frontend/Dockerfile
    frontend/nginx.conf
  002-wildfire-response-coordinator/
    backend/Dockerfile
    frontend/Dockerfile
    frontend/nginx.conf
  003-medi-cal-eligibility/
    backend/Dockerfile
    frontend/Dockerfile
    frontend/nginx.conf
  004-permit-streamliner/
    backend/Dockerfile
    frontend/Dockerfile
    frontend/nginx.conf
  005-genai-procurement-compliance/
    backend/Dockerfile
    (no frontend — API-only)
  006-cross-agency-knowledge-hub/
    backend/Dockerfile
    frontend/Dockerfile
    frontend/nginx.conf
  007-edd-claims-assistant/
    backend/Dockerfile
    frontend/Dockerfile
    frontend/nginx.conf
  008-multilingual-emergency-chat/
    backend/Dockerfile
    frontend/Dockerfile
    frontend/nginx.conf
```

**Key learnings:**
- Accelerator health endpoints are at `/health` (not `/api/health`)
- All backend Dockerfiles identical except for directory context
- All frontend Dockerfiles + nginx configs identical across accelerators
- Multi-stage builds keep frontend images small (~50MB vs ~1GB)
- Non-root users (appuser) improve container security posture
- Health checks enable Kubernetes/ACA readiness/liveness probes

### 2026-04-07 — Crawler Blocking & Footer Attribution (All Frontends)

**What:** Added `robots.txt` files and `noindex/nofollow` meta tags across all frontends to block search crawlers. Created `Footer.tsx` components with Sean Gayle attribution and Microsoft Azure branding for every frontend.

**Crawler blocking (robots.txt + meta tags):**
- `frontend/public/robots.txt` — created
- `docs/robots.txt` — created
- `accelerators/*/frontend/public/robots.txt` — created (7 files, new `public/` dirs)
- Meta tag `<meta name="robots" content="noindex, nofollow">` added to all 10 `index.html` files

**Footer components created:**
- `frontend/src/components/Footer.tsx` — Tailwind, dark gray-900 bar
- `accelerators/001-benefitscal-navigator/frontend/src/components/Footer.tsx` — Tailwind
- `accelerators/002-wildfire-response-coordinator/frontend/src/components/Footer.tsx` — inline styles (matches app style)
- `accelerators/003-medi-cal-eligibility/frontend/src/components/Footer.tsx` — inline styles (matches app style)
- `accelerators/004-permit-streamliner/frontend/src/components/Footer.tsx` — Tailwind
- `accelerators/006-cross-agency-knowledge-hub/frontend/src/components/Footer.tsx` — Tailwind
- `accelerators/007-edd-claims-assistant/frontend/src/components/Footer.tsx` — Tailwind
- `accelerators/008-multilingual-emergency-chat/frontend/src/components/Footer.tsx` — Tailwind

**Footer integrations (App.tsx imports + JSX):**
- `frontend/src/App.tsx` — Footer after `</main>`
- All 7 accelerator `App.tsx` files — Footer as last child before closing `</div>`

**Existing footer updates:**
- `workshop-site/src/components/Footer.tsx` — replaced "47 Doors / IU Bloomington" with msftsean + Azure branding
- `docs/index.html` footer (lines 872-882) — added "Built by Sean Gayle · ☁️ Powered by Microsoft Azure"

**Design decisions:**
- Accels 002 + 003 use inline CSS (matching their app-wide inline style pattern) instead of Tailwind
- Footer is `mt-auto` to stick to bottom in flex-col layouts
- All footers include `role="contentinfo"` and `aria-label` for accessibility
- Left: "Built by Sean Gayle" (GitHub link) · Right: "☁️ Powered by Microsoft Azure"

**Verification:** All 9 React frontends typecheck clean (`tsc --noEmit` passes)

**Orchestration session: 2026-04-03T16:38:41Z**

**Context:** Tank's infrastructure rebranding + loop pattern defined 8 accelerator deployment targets. Switch consumed Tank's azure.yaml service names to create standardized containerization.

**Switch's Deliverables:**
- **8 backend Dockerfiles** (Python 3.12-slim, FastAPI + uvicorn on 8000, `/health` endpoint, non-root appuser)
- **7 frontend Dockerfiles** (Node 20 builder stage → nginx 1.27 runtime, Vite build, BACKEND_URL envsubst)
- **7 nginx configs** (SPA routing to /index.html, reverse proxy /api/ → $BACKEND_URL, security headers, gzip, WebSocket upgrade)
- **Exception:** Accelerator 005 backend-only (no frontend, no nginx config)
- **Total:** 22 files, all following identical patterns for consistency

**Design Decisions:**
- Health endpoint: Accelerators use `/health` (scoped service check) vs. core platform `/api/health` (full API surface) — intentional distinction
- Nginx security headers: X-Frame-Options: DENY, X-Content-Type-Options: nosniff, X-XSS-Protection: 1; mode=block
- Static asset caching: 1-year expires for /assets/*, no-cache for HTML
- WebSocket support: Upgrade header passthrough, long proxy_read_timeout (600s) for streaming

**Cross-Agent Dependencies:**
- Consumed Tank's `azure.yaml` service names (accel-001 through accel-008, accel-001-fe through accel-008-fe)
- Validated port assumptions (8000 internal for all backends, 80 internal for all frontends)
- Enabled Morpheus to map ports correctly in docker-compose.accelerators.yml (8001-8008/3001-3008)

**Verification:**
- All Dockerfiles follow core platform patterns (same base images, security practices)
- nginx configs tested for syntax correctness (checked with nginx -t locally)
- Health checks confirmed by Morpheus in docker-compose service_healthy conditions

**Result:** All accelerators containerized and ready for ACR push + Azure Container Apps deployment.

**Decision merged:** `switch-dockerfiles.md` → `.squad/decisions.md`
