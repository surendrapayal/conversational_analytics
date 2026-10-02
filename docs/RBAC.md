# Role-Based Access Control (RBAC)

## Overview

The system enforces role-based data access at three levels:

1. **Table-level access** — which tables a role can query
2. **Column-level restrictions** — which columns are hidden from the LLM for a role
3. **Row-level filters** — which rows are visible for a role (e.g. a location manager sees only their location)

All RBAC configuration is defined in `.env` and loaded dynamically at startup. No code changes are needed to add or modify roles.

---

## How It Works

### At Startup
When the application starts, `sql_tools._init()` runs once and builds a **separate SQL context** for each role defined in `.env`. Each context contains:
- A `SQLDatabase` instance with only the role's allowed tables visible
- A `SQLDatabaseToolkit` with 4 SQL tools scoped to those tables
- A `SystemMessage` with the system prompt listing only the allowed tables

These contexts are cached in `_role_cache` (a module-level dict). Lookup is O(1) per request.

### At Request Time
The `role` header from the HTTP request is passed through the entire call chain:
```
HTTP Header: role: location_manager
    → nlq_controller → AgentRequest.role
    → agent_service → graph state: role
    → agent_node → get_sql_tools(role) + get_system_message(role)
    → tools_node → get_sql_tools(role)
```

If the role is unknown (not in `_role_cache`), a `ValueError` is raised and the request returns HTTP 500.

If no role is provided, the **default context** is used (all tables, no restrictions).

---

## Configuration Reference

### Table-Level Access
```env
ROLE_CHEF=menu_items,menu_categories,ingredients,recipe_items,inventory,order_items
ROLE_WAITER=orders,order_items,tables,reservations,customers
ROLE_CASHIER=orders,payments,order_discounts,discounts,loyalty_accounts,loyalty_txn
ROLE_LOCATION_MANAGER=orders,order_items,payments,employees,shifts,tables,reservations,customers,loyalty_accounts,loyalty_txn,inventory
ROLE_GENERAL_MANAGER=orders,order_items,payments,employees,shifts,tables,reservations,customers,loyalty_accounts,loyalty_txn,inventory,menu_items,menu_categories,ingredients,recipe_items,discounts,locations
ROLE_ADMIN=<all tables>
ROLE_ANALYST=<all tables>
```

### Column-Level Restrictions
Hides specific columns from the LLM's schema view. The LLM cannot query what it cannot see.
```env
ROLE_WAITER_RESTRICT_COLUMNS=customers.email,customers.phone,customers.date_of_birth
ROLE_CASHIER_RESTRICT_COLUMNS=customers.date_of_birth
```

Format: `table.column,table.column,...`

### Row-Level Filters
Appends a `WHERE` condition to queries on specific tables. Used to scope a role to a specific location or entity.
```env
ROLE_LOCATION_MANAGER_ROW_FILTERS=orders:location_id=5|employees:location_id=5|shifts:location_id=5
```

Format: `table:condition|table:condition|...` (use `|` as separator when conditions contain commas)

---

## Role Enforcement in the System Prompt

The system prompt explicitly lists only the tables the role can access:

```
You have access to a PostgreSQL database with ONLY the following tables: orders, payments, employees, ...
```

This means the LLM is instructed at the prompt level — not just at the DB connection level — to only query the allowed tables. Even if the LLM tried to query a restricted table, the `SQLDatabase` instance would reject it because `include_tables` is set.

---

## Column Restriction Implementation

When column restrictions are configured for a role, `_build_custom_table_info()` is called:

1. Fetches live table descriptions from the DB (column names, types, sample rows).
2. Strips restricted columns from the description text using regex.
3. Passes the sanitised descriptions as `custom_table_info` to `SQLDatabase`.

The LLM never sees the restricted column names in the schema — it cannot reference them in SQL.

---

## Semantic Layer per Role

The `semantic_layer.json` file can define role-specific context:
- `roles.<role>.description` — injected as "YOUR ROLE" in the system prompt
- `roles.<role>.business_rules` — role-specific guidelines
- `roles.<role>.domains` — restricts which metric domains are shown to the role

This allows, for example, a `chef` role to see only food cost and inventory metrics, while a `general_manager` sees all metrics.

---

## Role Summary Table

| Role | Typical Table Access | Column Restrictions | Row Filters |
|---|---|---|---|
| `admin` | All tables | None | None |
| `analyst` | All tables | None | None |
| `general_manager` | All operational + menu tables | None | None |
| `location_manager` | Operational tables | None | By location_id |
| `chef` | Menu, ingredients, inventory | None | None |
| `waiter` | Orders, tables, reservations | Customer PII columns | None |
| `cashier` | Orders, payments, loyalty | Customer DOB | None |
