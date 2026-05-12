# 013 — CDI Insurance Consumer Protection Agent

**Agency:** California Department of Insurance (CDI)

## Problem Statement

The California Department of Insurance is the largest consumer protection agency in the United States by budget, protecting 40 million Californians in a $310+ billion insurance marketplace. CDI processes over 300,000 consumer complaints and inquiries annually. Consumers struggle to understand complex insurance policies, know their rights after claim denials, identify licensed agents and companies, and navigate the complaint process. Meanwhile, thousands of insurance agents and brokers need to track continuing education requirements, license renewal deadlines, and regulatory bulletins. Fraud referrals require complex form completion and documentation — a barrier that suppresses fraud reporting.

## Solution Overview

An AI-powered insurance consumer protection assistant that helps California consumers understand their insurance rights, navigate the complaint process, verify licenses, and get plain-language explanations of complex coverage questions. A second persona serves licensed producers (agents/brokers) with CE tracking, licensing requirements, and regulatory updates. The system uses the 3-agent pipeline to detect whether the user is a consumer or producer, route to the appropriate service domain, and deliver accurate guidance backed by CDI bulletins, insurance codes, and consumer guides.

## Quick Start

```bash
cd accelerators/013-cdi-insurance-consumer-agent

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8013

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Key Use Cases

**Consumer Persona:**
- **Claim Denial Appeals**: "My auto insurance claim was denied due to 'policy exclusion 12B.' What are my rights and how do I appeal?"
- **Rate Increase Challenges**: "My homeowner's insurance premium increased 40% at renewal. Can I challenge this? How does CDI's rate review process work?"
- **FAIR Plan Guidance**: "I was dropped by my insurer due to wildfire risk. How do I get coverage through the FAIR Plan?"
- **Complaint Filing**: "How do I file a complaint against my insurance company for bad faith claim handling?"
- **License Verification**: "Is Premier Auto Insurance Company licensed to sell auto insurance in California?"

**Producer Persona:**
- **License Renewal**: "My California P&C license expires in 90 days. What CE hours are required and are there any new compliance requirements?"
- **Regulatory Updates**: "Summarize CDI bulletin 2025-8 on catastrophic loss declarations and claims handling timelines"

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Data:** CDI Consumer Guides, CA Insurance Code, CDI Bulletins & Regulations, FAIR Plan docs (RAG)
- **Compliance:** EO N-12-23, CCPA/CPRA, California Insurance Code, Proposition 103 rate regulations

## Architecture Notes

The agent uses **intent classification** to distinguish consumer vs. producer queries and route to separate knowledge domains. License verification queries route to CDI's public License Lookup integration (mock in local dev). No consumer account data is accessed — all enforcement actions and formal complaints are routed to CDI's authenticated portal.

## Specification

See [../../specs/013-cdi-insurance-consumer-agent/spec.md](../../specs/013-cdi-insurance-consumer-agent/spec.md)

## Build & Deploy Prompt

Use the GitHub Copilot agent prompt to scaffold and deploy this accelerator:
[../../.github/prompts/accel-013-cdi-build.prompt.md](../../.github/prompts/accel-013-cdi-build.prompt.md)
