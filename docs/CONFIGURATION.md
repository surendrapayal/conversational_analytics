# Configuration Reference

All configuration is loaded from the `.env` file at the project root via `pydantic-settings`. The settings are validated at startup and cached as a singleton via `@lru_cache`.

---

## LLM Settings

The application supports two LLM providers, selected via `LLM_PROVIDER`. The app exposes a single `get_llm()` factory, so switching providers requires no code changes — only env configuration.

### Provider selection

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `vertexai` | Backend to use: `vertexai` (Google Gemini) or `bedrock` (AWS Bedrock) |

> `LLM_PROVIDER` is read from `.env`. Because the app loads `.env` with `override=True`, a value in `.env` takes precedence over a shell environment variable of the same name. To switch providers, change it in `.env`.

### Shared (both providers)

| Variable | Default | Description |
|---|---|---|
| `LLM_TEMPERATURE` | `0.7` | Sampling temperature (0.0–1.0) |
| `LLM_TOP_P` | `0.9` | Nucleus sampling parameter |

### Vertex AI (`LLM_PROVIDER=vertexai`)

Authenticates with Application Default Credentials (ADC).

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_CLOUD_PROJECT` | *(required for vertexai)* | GCP project ID for Vertex AI |
| `LLM_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `LLM_REGION` | `us-east1` | Vertex AI region |
| `LLM_MAX_OUTPUT_TOKENS` | `2048` | Maximum tokens in LLM response |
| `THINKING_LEVEL` | `medium` | Gemini thinking depth: `minimal`, `low`, `medium`, `high` |
| `INCLUDE_THOUGHTS` | `true` | Whether to capture chain-of-thought reasoning |

> `GOOGLE_CLOUD_PROJECT` is only required when `LLM_PROVIDER=vertexai`; a startup error is raised if it is missing in that case.

### AWS Bedrock (`LLM_PROVIDER=bedrock`)

Uses the Bedrock Converse API via `langchain-aws`. Credential resolution is delegated to boto3's standard chain, so AWS SSO, API keys, and static credentials all work.

| Variable | Default | Description |
|---|---|---|
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-haiku-20240307-v1:0` | Bedrock model ID or inference profile ID |
| `BEDROCK_MAX_TOKENS` | `2048` | Maximum tokens in LLM response |
| `AWS_PROFILE` | *(unset)* | Named AWS profile to authenticate with (SSO or credentials file) |
| `AWS_REGION` | *(unset)* | AWS region hosting the model |

#### Value resolution: `.env` → shell → boto3 default

For `AWS_PROFILE`, `AWS_REGION`, and `BEDROCK_MODEL_ID`, each value is resolved in this order:

1. The value in `.env`, if set.
2. Otherwise the shell environment variable of the same name (e.g. `$env:AWS_PROFILE`).
3. Otherwise it is omitted, and boto3 applies its own default resolution.

This lets you keep `.env` free of machine-specific profile names and instead set them per session in the shell.

#### Authenticating with AWS SSO (recommended)

```powershell
# 1. Log in once per session (opens a browser)
aws sso login --profile my-profile

# 2. Point the app at that profile + region (shell env; .env can stay unset)
$env:AWS_PROFILE = "my-profile"
$env:AWS_REGION  = "us-east-1"

# 3. Select the Bedrock provider in .env
# LLM_PROVIDER=bedrock
```

> Leave `AWS_PROFILE` / `AWS_REGION` **commented out** in `.env` to use the shell values. An empty assignment like `AWS_PROFILE=` in `.env` would overwrite the shell value with an empty string (because `.env` is loaded with `override=True`), breaking SSO fallback.

#### Alternative auth methods

These are read directly from the process environment by boto3 (not from `.env`):

- **API key:** `AWS_BEARER_TOKEN_BEDROCK` (short-term Bedrock API key). **If set, it takes priority over `AWS_PROFILE`** — the app logs a warning when both are present. On Windows, avoid `setx` for this value: it truncates strings longer than 1024 characters, corrupting the token. Use `$env:AWS_BEARER_TOKEN_BEDROCK = "..."` or `[Environment]::SetEnvironmentVariable("AWS_BEARER_TOKEN_BEDROCK", "...", "User")`.
- **Static credentials:** `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`.

> `THINKING_LEVEL`, `INCLUDE_THOUGHTS`, and Gemini safety settings do not apply to Bedrock models.

---

## Analytics Database

| Variable | Default | Description |
|---|---|---|
| `ANALYTICS_DB_HOST` | `localhost` | PostgreSQL host |
| `ANALYTICS_DB_PORT` | `5433` | PostgreSQL port |
| `ANALYTICS_DB_NAME` | `zenvyra` | Database name |
| `ANALYTICS_DB_USER` | `ca_agent_user` | DB user (read-only) |
| `ANALYTICS_DB_PASSWORD` | `ca_agent_password` | DB password |
| `DB_IGNORE_TABLES` | *(empty)* | Comma-separated tables to hide from all roles |
| `DB_INCLUDE_TABLES` | *(empty)* | Comma-separated tables to expose (mutually exclusive with IGNORE) |
| `DB_SAMPLE_ROWS_IN_TABLE_INFO` | `3` | Sample rows shown to LLM in schema info |
| `DB_VIEW_SUPPORT` | `false` | Whether to include DB views |
| `DB_RESTRICT_COLUMNS` | *(empty)* | Global column restrictions: `table.col,table.col` |

> `DB_IGNORE_TABLES` and `DB_INCLUDE_TABLES` are mutually exclusive. Setting both raises a startup error.

---

## Short-Term Memory (Redis)

| Variable | Default | Description |
|---|---|---|
| `SHORT_TERM_MEMORY_TYPE` | `redis` | `redis` or `inmemory` |
| `SHORT_TERM_MEMORY_HOST` | `localhost` | Redis host |
| `SHORT_TERM_MEMORY_PORT` | `6379` | Redis port |
| `SHORT_TERM_MEMORY_PASSWORD` | *(empty)* | Redis password (optional) |
| `SHORT_TERM_MEMORY_SESSION_TTL` | `3600` | Session TTL in seconds |

> Use `inmemory` for local development without Redis. State is lost on restart.

---

## Long-Term Memory (PostgreSQL + pgvector)

| Variable | Default | Description |
|---|---|---|
| `LONG_TERM_MEMORY_DB_HOST` | `localhost` | PostgreSQL host |
| `LONG_TERM_MEMORY_DB_PORT` | `5433` | PostgreSQL port |
| `LONG_TERM_MEMORY_DB_NAME` | `zenvyra` | Database name |
| `LONG_TERM_MEMORY_DB_USER` | `admin_user` | DB user (read/write) |
| `LONG_TERM_MEMORY_DB_PASSWORD` | `admin_password` | DB password |
| `LONG_TERM_MEMORY_ENABLED` | `true` | Master switch for all memory persistence |
| `MEMORY_SEMANTIC_SEARCH_ENABLED` | `true` | Enable semantic recall at query time |
| `MEMORY_LONG_TERM_RECALL_LIMIT` | `3` | Max past conversations to inject per query |
| `EMBEDDING_MODEL` | `text-embedding-005` | Google embedding model |
| `EMBEDDING_DIMENSION` | `768` | Embedding vector dimensions |
| `MEMORY_SHORT_TERM_MESSAGE_LIMIT` | `0` | Max messages in context (0 = unlimited) |

---

## Application Server

| Variable | Default | Description |
|---|---|---|
| `APP_HOST` | `0.0.0.0` | Bind address |
| `APP_PORT` | `8000` | Bind port |
| `LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `AGENT_MAX_ITERATIONS` | `10` | Max ReAct loop iterations before forced response |
| `SEMANTIC_LAYER_PATH` | *(empty)* | Path to `semantic_layer.json` (relative or absolute) |
| `LOG_PROMPT` | `false` | Log full system prompt to `query_log.prompt` |

