-- Insert data into menu_categories
-- Generated at: 2026-04-19T14:26:33.581840

INSERT INTO menu_categories (name) VALUES ('Appetizers') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Soups & Salads') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Main Courses') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Desserts') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Beverages') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Sides') RETURNING id;
