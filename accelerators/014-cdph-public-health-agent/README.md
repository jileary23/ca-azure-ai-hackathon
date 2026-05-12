# 014 — CDPH Public Health Surveillance Intelligence Agent

**Agency:** California Department of Public Health (CDPH)

## Problem Statement

The California Department of Public Health monitors the health of 40 million Californians through disease surveillance, vital statistics, laboratory testing, and environmental health programs. Public health investigators, epidemiologists, and local health officers spend excessive time manually querying surveillance systems, cross-referencing outbreak data, interpreting reportable disease regulations, and drafting public health orders. During outbreak events, delayed intelligence synthesis delays containment response. Community health advocates and providers struggle to access plain-language summaries of current disease conditions and vaccination requirements.

## Solution Overview

An AI-powered public health intelligence assistant that helps CDPH epidemiologists, local health officers, healthcare providers, and community advocates synthesize surveillance data, understand reportable disease regulations, navigate immunization requirements, and access plain-language public health guidance. The 3-agent pipeline detects the user role (investigator, provider, public), routes to the appropriate surveillance domain (communicable disease, vital statistics, environmental health, immunization), and delivers synthesized intelligence with citations to CDPH regulations and guidelines.

## Quick Start

```bash
cd accelerators/014-cdph-public-health-agent

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8014

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Key Use Cases

**Epidemiologist/Investigator Persona:**
- **Outbreak Intelligence**: "Summarize the current hepatitis A cluster activity in San Diego County and identify case-linked exposure sites"
- **Regulatory Guidance**: "What are the mandatory reporting timelines for a confirmed measles case for a clinic in Los Angeles County?"
- **Contact Tracing Support**: "What quarantine and isolation guidance applies to close contacts of a confirmed tuberculosis case?"
- **Syndromic Surveillance**: "Are there any unusual ED visit patterns in the Central Valley for the past 14 days that could indicate a novel cluster?"

**Provider/Clinic Persona:**
- **Immunization Requirements**: "What vaccinations are required for a 5-year-old entering kindergarten in California for the 2025-26 school year?"
- **Lab Reporting Obligations**: "Our lab detected Shiga toxin-producing E. coli. What is the mandatory reporting timeline and method?"

**Community/Public Persona:**
- **Disease Prevention**: "What are the current recommendations for preventing West Nile Virus exposure in Fresno County this summer?"

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Data:** CDPH Disease Investigation Guides, Title 17 CCR, CDPH CAIR immunization registry guides, CalREDIE references (RAG, mock)
- **Compliance:** EO N-12-23, HIPAA, CCPA/CPRA, Title 17 CCR mandatory reporting, 42 CFR Part 2 (substance use)

## Architecture Notes

Syndromic surveillance queries are served from synthetic mock data in local dev. The agent is role-aware — investigator queries receive detailed clinical and epidemiologic guidance; public-facing queries are formatted at a plain-language (8th grade) reading level per CDPH health equity standards. All identifiable health information is strictly excluded from agent responses.

## Specification

See [../../specs/014-cdph-public-health-agent/spec.md](../../specs/014-cdph-public-health-agent/spec.md)

## Build & Deploy Prompt

Use the GitHub Copilot agent prompt to scaffold and deploy this accelerator:
[../../.github/prompts/accel-014-cdph-build.prompt.md](../../.github/prompts/accel-014-cdph-build.prompt.md)
