-- ── loyalty_accounts (one per customer) ──────────────────────────────────────
INSERT INTO loyalty_accounts (customer_id, points_balance)
SELECT id, FLOOR(RANDOM() * 2000)::int FROM customers ORDER BY id;
