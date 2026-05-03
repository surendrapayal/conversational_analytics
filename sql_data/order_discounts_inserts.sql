-- ── order_discounts ───────────────────────────────────────────────────────────
-- Apply a random discount to ~30% of completed orders
-- Run AFTER orders_inserts.sql and discounts_inserts.sql

INSERT INTO order_discounts (order_id, discount_id)
SELECT
    o.id,
    (SELECT id FROM discounts ORDER BY RANDOM() LIMIT 1)
FROM orders o
WHERE o.status = 'completed'
  AND RANDOM() < 0.30;
