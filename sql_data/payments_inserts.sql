-- ── payments ──────────────────────────────────────────────────────────────────
-- One payment per completed order
-- Run AFTER orders_inserts.sql

INSERT INTO payments (order_id, payment_time, amount, method, status)
SELECT
    o.id,
    o.order_time + INTERVAL '30 minutes',
    o.total_amount + o.tax_amount + o.tip_amount,
    CASE FLOOR(RANDOM() * 5)::int
        WHEN 0 THEN 'cash'
        WHEN 1 THEN 'credit_card'
        WHEN 2 THEN 'debit_card'
        WHEN 3 THEN 'mobile_pay'
        ELSE 'gift_card'
    END,
    'paid'
FROM orders o
WHERE o.status = 'completed';
