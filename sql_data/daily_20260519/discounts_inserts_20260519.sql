-- Daily inserts into discounts (2026-05-19T10:00:00)

INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES ('PROMO001_9395', 'Trade race strong.', 'percent', 24.17, '2017-07-01'::date, '2017-07-18'::date) RETURNING id;
INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES ('PROMO002_5398', 'Some pay consumer then.', 'fixed', 30.46, '1999-09-11'::date, '1999-10-16'::date) RETURNING id;
INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES ('PROMO003_7394', 'Next knowledge sing result.', 'percent', 19.93, '1994-08-12'::date, '1994-09-17'::date) RETURNING id;
