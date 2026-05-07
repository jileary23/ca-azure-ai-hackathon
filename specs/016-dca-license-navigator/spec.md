# Feature Specification: DCA License Navigator

**Feature Branch**: `016-dca-license-navigator`  
**Created**: 2026-05-05  
**Status**: Draft  
**Agency**: California Department of Consumer Affairs (DCA)  
**Programs**: Professional Licensing (37 boards/bureaus), License Lookup, Complaint Filing, Renewal  
**Pattern Analog**: Permit Streamliner (004)

---

## Problem Context

DCA oversees 37 regulatory boards, bureaus, and committees that license more than 3.6 million professionals across 200+ license types — from physicians to contractors to cosmetologists. Applicants for new licenses face inconsistent application instructions, unclear experience documentation requirements, and exam eligibility rules that vary substantially across DCA entities. Licensees approaching renewal dates need accurate renewal timeline, continuing education (CE) requirements, and fee information — and must navigate DCA's BreEZe licensing system which combines dozens of legacy systems. Consumers seeking to verify a license or file a complaint face a fragmented website experience across 37 sub-sites.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — License Application Requirements (Priority: P1)

An applicant for a new professional license needs to understand the exact requirements, experience documentation, and timeline for their specific license type.

**Why this priority**: License application errors and incomplete submissions are the primary cause of processing delays — sometimes extending timelines by months. Accurate, license-type-specific guidance reduces application rejection rates and accelerates time-to-licensure for California professionals.

**Acceptance Scenarios**:
1. **Given** an applicant asks "What are the requirements to apply for a Registered Nurse license by examination in California?", **Then** the agent returns BRN application requirements: NCLEX eligibility, education transcript submission, background check, fingerprint requirements, and current fees
2. **Given** an applicant asks about experience documentation for a Contractor's license (CSLB), **Then** the agent returns the 4-year journeyman experience requirement, acceptable verification forms, and the journeyman letter format
3. **Given** an applicant asks "How long does it take to get a California real estate salesperson license?", **Then** the agent returns DRE's typical processing timeline, the pre-licensing education hours required, and the exam application process
4. **Given** an applicant asks about a license type not administered by DCA (e.g., teaching credential), **Then** the agent correctly identifies the Commission on Teacher Credentialing (CTC) as the responsible agency and provides the CTC website
5. **Given** an applicant asks about an out-of-state license reciprocity or endorsement, **Then** the agent explains whether the specific DCA board offers reciprocity and the applicable requirements

---

### User Story 2 — License Renewal Requirements (Priority: P2)

A licensed professional needs to know their renewal deadline, CE requirements, and renewal fee before their license expires.

**Acceptance Scenarios**:
1. **Given** a licensed cosmetologist asks "My Cosmetology license expires in 6 months. What continuing education do I need for renewal?", **Then** the agent returns the CBEC 8-hour CE requirement, approved topics, and the BreEZe renewal portal URL
2. **Given** a licensed general contractor (B license) asks about renewal, **Then** the agent returns the CSLB renewal period, license bond and workers' comp certificate requirements, and fee amounts
3. **Given** a licensee is past their expiration date, **Then** the agent explains the delinquent renewal process, penalty fees, and whether a current license is required to continue practicing

---

### User Story 3 — License Verification (Priority: P3)

A member of the public wants to verify that a professional is currently licensed and in good standing before hiring them.

**Acceptance Scenarios**:
1. **Given** a consumer asks "How do I check if a contractor is licensed in California?", **Then** the agent explains the CSLB License Check tool, URL, and how to interpret license status codes (active, inactive, expired, suspended)
2. **Given** a consumer asks about a licensee with a disciplinary action, **Then** the agent explains that disciplinary actions are public record on BreEZe and what citation types mean (citation, probation, revocation)
3. **Given** a consumer asks about verifying a healthcare provider license, **Then** the agent returns the BreEZe public search URL and explains which DCA boards cover the queried profession

---

### User Story 4 — Consumer Complaint Filing (Priority: P4)

A consumer wants to file a complaint against a licensed professional for poor workmanship or fraud.

**Acceptance Scenarios**:
1. **Given** a consumer asks "How do I file a complaint against a contractor who did shoddy work on my bathroom remodel?", **Then** the agent returns the CSLB complaint process, required documentation (contracts, photos, invoices), and the CSLB Arbitration Program for disputes under $12,500
2. **Given** a consumer asks about complaint status, **Then** the agent explains that complaint status is not publicly available and directs to the CSLB inquiry phone number
3. **Given** a consumer has a complaint about a healthcare professional, **Then** the agent routes to the appropriate board's complaint form (MBC, BRN, DPH, etc.) with the correct URL

---

## Compliance & Governance

- **EO N-12-23**: Agent identifies itself as AI; outputs are guidance only, not official board determinations
- **Business & Professions Code**: Responses cite applicable B&P Code sections and board-specific regulations
- **CCPA/CPRA**: No applicant or licensee personal data accessed; agent operates on published requirements
- **Cross-Board Accuracy**: Agent maintains distinct knowledge bases per board/bureau to prevent cross-contamination of requirements
- **Unauthorized Practice**: Agent includes disclaimers that unlicensed practice may violate B&P Code §§ related to each profession

---

## Tech Stack

| Component    | Technology                                                                      | Notes                                                             |
| ------------ | ------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| QueryAgent   | Azure OpenAI GPT-4o                                                             | Intent: new application / renewal / verification / complaint      |
| RouterAgent  | Semantic Kernel                                                                 | Routes to 37 board-specific handlers (grouped by profession type) |
| ActionAgent  | FastAPI + AI Search                                                             | Knowledge base: per-board application checklists, CE requirements |
| Data Sources | DCA board websites, BreEZe guides, B&P Code (RAG)                               | Public documents                                                  |
| Frontend     | React 18 + TypeScript                                                           | License type picker → requirements checklist + renewal calculator |
| Compliance   | B&P Code citations, cross-board routing accuracy, unauthorized practice warning |                                                                   |
