# BYO appendix — expose your own table or SP through hosted DAB

Same idea as the [step 4 BYO appendix](../../04-dab-local/byo/README.md),
but for the **hosted** image. There's just one difference: the file
you edit lives at `steps/05-dab-on-aca/docker/dab-config.json`, and
you have to rebuild + redeploy the image after editing.

---

## 1. Edit `docker/dab-config.json`

Add an entity (table) and/or stored procedure entry — same shape as step 4:

```jsonc
"MyDoc": {
  "source": { "object": "dbo.MyDocs", "type": "table" },
  "permissions": [
    { "role": "anonymous", "actions": ["read"] }
  ],
  "description": "Your documents table."
},
"FindSimilarMyDocsHybrid": {
  "source": {
    "object": "dbo.find_similar_mydocs_hybrid",
    "type": "stored-procedure"
  },
  "rest":    { "methods": ["POST"] },
  "graphql": { "operation": "mutation" },
  "permissions": [
    { "role": "anonymous", "actions": ["execute"] }
  ],
  "description": "Hybrid search over MyDocs."
}
```

> Don't change `connection-string` — it stays `@env('SQL_CONNECTION_STRING')`.
> ACA injects the real value from a secret at runtime.

---

## 2. Rebuild + redeploy

`deploy.ps1` is idempotent — re-running it picks up the edited
config, runs a fresh `az acr build` (producing a new image layer),
and rolls the ACA app to the new revision automatically:

```powershell
.\steps\05-dab-on-aca\deploy.ps1
```

To force a new tag (e.g. for rollback):

```powershell
.\steps\05-dab-on-aca\deploy.ps1 -ImageTag v2
```

---

## 3. Verify

```powershell
$dab = (Get-Content .\steps\05-dab-on-aca\outputs.json | ConvertFrom-Json).acaAppUrl
curl "$dab/api/MyDoc"
```

And the MCP `tools/list` (handshake snippet in [step5.md](../step5.md#mcp-toolslist))
will now include `MyDoc` plus the SP-backed entity.

---

## 4. Make sure the UAMI can see it

Step 2 granted the UAMI `db_datareader`, `db_datawriter`, and
`EXECUTE ON SCHEMA::dbo`. If your BYO table or SP lives in a
**different schema**, grant the corresponding rights:

```sql
GRANT EXECUTE ON SCHEMA::yourschema TO [sqlrag-uami-dev];
-- or, for a specific SP:
GRANT EXECUTE ON OBJECT::yourschema.find_similar_mydocs_hybrid TO [sqlrag-uami-dev];
```

Without that, DAB's call into the SP returns `The EXECUTE permission
was denied on the object …` in the container logs.
