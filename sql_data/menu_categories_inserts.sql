-- Insert data into menu_categories
-- Generated at: 2026-04-21T14:16:56.348729

INSERT INTO menu_categories (name) VALUES ('Appetizers') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Soups & Salads') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Main Courses') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Desserts') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Beverages') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Sides') RETURNING id;
