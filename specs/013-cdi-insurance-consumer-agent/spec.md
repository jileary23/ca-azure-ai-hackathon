# Feature Specification: CDI Insurance Consumer Protection Agent

**Feature Branch**: `013-cdi-insurance-consumer-agent`  
**Created**: 2026-05-05  
**Status**: Draft  
**Agency**: California Department of Insurance (CDI)  
**Programs**: Consumer Complaint Assistance, Rate Review, Licensing, Market Conduct  
**Pattern Analog**: BenefitsCal Navigator (001)

---

## Problem Context

CDI regulates a $310+ billion insurance marketplace and processes more than 300,000 consumer inquiries and complaints annually. Consumers facing insurance denials, claim delays, cancellations, or billing disputes often lack the knowledge to effectively communicate their rights to insurers or to file a formal complaint with CDI. The process for filing a complaint, understanding what CDI can and cannot do, and knowing when to escalate to the Department of Managed Health Care (DMHC) or engage the FAIR Plan is confusing and varies by insurance type. CDI staff spend significant time on calls explaining basic policyholder rights that could be self-served with accurate, plain-language AI guidance.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Insurance Claim Dispute Navigation (Priority: P1)

A homeowner whose wildfire claim was underpaid or denied needs guidance on their rights and how to dispute the claim.

**Why this priority**: Wildfire and natural disaster claim disputes represent CDI's highest-volume, highest-urgency complaint category. Providing immediate, accurate guidance on policyholder rights during post-disaster periods reduces harm and CDI complaint backlog.

**Acceptance Scenarios**:
1. **Given** a homeowner asks "My insurance company offered me $40,000 for smoke damage but the contractor says it will cost $80,000. What are my rights?", **Then** the agent explains the right to a public adjuster, the appraisal process, and the timeframes under California Insurance Code for claim resolution
2. **Given** a consumer asks about a claim denial for "arson" they did not commit, **Then** the agent explains the Notice of Denial requirements under IC §790.03, the right to the claim file, and the CDI complaint process
3. **Given** a consumer asks how to file a complaint against their insurer, **Then** the agent walks them through the CDI online complaint form, required documents, and typical 30-day investigation timeline
4. **Given** a consumer's inquiry is about health insurance (regulated by DMHC, not CDI), **Then** the agent accurately identifies the correct regulator and routes to DMHC Contact Center information
5. **Given** a consumer asks an ambiguous question about their policy, **Then** the agent asks for the type of insurance (auto, homeowners, life, commercial) before answering

---

### User Story 2 — Insurance Cancellation & Non-Renewal Rights (Priority: P2)

A homeowner in a wildfire-risk ZIP code receives a non-renewal notice and asks about their rights.

**Acceptance Scenarios**:
1. **Given** a consumer asks "My insurer cancelled my homeowner's policy because I filed two claims in 3 years. Is this legal?", **Then** the agent explains California's mid-term cancellation restrictions (IC §676) and the allowable cancellation grounds
2. **Given** a consumer asks about non-renewal following a declared disaster, **Then** the agent explains the CDI moratorium on non-renewals in declared disaster areas under IC §675.1
3. **Given** a consumer asks about FAIR Plan eligibility, **Then** the agent explains that FAIR Plan is the insurer of last resort, eligibility criteria, and how to apply through a licensed agent

---

### User Story 3 — Insurance Licensing Verification (Priority: P3)

A consumer wants to verify that an insurance agent or company is licensed in California before purchasing a policy.

**Acceptance Scenarios**:
1. **Given** a consumer asks "How do I check if an insurance agent is licensed in California?", **Then** the agent explains the CDI License Lookup tool, URL, and what the license status categories mean
2. **Given** a consumer asks about a company not appearing in the CDI database, **Then** the agent warns about unlicensed insurer risks and explains how to report suspected fraud to CDI

---

### User Story 4 — Auto Insurance & CLCA Program (Priority: P4)

A low-income California driver asks about the California Low Cost Automobile (CLCA) insurance program.

**Acceptance Scenarios**:
1. **Given** an eligible driver asks "Do I qualify for CLCA insurance?", **Then** the agent explains income thresholds, vehicle value limits, and coverage included
2. **Given** a driver asks about SR-22 filing requirements, **Then** the agent explains what an SR-22 is, when it is required, how long it must be maintained, and how to obtain it through a licensed insurer

---

## Compliance & Governance

- **EO N-12-23**: Agent identifies itself as AI; outputs are educational only, not legal advice
- **CCPA/CPRA**: No consumer PII collected; complaint filing occurs on CDI's official portal only
- **California Insurance Code**: Responses cite applicable IC sections for consumer verification
- **Jurisdictional Accuracy**: Agent distinguishes CDI (all insurance lines except most health) from DMHC (Knox-Keene health plans) and DFPI (specialty finance products) to prevent incorrect routing

---

## Tech Stack

| Component    | Technology                                                 | Notes                                                    |
| ------------ | ---------------------------------------------------------- | -------------------------------------------------------- |
| QueryAgent   | Azure OpenAI GPT-4o                                        | Intent: claim dispute / cancellation / licensing / CLCA  |
| RouterAgent  | Semantic Kernel                                            | Routes to 4 domain handlers + external regulator routing |
| ActionAgent  | FastAPI + AI Search                                        | Knowledge base: CA Insurance Code, CDI Consumer Guides   |
| Data Sources | CDI Consumer Guide PDFs, IC sections, FAIR Plan info (RAG) |                                                          |
| Frontend     | React 18 + TypeScript                                      | Complaint wizard + insurance type selector               |
| Compliance   | Advisory only, jurisdictional accuracy guardrails          |                                                          |
