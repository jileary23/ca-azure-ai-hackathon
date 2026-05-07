# Feature Specification: CDTFA Tax Compliance Navigator

**Feature Branch**: `015-cdtfa-tax-compliance-navigator`  
**Created**: 2026-05-05  
**Status**: Draft  
**Agency**: California Department of Tax and Fee Administration (CDTFA)  
**Programs**: Sales & Use Tax, Cannabis Tax, Fuel Tax (IFTA/MCFT), Cigarette & Tobacco Tax  
**Pattern Analog**: BenefitsCal Navigator (001)

---

## Problem Context

CDTFA administers more than 40 tax and fee programs generating approximately $90 billion in annual revenue — including sales and use tax, cannabis excise tax, fuel taxes, and cigarette/tobacco taxes. California's sales and use tax is among the most complex in the United States: rates vary by county, city, and special district; taxability rules differ by product category; and exemptions require specific documentation. Businesses registering for a seller's permit, filing their first return, or navigating an audit face steep learning curves. CDTFA's contact center handles thousands of calls monthly about registration, taxability determinations, and audit procedures — many of which could be resolved via accurate AI guidance.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Taxability Determination (Priority: P1)

A small business owner needs to determine whether a specific product or service they sell is taxable in California.

**Why this priority**: Taxability determination is the most common and consequential question for new businesses. Incorrect taxability determinations result in under-collection (creating audit liability) or over-collection (harming customers). This is the highest-volume query category for CDTFA.

**Acceptance Scenarios**:
1. **Given** a retailer asks "Is a custom-made wedding cake taxable in California?", **Then** the agent explains the food products exemption, the "hot prepared food" rule, and why a custom wedding cake at a bakery is generally taxable
2. **Given** a SaaS company asks "Is my software-as-a-service subscription taxable in California?", **Then** the agent explains the tangible personal property definition, the Digital Goods rule, and why California generally does not tax pure SaaS
3. **Given** a cannabis retailer asks "How do I calculate the cannabis excise tax on a $100 retail sale?", **Then** the agent applies the current 15% excise tax rate, explains the markup calculation, and summarizes who is responsible for remitting each component
4. **Given** a retailer asks about a taxability question involving a complex exemption (e.g., partial manufacturing exemption), **Then** the agent explains the general rules and recommends a CDTFA written tax advice (WTA) request for binding guidance
5. **Given** a business asks about sales tax rates for a specific city, **Then** the agent returns the applicable combined state, county, and local rate from mock rate data and explains the rate components

---

### User Story 2 — Seller's Permit Registration (Priority: P2)

A new business owner asks how to register for a California seller's permit and what business information is required.

**Acceptance Scenarios**:
1. **Given** a business owner asks "I'm starting an online Etsy store in California. Do I need a seller's permit?", **Then** the agent explains the nexus rules, the remote seller threshold, and provides the CDTFA online registration URL
2. **Given** a business asks about security deposit requirements at registration, **Then** the agent explains how CDTFA assesses and can waive security deposits for new businesses with good compliance history
3. **Given** a nonprofit asks if they are exempt from obtaining a seller's permit, **Then** the agent explains that nonprofits generally must collect sales tax on taxable sales and explains the BOE 400-AP exemption certificate process

---

### User Story 3 — Audit & Compliance Guidance (Priority: P3)

A business owner receives a CDTFA audit notice and needs to understand the audit process.

**Acceptance Scenarios**:
1. **Given** a business owner asks "I received a CDTFA audit letter. What records do I need to provide and what are my rights?", **Then** the agent explains the typical records requested (invoices, purchase records, Z-tapes), the statutory records retention period (4 years), and the right to representation
2. **Given** a business asks about a Managed Audit Program (MAP), **Then** the agent explains MAP eligibility, the self-review process, and its benefits (penalty waiver, extended filing period)
3. **Given** a business asks about a jeopardy assessment, **Then** the agent explains what triggers a jeopardy assessment, the timeframes for protest, and the importance of consulting a tax professional

---

### User Story 4 — IFTA & Fuel Tax (Priority: P4)

A motor carrier asks about International Fuel Tax Agreement (IFTA) registration and quarterly reporting requirements.

**Acceptance Scenarios**:
1. **Given** a carrier asks "My truck operates in California and Nevada. Do I need an IFTA license?", **Then** the agent explains the qualified motor vehicle definition, the 2-jurisdiction threshold, and how to register for IFTA through CDTFA
2. **Given** a carrier asks about the IFTA quarterly return calculation, **Then** the agent explains total miles, taxable miles, total gallons purchased, and net tax calculation logic with a simple worked example

---

## Compliance & Governance

- **EO N-12-23**: Agent identifies itself as AI; outputs are educational guidance only, not binding CDTFA tax advice
- **Revenue & Taxation Code**: Responses cite applicable R&TC sections for business verification
- **CCPA/CPRA**: No taxpayer account data accessed; agent operates on published guidance only
- **Written Tax Advice**: Agent proactively recommends CDTFA written tax advice (WTA) request for complex or binding determinations
- **Tax Privacy**: Agent declines to discuss specific taxpayer account information under R&TC §19542

---

## Tech Stack

| Component    | Technology                                                            | Notes                                                       |
| ------------ | --------------------------------------------------------------------- | ----------------------------------------------------------- |
| QueryAgent   | Azure OpenAI GPT-4o                                                   | Intent: taxability / registration / audit / fuel tax        |
| RouterAgent  | Semantic Kernel                                                       | Routes to 5 domain handlers by tax program                  |
| ActionAgent  | FastAPI + AI Search                                                   | Knowledge base: CDTFA publications, tax guides, rate tables |
| Data Sources | CDTFA Publication 31, 61, 73, rate database (mock) (RAG)              |                                                             |
| Frontend     | React 18 + TypeScript                                                 | Taxability wizard + rate lookup by city/county              |
| Compliance   | R&TC citations required, WTA recommendation trigger, no taxpayer data |                                                             |
