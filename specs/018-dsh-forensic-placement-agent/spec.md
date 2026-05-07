# Feature Specification: DSH Forensic Placement Intelligence Agent

**Feature Branch**: `018-dsh-forensic-placement-agent`  
**Created**: 2026-05-05  
**Status**: Draft  
**Agency**: Department of State Hospitals (DSH)  
**Programs**: Incompetent to Stand Trial (IST), Not Guilty by Reason of Insanity (NGI), Lanterman-Petris-Short (LPS), Sexually Violent Predator (SVP)  
**Pattern Analog**: Cross-Agency Knowledge Hub (006)

---

## Problem Context

DSH operates five state psychiatric hospitals (Atascadero, Coalinga, Metropolitan, Napa, Patton) with approximately 6,200 patients. The vast majority are forensically committed — placed by courts under four distinct legal pathways: IST (incompetent to stand trial), NGI (not guilty by reason of insanity), LPS (civil commitment), and SVP (sexually violent predator). Court-appointed attorneys, public defenders, county mental health staff, CDCR clinical staff, and county correctional judges must navigate highly specialized, frequently misunderstood legal timelines, restoration-to-competency protocols, hospital placement procedures, and conditional release (CONREP) program requirements. Delays in correctly processing commitment paperwork, computing maximum commitment periods, or understanding restoration criteria create patient harm and court calendar backlogs.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — IST Commitment & Restoration Guidance (Priority: P1)

A county public defender needs to understand the maximum commitment period and competency restoration timeline for a client found IST on a felony charge.

**Why this priority**: IST commitments represent the highest-volume category of DSH admissions and generate the most time-sensitive legal questions. Errors in calculating maximum commitment periods (Penal Code §1370) have direct liberty implications for defendants.

**Acceptance Scenarios**:
1. **Given** a defense attorney asks "My client was found IST on a felony with a maximum sentence of 6 years. What is the maximum DSH commitment period?", **Then** the agent returns the Penal Code §1370 maximum commitment calculation: one-third of the maximum sentence or 3 years, whichever is less, with the applicable code citation
2. **Given** a county mental health attorney asks "What are DSH's criteria for certifying a patient as restored to competency?", **Then** the agent returns the DSH competency restoration criteria (clinical standards under PC §1372), the court notification process, and typical documentation required
3. **Given** a public defender asks about outpatient IST restoration programs as an alternative to DSH hospitalization, **Then** the agent explains the Penal Code §1370.01 outpatient program criteria, county availability, and the court approval process
4. **Given** a query involves a misdemeanor IST commitment, **Then** the agent explains the different maximum commitment period under PC §1370.01 vs. felony IST and routes to the county jail-based competency restoration program if applicable
5. **Given** a query involves a client who has exceeded their maximum commitment period, **Then** the agent flags the potential PC §1370(c) hearing requirement and routes to legal team escalation

---

### User Story 2 — NGI Conditional Release (CONREP) Guidance (Priority: P2)

A DSH treatment team member needs to understand the conditional release criteria and CONREP supervision requirements for an NGI patient approaching community transition.

**Acceptance Scenarios**:
1. **Given** a DSH social worker asks "What are the criteria for recommending an NGI patient for CONREP?", **Then** the agent returns the Penal Code §1600-1610 CONREP criteria: low community risk, identified placement, treatment compliance history
2. **Given** a DSH clinician asks about the CONREP hearing process, **Then** the agent explains the DSH report submission to the court, the victim notification requirement, and the court hearing timeline
3. **Given** a CONREP provider asks about conditions of release and revocation triggers, **Then** the agent explains standard CONREP conditions and the PC §1608 revocation process for violations

---

### User Story 3 — LPS Civil Commitment Guidance (Priority: P3)

A county mental health clinic staff member needs to understand the Lanterman-Petris-Short Act holds and conservatorship pathways.

**Acceptance Scenarios**:
1. **Given** a mental health clinician asks "What is the difference between a 5150, 5250, 5270, and a Murphy conservatorship?", **Then** the agent explains each hold type, duration, legal standard, and the progression pathway under WIC §5150-5350
2. **Given** a county public guardian asks about the LPS conservatorship annual review process, **Then** the agent returns the Welfare & Institutions Code review hearing requirements and the recommitment petition timeline

---

### User Story 4 — Placement & Transfer Process (Priority: P4)

A county correctional facility needs to understand the process for transferring a patient from county jail to DSH for IST restoration.

**Acceptance Scenarios**:
1. **Given** a county jail mental health coordinator asks "What documents are required to transfer a patient to DSH for IST restoration?", **Then** the agent returns the required court order (PC §1370), transport order, medical clearance, and medical records packet requirements
2. **Given** a county court coordinator asks about DSH bed availability assessment, **Then** the agent explains the 15-day placement timeline under PC §1370(a)(1)(B) and the DSH Patient Flow process

---

## Compliance & Governance

- **EO N-12-23**: Agent identifies itself as AI; all legal commitment calculations require attorney and judicial review
- **HIPAA / CMIA**: Agent does not access patient records; operates on published legal statutes and DSH policy only
- **Penal Code / Welfare & Institutions Code**: All commitment period calculations cite applicable PC/WIC sections
- **CCPA/CPRA**: No patient, attorney, or court personal data collected or retained
- **Privilege Safeguard**: Agent notes that queries involving a specific named patient should not be entered; guidance is statute-based only

---

## Tech Stack

| Component    | Technology                                                                | Notes                                                     |
| ------------ | ------------------------------------------------------------------------- | --------------------------------------------------------- |
| QueryAgent   | Azure OpenAI GPT-4o                                                       | Intent: IST / NGI / LPS / SVP / placement / CONREP        |
| RouterAgent  | Semantic Kernel                                                           | Routes to 4 commitment-type handlers + CONREP handler     |
| ActionAgent  | FastAPI + AI Search                                                       | Knowledge base: Penal Code, WIC, DSH Policy Manuals (RAG) |
| Data Sources | California Penal Code, WIC, DSH Hospital Policy Documents                 |                                                           |
| Frontend     | React 18 + TypeScript                                                     | Commitment pathway selector + timeline calculator         |
| Compliance   | No patient data, PC/WIC citations mandatory, attorney escalation triggers |                                                           |
