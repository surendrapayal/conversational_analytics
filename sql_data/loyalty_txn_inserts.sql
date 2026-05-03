-- ── loyalty_txn ───────────────────────────────────────────────────────────────
-- Earn points on completed orders (1 point per $1 spent)
-- Redeem points on ~20% of orders with sufficient balance
-- Run AFTER orders_inserts.sql and loyalty_accounts_inserts.sql

-- Earn points for completed orders
INSERT INTO loyalty_txn (loyalty_id, points_change, txn_type, txn_time)
SELECT
    la.id,
    FLOOR(o.total_amount)::int,
    'earn',
    o.order_time
FROM orders o
JOIN loyalty_accounts la ON la.customer_id = o.customer_id
WHERE o.status = 'completed';

-- Redeem points on ~20% of completed orders
INSERT INTO loyalty_txn (loyalty_id, points_change, txn_type, txn_time)
SELECT
    la.id,
    -(FLOOR(RANDOM() * 100 + 50)::int),
    'redeem',
    o.order_time + INTERVAL '5 minutes'
FROM orders o
JOIN loyalty_accounts la ON la.customer_id = o.customer_id
WHERE o.status = 'completed'
  AND la.points_balance >= 50
  AND RANDOM() < 0.20;
