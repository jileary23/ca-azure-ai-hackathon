# 020 — CA State Fund Workers' Compensation Claims Navigator

**Agency:** State Compensation Insurance Fund (CA State Fund)

## Problem Statement

CA State Fund is a not-for-profit, self-supporting workers' compensation insurer established by the California Legislature in 1914. It insures more than 150,000 California employers — with a particular mission to serve small businesses and state agencies that may struggle to obtain coverage in the private market. Injured workers navigating the workers' compensation system face one of the most complex insurance processes in the United States: medical treatment authorization timelines, independent medical review (IMR), qualified medical evaluator (QME) panels, temporary and permanent disability benefit calculations, and return-to-work coordination. Employers managing their CA State Fund policies need guidance on audit preparation, experience modification (X-MOD) factors, safety program requirements, and claims management best practices.

## Solution Overview

An AI-powered workers' compensation claims navigator that guides injured workers through the claims process, helps employers understand their policy obligations and safety program requirements, and supports medical providers with billing and authorization questions. The system uses the 3-agent pipeline to identify the user persona (injured worker, employer, medical provider), route to the appropriate claims domain (medical treatment, disability benefits, return-to-work, employer audit), and deliver accurate, plain-language guidance with citations to the California Labor Code and CA State Fund policy documents.

## Quick Start

```bash
cd accelerators/020-statefund-workers-comp-navigator

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8020

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Key Use Cases

**Injured Worker Persona:**
- **Claim Process Guidance**: "I was injured at work yesterday. What are the steps to file a workers' comp claim and what are my employer's obligations?"
- **Benefit Questions**: "How is temporary disability calculated and when does it start? My employer says it takes 30 days."
- **Medical Treatment**: "My doctor recommended physical therapy but my employer's insurer denied the authorization. What are my rights and how do I request IMR?"
- **Return-to-Work**: "My doctor released me for modified duty but my employer has no modified work available. What are my options?"
- **Dispute Resolution**: "My claim was denied. What is the difference between an IMR, an IME, and a hearing at the WCAB?"

**Employer Persona:**
- **X-MOD Explanation**: "My experience modification factor increased from 0.94 to 1.12. What caused this and how can I improve it?"
- **Audit Preparation**: "CA State Fund is auditing my payroll. What records should I prepare and how are my premium classifications determined?"
- **Safety Program Requirements**: "What IIPP (Injury and Illness Prevention Program) elements are required under California Labor Code and how can AI help me maintain it?"

**Medical Provider Persona:**
- **Billing & Authorization**: "What is the correct billing code and authorization process for an MRI for a State Fund claimant with a lumbar injury?"

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Data:** CA Labor Code, CA State Fund Policy Documents, WCAB Rules, DWC Medical Treatment Utilization Schedule (MTUS), IMR/IME process guides (RAG)
- **Compliance:** EO N-12-23, CCPA/CPRA, CA Labor Code §3200+, DWC regulations, HIPAA (medical information)

## Architecture Notes

The agent is strictly **advisory** — it never accesses individual claim records, makes coverage determinations, or issues medical authorizations. All account-specific actions route to the authenticated CA State Fund policyholder or claimant portal. The agent is multi-persona aware: the same underlying pipeline serves three distinct user types with different vocabulary, knowledge needs, and regulatory contexts, controlled by the RouterAgent's persona classification.

## Specification

See [../../specs/020-statefund-workers-comp-navigator/spec.md](../../specs/020-statefund-workers-comp-navigator/spec.md)

## Build & Deploy Prompt

Use the GitHub Copilot agent prompt to scaffold and deploy this accelerator:
[../../.github/prompts/accel-020-statefund-build.prompt.md](../../.github/prompts/accel-020-statefund-build.prompt.md)
