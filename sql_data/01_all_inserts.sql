-- ── Master insert script — run in order ──────────────────────────────────────
-- Dependency order:
--   1. No dependencies
--   2. Depends on location, roles
--   3. Depends on employee, customers, menu_items, tables, discounts
--   4. Depends on orders, loyalty_accounts

\i sql_data/tables_inserts.sql
\i sql_data/supplier_inserts.sql
\i sql_data/supplier_items_inserts.sql
\i sql_data/inventory_inserts.sql
\i sql_data/loyalty_accounts_inserts.sql
\i sql_data/discounts_inserts.sql
\i sql_data/shifts_inserts.sql
\i sql_data/orders_inserts.sql
\i sql_data/order_items_inserts.sql
\i sql_data/payments_inserts.sql
\i sql_data/order_discounts_inserts.sql
\i sql_data/reservations_inserts.sql
\i sql_data/loyalty_txn_inserts.sql
