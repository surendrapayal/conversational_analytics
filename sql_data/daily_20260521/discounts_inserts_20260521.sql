-- Daily inserts into discounts (2026-05-21T10:00:00)

INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES ('PROMO001_2434', 'Dream mind team.', 'fixed', 16.12, '1998-12-11'::date, '1999-01-04'::date) RETURNING id;
INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES ('PROMO002_4161', 'Method price because.', 'percent', 29.89, '1993-05-11'::date, '1993-06-27'::date) RETURNING id;
INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES ('PROMO003_7444', 'Small catch itself free program.', 'percent', 17.29, '1989-10-21'::date, '1989-11-06'::date) RETURNING id;
