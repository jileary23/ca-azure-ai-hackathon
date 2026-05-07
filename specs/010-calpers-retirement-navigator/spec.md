# Feature Specification: CalPERS Retirement Benefits Navigator

**Feature Branch**: `010-calpers-retirement-navigator`  
**Created**: 2026-05-05  
**Status**: Draft  
**Agency**: California Public Employees' Retirement System (CalPERS)  
**Programs**: Pension (PEPRA/Classic), Health Benefits, Long-Term Care, Death Benefits  
**Pattern Analog**: BenefitsCal Navigator (001)

---

## Problem Context

CalPERS serves approximately 2 million members — active state and local public employees, retirees, and survivors. The retirement decision is one of the most consequential financial decisions a public employee makes, yet most members have limited financial literacy around pension formulas, survivor benefit elections, and health plan coordination. Uninformed decisions (e.g., choosing the wrong retirement option) cannot be reversed after retirement begins. CalPERS contact center demand peaks during open enrollment windows and before major plan changes, generating wait times exceeding 45 minutes. The rise of "pension spiking" audits and PEPRA reform compliance requirements also creates significant employer inquiry load.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Retirement Formula & Eligibility Q&A (Priority: P1)

A state employee approaching retirement asks the agent to explain their pension formula, service credit requirements, and earliest retirement date.

**Why this priority**: The foundational value proposition. Most CalPERS member inquiries begin with "how is my pension calculated?" Accurate formula guidance prevents member confusion and reduces advisors to focus on complex exceptions.

**Acceptance Scenarios**:
1. **Given** a member asks "I have 28 years of Classic state safety service. When can I retire and what is my benefit formula?", **Then** the agent explains the 2% at 50 or 3% at 50 safety formula (based on tier) and minimum retirement age requirements
2. **Given** a member asks about PEPRA vs. Classic membership, **Then** the agent explains the key differences: formula, benefit cap, final compensation calculation period, and which tier the member likely falls in based on hire date
3. **Given** a member asks "What does final compensation mean for my pension?", **Then** the agent explains the 1-year vs. 3-year final compensation period and which applies based on membership tier
4. **Given** a member asks about a formula that doesn't exist (e.g., "5% at 55"), **Then** the agent corrects the misunderstanding and explains the actual formulas available
5. **Given** an ambiguous query without membership details, **Then** the agent asks clarifying questions about hire date, employer type, and membership tier before answering

---

### User Story 2 — Health Plan Enrollment & Comparison (Priority: P2)

A CalPERS retiree asks the agent to compare health plans available in their county and understand Medicare coordination rules.

**Acceptance Scenarios**:
1. **Given** a retiree asks "What CalPERS health plans are available in Sacramento County for a retiree with Medicare Part A & B?", **Then** the agent lists available plans, premiums, and whether they coordinate with Medicare
2. **Given** a member asks about the Open Enrollment period, **Then** the agent explains the annual window and the rule that elections are irrevocable outside OE (except qualifying life events)
3. **Given** a retiree asks about the state's premium contribution, **Then** the agent explains the employer contribution formula (based on bargaining unit or retiree category) from current plan documents

---

### User Story 3 — Service Credit Purchase (Priority: P3)

A member asks whether they can purchase service credit for prior employment and what the cost rules are.

**Acceptance Scenarios**:
1. **Given** a member asks about purchasing "airtime" or non-qualified service credit, **Then** the agent explains PEPRA restrictions on airtime purchases and that Classic members may have different options
2. **Given** a member asks about redepositing previously refunded service credit, **Then** the agent explains the redeposit process, interest charges, and timeline
3. **Given** a member asks about reciprocal retirement service, **Then** the agent explains CalPERS reciprocal agreements with other California public pension systems

---

### User Story 4 — Survivor & Death Benefits (Priority: P4)

A member or surviving family member asks about death benefits, survivor continuance, and beneficiary designations.

**Acceptance Scenarios**:
1. **Given** a member asks "If I die before retiring, what benefits will my spouse receive?", **Then** the agent explains pre-retirement death benefits, survivor continuance options, and the basic death benefit
2. **Given** a retired member asks which retirement option election maximizes survivor benefit, **Then** the agent explains Option 1, 2, 3, 4, and the unmodified allowance tradeoffs — without making a specific recommendation (compliant with financial advice regulations)
3. **Given** a surviving spouse asks about reporting a member's death, **Then** the agent provides the reporting process and directs to the authenticated myCalPERS portal

---

## Compliance & Governance

- **EO N-12-23**: Agent identifies itself as AI; all benefit estimates are illustrative, not binding CalPERS determinations
- **CCPA/CPRA**: No member account data accessed; agent operates on published plan documents only
- **IRS Circular 230 / CA Financial Code**: Agent provides general educational guidance, not financial advice; directs members to licensed advisors for tax planning
- **CalPERS Board Policy**: Agent cannot provide binding elections, estimates, or determinations — all require authenticated myCalPERS portal
- **Government Code §20000+**: Responses cite applicable code sections for member verification

---

## Tech Stack

| Component    | Technology                                                    | Notes                                                                |
| ------------ | ------------------------------------------------------------- | -------------------------------------------------------------------- |
| QueryAgent   | Azure OpenAI GPT-4o                                           | Intent: pension formula / health / service credit / death benefits   |
| RouterAgent  | Semantic Kernel                                               | Routes to 5 domain handlers                                          |
| ActionAgent  | FastAPI + AI Search                                           | Knowledge base: Member Handbook, PEPRA documents, Health Plan guides |
| Data Sources | CalPERS Member Publications (RAG)                             | Public documents only; no member account data                        |
| Frontend     | React 18 + TypeScript                                         | Retirement calculator UI with illustrative projections               |
| Compliance   | Advisory only, no account access, IRS Circular 230 guardrails |                                                                      |
