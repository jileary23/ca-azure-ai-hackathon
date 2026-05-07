# 019 — OTSI Health & Human Services AI Integration Agent

**Agency:** California Health and Human Services Agency — Office of Technology and Solutions Integration (OTSI)

## Problem Statement

OTSI is the technology backbone of California's Health and Human Services Agency, building and maintaining integrated IT systems for CDSS, DHCS, DPH, and eight other CHHS departments that collectively serve millions of Californians. OTSI teams manage complex multi-system integration projects — connecting legacy eligibility systems (CalSAWS, MEDS), case management platforms, data warehouses, and new cloud services. Developers, business analysts, and project managers spend significant time navigating system architecture documentation, API specifications, data dictionaries, and inter-agency data sharing agreements. Cross-agency interoperability — critical for programs like CalAIM and Medi-Cal renewals — is impeded by siloed knowledge and inconsistent documentation standards.

## Solution Overview

An AI-powered systems integration intelligence agent that helps OTSI developers, architects, business analysts, and program managers navigate CHHS system documentation, API specifications, data dictionaries, integration patterns, and inter-agency data sharing requirements. The system uses the 3-agent pipeline to understand the technical or business query, route to the appropriate system domain (CalSAWS, MEDS, CalHEERS, CDW, API catalog), and deliver accurate technical guidance — accelerating development velocity and reducing integration errors across California's health and human services systems portfolio.

## Quick Start

```bash
cd accelerators/019-otsi-hhs-integration-agent

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8019

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Key Use Cases

**Developer Persona:**
- **API Discovery**: "What OTSI APIs are available for querying Medi-Cal eligibility status and what authentication method is required?"
- **Integration Pattern Guidance**: "What is the recommended CHHS integration pattern for a new application that needs to write case data to CalSAWS?"
- **Data Dictionary Lookup**: "What does the `ELIG_DET_RSN_CD` field in the MEDS eligibility response represent and what are its valid values?"
- **Error Resolution**: "I'm receiving a 422 response from the CalHEERS enrollment API. What does error code E-4422 mean and how do I resolve it?"

**Business Analyst Persona:**
- **Data Sharing Agreement Navigator**: "Which CHHS data sharing agreements govern sharing SNAP case data with a county behavioral health department?"
- **CalAIM Integration**: "What systems need to be integrated to support the Enhanced Care Management (ECM) data flow between a Medi-Cal managed care plan and DHCS?"

**Project Manager Persona:**
- **Project Lifecycle Guidance**: "What OTSI project intake and governance steps are required for a $500K system integration initiative?"
- **Security Review Checklist**: "What CA-PMSO and SIMM security review steps apply to a cloud-hosted application connecting to SAWS?"

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search / Azure API Management
- **Data:** OTSI API catalog, CHHS system architecture docs, CalAIM technical specs, SIMM standards (RAG)
- **Compliance:** EO N-12-23, EO N-5-26, CCPA/CPRA, HIPAA, IRS Publication 1075 (FTI), NIST SP 800-53

## Architecture Notes

This accelerator uniquely targets **internal government developer productivity** — a force multiplier for OTSI teams building the platform that delivers all CHHS programs. The agent is deployed as an internal tool with Azure Entra ID (formerly Azure AD) authentication, restricting access to OTSI staff and approved CHHS program agency developers. The knowledge base is built from internal documentation in mock mode, with real Azure AI Search indexes in production.

## Specification

See [../../specs/019-otsi-hhs-integration-agent/spec.md](../../specs/019-otsi-hhs-integration-agent/spec.md)
