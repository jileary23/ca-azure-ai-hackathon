# Feature Specification: CCHCS Clinical Support Agent

**Feature Branch**: `012-cchcs-clinical-support-agent`  
**Created**: 2026-05-05  
**Status**: Draft  
**Agency**: California Correctional Health Care Services (CCHCS)  
**Programs**: Medical Services, Mental Health Program (MHSDS), Dental Services, Pharmacy  
**Pattern Analog**: Medi-Cal Eligibility Agent (003)

---

## Problem Context

CCHCS provides constitutionally mandated health care to approximately 96,000 incarcerated people across 31 CDCR institutions, following a federal court receiver mandate under *Plata v. Schwarzenegger*. Medical staff — physicians, nurses, mental health clinicians, and dentists — navigate a complex set of clinical policies including the Health Care Services Policy & Procedure Manual (HCSPP), MHSDS Program Guide, Dental Program Guidelines, and Pharmacy formulary documents. The sheer volume of policy updates, the geographic distribution of 31 institutions, and the complexity of treating a high-acuity population (high rates of chronic disease, mental illness, and substance use disorder) makes rapid, accurate policy guidance critical for clinical quality and legal compliance.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Clinical Policy Lookup (Priority: P1)

A registered nurse at a Level III institution needs to confirm the CCHCS policy for management of a patient with chest pain who refuses evaluation.

**Why this priority**: Clinical policy adherence is both a patient safety requirement and a legal obligation under the Plata receivership. Reducing time spent navigating HCSPP PDFs directly reduces risk of policy deviations that generate Compliance Monitoring Reports.

**Acceptance Scenarios**:
1. **Given** a nurse asks "What is the CCHCS policy for managing a patient who refuses evaluation for chest pain?", **Then** the agent returns the applicable HCSPP section on Informed Refusal, required documentation, and escalation steps
2. **Given** a clinician asks about the medication formulary for a specific antihypertensive, **Then** the agent returns the formulary tier, non-formulary request process, and criteria from mock CCHCS formulary data
3. **Given** a staff member asks about a policy that was recently updated, **Then** the agent returns the most recently indexed version with an update date and recommends verifying with the CCHCS Policy Portal
4. **Given** a query involves a complex clinical scenario requiring physician judgment, **Then** the agent provides the relevant policy guidance and explicitly recommends physician review
5. **Given** a query involves potential patient safety emergency, **Then** the agent immediately routes to emergency response protocols and provides 24-hour clinical administrator contact

---

### User Story 2 — Mental Health Program Guide Navigation (Priority: P2)

A clinician in the Mental Health Crisis Bed (MHCB) unit needs to quickly locate the criteria for placing a patient in Enhanced Outpatient Program (EOP) housing.

**Acceptance Scenarios**:
1. **Given** a clinician asks "What are the placement criteria for EOP vs. CCCMS?", **Then** the agent returns the MHSDS Program Guide level-of-care criteria with distinguishing symptoms and functional impairment thresholds
2. **Given** a clinician asks about the documentation required for a Mental Health Crisis Bed admission, **Then** the agent returns the required forms, timeframes, and supervising psychiatrist notification requirements
3. **Given** a clinician asks about suicide risk assessment tools mandated by CCHCS, **Then** the agent identifies the Columbia Suicide Severity Rating Scale (C-SSRS) requirement and applicable policy sections

---

### User Story 3 — Pharmacy Formulary & Non-Formulary Requests (Priority: P3)

A physician needs to prescribe a non-formulary medication and needs to know the non-formulary request process.

**Acceptance Scenarios**:
1. **Given** a physician asks "How do I request a non-formulary medication for a patient with treatment-resistant depression?", **Then** the agent returns the Non-Formulary Drug Request form number, clinical criteria required, and typical turnaround time
2. **Given** a physician asks about a specific drug interaction within the formulary, **Then** the agent notes this is outside the agent's scope and recommends consulting CCHCS Pharmacy or a clinical pharmacist
3. **Given** a physician asks about controlled substance prescribing limits in a CDCR institution, **Then** the agent returns the applicable HCSPP section on controlled substance management

---

### User Story 4 — Staff Administrative Guidance (Priority: P4)

A newly hired medical officer asks about CCHCS onboarding requirements, mandatory training, and credentialing timelines.

**Acceptance Scenarios**:
1. **Given** a new hire asks about initial mandatory training requirements, **Then** the agent returns the CCHCS onboarding checklist with training module names, due dates, and the CDCR Learning Management System link
2. **Given** a staff member asks about the privileging and credentialing process for a new physician, **Then** the agent returns the credentialing steps, required documents, and typical timeline

---

## Compliance & Governance

- **EO N-12-23**: Agent identifies itself as AI; all clinical guidance is policy-reference only, not a substitute for clinical judgment
- **HIPAA / CMIA**: Agent does not access or display any individual patient health records; operates on published policy documents only
- **Plata Receivership**: Agent outputs are advisory; compliance determinations remain with CCHCS clinical leadership
- **CCPA/CPRA**: No patient or staff PII collected or retained
- **Safety Guardrail**: Any query indicating a medical emergency immediately routes to emergency protocols

---

## Tech Stack

| Component    | Technology                                              | Notes                                                       |
| ------------ | ------------------------------------------------------- | ----------------------------------------------------------- |
| QueryAgent   | Azure OpenAI GPT-4o                                     | Intent: clinical policy / MHSDS / pharmacy / admin          |
| RouterAgent  | Semantic Kernel                                         | Routes to 4 domain handlers; emergency escalation path      |
| ActionAgent  | FastAPI + AI Search                                     | Knowledge base: HCSPP, MHSDS Program Guide, Formulary (RAG) |
| Data Sources | CCHCS Policy Portal documents, MHSDS Program Guide      | Staff-facing internal use                                   |
| Frontend     | React 18 + TypeScript                                   | Policy search with section deep-links                       |
| Compliance   | HIPAA guardrails, no PHI, emergency escalation required |                                                             |
