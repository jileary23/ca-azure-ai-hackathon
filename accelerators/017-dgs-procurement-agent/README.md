# 017 — DGS Procurement Intelligence Agent

**Agency:** California Department of General Services (DGS)

## Problem Statement

The California Department of General Services serves as the "business manager" for California state government, processing over $15 billion in state procurement annually. Procurement officers, project managers, and vendors navigate a complex web of purchasing authorities: California Multiple Award Schedule (CMAS), Software Licensing Program (SLP), Master Agreements, California's Small Business and DVBE preference programs, and IT procurement thresholds under Public Contract Code. Agencies frequently delay projects due to uncertainty about which contracting vehicle to use, what documentation is required for a non-competitive justification, or whether a proposed purchase triggers California Environmental Preferable Purchasing requirements. Vendors seeking to do business with the state face an opaque qualification and certification process.

## Solution Overview

An AI-powered procurement intelligence agent that helps state agency procurement officers identify the correct contracting vehicle, understand procurement thresholds and competition requirements, draft compliant justifications, and navigate Small Business/DVBE certification requirements. A second persona helps vendors understand how to qualify for and navigate state contracting vehicles. The 3-agent pipeline identifies the user role (agency buyer, vendor, auditor), routes to the appropriate procurement domain (IT, non-IT goods, services, construction, SB/DVBE), and delivers accurate, compliance-backed procurement guidance with citations to the State Contracting Manual and Public Contract Code.

## Quick Start

```bash
cd accelerators/017-dgs-procurement-agent

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8017

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Key Use Cases

**Agency Buyer Persona:**
- **Contract Vehicle Selection**: "I need to procure a $180,000 software-as-a-service contract for my agency. What contracting vehicles are available and what are the competition requirements?"
- **Non-Competitive Justification**: "My agency needs to sole source a contract to a specific vendor. What are the legal bases for a non-competitive procurement and what documentation is required?"
- **SB/DVBE Requirements**: "What is the state's Small Business preference program and how does it affect my solicitation evaluation scoring?"
- **IT Procurement Rules**: "What approval thresholds and oversight requirements apply to an IT project with a 3-year total cost of $2.5M?"

**Vendor Persona:**
- **CMAS Application**: "How do I get a California Multiple Award Schedule (CMAS) contract? What are the eligibility and documentation requirements?"
- **Small Business Certification**: "What is the process to certify my company as a California Small Business to participate in set-asides?"
- **Bid Protest Process**: "My company was not awarded a state contract. What is the formal protest process and timeline?"

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Data:** State Contracting Manual (SCM), Public Contract Code, DGS CMAS guides, SB/DVBE Program guides, IT procurement regulations (RAG)
- **Compliance:** EO N-12-23, CCPA/CPRA, Public Contract Code, Government Code §4527+, EO N-5-26 (AI procurement)

## Architecture Notes

This accelerator directly supports EO N-5-26 AI procurement compliance. The agent includes a specialized **AI Procurement** routing branch that applies EO N-5-26 vendor attestation requirements and SB 53 accountability standards to AI/ML procurement requests — making it meta-applicable for state agencies procuring AI solutions.

## Specification

See [../../specs/017-dgs-procurement-agent/spec.md](../../specs/017-dgs-procurement-agent/spec.md)
