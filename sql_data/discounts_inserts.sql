-- ── discounts ─────────────────────────────────────────────────────────────────
INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES
('WELCOME10',  'Welcome discount for new customers',          'percent', 10.00, '2026-01-01', '2026-12-31'),
('SUMMER20',   'Summer season promotion',                     'percent', 20.00, '2026-06-01', '2026-08-31'),
('HAPPY5',     'Happy hour fixed discount',                   'fixed',    5.00, '2026-01-01', '2026-12-31'),
('LOYALTY15',  'Loyalty member discount',                     'percent', 15.00, '2026-01-01', '2026-12-31'),
('WEEKEND10',  'Weekend special discount',                    'percent', 10.00, '2026-01-01', '2026-12-31'),
('BIRTHDAY25', 'Birthday month special',                      'percent', 25.00, '2026-01-01', '2026-12-31'),
('FLAT10',     'Flat $10 off on orders above $50',            'fixed',   10.00, '2026-01-01', '2026-12-31'),
('LUNCH15',    'Weekday lunch discount',                      'percent', 15.00, '2026-01-01', '2026-12-31'),
('FAMILY20',   'Family meal deal discount',                   'percent', 20.00, '2026-01-01', '2026-12-31'),
('EARLYBIRD',  'Early bird dinner discount before 6pm',       'percent', 12.00, '2026-01-01', '2026-12-31'),
('FALL10',     'Fall season promotion',                       'percent', 10.00, '2026-09-01', '2026-11-30'),
('HOLIDAY30',  'Holiday season special',                      'percent', 30.00, '2026-12-01', '2026-12-31'),
('FLAT5',      'Flat $5 off any order',                       'fixed',    5.00, '2026-01-01', '2026-06-30'),
('GROUPDINE',  '10% off for groups of 6 or more',             'percent', 10.00, '2026-01-01', '2026-12-31'),
('NEWMENU',    'Try our new menu — 15% off selected items',   'percent', 15.00, '2026-04-01', '2026-05-31');
