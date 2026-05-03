-- ── orders ────────────────────────────────────────────────────────────────────
-- Generates ~300 orders spread across 5 dates and 20 locations
-- Uses generate_series + random to create realistic data
-- status distribution: 80% completed, 10% cancelled, 10% open

INSERT INTO orders (location_id, customer_id, employee_id, table_id, order_time, total_amount, tax_amount, tip_amount, status)
SELECT
    loc.id                                                          AS location_id,
    (SELECT id FROM customers ORDER BY RANDOM() LIMIT 1)           AS customer_id,
    (SELECT e.id FROM employee e WHERE e.location_id = loc.id ORDER BY RANDOM() LIMIT 1) AS employee_id,
    (SELECT t.id FROM tables t WHERE t.location_id = loc.id ORDER BY RANDOM() LIMIT 1)   AS table_id,
    order_date + (INTERVAL '1 hour' * (10 + FLOOR(RANDOM() * 12)::int)) AS order_time,
    ROUND((RANDOM() * 120 + 20)::numeric, 2)                       AS total_amount,
    ROUND((RANDOM() * 10 + 2)::numeric, 2)                         AS tax_amount,
    ROUND((RANDOM() * 15)::numeric, 2)                             AS tip_amount,
    CASE WHEN RANDOM() < 0.80 THEN 'completed'
         WHEN RANDOM() < 0.50 THEN 'cancelled'
         ELSE 'open' END                                            AS status
FROM
    location loc,
    (VALUES
        ('2026-04-19'::date),
        ('2026-04-20'::date),
        ('2026-04-21'::date),
        ('2026-04-22'::date),
        ('2026-04-25'::date)
    ) AS dates(order_date),
    generate_series(1, 3) AS gs  -- 3 orders per location per date = 300 total
WHERE EXISTS (SELECT 1 FROM employee e WHERE e.location_id = loc.id)
  AND EXISTS (SELECT 1 FROM tables t WHERE t.location_id = loc.id);
