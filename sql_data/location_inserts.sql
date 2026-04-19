-- Insert data into location
-- Generated at: 2026-04-19T14:26:33.580193

INSERT INTO location (name, address, timezone) VALUES ('Downtown Diner', '682 Lamb Island Apt. 046, Lake Deniseberg, MO 49356', 'MST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Uptown Bistro', '3657 Anna Mountain Apt. 485, New Dorischester, AZ 65297', 'CST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Riverside Cafe', '5957 Michael Bypass Suite 235, South Johnburgh, NY 91228', 'EST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Mountain View Restaurant', '8789 Griffin Canyon, West Courtney, NJ 05976', 'CST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Lakeside Grill', '359 Jennifer Plains, Christianland, AS 40964', 'PST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Harbor Point Eatery', '559 Church Mountain, Port Claudiaview, VT 17202', 'CST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Sunset Plaza Restaurant', 'USS Shaffer, FPO AP 04301', 'MST') RETURNING id;
INSERT INTO location (name, address, timezone) VALUES ('Garden District Cafe', '86333 Taylor Club Suite 413, Lake Michaelhaven, HI 51992', 'CST') RETURNING id;
