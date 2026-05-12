# 010 — CalPERS Retirement Benefits Navigator

**Agency:** California Public Employees' Retirement System (CalPERS)

## Problem Statement

CalPERS serves nearly 2 million active and retired public employees, the largest public pension fund in the United States. Members — including teachers, firefighters, police officers, and state employees — face complex retirement decisions at critical life milestones: retirement date calculations, beneficiary designations, health plan elections, and service credit purchases. The CalPERS contact center handles over 1.5 million member interactions annually, with average wait times exceeding 30 minutes during open enrollment periods. Members who make uninformed elections cannot easily correct them after the fact, creating irreversible financial harm.

## Solution Overview

An AI-powered retirement benefits navigator that helps CalPERS members understand their pension options, calculate retirement projections, navigate health plan enrollment, and prepare for key life events. The system uses the 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) to detect member intent, route to the appropriate benefit domain (pension, health, long-term care), and deliver accurate, citation-backed guidance — while maintaining strict PII protection boundaries by directing all account-specific actions to authenticated member portals.

## Quick Start

```bash
cd accelerators/010-calpers-retirement-navigator

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8010

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Key Use Cases

- **Retirement Readiness Q&A**: "I'm 58 with 25 years of service. What are my retirement options under PEPRA vs Classic membership?"
- **Benefit Calculation Guidance**: "Explain how the 2% at 55 formula works and what my final compensation period means"
- **Health Plan Navigation**: "Compare the PERS Choice and PERS Care health plans for a retiree living in Sacramento County"
- **Service Credit Purchase**: "Can I buy service credit for my prior private sector employment? What are the cost and deadline rules?"
- **Survivor & Beneficiary Planning**: "What happens to my CalPERS pension when I die? What survivor benefit options should I consider?"
- **Life Event Guidance**: "I'm getting divorced. How does CalPERS handle domestic relations orders and community property division?"

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Data:** CalPERS Member Handbook, PEPRA/Classic plan documents, Health Plan Comparison guides (RAG)
- **Compliance:** EO N-12-23, CCPA/CPRA, California Government Code §20000+, IRS Circular 230 boundaries

## Architecture Notes

The agent operates in a **strictly advisory capacity** — it never accesses member account data or initiates transactions. All account-specific actions (benefit elections, address changes, estimates) redirect members to the authenticated myCalPERS portal. The knowledge base is built from official CalPERS publications, Member Handbooks, and the PEPRA statutory framework.

## Specification

See [../../specs/010-calpers-retirement-navigator/spec.md](../../specs/010-calpers-retirement-navigator/spec.md)

## Build & Deploy Prompt

Use the GitHub Copilot agent prompt to scaffold and deploy this accelerator:
[../../.github/prompts/accel-010-calpers-build.prompt.md](../../.github/prompts/accel-010-calpers-build.prompt.md)
