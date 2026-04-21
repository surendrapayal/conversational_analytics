-- Insert data into location
-- Generated at: 2026-04-21T14:16:56.347133

INSERT INTO location (name, address, timezone) VALUES ('Downtown Diner', '1632 Collins Lane Suite 286, New Margaret, MI 71959', 'EST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Uptown Bistro', '786 Hall Wells, Brewerbury, NM 88572', 'UTC') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Riverside Cafe', 'PSC 0529, Box 7108, APO AA 07715', 'EST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Mountain View Restaurant', 'PSC 3137, Box 8712, APO AA 26696', 'PST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Lakeside Grill', '634 Heather Keys, Anthonyhaven, OK 14654', 'UTC') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Harbor Point Eatery', '4084 Thomas Green Apt. 644, Dawnberg, WI 62309', 'PST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Sunset Plaza Restaurant', '741 Charles Skyway, Christinamouth, MO 74804', 'CST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Garden District Cafe', '786 Robert Cove Suite 115, Tranbury, RI 94298', 'UTC') RETURNING id;
