# 011 — Caltrans Transportation Project Intelligence Agent

**Agency:** California Department of Transportation (Caltrans)

## Problem Statement

Caltrans manages over 50,000 lane miles of state highway, coordinates thousands of capital improvement projects, and processes more than 40,000 encroachment permits annually. Project delivery is slowed by complex environmental review requirements, multi-agency coordination across federal (FHWA, EPA), state (Caltrans, CARB, DFW), and local entities, and manual lookup of permit conditions, standard plans, and design specifications. Engineers and project managers spend significant time navigating the Highway Design Manual, the Standard Plans, and the CEQA/NEPA regulatory framework. Encroachment permit applicants — utilities, developers, local agencies — face opaque queues and inconsistent guidance on submittal requirements.

## Solution Overview

An AI-powered transportation project intelligence assistant that accelerates project delivery by helping Caltrans engineers, project managers, and external applicants navigate encroachment permits, design standards, environmental review checklists, and project status inquiries. The system uses the 3-agent pipeline to interpret queries about permits, routing to the appropriate knowledge domain (design standards, environmental, permits, traffic operations), and delivers precise, citation-backed guidance from official Caltrans manuals and CEQA/NEPA requirements.

## Quick Start

```bash
cd accelerators/011-caltrans-project-intelligence-agent

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8011

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Key Use Cases

- **Encroachment Permit Guidance**: "What documentation is required to install a fiber optic conduit within Caltrans right-of-way on a Route 101 corridor?"
- **Design Standards Q&A**: "What are the HDM requirements for bicycle lane widths on a Class III expressway with 45 mph posted speed?"
- **Environmental Review Navigator**: "Does my project require a full CEQA EIR or can I use a Categorical Exemption? My project adds a turn pocket on SR-99."
- **Construction Zone Compliance**: "What CMS message and traffic control plan requirements apply for a lane closure on I-5 during peak hours?"
- **Project Status Inquiry**: "What permits and clearances are still outstanding for Project EA 03-123456?"
- **ADA Transition Plan**: "What are Caltrans requirements for pedestrian access routes during construction in the public right-of-way?"

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search / Azure Document Intelligence
- **Data:** Caltrans Highway Design Manual, Standard Plans, Encroachment Permits Manual, CEQA/NEPA guidelines (RAG)
- **Compliance:** EO N-12-23, FHWA requirements, CEQA, NEPA, ADA, Caltrans Right-of-Way Manual

## Architecture Notes

Azure Document Intelligence is used to parse submitted encroachment permit drawings and extract key parameters (dimensions, materials, locations) for automated pre-screening. The agent supports role-based routing: external applicants see public-facing guidance, while authenticated Caltrans staff access internal project tracking context.

## Specification

See [../../specs/011-caltrans-project-intelligence-agent/spec.md](../../specs/011-caltrans-project-intelligence-agent/spec.md)

## Build & Deploy Prompt

Use the GitHub Copilot agent prompt to scaffold and deploy this accelerator:
[../../.github/prompts/accel-011-caltrans-build.prompt.md](../../.github/prompts/accel-011-caltrans-build.prompt.md)
