-- Insert data into location
-- Generated at: 2026-04-20T10:07:35.616329

INSERT INTO location (name, address, timezone) VALUES ('Downtown Diner', '4892 Brian Spur Suite 803, Mistyland, TN 16373', 'CST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Uptown Bistro', 'USNV Carr, FPO AP 00799', 'PST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Riverside Cafe', '969 Williamson Underpass Suite 879, West Joshuastad, WY 01139', 'CST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Mountain View Restaurant', '616 Carly Lane Suite 524, North Erinview, NH 68283', 'EST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Lakeside Grill', '5297 Arnold Via Suite 704, Muellerbury, IL 51509', 'UTC') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Harbor Point Eatery', '51177 Lorraine View Suite 256, Jeffreychester, OH 41433', 'UTC') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Sunset Plaza Restaurant', '82778 Katherine Harbor Apt. 904, East Amy, NH 91628', 'CST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Garden District Cafe', '88523 Janet Cove Apt. 254, Hooverton, AZ 36482', 'PST') RETURNING id;
