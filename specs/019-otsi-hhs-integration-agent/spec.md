# Feature Specification: OTSI Health & Human Services AI Integration Agent

**Feature Branch**: `019-otsi-hhs-integration-agent`  
**Created**: 2026-05-05  
**Status**: Draft  
**Agency**: California Health and Human Services Agency — Office of Technology and Solutions Integration (OTSI)  
**Programs**: CalSAWS, MEDS, CalHEERS, CHHS Data De-Identification, API Catalog  
**Pattern Analog**: Cross-Agency Knowledge Hub (006)

---

## Problem Context

OTSI is the technology delivery arm of CHHS, building and maintaining the integrated IT systems used by CDSS, DHCS, DPH, and eight other departments serving millions of Californians. Developer teams working on system integrations face a recurring productivity challenge: navigating thousands of pages of technical documentation, inter-agency data sharing agreements (DSAs), and legacy API specifications scattered across SharePoint sites, Confluence wikis, and PDF repositories. New CHHS program initiatives — like CalAIM, continuous Medi-Cal coverage, and Bolster SAWS 2.0 — require rapid cross-system integration design with complex data privacy constraints (HIPAA, IRS Pub 1075 FTI rules, CCPA). Developers and architects spend 20-40% of project time simply finding and interpreting existing technical documentation.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — CHHS System Integration Q&A (Priority: P1)

An OTSI developer building a new DHCS case management module needs to understand the CalSAWS API integration requirements and data exchange format.

**Why this priority**: Integration documentation discovery is the highest-friction bottleneck for OTSI developer productivity. Faster, more accurate technical guidance directly reduces integration errors, security defects, and project delays across all CHHS programs.

**Acceptance Scenarios**:
1. **Given** a developer asks "What API does CalSAWS expose for querying SNAP household case status and what authentication method is required?", **Then** the agent returns the CalSAWS API endpoint type, authentication method (OAuth 2.0 or mutual TLS), and available case status fields from mock API catalog
2. **Given** a developer asks about the MEDS enrollment data schema for Medi-Cal eligibility, **Then** the agent returns the key data elements, their data types, and the MEDS data dictionary section reference
3. **Given** a developer asks about IRS Publication 1075 compliance requirements for a system that accesses Federal Tax Information (FTI), **Then** the agent returns the applicable IRS Pub 1075 controls: access logging, encryption at rest/transit, incident reporting, and annual self-assessment
4. **Given** a developer asks about an API version that has been deprecated, **Then** the agent informs them of the deprecation date, the replacement endpoint, and migration timeline from mock data
5. **Given** a developer asks about a system outside OTSI's portfolio (e.g., Caltrans SHO system), **Then** the agent acknowledges scope and routes to the appropriate agency contact

---

### User Story 2 — Data Sharing Agreement Navigator (Priority: P2)

A business analyst needs to identify whether a proposed data sharing between CDSS and a county behavioral health department is permissible under existing DSAs and applicable law.

**Acceptance Scenarios**:
1. **Given** an analyst asks "Is there a data sharing agreement that allows CDSS to share CalWORKs participation data with a county behavioral health department?", **Then** the agent returns the applicable CHHS DSA reference, the permissible data elements, and the consent/authorization requirements from mock DSA data
2. **Given** an analyst asks about the minimum necessary principle for HIPAA-covered data within CHHS, **Then** the agent explains HIPAA's minimum necessary standard, its application to CHHS covered components, and the CHHS Privacy Officer contact for complex determinations
3. **Given** an analyst asks about de-identification standards for CHHS program data, **Then** the agent returns the CHHS Data De-Identification Guidelines, Safe Harbor vs. Expert Determination method, and the applicable CHHS policy document

---

### User Story 3 — SIMM Standards & Security Review (Priority: P3)

A project manager preparing a new cloud-hosted CHHS application needs to know the SIMM security review requirements.

**Acceptance Scenarios**:
1. **Given** a project manager asks "What SIMM standards apply to a new cloud application that processes HIPAA-covered data?", **Then** the agent returns the applicable SIMM 5300 series security standards, HIPAA Security Rule alignment, and the CA-PMSO review process
2. **Given** a technical lead asks about the CDT Cybersecurity Review Board (CRB) threshold, **Then** the agent returns the project cost/risk criteria that trigger CRB review and the submission timeline
3. **Given** a developer asks about state-approved cloud service providers, **Then** the agent returns the CDT Cloud Computing Services Policy and the list of pre-approved IaaS/PaaS vendors from mock data

---

### User Story 4 — CalAIM Technical Integration Guidance (Priority: P4)

A DHCS CalAIM program team member needs to understand the technical integration requirements for Enhanced Care Management (ECM) data reporting.

**Acceptance Scenarios**:
1. **Given** a program team member asks "What data does DHCS require managed care plans to submit for ECM monthly reporting and what is the submission format?", **Then** the agent returns the ECM reporting data elements, HL7 FHIR or CSV format requirements, and the submission deadline from mock CalAIM technical specs
2. **Given** a developer asks about the CHHS API Gateway for CalAIM data flows, **Then** the agent explains the CHHS enterprise API gateway, its rate limits, and the onboarding process for managed care plan developers

---

## Compliance & Governance

- **EO N-12-23**: Agent identifies itself as AI; technical guidance is advisory, not a substitute for OTSI architecture review
- **HIPAA / IRS Pub 1075 / CCPA**: Agent enforces scope: no individual beneficiary data, no FTI, no production credentials
- **SIMM Compliance**: Agent cites SIMM section numbers for all security and technology guidance
- **Authentication**: Production deployment uses Azure Entra ID SSO; agent is restricted to OTSI and approved CHHS staff
- **Scope Boundary**: Agent does not expose production API credentials, connection strings, or system access paths

---

## Tech Stack

| Component    | Technology                                                            | Notes                                                                |
| ------------ | --------------------------------------------------------------------- | -------------------------------------------------------------------- |
| QueryAgent   | Azure OpenAI GPT-4o                                                   | Intent: API integration / DSA / SIMM / CalAIM                        |
| RouterAgent  | Semantic Kernel                                                       | Routes to 5 domain handlers (by CHHS system)                         |
| ActionAgent  | FastAPI + AI Search                                                   | Knowledge base: OTSI API catalog, SIMM, CHHS DSA index, CalAIM specs |
| Data Sources | SIMM, CHHS DSA catalog (mock), CalAIM technical specifications (mock) | Internal staff use                                                   |
| Frontend     | React 18 + TypeScript                                                 | System/API browser + DSA search                                      |
| Compliance   | HIPAA/FTI guardrails, Azure Entra ID auth, SIMM citations required    |                                                                      |
