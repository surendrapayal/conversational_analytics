# Database Schema

## Overview

The system uses a single PostgreSQL instance (port 5433, database `zenvyra`) for three purposes:

1. **Analytics data** — the restaurant operational data the agent queries
2. **Agent memory** — long-term conversation store (pgvector) and audit log
3. **Short-term checkpoints** — stored in Redis (separate service)

Two separate DB users are used:
- `ca_agent_user` — read-only access to analytics tables
- `admin_user` — read/write access to memory and audit tables

---

## Analytics Database Schema

The restaurant analytics database contains the following tables:

### Core Entities

#### `locations`
Restaurant locations/branches.
| Column | Type | Description |
|---|---|---|
| location_id | INT PK | Unique location identifier |
| name | TEXT | Location name |
| address | TEXT | Physical address |
| city | TEXT | City |
| phone | TEXT | Contact number |
| manager_id | INT FK→employees | Assigned manager |

#### `employees`
Staff members across all locations.
| Column | Type | Description |
|---|---|---|
| employee_id | INT PK | Unique employee identifier |
| first_name | TEXT | First name |
| last_name | TEXT | Last name |
| role | TEXT | Job role (manager, chef, waiter, etc.) |
| location_id | INT FK→locations | Assigned location |
| hire_date | DATE | Date of hire |
| hourly_rate | NUMERIC | Pay rate |

#### `customers`
Registered customers.
| Column | Type | Description |
|---|---|---|
| customer_id | INT PK | Unique customer identifier |
| first_name | TEXT | First name |
| last_name | TEXT | Last name |
| email | TEXT | Email address (PII — restricted for some roles) |
| phone | TEXT | Phone number (PII — restricted for some roles) |
| date_of_birth | DATE | DOB (PII — restricted for some roles) |

#### `tables`
Physical dining tables per location.
| Column | Type | Description |
|---|---|---|
| table_id | INT PK | Unique table identifier |
| location_id | INT FK→locations | Location |
| table_number | INT | Table number within location |
| capacity | INT | Seating capacity |

---

### Menu

#### `menu_categories`
Top-level menu groupings (Starters, Mains, Desserts, Drinks, etc.).
| Column | Type | Description |
|---|---|---|
| category_id | INT PK | Unique category identifier |
| name | TEXT | Category name |
| description | TEXT | Description |

#### `menu_items`
Individual dishes and drinks on the menu.
| Column | Type | Description |
|---|---|---|
| item_id | INT PK | Unique item identifier |
| category_id | INT FK→menu_categories | Category |
| name | TEXT | Item name |
| description | TEXT | Description |
| price | NUMERIC | Selling price |
| is_active | BOOLEAN | Whether currently available |

#### `ingredients`
Raw ingredients used in recipes.
| Column | Type | Description |
|---|---|---|
| ingredient_id | INT PK | Unique ingredient identifier |
| name | TEXT | Ingredient name |
| unit | TEXT | Unit of measure (kg, litre, etc.) |
| cost_per_unit | NUMERIC | Cost per unit |

#### `recipe_items`
Links menu items to their ingredients (bill of materials).
| Column | Type | Description |
|---|---|---|
| recipe_id | INT PK | Unique recipe entry |
| item_id | INT FK→menu_items | Menu item |
| ingredient_id | INT FK→ingredients | Ingredient |
| quantity | NUMERIC | Quantity required |

#### `inventory`
Current stock levels per ingredient per location.
| Column | Type | Description |
|---|---|---|
| inventory_id | INT PK | Unique inventory record |
| location_id | INT FK→locations | Location |
| ingredient_id | INT FK→ingredients | Ingredient |
| quantity_on_hand | NUMERIC | Current stock |
| reorder_level | NUMERIC | Reorder trigger threshold |
| last_updated | TIMESTAMPTZ | Last stock update time |

---

### Orders & Payments

#### `orders`
Customer orders.
| Column | Type | Description |
|---|---|---|
| order_id | INT PK | Unique order identifier |
| location_id | INT FK→locations | Location |
| table_id | INT FK→tables | Table (nullable for takeaway) |
| customer_id | INT FK→customers | Customer (nullable for walk-ins) |
| employee_id | INT FK→employees | Serving staff |
| order_time | TIMESTAMPTZ | When order was placed |
| status | TEXT | pending / in_progress / completed / cancelled |
| order_type | TEXT | dine_in / takeaway / delivery |
| total_amount | NUMERIC | Gross order total |
| notes | TEXT | Special instructions |

#### `order_items`
Line items within an order.
| Column | Type | Description |
|---|---|---|
| order_item_id | INT PK | Unique line item identifier |
| order_id | INT FK→orders | Parent order |
| item_id | INT FK→menu_items | Menu item |
| quantity | INT | Quantity ordered |
| unit_price | NUMERIC | Price at time of order |
| subtotal | NUMERIC | quantity × unit_price |

#### `payments`
Payment records for orders.
| Column | Type | Description |
|---|---|---|
| payment_id | INT PK | Unique payment identifier |
| order_id | INT FK→orders | Associated order |
| payment_method | TEXT | cash / card / mobile / voucher |
| amount | NUMERIC | Amount paid |
| tip_amount | NUMERIC | Tip included |
| payment_time | TIMESTAMPTZ | When payment was made |
| status | TEXT | completed / refunded / pending |

#### `discounts`
Discount definitions.
| Column | Type | Description |
|---|---|---|
| discount_id | INT PK | Unique discount identifier |
| name | TEXT | Discount name |
| discount_type | TEXT | percentage / fixed |
| value | NUMERIC | Discount amount or percentage |
| is_active | BOOLEAN | Whether currently active |

