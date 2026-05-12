# 009 — CAISO Grid Operations Intelligence Agent

**Agency:** California Independent System Operator (CAISO)

## Problem Statement

CAISO grid operators manage one of the most complex electricity grids in the world, balancing supply and demand across 80% of California's high-voltage transmission system in real time. Operators sift through hundreds of operational alerts, market signals, and weather forecasts simultaneously — often under severe time pressure. Delayed responses to grid anomalies, sub-optimal renewable dispatch decisions, and missed Flex Alert thresholds cost ratepayers millions and risk reliability events.

## Solution Overview

An AI-powered grid operations intelligence assistant that aggregates real-time market data, OASIS feeds, weather forecasts, and operational alerts to support CAISO operators and market participants. The system uses the 3-agent pipeline (QueryAgent → RouterAgent → ActionAgent) to detect intent from operator queries, route to the appropriate data domain (real-time operations, day-ahead markets, transmission planning), and deliver synthesized, actionable intelligence — including renewable integration status, demand response capacity, and Flex Alert recommendation summaries.

## Quick Start

```bash
cd accelerators/009-caiso-grid-operations-agent

# Backend
cd backend
pip install -r requirements.txt
USE_MOCK_SERVICES=true uvicorn app.main:app --reload --port 8009

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Key Use Cases

- **Real-Time Operations Q&A**: "What is the current net import status and how much renewable capacity is curtailed right now?"
- **Market Intelligence**: "Summarize today's day-ahead LMP spreads and identify high-congestion nodes"
- **Demand Response Planning**: "Which demand response programs have capacity available for a Flex Alert this afternoon?"
- **Renewable Integration**: "What is the forecast solar over-generation risk for tomorrow's peak hours?"
- **Outage Coordination**: "Show all planned transmission outages for the next 72 hours and assess grid impact"

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Semantic Kernel
- **Frontend:** React 18 / TypeScript / Vite / Tailwind CSS
- **AI:** Azure OpenAI (GPT-4o) / Azure AI Search
- **Data:** CAISO OASIS API, CAISO Today feed (mock in local dev), NWS weather data
- **Compliance:** EO N-12-23, NERC CIP cybersecurity standards, CAISO Tariff

## Architecture Notes

The ActionAgent integrates with CAISO's publicly available OASIS data feeds in production. In mock mode (`USE_MOCK_SERVICES=true`), synthetic grid telemetry and market data are served from `backend/mock_data/caiso/`. The agent is **read-only** — it never issues dispatch commands or market submissions.

## Specification

See [../../specs/009-caiso-grid-operations-agent/spec.md](../../specs/009-caiso-grid-operations-agent/spec.md)

## Build & Deploy Prompt

Use the GitHub Copilot agent prompt to scaffold and deploy this accelerator:
[../../.github/prompts/accel-009-caiso-build.prompt.md](../../.github/prompts/accel-009-caiso-build.prompt.md)
