-- Insert data into supplier
-- Generated at: 2026-04-21T14:16:56.354711

INSERT INTO supplier (name) VALUES ('Fresh Farms Co.') RETURNING id;
INSERT INTO supplier (name) VALUES ('Global Ingredients Ltd.') RETURNING id;
INSERT INTO supplier (name) VALUES ('Local Produce Market') RETURNING id;
INSERT INTO supplier (name) VALUES ('Premium Suppliers Inc.') RETURNING id;
INSERT INTO supplier (name) VALUES ('Quality Foods Wholesale') RETURNING id;
