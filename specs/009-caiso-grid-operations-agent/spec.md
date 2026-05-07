# Feature Specification: CAISO Grid Operations Intelligence Agent

**Feature Branch**: `009-caiso-grid-operations-agent`  
**Created**: 2026-05-05  
**Status**: Draft  
**Agency**: California Independent System Operator (CAISO)  
**Programs**: Grid Operations, Day-Ahead & Real-Time Markets, Transmission Planning, Flex Alert  
**Pattern Analog**: Wildfire Response Coordinator (002)

---

## Problem Context

CAISO manages the flow of electricity across high-voltage, long-distance power lines serving approximately 80% of California's electrical demand. Grid operators must simultaneously monitor hundreds of real-time alerts, interpret market signals, forecast renewable generation variability, and coordinate demand response programs — often making decisions in minutes that affect millions of Californians. California's rapid shift to renewable energy (solar, wind) creates novel operational challenges: managing over-generation periods, coordinating battery storage dispatch, and maintaining grid reliability as fossil generation retires.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Real-Time Grid Operations Q&A (Priority: P1)

A CAISO grid operator on shift asks the agent about current grid conditions during a tight supply period. The operator needs a synthesized view of net imports, renewable generation levels, and demand response headroom — without toggling between five separate monitoring dashboards.

**Why this priority**: Core operational value. Reduces cognitive load for operators managing complex, high-stakes grid events. Directly addresses the challenge of information overload during peak demand or supply stress events.

**Acceptance Scenarios**:
1. **Given** an operator asks "What is current renewable curtailment and what is the primary cause?", **Then** the agent returns a synthesized summary with curtailment volume (MW) and root cause (e.g., over-generation, transmission constraint) from mock OASIS data
2. **Given** an operator asks "How much demand response capacity is available right now across all programs?", **Then** the agent returns aggregate DR capacity by program type with confidence level
3. **Given** a query involves grid safety boundaries (e.g., transmission limits), **Then** the agent responds with the relevant system operating limit and a link to the relevant NERC/WECC reliability standard
4. **Given** a query is outside the agent's knowledge scope (e.g., specific switching orders), **Then** the agent acknowledges its scope and routes to appropriate CAISO operational staff contact

---

### User Story 2 — Day-Ahead Market Intelligence (Priority: P2)

A market participant (utility scheduler) asks the agent to summarize day-ahead LMP results, identify congestion patterns, and flag any notable deviations from the day-ahead forecast.

**Acceptance Scenarios**:
1. **Given** a participant asks "What were the top 5 highest LMP nodes in yesterday's day-ahead market?", **Then** the agent returns a ranked summary with node names, prices, and congestion components from mock OASIS data
2. **Given** a participant asks about a specific inter-tie, **Then** the agent provides the scheduled flow and any binding constraints from mock data
3. **Given** the participant is not a registered CAISO market participant (unauthenticated), **Then** the agent provides only publicly available OASIS data and directs them to the Market Participant Portal for proprietary data

---

### User Story 3 — Demand Response & Flex Alert Planning (Priority: P3)

A CAISO demand response coordinator needs to assess whether conditions warrant issuing a Flex Alert and which demand response programs to activate.

**Acceptance Scenarios**:
1. **Given** forecast demand minus supply shows a margin below 3% reserve for tomorrow's peak hour, **Then** the agent surfaces a Flex Alert recommendation with supporting data
2. **Given** the coordinator asks "Which demand response programs have the fastest activation time for a 4-hour event?", **Then** the agent ranks DR programs by activation speed and available capacity from the mock DR catalog
3. **Given** a question about a specific DR program's rules, **Then** the agent provides program eligibility, activation notice requirements, and compensation structure

---

### User Story 4 — Transmission Planning Q&A (Priority: P4)

A transmission planner needs to understand the impact of a proposed new solar project interconnection on the existing grid.

**Acceptance Scenarios**:
1. **Given** a planner asks about congestion patterns on a specific 500kV path, **Then** the agent summarizes historical binding constraint frequency from mock data
2. **Given** a planner asks about renewable integration capacity in a specific load-pocket, **Then** the agent provides the regional hosting capacity estimate and identifies any known constraints

---

## Compliance & Governance

- **EO N-12-23**: AI must be identified; outputs are advisory only, not operational commands
- **NERC CIP**: Agent is read-only; no write access to any operational technology systems
- **CAISO Tariff**: Agent does not provide binding market advice; directs participants to CAISO market portal
- **CCPA**: No constituent PII collected; market participant queries do not reveal proprietary position data
- **Agent Scope Boundary**: The agent NEVER issues dispatch instructions, market bids, or operational commands of any kind

---

## Tech Stack

| Component    | Technology                                     | Notes                                                  |
| ------------ | ---------------------------------------------- | ------------------------------------------------------ |
| QueryAgent   | Azure OpenAI GPT-4o                            | Intent: grid ops / market / DR / transmission planning |
| RouterAgent  | Semantic Kernel                                | Routes to 4 domain handlers                            |
| ActionAgent  | FastAPI + AI Search                            | OASIS data RAG + mock data                             |
| Data Sources | CAISO OASIS API (mock), NWS weather API (mock) | Public data only                                       |
| Frontend     | React 18 + TypeScript                          | Real-time dashboard with chart components              |
| Compliance   | Read-only, advisory, NERC CIP guardrails       |                                                        |
