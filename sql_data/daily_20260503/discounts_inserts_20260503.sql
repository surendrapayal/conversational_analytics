-- Daily inserts into discounts (2026-05-03T18:48:26.989853)

INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES ('PROMO001_9330', 'Middle tax by activity song.', 'fixed', 48.17, '2010-08-23'::date, '2010-10-16'::date) RETURNING id;
INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES ('PROMO002_1727', 'Capital buy nation.', 'fixed', 23.35, '2010-11-30'::date, '2010-12-16'::date) RETURNING id;
INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES ('PROMO003_3116', 'Building cut material high environmental to.', 'percent', 26.56, '2025-07-22'::date, '2025-08-28'::date) RETURNING id;
