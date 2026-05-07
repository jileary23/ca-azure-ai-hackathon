# 015 — CDTFA Tax Compliance Navigator

**Agency:** California Department of Tax and Fee Administration (CDTFA)

## Problem Statement

The California Department of Tax and Fee Administration administers over 40 tax and fee programs generating more than $90 billion annually — including sales and use tax, cannabis taxes, fuel taxes, and cigarette taxes. CDTFA processes millions of returns from hundreds of thousands of registered businesses. Businesses — especially small businesses and new registrants — struggle to understand which taxes apply to their business model, navigate multi-rate sales tax calculations for California's 500+ tax jurisdictions, understand nexus rules for online sellers, and interpret complex exemption certificates. CDTFA call centers handle over 1 million contacts annually, with complex tax rate and exemption questions consuming the most staff time.

## Solution Overview

An AI-powered tax compliance navigator that helps California businesses understand their registration requirements, applicable tax rates, filing schedules, exemption eligibility, and audit preparation. The system uses the 3-agent pipeline to understand business type and transaction context, route to the appropriate tax program knowledge base (sales/use, cannabis, fuel, special taxes), and deliver accurate, jurisdiction-aware tax guidance with citations to California Revenue and Taxation Code and CDTFA publications.

## Quick Start

```bash
cd accelerators/015-cdtfa-tax-compliance-navigator

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8015

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Key Use Cases

- **Tax Rate Lookup**: "What is the current sales tax rate for a retail transaction in Culver City, California?"
- **Business Registration Guidance**: "I'm opening an online store shipping goods to California customers from Nevada. Do I need to register with CDTFA? What is economic nexus?"
- **Exemption Certificate Navigator**: "I'm a manufacturer purchasing raw materials. Do I qualify for the manufacturing exemption? What form do I need?"
- **Cannabis Tax Compliance**: "I operate a licensed cannabis dispensary. What taxes apply to my retail sales and what are my reporting timelines?"
- **Audit Preparation**: "CDTFA notified me of a sales tax audit. What records should I gather and what are my rights?"
- **Filing Deadline Calculator**: "I'm a quarterly filer. When is my next sales tax return due, and what happens if I miss the deadline?"

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Data:** CDTFA Publications (73, 31, 45, etc.), CA Revenue & Taxation Code, tax rate schedules, exemption guides (RAG)
- **Compliance:** EO N-12-23, CCPA/CPRA, CA Revenue & Taxation Code, IRS information return standards

## Architecture Notes

The agent integrates with CDTFA's public Tax Rate API for jurisdiction-specific rate lookups (mock data in local dev). Tax advice is provided at the **general guidance** level — users are directed to CDTFA's authenticated portal for account-specific actions (filing, payments, audit responses). The agent is carefully scoped to avoid constituting legal or professional tax advice per CA Business & Professions Code §22250+.

## Specification

See [../../specs/015-cdtfa-tax-compliance-navigator/spec.md](../../specs/015-cdtfa-tax-compliance-navigator/spec.md)
