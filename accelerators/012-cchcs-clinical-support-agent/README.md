# 012 — CCHCS Correctional Health Clinical Support Agent

**Agency:** California Correctional Health Care Services (CCHCS)

## Problem Statement

California Correctional Health Care Services provides medical, dental, and mental health care to approximately 96,000 incarcerated individuals across 31 CDCR institutions statewide. Clinical staff navigate a complex care environment: a large formulary (~650 medications), dozens of CCHCS Policies and Procedures, evidence-based treatment guidelines, CalAIM community reintegration protocols, and time-sensitive care coordination across institutions. Clinicians spend excessive time on policy lookups during care delivery. Patients transferred between institutions face care coordination gaps. Reentry planning — connecting patients to community-based care prior to release — is often delayed by manual resource lookup.

## Solution Overview

An AI-powered clinical support assistant that helps CCHCS clinical staff (physicians, nurses, mental health clinicians, dental staff) efficiently access clinical guidelines, formulary information, CCHCS policies, and community reentry resources. The system uses the 3-agent pipeline to understand clinical queries, route to the appropriate knowledge domain (formulary, mental health, dental, CalAIM, reentry resources), and surface accurate, citation-backed clinical guidance. The agent also supports care transition planning by identifying available community health resources for patients approaching release.

## Quick Start

```bash
cd accelerators/012-cchcs-clinical-support-agent

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8012

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Key Use Cases

- **Formulary Q&A**: "What are the prescribing restrictions and tier criteria for gabapentin in the CCHCS formulary?"
- **Clinical Protocol Guidance**: "What is the CCHCS protocol for managing a patient with newly diagnosed Type 2 diabetes?"
- **Mental Health Policy**: "What are the required timelines and documentation for MHSDS Level of Care placement reviews?"
- **CalAIM Reentry Planning**: "What Enhanced Care Management services are available for patients with SMI releasing to Alameda County?"
- **Dental Triage**: "What is the CCHCS priority classification for an acute pulpal abscess and what is the required response time?"
- **Medication Reconciliation**: "A patient arriving from DVI has a prescription for a non-formulary medication. What is the exception request process?"

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Data:** CCHCS Formulary, CCHCS Policies & Procedures, MHSDS Program Guide, CalAIM ECM/CS guides (RAG)
- **Compliance:** EO N-12-23, HIPAA, CCPA/CPRA, Plata v. Newsom court orders, Coleman v. Newsom requirements

## Architecture Notes

This agent is strictly **clinical decision support** — it does not access or modify patient medical records (EHR/EHRS is handled by CCHCS's separate system). All responses include clinical citations and direct clinicians to consult the supervising provider for individual patient care decisions. PII protections are strictly enforced per HIPAA and CCPA.

## Specification

See [../../specs/012-cchcs-clinical-support-agent/spec.md](../../specs/012-cchcs-clinical-support-agent/spec.md)

## Build & Deploy Prompt

Use the GitHub Copilot agent prompt to scaffold and deploy this accelerator:
[../../.github/prompts/accel-012-cchcs-build.prompt.md](../../.github/prompts/accel-012-cchcs-build.prompt.md)
