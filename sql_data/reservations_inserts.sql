-- ── reservations ─────────────────────────────────────────────────────────────
-- ~2 reservations per location per date across 5 dates
-- Run AFTER tables_inserts.sql

INSERT INTO reservations (table_id, customer_id, start_time, end_time, status)
SELECT
    t.id                                                                AS table_id,
    (SELECT id FROM customers ORDER BY RANDOM() LIMIT 1)               AS customer_id,
    res_date + (INTERVAL '1 hour' * (17 + FLOOR(RANDOM() * 4)::int))   AS start_time,
    res_date + (INTERVAL '1 hour' * (19 + FLOOR(RANDOM() * 4)::int))   AS end_time,
    CASE WHEN RANDOM() < 0.70 THEN 'checked_in'
         WHEN RANDOM() < 0.50 THEN 'booked'
         WHEN RANDOM() < 0.50 THEN 'no_show'
         ELSE 'cancelled' END                                           AS status
FROM
    (VALUES
        ('2026-04-19'::date),
        ('2026-04-20'::date),
        ('2026-04-21'::date),
        ('2026-04-22'::date),
        ('2026-04-25'::date)
    ) AS dates(res_date),
    LATERAL (
        SELECT t.id
        FROM tables t
        ORDER BY RANDOM()
        LIMIT 8
    ) t;
