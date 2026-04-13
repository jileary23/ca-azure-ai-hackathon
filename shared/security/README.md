# Shared Security Utilities

Input validation and security middleware for all California State AI Accelerators.

## Purpose

This module provides a shared input validation layer that sits between user input and the LLM. All accelerator agents should validate input through this module before passing it to the language model.

## Features

| Feature | Description | Default |
|---------|-------------|---------|
| **Length Enforcement** | Truncates input exceeding max length | 2000 chars |
| **Prompt Injection Detection** | Regex-based detection of known injection patterns | Enabled |
| **PII Flagging** | Detects SSNs, emails, phone numbers, credit cards, CA driver's licenses | Enabled (flag only) |
| **HTML/Script Stripping** | Removes HTML tags and dangerous elements | Enabled |
| **Unicode Normalization** | NFKC normalization + zero-width character removal | Enabled |

## Quick Start

```python
from shared.security import validate_input

result = validate_input(user_message)

if not result.is_safe:
    # Input failed validation — prompt injection or too long
    log.warning(f"Unsafe input: {result.flags}")
    return "I cannot process that request."

if result.has_pii:
    # PII detected — flag for review but allow processing
    log.info(f"PII detected: {result.details['pii']}")

# Use sanitized text for LLM
response = await llm.generate(result.sanitized_text)
```

## Custom Configuration

```python
from shared.security import InputValidator

validator = InputValidator(
    max_length=4000,       # Allow longer inputs
    strip_html=True,       # Strip HTML tags
    check_pii=True,        # Flag PII
    check_injection=True,  # Detect prompt injections
    normalize_unicode=True, # NFKC normalize
)

result = validator.validate(user_input)
```

## Security Flags

- `INPUT_TOO_LONG` — Input exceeds max length (truncated)
- `PROMPT_INJECTION` — Known injection pattern detected (blocked)
- `PII_DETECTED` — PII found in input (flagged, not blocked)
- `HTML_SCRIPT_DETECTED` — HTML/script tags found (stripped)
- `SUSPICIOUS_UNICODE` — Zero-width or invisible characters detected (removed)

## Prompt Injection Patterns Detected

- **Role override**: "you are now", "act as", "pretend to be"
- **Instruction override**: "ignore previous instructions", "forget your rules"
- **System directives**: "SYSTEM:", "admin override", "authorization code"
- **Output manipulation**: "export all data", "enter debug mode", "disable safety"
- **Delimiter injection**: `[INST]`, `<<SYS>>`, `<|im_start|>`

## Compliance

This module supports compliance with:
- **EO N-12-23**: GenAI safety guidelines for state agencies
- **CCPA/CPRA**: PII detection helps prevent unintentional data exposure
- **SB 53**: AI safety requirements for input validation

## Integration with Red Team Tests

Each accelerator has domain-specific red team configs at `accelerators/*/backend/evals/red_team_config.json`. The input validator works as the first line of defense — red team scenarios test both the validator and the agent's behavioral guardrails.
