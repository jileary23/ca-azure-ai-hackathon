# Feature Specification: CA State Fund Workers' Compensation Claims Navigator

**Feature Branch**: `020-statefund-workers-comp-navigator`  
**Created**: 2026-05-05  
**Status**: Draft  
**Agency**: State Compensation Insurance Fund (CA State Fund)  
**Programs**: Workers' Compensation Claims, Employer Policy, Medical Provider Billing, Safety Programs  
**Pattern Analog**: BenefitsCal Navigator (001) + CDI Consumer Agent (013)

---

## Problem Context

CA State Fund has insured California employers since 1914, currently serving more than 150,000 policyholders — with a unique statutory mission to ensure workers' compensation coverage is available to all California employers, including small businesses and state agencies that struggle to find coverage in the private market. Workers' compensation is one of the most legally and medically complex insurance systems in the United States. Injured workers navigating the claims process — medical treatment authorization, independent medical review (IMR), temporary and permanent disability, return-to-work — lack plain-language guidance and often forego entitled benefits due to confusion. Employers managing CA State Fund policies face questions about audit preparation, experience modification (X-MOD) factors, and the OSHA-required Injury and Illness Prevention Program (IIPP). The workers' comp system generates tens of thousands of WCAB disputes annually, many arising from preventable miscommunications.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Injured Worker Claims Navigation (Priority: P1)

An injured worker recently hurt on the job asks about the claim filing process, their rights, and what to expect from the workers' compensation system.

**Why this priority**: Injured workers are the ultimate beneficiaries of the workers' comp system. Many do not receive benefits they are entitled to simply due to lack of information about the claims process — creating both harm and downstream WCAB disputes that cost the system significantly.

**Acceptance Scenarios**:
1. **Given** an injured worker asks "I hurt my back at work yesterday. What should I do first?", **Then** the agent explains: report the injury to your supervisor, receive a DWC-1 claim form within 24 hours (employer obligation under LC §5401), employer's obligation to authorize medical treatment while claim is pending, and the 90-day presumption of compensability
2. **Given** an injured worker asks "How is my temporary disability calculated?", **Then** the agent explains the 2/3 of pre-injury average weekly wage formula, the minimum and maximum TD weekly benefit rates for the current year, and the 104-week duration limit
3. **Given** an injured worker asks "My medical treatment was denied. How do I challenge it?", **Then** the agent explains the Utilization Review (UR) process, the 30-day appeal window, the Independent Medical Review (IMR) process, and how to request an IMR from Maximus Federal Services
4. **Given** an injured worker asks about permanent disability, **Then** the agent explains the AMA Guides rating system, the role of the Qualified Medical Evaluator (QME), the 2005 PDRS, and the difference between permanent disability and future medical care
5. **Given** an injured worker asks about returning to work with limitations, **Then** the agent explains the Supplemental Job Displacement Benefit (SJDB) voucher, the Return-to-Work Supplement Program ($5,000), and what to do if the employer has no modified duty

---

### User Story 2 — Employer Policy & Audit Guidance (Priority: P2)

An employer with a CA State Fund policy receives an audit notice and needs to understand the audit process and premium classification rules.

**Acceptance Scenarios**:
1. **Given** an employer asks "CA State Fund is auditing my payroll. What records should I prepare?", **Then** the agent explains the payroll records required (941s, W-2s, certified payroll for contractors), the 4-year records retention requirement, and how classification codes are determined
2. **Given** an employer asks "My X-MOD factor went up from 1.0 to 1.22 this year. What caused this?", **Then** the agent explains the Experience Modification Rating formula: actual vs. expected losses, primary vs. excess losses, and how a serious claim affects the X-MOD for 3 policy years
3. **Given** an employer asks how to improve their X-MOD, **Then** the agent explains loss control programs, CA State Fund safety consultation services, and the impact of early return-to-work on loss development
4. **Given** an employer asks about their IIPP requirement, **Then** the agent explains the California Labor Code §6401.7 IIPP requirement, the 8 required elements, and how CA State Fund's free safety consultation program can assist

---

### User Story 3 — Medical Treatment Authorization (Priority: P3)

A treating physician or injured worker needs to understand the medical treatment authorization process and timeline.

**Acceptance Scenarios**:
1. **Given** a physician asks "How do I request authorization for an MRI for a workers' comp patient with a lumbar injury?", **Then** the agent explains the Request for Authorization (RFA) form requirement, the UR 5-day standard review timeline, the 24-hour expedited review for urgent cases, and the Medical Treatment Utilization Schedule (MTUS) as the standard of care
2. **Given** an injured worker asks "My doctor requested an epidural steroid injection but it was denied. Is there evidence it is necessary?", **Then** the agent explains that the MTUS is based on evidence-based medicine guidelines, the IMR process for challenging a UR denial, and that they should work with their treating physician on the IMR application
3. **Given** a physician asks about the MTUS chronic pain treatment guidelines, **Then** the agent returns the applicable MTUS chapter summary and the ACOEM guideline basis

---

### User Story 4 — WCAB Dispute Resolution (Priority: P4)

An injured worker or their attorney asks about the Workers' Compensation Appeals Board process for a disputed claim.

**Acceptance Scenarios**:
1. **Given** an injured worker asks "My claim was denied. How do I appeal to the WCAB?", **Then** the agent explains the Application for Adjudication of Claim (WCAB Form 1), the need to file a Declaration of Readiness (DOR) for a hearing, and the option for a free Information and Assistance officer consultation with DWC
2. **Given** an attorney asks about the Lien Activation Fee for a medical provider lien, **Then** the agent explains the LC §4903.06 lien activation fee, the annual activation requirement, and the lien conference process
3. **Given** a claimant asks about settlement options, **Then** the agent explains the difference between a Compromise & Release (C&R) and a Stipulation with Request for Award, and recommends consulting a workers' comp attorney for advice on their specific situation

---

## Compliance & Governance

- **EO N-12-23**: Agent identifies itself as AI; outputs are educational only, not legal or medical advice
- **CA Labor Code §3200+**: All benefit calculations and process guidance cite applicable Labor Code sections
- **CCPA/CPRA**: No claim or account data accessed; agent operates on published statutory and regulatory guidance
- **HIPAA**: Medical information in workers' comp claims is protected; agent does not request or process claim-specific medical data
- **DWC Regulations / WCAB Rules**: Agent cites applicable DWC regulations (8 CCR §§) for procedural guidance
- **Unauthorized Practice of Law**: Agent explicitly recommends consulting a workers' comp attorney for legal advice on specific disputes

---

## Tech Stack

| Component    | Technology                                                                            | Notes                                                                            |
| ------------ | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| QueryAgent   | Azure OpenAI GPT-4o                                                                   | Intent: injured worker / employer / medical provider / WCAB                      |
| RouterAgent  | Semantic Kernel                                                                       | Routes to 4 persona-based handlers; persona detection from initial query         |
| ActionAgent  | FastAPI + AI Search                                                                   | Knowledge base: CA Labor Code, DWC regulations, MTUS, WCAB rules (RAG)           |
| Data Sources | CA Labor Code, DWC publications, MTUS, CA State Fund employer guides                  | Public documents                                                                 |
| Frontend     | React 18 + TypeScript                                                                 | Persona selector (injured worker / employer / provider) + claim process timeline |
| Compliance   | No claim data, LC citations required, unauthorized practice warning, HIPAA guardrails |                                                                                  |
