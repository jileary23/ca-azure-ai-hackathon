### Graceful Mock Fallback Pattern for ActionAgents
**Timestamp:** 2026-04-13
**Authority:** Tank (Backend Dev)
**Decision:** All accelerator ActionAgents must gracefully fall back to mock services when live Azure services are not yet implemented, instead of raising NotImplementedError.

**Pattern:**
```python
async def execute(self, query, routing):
    if self.mock_mode:
        return self._handle_mock(query, routing)
    try:
        return self._handle_live(query, routing)
    except NotImplementedError:
        return self._handle_mock(query, routing)
```

**Rationale:** Azure deployments set `USE_MOCK_SERVICES=false`. If an accelerator's live services aren't ready yet, the app should still work by falling back to mock rather than crashing with a 500. This makes all accelerators deployable to Azure immediately, and live services can be wired in incrementally by implementing `_handle_live()`.

**Also decided:** CORS origins are now driven by `CORS_ORIGINS` env var (comma-separated, defaults to `"*"`). This allows tightening origins per-environment without code changes.
