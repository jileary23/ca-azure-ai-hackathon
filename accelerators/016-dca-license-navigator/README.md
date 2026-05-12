# 016 — DCA Professional License Navigator

**Agency:** California Department of Consumer Affairs (DCA)

## Problem Statement

The California Department of Consumer Affairs oversees 3.6 million active licensees across more than 200 professions and vocations through 37 regulatory boards, bureaus, and committees — from contractors and cosmetologists to physicians and engineers. License applicants face complex, board-specific requirements: education transcripts, examination scheduling, fingerprinting, experience verification, and application fees. Renewal timelines and continuing education requirements vary widely by profession. Consumers checking whether a professional is licensed, in good standing, or subject to disciplinary action must navigate multiple separate databases. Enforcement staff manually triage incoming complaints against thousands of licensees.

## Solution Overview

An AI-powered professional licensing navigator that guides applicants through the correct licensing pathway for their profession, helps existing licensees track renewal requirements and CE obligations, enables consumers to verify license status and understand disciplinary history, and supports DCA enforcement staff in complaint intake triage. The 3-agent pipeline identifies the user role (applicant, licensee, consumer, enforcement), routes to the appropriate board/bureau knowledge base, and delivers accurate, step-by-step guidance with citations to California Business & Professions Code and board-specific regulations.

## Quick Start

```bash
cd accelerators/016-dca-license-navigator

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8016

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Key Use Cases

**Applicant Persona:**
- **Pathway Guidance**: "I'm a licensed electrician from Texas moving to California. What is the process to get a California C-10 Electrical Contractor license?"
- **Exam Prep**: "What subjects are covered on the California Cosmetology State Board exam and where can I register?"
- **Document Checklist**: "I'm applying for a California Registered Nurse license. Give me a complete document checklist for a new graduate applicant."

**Licensee Persona:**
- **CE Requirements**: "I'm a California licensed marriage and family therapist (LMFT). What continuing education hours are required to renew my license this cycle?"
- **License Reinstatement**: "My Contractor's State License Board license lapsed. What is the reinstatement process vs. applying new?"

**Consumer Persona:**
- **License Verification**: "How do I verify if a contractor is licensed and bonded in California before hiring them?"
- **Complaint Filing**: "A licensed physician billed me for services not rendered. How do I file a complaint with the Medical Board?"

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Data:** DCA Board regulations (37 boards/bureaus), CA Business & Professions Code, License Lookup API (RAG + API integration)
- **Compliance:** EO N-12-23, CCPA/CPRA, CA Business & Professions Code, CSLB contractor regulations

## Architecture Notes

The agent integrates with DCA's public License Lookup system for real-time license status verification (mock in local dev). With 37+ boards and bureaus, the RouterAgent uses a two-level routing strategy: first identifying the profession category, then routing to the specific board knowledge base. This prevents hallucinated requirements across the complex multi-board landscape.

## Specification

See [../../specs/016-dca-license-navigator/spec.md](../../specs/016-dca-license-navigator/spec.md)

## Build & Deploy Prompt

Use the GitHub Copilot agent prompt to scaffold and deploy this accelerator:
[../../.github/prompts/accel-016-dca-build.prompt.md](../../.github/prompts/accel-016-dca-build.prompt.md)