#### `order_discounts`
Applied discounts on orders.
| Column | Type | Description |
|---|---|---|
| id | INT PK | Unique record |
| order_id | INT FK→orders | Order |
| discount_id | INT FK→discounts | Applied discount |
| discount_amount | NUMERIC | Actual amount discounted |

---

### Reservations & Loyalty

#### `reservations`
Table reservations.
| Column | Type | Description |
|---|---|---|
| reservation_id | INT PK | Unique reservation identifier |
| location_id | INT FK→locations | Location |
| table_id | INT FK→tables | Reserved table |
| customer_id | INT FK→customers | Customer |
| reservation_time | TIMESTAMPTZ | Reservation date/time |
| party_size | INT | Number of guests |
| status | TEXT | confirmed / cancelled / completed / no_show |
| notes | TEXT | Special requests |

#### `loyalty_accounts`
Customer loyalty programme accounts.
| Column | Type | Description |
|---|---|---|
| loyalty_id | INT PK | Unique loyalty account |
| customer_id | INT FK→customers | Customer |
| points_balance | INT | Current points balance |
| tier | TEXT | bronze / silver / gold / platinum |
| joined_date | DATE | Enrolment date |

#### `loyalty_txn`
Loyalty points transactions.
| Column | Type | Description |
|---|---|---|
| txn_id | INT PK | Unique transaction |
| loyalty_id | INT FK→loyalty_accounts | Loyalty account |
| order_id | INT FK→orders | Associated order (nullable) |
| txn_type | TEXT | earn / redeem / adjustment |
| points | INT | Points earned or redeemed |
| txn_date | TIMESTAMPTZ | Transaction timestamp |

---

### Workforce

#### `shifts`
Employee shift records.
| Column | Type | Description |
|---|---|---|
| shift_id | INT PK | Unique shift identifier |
| employee_id | INT FK→employees | Employee |
| location_id | INT FK→locations | Location |
| shift_date | DATE | Date of shift |
| start_time | TIME | Shift start |
| end_time | TIME | Shift end |
| hours_worked | NUMERIC | Total hours |
| role | TEXT | Role during this shift |

---

### Suppliers

#### `suppliers`
Ingredient suppliers.
| Column | Type | Description |
|---|---|---|
| supplier_id | INT PK | Unique supplier identifier |
| name | TEXT | Supplier name |
| contact_name | TEXT | Contact person |
| email | TEXT | Email |
| phone | TEXT | Phone |

#### `supplier_items`
Which suppliers provide which ingredients at what price.
| Column | Type | Description |
|---|---|---|
| id | INT PK | Unique record |
| supplier_id | INT FK→suppliers | Supplier |
| ingredient_id | INT FK→ingredients | Ingredient |
| unit_price | NUMERIC | Supplier's price per unit |
| lead_time_days | INT | Delivery lead time |

---

## Agent Memory Schema

Initialised by `pgscript/agent-memory-db-init.sql`.

### `store`
LangGraph `AsyncPostgresStore` document store. One row per saved conversation summary.
- `prefix`: namespace key (`conversation_summaries\x1f{user_id}`)
- `key`: `conversation_id` (UUID)
- `value`: JSONB `{summary, session_id, conversation_id, role}`

### `store_vectors`
pgvector embeddings for semantic search. One row per stored document field.
- `embedding`: `vector(768)` — Google `text-embedding-005` output
- HNSW index with cosine similarity for fast approximate nearest-neighbour search

### `query_log`
Audit trail — one row per conversation. See [Memory Architecture](MEMORY_ARCHITECTURE.md) for full schema.

### `agent_steps`
Audit trail — one row per ReAct step. See [Memory Architecture](MEMORY_ARCHITECTURE.md) for full schema.

---

## Key Relationships (Join Guide)

```
orders ──────────────────→ locations       (orders.location_id = locations.location_id)
orders ──────────────────→ customers       (orders.customer_id = customers.customer_id)
orders ──────────────────→ employees       (orders.employee_id = employees.employee_id)
orders ──────────────────→ tables          (orders.table_id = tables.table_id)
order_items ─────────────→ orders          (order_items.order_id = orders.order_id)
order_items ─────────────→ menu_items      (order_items.item_id = menu_items.item_id)
payments ────────────────→ orders          (payments.order_id = orders.order_id)
order_discounts ─────────→ orders          (order_discounts.order_id = orders.order_id)
order_discounts ─────────→ discounts       (order_discounts.discount_id = discounts.discount_id)
menu_items ──────────────→ menu_categories (menu_items.category_id = menu_categories.category_id)
recipe_items ────────────→ menu_items      (recipe_items.item_id = menu_items.item_id)
recipe_items ────────────→ ingredients     (recipe_items.ingredient_id = ingredients.ingredient_id)
inventory ───────────────→ locations       (inventory.location_id = locations.location_id)
inventory ───────────────→ ingredients     (inventory.ingredient_id = ingredients.ingredient_id)
reservations ────────────→ locations       (reservations.location_id = locations.location_id)
reservations ────────────→ customers       (reservations.customer_id = customers.customer_id)
loyalty_accounts ────────→ customers       (loyalty_accounts.customer_id = customers.customer_id)
loyalty_txn ─────────────→ loyalty_accounts(loyalty_txn.loyalty_id = loyalty_accounts.loyalty_id)
shifts ──────────────────→ employees       (shifts.employee_id = employees.employee_id)
shifts ──────────────────→ locations       (shifts.location_id = locations.location_id)
employees ───────────────→ locations       (employees.location_id = locations.location_id)
supplier_items ──────────→ suppliers       (supplier_items.supplier_id = suppliers.supplier_id)
supplier_items ──────────→ ingredients     (supplier_items.ingredient_id = ingredients.ingredient_id)
```
