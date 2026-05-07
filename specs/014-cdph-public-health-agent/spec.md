# Feature Specification: CDPH Public Health Intelligence Agent

**Feature Branch**: `014-cdph-public-health-agent`  
**Created**: 2026-05-05  
**Status**: Draft  
**Agency**: California Department of Public Health (CDPH)  
**Programs**: Communicable Disease Control, Immunization, Vital Statistics, Environmental Health, Women Infants & Children (WIC)  
**Pattern Analog**: BenefitsCal Navigator (001) + Wildfire Response Coordinator (002)

---

## Problem Context

CDPH serves as California's lead public health authority for 40 million residents. It manages disease surveillance systems, immunization registries, vital statistics (birth/death certificates), environmental health programs, and the WIC nutrition program serving 800,000+ participants. During disease outbreaks, local public health departments (LHDs) in all 58 California counties need rapid access to CDPH guidance documents, reporting timelines, case definitions, and specimen submission protocols — information currently scattered across CDPH.ca.gov in dozens of individual PDF memos. Simultaneously, the public needs trusted, accurate health guidance during emerging outbreak situations that is faster than official press releases but more reliable than social media.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Disease Reporting & Outbreak Response Guidance (Priority: P1)

A local health officer at a county public health department receives a report of a suspected foodborne illness cluster and needs to know CDPH reporting requirements and investigation protocols.

**Why this priority**: Timely, accurate disease investigation is the core mission of communicable disease control. Faster access to case definitions, reporting timelines, and lab submission guidance directly improves outbreak detection and response speed — potentially preventing additional illness.

**Acceptance Scenarios**:
1. **Given** an LHD nurse asks "What is the CDPH case definition for a confirmed case of Hepatitis A and what is the reporting timeline?", **Then** the agent returns the case definition, the 1-working-day reporting requirement, and the CalREDIE system instructions from mock data
2. **Given** a public health officer asks about specimen submission for a suspected Shiga toxin-producing E. coli (STEC) cluster, **Then** the agent returns the CDPH lab submission requirements, packaging guidelines, and the VRDL contact information
3. **Given** an LHD asks about post-exposure prophylaxis (PEP) protocols for a meningococcal exposure in a daycare, **Then** the agent returns the CDPH guidance on PEP indication criteria and recommended chemoprophylaxis regimen with the relevant guidance document citation
4. **Given** a query involves a Novel or Priority 1 pathogen requiring immediate CDPH notification, **Then** the agent returns the Emergency Operations Center (EOC) contact alongside standard guidance
5. **Given** a query is from a member of the general public about disease risk (not an LHD professional), **Then** the agent responds with publicly appropriate health education content and recommends consulting their local health department

---

### User Story 2 — Immunization & CAIR Guidance (Priority: P2)

A healthcare provider needs to understand California's immunization schedule requirements and how to use the California Immunization Registry (CAIR).

**Acceptance Scenarios**:
1. **Given** a school nurse asks "What vaccines are required for a 7th grader entering a California public school?", **Then** the agent returns the CDPH school immunization requirements for 7th grade entry with the applicable Health & Safety Code section
2. **Given** a provider asks about reporting to CAIR, **Then** the agent explains the mandatory reporting requirement (HSC §120440) and the CAIR reporting portal instructions
3. **Given** a provider asks about an outbreak immunization response, **Then** the agent explains outbreak response vaccination strategies and where to order emergency vaccine stock through CDPH

---

### User Story 3 — Vital Statistics & Birth/Death Records (Priority: P3)

A member of the public needs to obtain a certified copy of a birth or death certificate.

**Acceptance Scenarios**:
1. **Given** a person asks "How do I get a certified copy of a California birth certificate?", **Then** the agent explains the authorized requestor rules (Health & Safety Code §103526), the VitalChek ordering option, the fee, and expected processing time
2. **Given** a person asks about amending a birth certificate (e.g., gender marker change), **Then** the agent explains the Voluntary Declaration of Gender Change process and the applicable HSC sections

---

### User Story 4 — WIC Program Eligibility & Benefits (Priority: P4)

A pregnant woman asks about WIC program eligibility and how to apply in California.

**Acceptance Scenarios**:
1. **Given** a woman asks "I'm pregnant with my second child. Am I eligible for WIC?", **Then** the agent explains income eligibility thresholds, nutritional risk criteria, and how to find a local WIC agency
2. **Given** a WIC participant asks what foods are covered on their WIC card, **Then** the agent explains the California WIC approved food list categories from mock WIC guidance data
3. **Given** a participant asks about eWIC card use at farmers markets, **Then** the agent explains the California Farmers Market WIC program with applicable markets from mock data

---

## Compliance & Governance

- **EO N-12-23**: Agent identifies itself as AI; public health guidance cites CDPH source documents
- **CCPA/CPRA**: No health information collected; disease reports are submitted through official CalREDIE and CDPH systems
- **HIPAA / CMIA**: Agent does not access or process individual patient or case records
- **Emergency Alert Integration**: Outbreak guidance updated from CDPH alert feed in production mode; mock data used in Labs 00-03

---

## Tech Stack

| Component    | Technology                                           | Notes                                                                 |
| ------------ | ---------------------------------------------------- | --------------------------------------------------------------------- |
| QueryAgent   | Azure OpenAI GPT-4o                                  | Intent: disease reporting / immunization / vital stats / WIC          |
| RouterAgent  | Semantic Kernel                                      | Routes to 5 domain handlers; LHD vs. public persona detection         |
| ActionAgent  | FastAPI + AI Search                                  | Knowledge base: CDPH guidance memos, immunization schedules, WIC info |
| Data Sources | CDPH.ca.gov publications, ACIP recommendations (RAG) | Public documents                                                      |
| Frontend     | React 18 + TypeScript                                | Disease reporting checklist + immunization lookup                     |
| Compliance   | HIPAA guardrails, no PHI, source citation required   |                                                                       |
