# Feature Specification: Caltrans Project Intelligence Agent

**Feature Branch**: `011-caltrans-project-intelligence-agent`  
**Created**: 2026-05-05  
**Status**: Draft  
**Agency**: California Department of Transportation (Caltrans)  
**Programs**: Encroachment Permits, Highway Design Manual, CEQA/NEPA Review, Capital Outlay Projects  
**Pattern Analog**: Permit Streamliner (004)

---

## Problem Context

Caltrans manages over 50,000 lane miles of state highway, 13,000+ bridges, and thousands of active capital projects ranging from pothole repair to multi-billion dollar interchange reconstructions. Three distinct user communities struggle with information access: (1) local agencies and contractors submitting encroachment permits face a 40+ page application and complex fee schedules; (2) environmental staff conducting CEQA/NEPA reviews must navigate evolving guidance documents across 12 Caltrans districts; (3) capital project managers need rapid access to the Highway Design Manual (HDM) and Standard Plans to make design decisions. Each of these workflows generates significant staff time interpreting complex, multi-document guidance.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Encroachment Permit Guidance (Priority: P1)

A contractor or local agency representative needs to understand requirements for a utility installation in the Caltrans right-of-way.

**Why this priority**: Encroachment permits are the most frequent interface between Caltrans and external stakeholders. Reducing application errors and back-and-forth review cycles directly reduces permit processing time and construction delays.

**Acceptance Scenarios**:
1. **Given** a contractor asks "What are the requirements to install a fiber optic conduit in a Caltrans right-of-way on a state route with 85mph design speed?", **Then** the agent returns the applicable HDM section, bonding requirements, and traffic control plan requirements
2. **Given** an applicant asks about permit fees, **Then** the agent returns the current fee schedule from mock permit fee data and explains deposit vs. final fee structure
3. **Given** a local agency asks about the standard conditions for a storm drain connection to a state highway, **Then** the agent returns the standard conditions from mock Caltrans encroachment permit conditions library
4. **Given** a query involves work near a Caltrans bridge structure, **Then** the agent adds a warning that a Structure Maintenance and Investigation review is required and provides the District contact
5. **Given** an applicant asks about an emergency permit, **Then** the agent explains the expedited permit process, 24-hour contact numbers, and conditions under which emergency permits are issued

---

### User Story 2 — Highway Design Manual Q&A (Priority: P2)

A Caltrans project engineer needs to determine the design standards for a curve on a rural two-lane highway.

**Acceptance Scenarios**:
1. **Given** an engineer asks "What is the minimum sight distance requirement for a STOP sign intersection approach on a 45mph state route?", **Then** the agent returns the applicable HDM topic (301.1) with the standard and a link to the HDM PDF
2. **Given** an engineer asks about guardrail placement criteria near a bridge end, **Then** the agent returns the relevant HDM section and Standard Plan reference
3. **Given** the query involves a standard that has been recently amended, **Then** the agent indicates the amendment date and recommends verifying with the current online HDM version

---

### User Story 3 — CEQA/NEPA Environmental Review Process (Priority: P3)

An environmental planner at a local agency asks about the environmental document requirements for a Caltrans-funded project.

**Acceptance Scenarios**:
1. **Given** a planner asks "What is the difference between a Categorical Exclusion and a Mitigated Negative Declaration for a resurfacing project?", **Then** the agent explains both pathways, the qualifying criteria, and which is appropriate for federally-funded vs. state-only projects
2. **Given** a planner asks about the standard biological surveys required for a state highway widening project, **Then** the agent returns the applicable Caltrans standard protocol surveys (botanical, wildlife) and trigger thresholds
3. **Given** a query involves consultation with USFWS or CDFW, **Then** the agent explains the Section 7 and Section 2081 permit processes and typical timelines

---

### User Story 4 — Capital Project Status Inquiry (Priority: P4)

A local elected official or their staff asks about the status of a specific capital highway project in their district.

**Acceptance Scenarios**:
1. **Given** a query asks about a specific project by name or route number, **Then** the agent returns project status, funding sources, and the responsible District contact from mock project data
2. **Given** a query asks about a project not in the mock data, **Then** the agent directs to the Caltrans Project Atlas map and District 7 project website as appropriate

---

## Compliance & Governance

- **EO N-12-23**: Agent identifies itself as AI; outputs are guidance only, not official Caltrans determinations
- **CCPA**: No PII collected; queries about specific parcel or permit applicant data are redirected to official permit portal
- **CEQA / NEPA**: Agent provides process guidance only; does not substitute for official environmental review or legal counsel
- **ADA/WCAG 2.1 AA**: All HDM references include alternative text descriptions for figures

---

## Tech Stack

| Component    | Technology                                                 | Notes                                                               |
| ------------ | ---------------------------------------------------------- | ------------------------------------------------------------------- |
| QueryAgent   | Azure OpenAI GPT-4o                                        | Intent: permit / HDM / environmental / project status               |
| RouterAgent  | Semantic Kernel                                            | Routes to 4 domain handlers                                         |
| ActionAgent  | FastAPI + AI Search                                        | Knowledge base: HDM, Standard Plans, encroachment permit conditions |
| Data Sources | Caltrans HDM (RAG), LAPG, encroachment permit fee schedule | Public documents                                                    |
| Frontend     | React 18 + TypeScript                                      | Permit checklist wizard + project status map embed                  |
| Compliance   | Advisory only, CEQA/NEPA guidance guardrails               |                                                                     |
