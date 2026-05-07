# Red Team Adversarial Testing Framework

Shared adversarial testing suite for all California State AI Accelerators. Tests agent robustness against prompt injection, PII leakage, constitutional compliance violations, boundary attacks, escalation manipulation, and authority bypass.

## Quick Start

```bash
# Run against local accelerator 001 (default)
cd /workspaces/ca-hackathon/shared/red-team
python -m pytest --accel 001 -v

# Run against a specific accelerator
python -m pytest --accel 004 -v

# Run against a deployed Azure endpoint
python -m pytest --base-url https://accel-001.example.azurecontainerapps.io -v

# Run only prompt injection tests
python -m pytest test_prompt_injection.py --accel 001 -v

# Collect tests without running (dry run)
python -m pytest --collect-only
```

## Test Modules

| Module | Tests | What It Covers |
|--------|-------|----------------|
| `test_prompt_injection.py` | 18+ | Instruction override, DAN jailbreaks, encoding tricks, multi-turn injection |
| `test_pii_leakage.py` | 17+ | SSN echo, financial data, PII extraction, cross-session leakage |
| `test_constitutional_compliance.py` | 10+ | Scope boundaries, escalation triggers, no eligibility determinations, AI disclosure |
| `test_boundary.py` | 15+ | Oversized input, empty strings, Unicode attacks, SQL injection, XSS |
| `test_escalation.py` | 6+ | Escalation bypass, forced misrouting, post-injection escalation integrity |
| `test_authority_bypass.py` | 9+ | Eligibility rulings, legal/medical/tax advice, record modification |

## Architecture

```
shared/red-team/
├── conftest.py                 # Shared fixtures (--accel, --base-url flags)
├── test_prompt_injection.py    # Prompt injection resistance
├── test_pii_leakage.py         # PII handling verification
├── test_constitutional_compliance.py  # Constitution rule enforcement
├── test_boundary.py            # Input boundary & encoding tests
├── test_escalation.py          # Escalation manipulation tests
├── test_authority_bypass.py    # Authority boundary tests
├── payloads/
│   ├── injection_payloads.json # Categorized injection payloads
│   └── pii_test_data.json      # Synthetic PII test patterns
└── README.md                   # This file
```

## Configuration

### CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--accel` | `001` | Accelerator ID (determines default port: `800{id}`) |
| `--base-url` | `None` | Full URL override for Azure or custom deployments |

### Port Mapping (Local)

| Accelerator | Default URL |
|-------------|-------------|
| 001 | `http://localhost:8001` |
| 002 | `http://localhost:8002` |
| 003 | `http://localhost:8003` |
| 004 | `http://localhost:8004` |
| 005 | `http://localhost:8005` |
| 006 | `http://localhost:8006` |
| 007 | `http://localhost:8007` |
| 008 | `http://localhost:8008` |

## Adding New Tests

1. Create a new `test_*.py` file or add to an existing module
2. Use `chat_url` fixture from conftest for API calls
3. Use `pytest.mark.parametrize` for data-driven tests
4. Add payloads to `payloads/` JSON files for reusable attack vectors

### Example

```python
import httpx
import pytest

def test_my_new_attack(chat_url):
    resp = httpx.post(chat_url, json={"message": "attack payload"}, timeout=30.0)
    assert resp.status_code == 200
    text = resp.json().get("response", "").lower()
    assert "dangerous_output" not in text
```

## Compliance Context

These tests verify compliance with:
- **EO N-12-23**: GenAI transparency and safety guidelines
- **EO N-5-26**: AI vendor attestation requirements
- **SB 53**: AI safety legislation
- **CCPA/CPRA**: California consumer privacy
- **shared/constitution.md**: Project-specific agent boundaries

## Dependencies

- `pytest` (test runner)
- `httpx` (HTTP client for API calls)
- `pytest-asyncio` (if async tests are added)
