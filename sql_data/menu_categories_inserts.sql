-- Insert data into menu_categories
-- Generated at: 2026-04-21T14:16:56.348729

INSERT INTO menu_categories (name) VALUES ('Appetizers') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Soups & Salads') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Main Courses') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Desserts') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Beverages') RETURNING id;
INSERT INTO menu_categories (name) VALUES ('Sides') RETURNING id;



-- Breakfast & Brunch
INSERT INTO menu_categories (name) VALUES ('Breakfast');
INSERT INTO menu_categories (name) VALUES ('Brunch Specials');
INSERT INTO menu_categories (name) VALUES ('Eggs & Omelettes');

-- Starters & Sharing
INSERT INTO menu_categories (name) VALUES ('Flatbreads & Pizzas');
INSERT INTO menu_categories (name) VALUES ('Sliders & Small Bites');
INSERT INTO menu_categories (name) VALUES ('Charcuterie & Cheese');

-- Mains
INSERT INTO menu_categories (name) VALUES ('Burgers & Sandwiches');
INSERT INTO menu_categories (name) VALUES ('Steaks & Grills');
INSERT INTO menu_categories (name) VALUES ('Seafood');
INSERT INTO menu_categories (name) VALUES ('Pasta & Risotto');
INSERT INTO menu_categories (name) VALUES ('Vegetarian & Vegan');
INSERT INTO menu_categories (name) VALUES ('Tacos & Wraps');
INSERT INTO menu_categories (name) VALUES ('Rice & Noodles');

-- Kids
INSERT INTO menu_categories (name) VALUES ('Kids Menu');

-- Desserts
INSERT INTO menu_categories (name) VALUES ('Ice Cream & Gelato');
INSERT INTO menu_categories (name) VALUES ('Cakes & Pastries');

-- Drinks
INSERT INTO menu_categories (name) VALUES ('Cocktails');
INSERT INTO menu_categories (name) VALUES ('Mocktails');
INSERT INTO menu_categories (name) VALUES ('Wine & Beer');
INSERT INTO menu_categories (name) VALUES ('Coffee & Tea');
INSERT INTO menu_categories (name) VALUES ('Fresh Juices & Smoothies');
INSERT INTO menu_categories (name) VALUES ('Milkshakes');

-- Specials
INSERT INTO menu_categories (name) VALUES ('Chef Specials');
INSERT INTO menu_categories (name) VALUES ('Seasonal Menu');
INSERT INTO menu_categories (name) VALUES ('Happy Hour');
INSERT INTO menu_categories (name) VALUES ('Catering Packages');
