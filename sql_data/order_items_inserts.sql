-- ── order_items ───────────────────────────────────────────────────────────────
-- Each order gets 1-4 random active menu items
-- Run AFTER orders_inserts.sql

INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price)
SELECT
    o.id                                                                AS order_id,
    mi.id                                                               AS menu_item_id,
    (FLOOR(RANDOM() * 3) + 1)::int                                      AS quantity,
    mi.base_price                                                       AS unit_price
FROM orders o
JOIN LATERAL (
    SELECT id, base_price
    FROM menu_items
    WHERE is_active = true
    ORDER BY RANDOM()
    LIMIT (FLOOR(RANDOM() * 3) + 1)::int
) mi ON true;
