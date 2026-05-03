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
-- Additional locations
INSERT INTO location (name, address, timezone) VALUES ('Midtown Steakhouse', '245 Park Avenue, New York, NY 10017', 'America/New_York');
INSERT INTO location (name, address, timezone) VALUES ('Beachfront Grille', '1420 Ocean Drive, Miami Beach, FL 33139', 'America/New_York');
INSERT INTO location (name, address, timezone) VALUES ('The Golden Fork', '832 Michigan Avenue, Chicago, IL 60611', 'America/Chicago');
INSERT INTO location (name, address, timezone) VALUES ('Lone Star Kitchen', '5610 Westheimer Road, Houston, TX 77056', 'America/Chicago');
INSERT INTO location (name, address, timezone) VALUES ('Desert Rose Diner', '3210 E Camelback Road, Phoenix, AZ 85018', 'America/Phoenix');
INSERT INTO location (name, address, timezone) VALUES ('Pacific Rim Bistro', '1128 Sunset Boulevard, Los Angeles, CA 90026', 'America/Los_Angeles');
INSERT INTO location (name, address, timezone) VALUES ('Bay Area Brasserie', '450 Powell Street, San Francisco, CA 94102', 'America/Los_Angeles');
INSERT INTO location (name, address, timezone) VALUES ('Pike Place Tavern', '1923 1st Avenue, Seattle, WA 98101', 'America/Los_Angeles');
INSERT INTO location (name, address, timezone) VALUES ('Rocky Mountain Grill', '1560 Blake Street, Denver, CO 80202', 'America/Denver');
INSERT INTO location (name, address, timezone) VALUES ('Bourbon Street Bistro', '612 Bourbon Street, New Orleans, LA 70116', 'America/Chicago');
INSERT INTO location (name, address, timezone) VALUES ('Peach Tree Kitchen', '875 Peachtree Street NE, Atlanta, GA 30309', 'America/New_York');
INSERT INTO location (name, address, timezone) VALUES ('Capitol Hill Cafe', '320 Massachusetts Avenue NE, Washington, DC 20002', 'America/New_York');

UPDATE location SET timezone = 'America/New_York'    WHERE name = 'Downtown Diner';
UPDATE location SET timezone = 'America/New_York'    WHERE name = 'Riverside Cafe';
UPDATE location SET timezone = 'America/Los_Angeles' WHERE name = 'Mountain View Restaurant';
UPDATE location SET timezone = 'America/Los_Angeles' WHERE name = 'Harbor Point Eatery';
UPDATE location SET timezone = 'America/Chicago'     WHERE name = 'Sunset Plaza Restaurant';
UPDATE location SET timezone = 'America/Chicago'     WHERE name = 'Uptown Bistro';
UPDATE location SET timezone = 'America/Chicago'     WHERE name = 'Lakeside Grill';
UPDATE location SET timezone = 'America/New_York'    WHERE name = 'Garden District Cafe';