---

## Role-Based Access Control

Roles are auto-discovered from env vars matching `ROLE_<NAME>=...`.

### Table access
```env
ROLE_CHEF=menu_items,menu_categories,ingredients,recipe_items,inventory,order_items
ROLE_WAITER=orders,order_items,tables,reservations,customers
ROLE_CASHIER=orders,payments,order_discounts,discounts,loyalty_accounts,loyalty_txn
ROLE_LOCATION_MANAGER=orders,order_items,payments,employees,shifts,tables,reservations,customers,loyalty_accounts,loyalty_txn,inventory
ROLE_GENERAL_MANAGER=orders,order_items,payments,employees,shifts,tables,reservations,customers,loyalty_accounts,loyalty_txn,inventory,menu_items,menu_categories,ingredients,recipe_items,discounts,locations
ROLE_ANALYST=orders,order_items,payments,employees,shifts,tables,reservations,customers,loyalty_accounts,loyalty_txn,inventory,menu_items,menu_categories,ingredients,recipe_items,discounts,locations,suppliers,supplier_items
```

### Column restrictions (per role)
```env
ROLE_WAITER_RESTRICT_COLUMNS=customers.email,customers.phone,customers.date_of_birth
ROLE_CASHIER_RESTRICT_COLUMNS=customers.date_of_birth
```

### Row filters (per role)
```env
# Use | as separator when conditions contain commas
ROLE_LOCATION_MANAGER_ROW_FILTERS=orders:location_id=5|employees:location_id=5|shifts:location_id=5
```

---

## Minimal `.env` Example

```env
# LLM provider: vertexai | bedrock
LLM_PROVIDER=vertexai

# Vertex AI (required when LLM_PROVIDER=vertexai)
GOOGLE_CLOUD_PROJECT=my-gcp-project

# AWS Bedrock (used when LLM_PROVIDER=bedrock)
# BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
# Auth via SSO (recommended): run `aws sso login --profile my-profile`,
# then set these in the shell (keep them commented out here):
#   $env:AWS_PROFILE = "my-profile"
#   $env:AWS_REGION  = "us-east-1"

# Analytics DB
ANALYTICS_DB_HOST=localhost
ANALYTICS_DB_PORT=5433
ANALYTICS_DB_NAME=zenvyra
ANALYTICS_DB_USER=ca_agent_user
ANALYTICS_DB_PASSWORD=ca_agent_password

# Memory DB
LONG_TERM_MEMORY_DB_HOST=localhost
LONG_TERM_MEMORY_DB_PORT=5433
LONG_TERM_MEMORY_DB_NAME=zenvyra
LONG_TERM_MEMORY_DB_USER=admin_user
LONG_TERM_MEMORY_DB_PASSWORD=admin_password

# Redis
SHORT_TERM_MEMORY_HOST=localhost
SHORT_TERM_MEMORY_PORT=6379

# Roles
ROLE_ANALYST=orders,order_items,payments,employees,shifts,tables,reservations,customers,loyalty_accounts,loyalty_txn,inventory,menu_items,menu_categories,ingredients,recipe_items,discounts,locations
ROLE_CHEF=menu_items,menu_categories,ingredients,recipe_items,inventory,order_items
ROLE_WAITER=orders,order_items,tables,reservations,customers
ROLE_WAITER_RESTRICT_COLUMNS=customers.email,customers.phone,customers.date_of_birth
```
