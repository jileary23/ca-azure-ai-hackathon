# Step 1 — Foundation

> Goal: stand up the Azure resources that **every later step depends on**, and
> get a SQL database that's ready to be embedded against.
>
> Time: ~5–10 minutes. Cost while idle: a few cents per day (SQL serverless
> auto-pauses; Foundry only bills for tokens you actually consume).

By the end of this step you will have:

- A **resource group** holding everything in this tutorial.
- One **User-Assigned Managed Identity (UAMI)** that is reused for every
  service-to-service call in the entire tutorial — no keys, no passwords.
- An **Azure SQL** logical server + database (`ProductsDB`) with the UAMI
  attached and you set as the AAD admin.
- An **Azure AI Foundry** account + project with one **embedding model**
  deployment (`text-embedding-3-small`, 1536 dimensions).
- The role assignment that lets the **UAMI call the embedding endpoint**.
- (Default) the demo `Products` and `ProductReviews` tables, populated with
  a small dataset you can immediately embed in step 2.

You will **not** yet have: ACR, Container Apps, DAB, a chat model, a webapp,
or a Foundry agent. Each of those is added in its own later step.

---

## Architecture you're about to deploy

```
┌─────────────────────────────────────────────────────────────────┐
│ Resource group  (e.g. rg-sqlrag-dev)                            │
│                                                                 │
│   ┌──────────────────────────┐                                  │
│   │ User-Assigned Managed    │  ← used everywhere in the        │
│   │ Identity  (the "UAMI")   │     tutorial. One identity,      │
│   └────────────┬─────────────┘     many roles.                  │
│                │                                                │
│                ├── attached to Azure SQL server                 │
│                │     (primary identity for outbound HTTP        │
│                │      from sp_invoke_external_rest_endpoint)    │
│                │                                                │
│                └── role: "Cognitive Services OpenAI User"       │
│                      on the Foundry account                     │
│                                                                 │
│   ┌──────────────────────────┐    ┌─────────────────────────┐   │
│   │ Azure SQL server         │    │ Azure AI Foundry        │   │
│   │   GP_Gen5 serverless     │    │   account + project     │   │
│   │   Entra-only auth        │    │   embedding deploy:     │   │
│   │   You = AAD admin        │    │   text-embedding-3-small│   │
│   │   DB: ProductsDB         │    │   (1536 dims)           │   │
│   └──────────────────────────┘    └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Why one UAMI for everything?

A UAMI is an Entra identity that lives in your subscription and can be
attached to many Azure resources. We use one for the whole tutorial so
that:

- There is **one principal** to grant data + model access to. You don't
  end up with five system-assigned identities to keep track of.
- Service-to-service calls **never need a key or password**. The Azure
  policy on the target subscription forbids local auth on Azure SQL and
  on Foundry, so MI is the only working option anyway.
- Deleting the UAMI is a single, clean revocation point.

| Step | Where the UAMI is used | Permission granted |
|------|------------------------|--------------------|
| **1 (here)** | Attached as primary identity on the **Azure SQL server**. Lets `sp_invoke_external_rest_endpoint` acquire tokens as the UAMI. | — |
| **1 (here)** | On the **Foundry account** | `Cognitive Services OpenAI User` (so SQL can call the embedding endpoint) |
| **2** | Inside the **database** | `CREATE USER … FROM EXTERNAL PROVIDER`, granted least-privilege EXEC/SELECT (so DAB can later query as the UAMI) |
| **5** | On the **Azure Container Registry** | `AcrPull` (so ACA can pull the DAB image without admin creds) |
| **5** | Attached to the **DAB Container App** | UAMI is the app's identity → tokens for SQL + ACR |

You as a person also get one role here: **SQL AAD admin** on the new SQL
server. That's how you connect with `sqlcmd -G`, SSMS, or Azure Data
Studio to run the SQL scripts in steps 2 and 3.

---

## Prerequisites

This step assumes you have already completed the
[**Prerequisites** section in the root README](../../README.md#prerequisites-one-time-setup--do-this-before-step-1).
You need at minimum:

- `pwsh` 7+, `az` 2.60+, `az bicep` installed, `sqlcmd` (go-sqlcmd, with `-G` support)
- You are logged in (`az login`) and on the right subscription (`az account show`)
- Subscription permission to create resources **and** create role assignments in the target RG

> **Region.** The default in the script is `eastus2` because it has broad
> Foundry model availability. If your tenant restricts regions, pass
> `-Location` to whatever you're allowed. The Bicep is region-agnostic.

> **Subscription policy.** If your sub denies UAMI on Azure SQL or
> denies `disableLocalAuth` on Cognitive Services, the deploy will fail
> at the policy check. Capture the exact policy denial — that determines
> the smallest possible workaround we'd need to add.

---

## Pick your sample data path

You have **three** options for what data to embed:

1. **Use the included sample data** *(default)* — 10 products, 18 reviews
   about office equipment. Fastest path to a working demo. Good if you
   want to see the whole tutorial work first and bring your own data
   later.
2. **Skip the sample data** — pass `-SeedSampleData:$false` to the deploy
   script. Tables `dbo.Products` and `dbo.ProductReviews` will exist but
   be empty. Use the BYO appendix in step 2 to point everything at your
   own table.
3. **Both** — let the sample data deploy here, then **also** create your
   own table later. Step 2's BYO appendix walks through making a parallel
   `find_similar_<your_table>_hybrid` SP. The two paths don't conflict.

You can change your mind any time. Choosing "sample data" now does
**not** prevent you from adding your own table later.

---

## Run it

From the repo root, in PowerShell 7:

```powershell
# Login if you haven't already
az login

