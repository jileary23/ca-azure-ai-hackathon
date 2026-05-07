# Feature Specification: DGS Procurement Intelligence Agent

**Feature Branch**: `017-dgs-procurement-agent`  
**Created**: 2026-05-05  
**Status**: Draft  
**Agency**: California Department of General Services (DGS)  
**Programs**: California Multiple Award Schedules (CMAS), Statewide Contracts, Small Business (SB) / DVBE Programs, State Surplus  
**Pattern Analog**: GenAI Procurement Compliance (005)

---

## Problem Context

DGS manages procurement for California state government, overseeing more than $15 billion in annual purchasing activity. State agency procurement staff navigate a complex ecosystem: California Multiple Award Schedules (CMAS), Leveraged Procurement Agreements (LPAs), the State Contracting Manual (SCM), Small Business (SB) and Disabled Veteran Business Enterprise (DVBE) preference and certification rules, and competitive bid thresholds that vary by acquisition type. Procurement officers — especially at smaller agencies — spend significant time determining the correct procurement vehicle, calculating SB/DVBE participation goals, and ensuring compliance with SCM requirements. Vendors seeking CMAS certification or SB/DVBE certification face complex applications and documentation requirements.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Procurement Vehicle Selection (Priority: P1)

A state agency procurement officer needs to purchase $150,000 in IT professional services and needs to identify the appropriate procurement vehicle and required approvals.

**Why this priority**: Choosing the wrong procurement vehicle — or missing required approvals — creates audit findings, contract rescissions, and project delays. This is the most common and highest-risk procurement question for agency staff.

**Acceptance Scenarios**:
1. **Given** a procurement officer asks "I need to procure $150K in IT project management services. Can I use CMAS? What approvals do I need?", **Then** the agent confirms IT services are CMAS-eligible, explains the informal competitive bid requirement for IT contracts $50K-$250K, and lists the required approvals (Department Director delegation)
2. **Given** a procurement officer asks about the difference between CMAS, MSA, and SWPD contracts, **Then** the agent explains each vehicle, their use cases, and when a competitive bid is required vs. direct award
3. **Given** a procurement officer asks about a non-IT purchase over $100K, **Then** the agent identifies the applicable SCM Chapter (Vol. 1 or 2) requirements and IFB/RFP threshold rules
4. **Given** a procurement officer asks about an emergency purchase, **Then** the agent explains the Emergency Acquisition authority under Government Code §14600 and required after-the-fact documentation
5. **Given** a procurement officer asks about a purchase involving IT software, **Then** the agent reminds them of the CDT Technology Review requirement for software over the threshold amount

---

### User Story 2 — Small Business & DVBE Program Compliance (Priority: P2)

A state agency needs to determine its SB and DVBE participation goals and document compliance for a $500K construction services contract.

**Acceptance Scenarios**:
1. **Given** a procurement officer asks "What is the SB participation goal for a $500K construction contract?", **Then** the agent returns the 25% SB participation goal and 3% DVBE goal and explains how to document good faith efforts if goals are not met
2. **Given** a vendor asks how to apply for SB certification with the California Department of General Services, **Then** the agent explains the eligibility criteria (revenue limits, ownership requirements), required documents, and the CalEPA/DGS online certification portal
3. **Given** an agency asks about a SB/DVBE waiver request, **Then** the agent explains when waivers are available, the required documentation, and the DGS approval process
4. **Given** a DVBE asks about the 5% DVBE incentive for competitive bids, **Then** the agent explains the incentive calculation formula and documentation requirements

---

### User Story 3 — CMAS Vendor Certification (Priority: P3)

A vendor wants to add a new product/service to their existing CMAS schedule.

**Acceptance Scenarios**:
1. **Given** a vendor asks "I have a CMAS IT schedule. How do I add a new software product?", **Then** the agent returns the CMAS modification process, required federal GSA schedule documentation, and typical processing timeline from mock CMAS data
2. **Given** a vendor asks about initial CMAS certification for a cloud services product, **Then** the agent explains the GSA Federal Supply Schedule prerequisite, the California-specific modifications required, and the submission process

---

### User Story 4 — State Surplus Property (Priority: P4)

A state agency needs to surplus obsolete computer equipment and a nonprofit wants to know how to purchase surplus state property.

**Acceptance Scenarios**:
1. **Given** a state agency asks "How do we surplus 50 obsolete laptops that contain state data?", **Then** the agent explains the data sanitization requirement (NIST 800-88), the DGS Surplus Property program transfer form, and e-waste disposal options
2. **Given** a nonprofit asks "How can our school district purchase surplus computers from the state?", **Then** the agent explains the Donated Property for Education program, eligibility requirements, and the CalRecycle surplus portal

---

## Compliance & Governance

- **EO N-12-23**: Agent identifies itself as AI; procurement determinations require procurement officer review and approval
- **SCM Compliance**: Agent cites SCM volume and chapter for all procurement guidance
- **CCPA/CPRA**: No vendor or procurement officer personal data collected
- **SB 96 / Government Code §14838**: SB/DVBE program guidance cites applicable code sections
- **Scope Boundary**: Agent does not draft actual contracts or solicitations; it guides the procurement officer to the correct process

---

## Tech Stack

| Component    | Technology                                                        | Notes                                                                   |
| ------------ | ----------------------------------------------------------------- | ----------------------------------------------------------------------- |
| QueryAgent   | Azure OpenAI GPT-4o                                               | Intent: vehicle selection / SB-DVBE / CMAS / surplus                    |
| RouterAgent  | Semantic Kernel                                                   | Routes to 4 domain handlers; routes to CDT for IT-specific requirements |
| ActionAgent  | FastAPI + AI Search                                               | Knowledge base: SCM Vol 1 & 2, CMAS catalog, SB/DVBE program rules      |
| Data Sources | DGS publications, SCM, CMAS catalog (mock), Government Code (RAG) |                                                                         |
| Frontend     | React 18 + TypeScript                                             | Procurement vehicle selector wizard + SB/DVBE goal calculator           |
| Compliance   | SCM citations required, IT review routing, no contract drafting   |                                                                         |
