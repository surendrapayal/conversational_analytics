# Configuration Reference

All configuration is loaded from the `.env` file at the project root via `pydantic-settings`. The settings are validated at startup and cached as a singleton via `@lru_cache`.

---

## LLM Settings

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_CLOUD_PROJECT` | *(required)* | GCP project ID for Vertex AI |
| `LLM_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `LLM_REGION` | `us-east1` | Vertex AI region |
| `LLM_TEMPERATURE` | `0.7` | Sampling temperature (0.0–1.0) |
| `LLM_MAX_OUTPUT_TOKENS` | `2048` | Maximum tokens in LLM response |
| `LLM_TOP_P` | `0.9` | Nucleus sampling parameter |
| `THINKING_LEVEL` | `medium` | Gemini thinking depth: `none`, `low`, `medium`, `high` |
| `INCLUDE_THOUGHTS` | `true` | Whether to capture chain-of-thought reasoning |

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
# Required
GOOGLE_CLOUD_PROJECT=my-gcp-project

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
