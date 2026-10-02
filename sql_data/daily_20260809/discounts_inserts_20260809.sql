-- Daily inserts into discounts (2026-08-09T18:17:26.731319)

INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES ('PROMO001_2871', 'Large stage others central choose.', 'fixed', 36.08, '1988-11-18'::date, '1989-01-29'::date) RETURNING id;
INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES ('PROMO002_1893', 'Cultural hit between.', 'percent', 8.69, '2004-03-14'::date, '2004-05-13'::date) RETURNING id;
INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES ('PROMO003_2981', 'Continue suffer city.', 'fixed', 23.58, '2024-05-31'::date, '2024-08-04'::date) RETURNING id;
