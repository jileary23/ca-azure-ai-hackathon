# 018 — DSH Forensic Mental Health Placement Agent

**Agency:** California Department of State Hospitals (DSH)

## Problem Statement

The California Department of State Hospitals operates five state psychiatric hospitals providing inpatient mental health treatment to approximately 6,200 patients — including individuals found incompetent to stand trial (IST), not guilty by reason of insanity (NGI), civil commitments under the Lanterman-Petris-Short (LPS) Act, and Sexually Violent Predators (SVP). Courts, county jails, public defenders, and county mental health departments submit placement referrals and must navigate complex admission criteria, waitlist status, level-of-care requirements, and restoration-to-competency timelines. DSH clinical staff need rapid access to treatment protocols, legal hold requirements, and community reentry resources. The IST waitlist crisis — with hundreds of defendants awaiting competency restoration placement — requires intelligent triage and capacity management.

## Solution Overview

An AI-powered forensic mental health placement and clinical support agent that helps courts, referral sources, and DSH clinical staff understand admission criteria, navigate placement pathways, and access clinical protocol guidance. The system uses the 3-agent pipeline to identify the referral context (IST, NGI, LPS, SVP, conditional release), route to the appropriate clinical and legal knowledge domain, and deliver accurate guidance on placement criteria, legal hold timelines, treatment protocols, and CONREP/community reentry resources.

## Quick Start

```bash
cd accelerators/018-dsh-forensic-placement-agent

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8018

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Key Use Cases

**Court/Referral Source Persona:**
- **IST Placement Inquiry**: "I have a misdemeanor defendant found incompetent to stand trial. What are the DSH placement criteria and expected wait time under Penal Code 1370?"
- **LPS Commitment Guidance**: "What is the process for a conservator referral for involuntary treatment under the LPS Act and what documentation does DSH require?"
- **Diversion Programs**: "Are there alternatives to DSH placement for my client who is IST with a non-violent charge? What diversion programs exist?"

**DSH Clinical Staff Persona:**
- **Treatment Protocol Access**: "What is the DSH protocol for managing acute psychosis with comorbid substance use disorder in a forensic inpatient setting?"
- **Restoration Timelines**: "What are the maximum commitment periods for IST restoration under PC 1370 for a misdemeanor vs. felony charge?"
- **CONREP Reentry Planning**: "What community support requirements must be in place before recommending conditional release for an NGI patient?"

**Community Partner Persona:**
- **Post-Release Resources**: "What Medi-Cal mental health services are available in Sacramento County for a patient transitioning from DSH?"

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Data:** DSH Admission Criteria, CA Penal Code §1370+, LPS Act, CONREP program guides, DSH Policies & Procedures (RAG)
- **Compliance:** EO N-12-23, HIPAA, CCPA/CPRA, Penal Code §1370+, Welfare & Institutions Code §5000+, Coleman v. Newsom stipulations

## Architecture Notes

The agent operates in a **strictly advisory capacity** on clinical and legal matters — it never provides individual patient placement decisions. Placement decisions remain with DSH clinical staff and are subject to court orders. The agent's knowledge base covers publicly available statutes, DSH program guides, and published admission criteria. All patient-identifiable information is excluded from agent interactions.

## Specification

See [../../specs/018-dsh-forensic-placement-agent/spec.md](../../specs/018-dsh-forensic-placement-agent/spec.md)

## Build & Deploy Prompt

Use the GitHub Copilot agent prompt to scaffold and deploy this accelerator:
[../../.github/prompts/accel-018-dsh-build.prompt.md](../../.github/prompts/accel-018-dsh-build.prompt.md)
