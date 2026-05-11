# Step 6 — Use the hosted DAB MCP server from GitHub Copilot Chat in VS Code

> Pre-reqs: [step 5](../05-dab-on-aca/step5.md) deployed and verified.
> You should have a public URL written to
> `steps/05-dab-on-aca/outputs.json` field `acaAppUrl`, e.g.
> `https://sqlrag-dab-dev.<hash>.<region>.azurecontainerapps.io`.

Step 5 already smoke-tested the hosted endpoint over REST and MCP
from PowerShell. This step does the practical thing with it: wires
the same `/mcp` endpoint into **GitHub Copilot Chat** in VS Code so
the agent can call your SQL data directly while answering questions.

There's no code to run — just a one-file config change and a reload.

> Auth is **anonymous** (matches step 5's `dab-config.json`). For
> anything past a local demo, switch DAB to Entra auth before
> exposing the URL beyond your machine. The last section sketches
> what that looks like.

---

## What's in this folder

```
steps/06-calling-hosted-dab/
├── step6.md                       ← this file
└── vscode/
    └── mcp.template.json          ← reference shape only; the live config is .vscode/mcp.json
```

The live config you actually edit is the workspace's [`.vscode/mcp.json`](../../.vscode/mcp.json) — it already exists from step 4 (it wires the **local** stdio DAB) and now also has a stub `sql-mcp-hosted` entry pointing at the ACA URL. All you do in this step is paste your real URL into that stub.

---

## 1. Make sure the prerequisites are installed

- **VS Code 1.99 or newer** — `Help: About` shows the version.
- **GitHub Copilot Chat extension** with **agent mode**. Open Copilot
  Chat (`Ctrl+Alt+I`); the dropdown at the top of the chat input has
  `Ask`, `Edit`, `Agent`. If you don't see `Agent`, update the
  extension.
- You're signed into a GitHub account with Copilot enabled.

VS Code's built-in MCP client ships with the editor — nothing extra
to install for the protocol itself.

---

## 2. Point the existing config at your hosted URL

Open [`.vscode/mcp.json`](../../.vscode/mcp.json). It already has
two server entries:

- `sql-mcp-local` — stdio launch of DAB against your local config (from step 4).
- `sql-mcp-hosted` — HTTP entry pointing at the ACA URL, with a
  `REPLACE_ME` placeholder.

Get your real URL:

```powershell
(Get-Content .\steps\05-dab-on-aca\outputs.json | ConvertFrom-Json).acaAppUrl
```

Replace the placeholder URL in the `sql-mcp-hosted` entry with that
value, **keeping the `/mcp` suffix**:

```jsonc
"sql-mcp-hosted": {
    "type": "http",
    "url": "https://sqlrag-dab-dev.redbay-c65fa1d0.westus.azurecontainerapps.io/mcp"
}
```

Save the file. VS Code picks the change up automatically; if it
doesn't, run `Developer: Reload Window`.

> The shape shown in [`vscode/mcp.template.json`](vscode/mcp.template.json)
> is identical — it's a reference for anyone wiring the same server
> into a different workspace or into the user-scope `mcp.json`
> (`Command Palette → MCP: Open User Configuration`).

---

## 3. Verify the server is registered

`Command Palette → MCP: List Servers` should show `sql-mcp-hosted`
with a green dot. Pick it and click **Show Output** — the log should
end with something like `tools/list returned 6 tools`. That's the
same six DAB exposes: `describe_entities`, `read_records`,
`create_record`, `update_record`, `delete_record`, `execute_entity`.

If the dot is red, hover for the error or open the output panel —
the [troubleshooting table below](#troubleshooting) has the common
ones.

---

## 4. Use it from Copilot Chat

Open Copilot Chat (`Ctrl+Alt+I`), switch the mode dropdown to
**Agent**, and click the **🔧 Tools** button above the chat input.
Toggle `sql-mcp-hosted` on (you can leave `sql-mcp-local` on too —
Copilot will pick the right tool per question, and you can use the
local one as a quick offline sanity check).

Now ask the agent something that needs your SQL data:

> Find the three most relevant product reviews for "lightweight
> running shoes that handle rain" and summarise the common themes.

Watch the **Tool calls** panel as the agent works. You should see:

1. `describe_entities` (no args) — the agent discovers `Product`,
   `ProductReview`, and `FindSimilarReviewsHybrid`.
2. `execute_entity` with
   `{ entity: "FindSimilarReviewsHybrid", parameters: { queryText, top } }`
   — the agent fills in `queryText` from your prompt and picks a
   reasonable `top` (3–5). No endpoint or deployment values needed:
   the SP looks them up via the `EmbeddingModel` registered in
   step 3's required follow-on.
3. A natural-language summary of the rows it got back.

Other prompts worth trying:

- *"List the five highest-priced products and their categories."* →
  drives `read_records` against `Product`.
- *"How many 1- or 2-star reviews are there across all products?"*
  → `read_records` with a filter.
- *"Which reviews mention 'battery life'?"* → `read_records` with a
  `$filter` containing `contains(ReviewText, 'battery life')`.

> **Why DAB doesn't always discover the parameter schema**: the agent
> can read the SP's description from `describe_entities`, but DAB
> doesn't currently publish the parameter schema. The first time the
> agent calls `execute_entity` it'll usually try without all the
> required parameters — DAB returns a clear error and the agent
> retries. With the v2 SP signature there are only two parameters
> (`queryText` and `top`), so this almost never trips it up.

---

## Locking it down (preview)

Everything above is anonymous. Once the URL is anywhere it might be
reached by anyone else, switch DAB to **Entra authentication** —
that's a config-only change in `docker/dab-config.json`:

```jsonc
"authentication": {
  "provider": "AzureAD",
  "jwt": {
    "audience": "api://<dab-app-registration-client-id>",
    "issuer":   "https://login.microsoftonline.com/<tenantId>/v2.0"
  }
}
```

…plus changing each entity's `"role"` from `"anonymous"` to
`"authenticated"` (or a custom role mapped from Entra groups via the
`X-MS-API-ROLE` header). Container, UAMI, AcrPull, and ACA
networking from step 5 all stay the same. The VS Code MCP client
then needs an `Authorization: Bearer <token>` header attached to
every request, which the same `mcp.json` entry supports via an
`auth` block (Entra device-code or AAD).

That's a deliberate follow-up step, slotted in before steps 7 and 8
so the optional web app and Foundry agent can both pick up the
per-user identity instead of running as `anonymous`.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `MCP: List Servers` doesn't show `sql-mcp-hosted` | `.vscode/mcp.json` not saved, or VS Code didn't pick up the change | Save the file, then `Developer: Reload Window`. |
| Red dot on `sql-mcp-hosted`, output shows JSON parse error | Trailing comma or stray bracket in `mcp.json` | Fix the JSON. VS Code highlights the offending line. |
| Red dot, output shows `404` on `/mcp` | URL is missing `/mcp` suffix, or you copied the FQDN without `https://` | The full value is the step 5 `acaAppUrl` **plus** `/mcp`. |
| Red dot, output shows `Not Acceptable` or `Session not found` | DAB's MCP not enabled in the running revision | Confirm `runtime.host.mcp.enabled = true` in `docker/dab-config.json` and that step 5 was deployed with it. Rebuild with `.\steps\05-dab-on-aca\deploy.ps1 -ImageTag v2` if needed. |
| Tool calls return `DatabaseOperationFailed` | Real error is in the container logs, not the chat output | `az containerapp logs show -g rg-sqlrag-dev -n sqlrag-dab-dev --tail 100 --type console` — the [step 5 troubleshooting table](../05-dab-on-aca/step5.md#troubleshooting) lists the common SQL-side ones. |
| Agent calls `execute_entity` but it returns `Missing required argument 'entity'` | The agent invented its own arg name (e.g. `entityName`) | The argument is literally `entity`. Tell the agent "use `entity` for the entity name argument" and it'll correct on the next call. |
| Agent calls `execute_entity` but it returns `Invalid request. Missing required request parameters.` | Agent forgot to nest the SP args under `parameters` | The shape is `{ entity, parameters: { queryText, top } }`. Telling the agent that once is usually enough. |
| `read_records` returns `UnexpectedError` / `Unexpected error occurred in ReadRecordsTool` after passing a `select` or `orderby` | Misspelled or wrong-cased column name (e.g. `ProductId` vs `ProductID`). DAB swallows the underlying SQL `Invalid column name` and only surfaces the generic message. `describe_entities` may also return `"fields": []` so column names aren't discoverable that way. | Call `read_records` once with **only** `entity` + `first: 1` to see the real column casing in the response, then retry with `select` / `orderby` using those exact names. The full error is in the container log: `az containerapp logs show -g rg-sqlrag-dev -n sqlrag-dab-dev --tail 50 --type console`. |

---

## What's next

- **Entra auth step** — locks the surface this step is calling
  anonymously today. Slots in before 7 and 8.
- **Step 7** (optional) — a minimal web app in front of DAB so a
  human can type into a search box.
- **Step 8** (optional) — a Foundry agent that uses the hosted DAB
  MCP server as its only tool.