# Pick a subscription (optional)
az account set --subscription "<your subscription name or id>"

# Deploy
.\steps\01-foundation\deploy.ps1 `
    -ResourceGroupName rg-sqlrag-dev `
    -Location westus `
    -NamePrefix sqlrag
```

Skip the sample data:

```powershell
.\steps\01-foundation\deploy.ps1 `
    -ResourceGroupName rg-sqlrag-dev `
    -Location westus `
    -NamePrefix sqlrag `
    -SeedSampleData:$false
```

Skip every SQL script (just the Bicep — useful if your client cannot
reach Azure SQL on port 1433 from where you are):

```powershell
.\steps\01-foundation\deploy.ps1 `
    -ResourceGroupName rg-sqlrag-dev `
    -NamePrefix sqlrag `
    -SkipSqlScripts
```

The script prints what it's doing in 8 numbered sections. The slow
section is **5/8** — Bicep deploy — typically 3–6 minutes. Foundry
account creation is the long pole.

---

## What the script does, mapped to files

| Script step | Action | Files involved |
|---|---|---|
| 1/8 | Verifies `az login`, optionally switches subscription | — |
| 2/8 | Resolves your AAD object id + UPN — used as SQL AAD admin | `az ad signed-in-user show` |
| 3/8 | Resolves your public IPv4 — added to SQL firewall | `https://api.ipify.org` |
| 4/8 | Creates the resource group if missing | `az group create` |
| 5/8 | Deploys the Bicep template | [bicep/main.bicep](bicep/main.bicep) |
| 6/8 | Creates `Products` + `ProductReviews` (the `ReviewEmbedding VECTOR(1536)` column is created here but stays NULL) | [sql/00-create-schema.sql](sql/00-create-schema.sql) |
| 7/8 | (default) seeds 10 products + 18 reviews | [sql/01-seed-products.sql](sql/01-seed-products.sql), [sql/02-seed-reviews.sql](sql/02-seed-reviews.sql) |
| 8/8 | Prints summary; writes `outputs.json` for later steps | `steps/01-foundation/outputs.json` |

---

## Verify

After the script finishes, confirm three things.

### 1. Resources exist

```powershell
az resource list --resource-group rg-sqlrag-dev --output table
```

You should see roughly:

| Type | Name |
|------|------|
| `Microsoft.ManagedIdentity/userAssignedIdentities` | `sqlrag-uami-dev` |
| `Microsoft.Sql/servers` | `sqlrag-sql-dev-<6char>` |
| `Microsoft.Sql/servers/databases` | `ProductsDB` (under the server) |
| `Microsoft.CognitiveServices/accounts` | `sqlrag-ai-dev-<6char>` |
| `Microsoft.CognitiveServices/accounts/projects` | `sqlrag-proj-dev` |
| `Microsoft.CognitiveServices/accounts/deployments` | `embedding` |

### 2. You can connect to SQL with your AAD identity

```powershell
$fqdn = (Get-Content .\steps\01-foundation\outputs.json | ConvertFrom-Json).sqlServerFqdn
sqlcmd -S $fqdn -d ProductsDB -G -Q "SELECT SUSER_NAME() AS who, DB_NAME() AS db;"
```

`who` should be your UPN. If you get a login failure, the most common
cause is that `az login` is using a different tenant than the one your
SQL server lives in. Run `az account show` and reconcile.

### 3. The sample data is there (skip if you used `-SeedSampleData:$false`)

```powershell
sqlcmd -S $fqdn -d ProductsDB -G -Q "SELECT COUNT(*) AS products FROM dbo.Products; SELECT COUNT(*) AS reviews FROM dbo.ProductReviews;"
```

Expect 10 products and 18 reviews. The `ReviewEmbedding` column is
NULL — that's correct, you'll fill it in step 2.



## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Not logged in. Run "az login" first.` | No active az session | `az login`, then re-run |
| `Forbidden` during Bicep deploy on the Foundry account | Subscription policy denies `disableLocalAuth = false` *or* requires CMK *or* denies the model | Capture the exact policy id from the error; that tells us which property to flip |
| `Login failed for user '<token-identified principal>'` when sqlcmd runs | You are signed into a tenant that isn't the SQL admin tenant | `az logout`, `az login --tenant <correct tenant>`, re-run with `-SkipSqlScripts` then run the SQL files manually |
| `Could not detect public IP` warning | Your network blocks `api.ipify.org` | Run the deploy with `-SkipSqlScripts`, then add a firewall rule manually: `az sql server firewall-rule create -g <rg> -s <server> -n dev --start-ip-address <ip> --end-ip-address <ip>` |
| Embedding deployment fails with `Quota exceeded` | The sub has no quota for `text-embedding-3-small` in this region | Try a different region, or request quota in the portal: **Azure AI Foundry → Quotas** |
| `sqlcmd : The term 'sqlcmd' is not recognized` | `go-sqlcmd` is not installed | Install via `winget install Microsoft.Sqlcmd` (Windows) or follow the [docs](https://learn.microsoft.com/sql/tools/sqlcmd/go-sqlcmd-utility) |

---

## Next

Open [steps/02-embeddings-in-sql/step2.md](../02-embeddings-in-sql/step2.md).
You'll wire SQL to the embedding endpoint via the UAMI, create
`get_embedding`, add the vector column (already there from step 1, you'll
just verify), and backfill embeddings for the seeded reviews.
