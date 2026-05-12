# 01 — Solution overview

End-to-end picture of what the tutorial deploys. The same
**User-Assigned Managed Identity (UAMI)** is used by every Azure
service-to-service call — there are no keys or passwords anywhere in
the deployed system.

![Solution overview](01-solution-overview.svg)

## Reading this diagram

- **Three client paths, one server.** Whether you talk to the system
  from VS Code (MCP), the optional Streamlit app (REST), or a Foundry
  agent (MCP), every request lands at the same DAB instance.
- **DAB is the single front door.** It exposes the same data three
  ways — REST, GraphQL, and MCP — without any custom code.
- **Embeddings live next to the data.** The vector column, the
  full-text index, the search SP, and the registered embedding model
  are all inside Azure SQL. The application tier never touches the
  embeddings API directly.
- **One identity does everything.** The UAMI is attached to the ACA
  app (so DAB can log into SQL) and is mapped as a database user in
  SQL (so SQL can call Azure OpenAI). No keys, no secrets in env vars,
  no credential rotation.

## Tutorial-step mapping

| Layer in diagram                | Built in step |
|---------------------------------|---------------|
| UAMI, SQL, OpenAI deployment    | [Step 1](../../steps/01-foundation/step1.md) |
| `EXTERNAL MODEL` + DSC          | [Step 2](../../steps/02-embeddings-in-sql/step2.md) + [Step 3 upgrade](../../steps/03-hybrid-search-sp/upgrade-external-model/README.md) |
| Hybrid search SP                | [Step 3](../../steps/03-hybrid-search-sp/step3.md) |
| DAB (local)                     | [Step 4](../../steps/04-dab-local/step4.md) |
| DAB on ACA (this diagram)       | [Step 5](../../steps/05-dab-on-aca/step5.md) |
| VS Code MCP wire-up             | [Step 6](../../steps/06-calling-hosted-dab/step6.md) |

## Source

Diagram is hand-authored SVG ([`01-solution-overview.svg`](01-solution-overview.svg)) so it renders inline in VS Code's built-in markdown preview, on GitHub, and anywhere else. The original visual source ([`01-solution-overview.drawio`](01-solution-overview.drawio)) is kept as a convenience for slide-deck exports.
