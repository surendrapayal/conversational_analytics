-- Insert data into recipe_items
-- Generated at: 2026-04-21T14:16:56.352799

-- ── Appetizers ────────────────────────────────────────────────────────────────
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Nachos' AND mi.is_active = true AND i.name = 'Flour' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Nachos' AND mi.is_active = true AND i.name = 'Cheese' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Nachos' AND mi.is_active = true AND i.name = 'Tomato' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Nachos' AND mi.is_active = true AND i.name = 'Chili Powder' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Calamari' AND mi.is_active = true AND i.name = 'Flour' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'Calamari' AND mi.is_active = true AND i.name = 'Salt' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Calamari' AND mi.is_active = true AND i.name = 'Lemon Juice' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Calamari' AND mi.is_active = true AND i.name = 'Vegetable Oil' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Bruschetta' AND mi.is_active = true AND i.name = 'Tomato' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Bruschetta' AND mi.is_active = true AND i.name = 'Basil' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Bruschetta' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Bruschetta' AND mi.is_active = true AND i.name = 'Flour' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Spring Rolls' AND mi.is_active = true AND i.name = 'Cabbage' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Spring Rolls' AND mi.is_active = true AND i.name = 'Carrot' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Spring Rolls' AND mi.is_active = true AND i.name = 'Soy Sauce' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Spring Rolls' AND mi.is_active = true AND i.name = 'Flour' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Shrimp Cocktail' AND mi.is_active = true AND i.name = 'Prawns' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Shrimp Cocktail' AND mi.is_active = true AND i.name = 'Lemon Juice' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Shrimp Cocktail' AND mi.is_active = true AND i.name = 'Ketchup' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.30 FROM menu_items mi, ingredients i WHERE mi.name = 'Chicken Wings' AND mi.is_active = true AND i.name = 'Chicken' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Chicken Wings' AND mi.is_active = true AND i.name = 'Paprika' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Chicken Wings' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Chicken Wings' AND mi.is_active = true AND i.name = 'Honey' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Spinach Artichoke Dip' AND mi.is_active = true AND i.name = 'Spinach' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Spinach Artichoke Dip' AND mi.is_active = true AND i.name = 'Cream' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Spinach Artichoke Dip' AND mi.is_active = true AND i.name = 'Cheese' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Tuna Tartare' AND mi.is_active = true AND i.name = 'Tuna' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Tuna Tartare' AND mi.is_active = true AND i.name = 'Soy Sauce' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Tuna Tartare' AND mi.is_active = true AND i.name = 'Sesame Oil' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Tuna Tartare' AND mi.is_active = true AND i.name = 'Lemon Juice' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Beef Sliders' AND mi.is_active = true AND i.name = 'Beef' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Beef Sliders' AND mi.is_active = true AND i.name = 'Cheese' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Beef Sliders' AND mi.is_active = true AND i.name = 'Flour' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Stuffed Mushrooms' AND mi.is_active = true AND i.name = 'Cheese' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Stuffed Mushrooms' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Stuffed Mushrooms' AND mi.is_active = true AND i.name = 'Parsley' LIMIT 1;

-- ── Soups & Salads ────────────────────────────────────────────────────────────
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Caesar Salad' AND mi.is_active = true AND i.name = 'Parmesan' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Caesar Salad' AND mi.is_active = true AND i.name = 'Lemon Juice' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Caesar Salad' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Caprese Salad' AND mi.is_active = true AND i.name = 'Mozzarella' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Caprese Salad' AND mi.is_active = true AND i.name = 'Tomato' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Caprese Salad' AND mi.is_active = true AND i.name = 'Basil' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Greek Salad' AND mi.is_active = true AND i.name = 'Tomato' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Greek Salad' AND mi.is_active = true AND i.name = 'Cheese' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Greek Salad' AND mi.is_active = true AND i.name = 'Vinegar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Greek Salad' AND mi.is_active = true AND i.name = 'Oregano' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.30 FROM menu_items mi, ingredients i WHERE mi.name = 'Tomato Soup' AND mi.is_active = true AND i.name = 'Tomato' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Tomato Soup' AND mi.is_active = true AND i.name = 'Cream' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Tomato Soup' AND mi.is_active = true AND i.name = 'Basil' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Tomato Soup' AND mi.is_active = true AND i.name = 'Stock' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.30 FROM menu_items mi, ingredients i WHERE mi.name = 'Minestrone' AND mi.is_active = true AND i.name = 'Tomato' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Minestrone' AND mi.is_active = true AND i.name = 'Carrot' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Minestrone' AND mi.is_active = true AND i.name = 'Zucchini' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Minestrone' AND mi.is_active = true AND i.name = 'Pasta' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.30 FROM menu_items mi, ingredients i WHERE mi.name = 'French Onion Soup' AND mi.is_active = true AND i.name = 'Onion' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.30 FROM menu_items mi, ingredients i WHERE mi.name = 'French Onion Soup' AND mi.is_active = true AND i.name = 'Stock' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'French Onion Soup' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.25 FROM menu_items mi, ingredients i WHERE mi.name = 'Clam Chowder' AND mi.is_active = true AND i.name = 'Cream' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Clam Chowder' AND mi.is_active = true AND i.name = 'Bacon' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Clam Chowder' AND mi.is_active = true AND i.name = 'Stock' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.25 FROM menu_items mi, ingredients i WHERE mi.name = 'Chicken Noodle Soup' AND mi.is_active = true AND i.name = 'Chicken' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Chicken Noodle Soup' AND mi.is_active = true AND i.name = 'Carrot' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Chicken Noodle Soup' AND mi.is_active = true AND i.name = 'Stock' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Lobster Bisque' AND mi.is_active = true AND i.name = 'Cream' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.30 FROM menu_items mi, ingredients i WHERE mi.name = 'Lobster Bisque' AND mi.is_active = true AND i.name = 'Stock' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Lobster Bisque' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Cobb Salad' AND mi.is_active = true AND i.name = 'Chicken' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Cobb Salad' AND mi.is_active = true AND i.name = 'Bacon' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Cobb Salad' AND mi.is_active = true AND i.name = 'Cheese' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Spinach Salad' AND mi.is_active = true AND i.name = 'Spinach' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Spinach Salad' AND mi.is_active = true AND i.name = 'Walnuts' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Spinach Salad' AND mi.is_active = true AND i.name = 'Vinegar' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Wedge Salad' AND mi.is_active = true AND i.name = 'Bacon' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Wedge Salad' AND mi.is_active = true AND i.name = 'Cheese' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Wedge Salad' AND mi.is_active = true AND i.name = 'Tomato' LIMIT 1;

-- ── Main Courses ──────────────────────────────────────────────────────────────
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Pasta Carbonara' AND mi.is_active = true AND i.name = 'Pasta' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Pasta Carbonara' AND mi.is_active = true AND i.name = 'Bacon' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Pasta Carbonara' AND mi.is_active = true AND i.name = 'Parmesan' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Pasta Carbonara' AND mi.is_active = true AND i.name = 'Pepper' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.25 FROM menu_items mi, ingredients i WHERE mi.name = 'Grilled Salmon' AND mi.is_active = true AND i.name = 'Salmon' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Grilled Salmon' AND mi.is_active = true AND i.name = 'Lemon Juice' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Grilled Salmon' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Grilled Salmon' AND mi.is_active = true AND i.name = 'Thyme' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.30 FROM menu_items mi, ingredients i WHERE mi.name = 'Chicken Parmesan' AND mi.is_active = true AND i.name = 'Chicken' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Chicken Parmesan' AND mi.is_active = true AND i.name = 'Mozzarella' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Chicken Parmesan' AND mi.is_active = true AND i.name = 'Tomato' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Chicken Parmesan' AND mi.is_active = true AND i.name = 'Pasta' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.35 FROM menu_items mi, ingredients i WHERE mi.name = 'Beef Steak' AND mi.is_active = true AND i.name = 'Beef' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Beef Steak' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Beef Steak' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'Beef Steak' AND mi.is_active = true AND i.name = 'Thyme' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.40 FROM menu_items mi, ingredients i WHERE mi.name = 'Ribeye Steak' AND mi.is_active = true AND i.name = 'Beef' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Ribeye Steak' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Ribeye Steak' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'Ribeye Steak' AND mi.is_active = true AND i.name = 'Salt' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.40 FROM menu_items mi, ingredients i WHERE mi.name = 'Rack of Lamb' AND mi.is_active = true AND i.name = 'Lamb' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Rack of Lamb' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Rack of Lamb' AND mi.is_active = true AND i.name = 'Thyme' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Rack of Lamb' AND mi.is_active = true AND i.name = 'Mustard' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.35 FROM menu_items mi, ingredients i WHERE mi.name = 'BBQ Baby Back Ribs' AND mi.is_active = true AND i.name = 'Pork' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'BBQ Baby Back Ribs' AND mi.is_active = true AND i.name = 'Honey' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'BBQ Baby Back Ribs' AND mi.is_active = true AND i.name = 'Paprika' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'BBQ Baby Back Ribs' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Mushroom Risotto' AND mi.is_active = true AND i.name = 'Rice' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Mushroom Risotto' AND mi.is_active = true AND i.name = 'Parmesan' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Mushroom Risotto' AND mi.is_active = true AND i.name = 'Stock' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Mushroom Risotto' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Mushroom Risotto' AND mi.is_active = true AND i.name = 'Thyme' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.35 FROM menu_items mi, ingredients i WHERE mi.name = 'Duck Confit' AND mi.is_active = true AND i.name = 'Stock' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Duck Confit' AND mi.is_active = true AND i.name = 'Thyme' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Duck Confit' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'Duck Confit' AND mi.is_active = true AND i.name = 'Salt' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.25 FROM menu_items mi, ingredients i WHERE mi.name = 'Shrimp Scampi' AND mi.is_active = true AND i.name = 'Prawns' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Shrimp Scampi' AND mi.is_active = true AND i.name = 'Pasta' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Shrimp Scampi' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Shrimp Scampi' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Shrimp Scampi' AND mi.is_active = true AND i.name = 'Lemon Juice' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.35 FROM menu_items mi, ingredients i WHERE mi.name = 'Roast Chicken' AND mi.is_active = true AND i.name = 'Chicken' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Roast Chicken' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Roast Chicken' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Roast Chicken' AND mi.is_active = true AND i.name = 'Thyme' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.25 FROM menu_items mi, ingredients i WHERE mi.name = 'Lobster Tail' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Lobster Tail' AND mi.is_active = true AND i.name = 'Lemon Juice' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Lobster Tail' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Lobster Tail' AND mi.is_active = true AND i.name = 'Parsley' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.25 FROM menu_items mi, ingredients i WHERE mi.name = 'Fish Tacos' AND mi.is_active = true AND i.name = 'Salmon' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Fish Tacos' AND mi.is_active = true AND i.name = 'Cabbage' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Fish Tacos' AND mi.is_active = true AND i.name = 'Lemon Juice' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Fish Tacos' AND mi.is_active = true AND i.name = 'Mayonnaise' LIMIT 1;

-- ── Desserts ──────────────────────────────────────────────────────────────────
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Ice Cream' AND mi.is_active = true AND i.name = 'Milk' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Ice Cream' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Ice Cream' AND mi.is_active = true AND i.name = 'Vanilla' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Ice Cream' AND mi.is_active = true AND i.name = 'Cream' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Tiramisu' AND mi.is_active = true AND i.name = 'Cream' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Tiramisu' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Tiramisu' AND mi.is_active = true AND i.name = 'Chocolate' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Cheesecake' AND mi.is_active = true AND i.name = 'Cream' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Cheesecake' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Cheesecake' AND mi.is_active = true AND i.name = 'Flour' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Cheesecake' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Chocolate Cake' AND mi.is_active = true AND i.name = 'Chocolate' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Chocolate Cake' AND mi.is_active = true AND i.name = 'Flour' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Chocolate Cake' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Chocolate Cake' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Chocolate Cake' AND mi.is_active = true AND i.name = 'Milk' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Crème Brûlée' AND mi.is_active = true AND i.name = 'Cream' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Crème Brûlée' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Crème Brûlée' AND mi.is_active = true AND i.name = 'Vanilla' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Lava Cake' AND mi.is_active = true AND i.name = 'Chocolate' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Lava Cake' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Lava Cake' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Lava Cake' AND mi.is_active = true AND i.name = 'Flour' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Banana Foster' AND mi.is_active = true AND i.name = 'Banana' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Banana Foster' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Banana Foster' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Panna Cotta' AND mi.is_active = true AND i.name = 'Cream' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Panna Cotta' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Panna Cotta' AND mi.is_active = true AND i.name = 'Vanilla' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Apple Pie' AND mi.is_active = true AND i.name = 'Apple' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Apple Pie' AND mi.is_active = true AND i.name = 'Flour' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Apple Pie' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Apple Pie' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Sorbet Trio' AND mi.is_active = true AND i.name = 'Strawberry' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Sorbet Trio' AND mi.is_active = true AND i.name = 'Mango' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Sorbet Trio' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Sorbet Trio' AND mi.is_active = true AND i.name = 'Lemon Juice' LIMIT 1;

-- ── Beverages ─────────────────────────────────────────────────────────────────
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.30 FROM menu_items mi, ingredients i WHERE mi.name = 'Coffee' AND mi.is_active = true AND i.name = 'Water' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Coffee' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Coffee' AND mi.is_active = true AND i.name = 'Milk' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.25 FROM menu_items mi, ingredients i WHERE mi.name = 'Cappuccino' AND mi.is_active = true AND i.name = 'Milk' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Cappuccino' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.25 FROM menu_items mi, ingredients i WHERE mi.name = 'Hot Chocolate' AND mi.is_active = true AND i.name = 'Milk' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Hot Chocolate' AND mi.is_active = true AND i.name = 'Chocolate' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Hot Chocolate' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Lemonade' AND mi.is_active = true AND i.name = 'Lemon Juice' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Lemonade' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.30 FROM menu_items mi, ingredients i WHERE mi.name = 'Lemonade' AND mi.is_active = true AND i.name = 'Water' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Fresh Orange Juice' AND mi.is_active = true AND i.name = 'Orange' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Fresh Orange Juice' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Mango Lassi' AND mi.is_active = true AND i.name = 'Mango' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Mango Lassi' AND mi.is_active = true AND i.name = 'Yogurt' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Mango Lassi' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.30 FROM menu_items mi, ingredients i WHERE mi.name = 'Iced Tea' AND mi.is_active = true AND i.name = 'Water' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Iced Tea' AND mi.is_active = true AND i.name = 'Sugar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Iced Tea' AND mi.is_active = true AND i.name = 'Lemon Juice' LIMIT 1;

-- ── Sides ─────────────────────────────────────────────────────────────────────
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'French Fries' AND mi.is_active = true AND i.name = 'Vegetable Oil' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'French Fries' AND mi.is_active = true AND i.name = 'Salt' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Mashed Potatoes' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Mashed Potatoes' AND mi.is_active = true AND i.name = 'Milk' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'Mashed Potatoes' AND mi.is_active = true AND i.name = 'Salt' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Mac and Cheese' AND mi.is_active = true AND i.name = 'Pasta' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Mac and Cheese' AND mi.is_active = true AND i.name = 'Cheese' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Mac and Cheese' AND mi.is_active = true AND i.name = 'Milk' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Mac and Cheese' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Steamed Broccoli' AND mi.is_active = true AND i.name = 'Broccoli' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Steamed Broccoli' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Steamed Broccoli' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'Steamed Broccoli' AND mi.is_active = true AND i.name = 'Salt' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Roasted Asparagus' AND mi.is_active = true AND i.name = 'Vegetable Oil' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Roasted Asparagus' AND mi.is_active = true AND i.name = 'Parmesan' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Roasted Asparagus' AND mi.is_active = true AND i.name = 'Lemon Juice' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'Roasted Asparagus' AND mi.is_active = true AND i.name = 'Salt' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Sweet Potato Fries' AND mi.is_active = true AND i.name = 'Vegetable Oil' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Sweet Potato Fries' AND mi.is_active = true AND i.name = 'Paprika' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'Sweet Potato Fries' AND mi.is_active = true AND i.name = 'Salt' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Rice Pilaf' AND mi.is_active = true AND i.name = 'Rice' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Rice Pilaf' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Rice Pilaf' AND mi.is_active = true AND i.name = 'Onion' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Rice Pilaf' AND mi.is_active = true AND i.name = 'Stock' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'Rice Pilaf' AND mi.is_active = true AND i.name = 'Salt' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Coleslaw' AND mi.is_active = true AND i.name = 'Cabbage' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Coleslaw' AND mi.is_active = true AND i.name = 'Carrot' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Coleslaw' AND mi.is_active = true AND i.name = 'Mayonnaise' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Coleslaw' AND mi.is_active = true AND i.name = 'Vinegar' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Bread Basket' AND mi.is_active = true AND i.name = 'Flour' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Bread Basket' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Bread Basket' AND mi.is_active = true AND i.name = 'Yeast' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'Bread Basket' AND mi.is_active = true AND i.name = 'Salt' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.15 FROM menu_items mi, ingredients i WHERE mi.name = 'Garlic Bread' AND mi.is_active = true AND i.name = 'Flour' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Garlic Bread' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Garlic Bread' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Garlic Bread' AND mi.is_active = true AND i.name = 'Parsley' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Side Salad' AND mi.is_active = true AND i.name = 'Tomato' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.05 FROM menu_items mi, ingredients i WHERE mi.name = 'Side Salad' AND mi.is_active = true AND i.name = 'Vinegar' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Side Salad' AND mi.is_active = true AND i.name = 'Vegetable Oil' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.20 FROM menu_items mi, ingredients i WHERE mi.name = 'Corn on the Cob' AND mi.is_active = true AND i.name = 'Butter' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'Corn on the Cob' AND mi.is_active = true AND i.name = 'Salt' LIMIT 1;

INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Vegetables' AND mi.is_active = true AND i.name = 'Carrot' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Vegetables' AND mi.is_active = true AND i.name = 'Broccoli' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.10 FROM menu_items mi, ingredients i WHERE mi.name = 'Vegetables' AND mi.is_active = true AND i.name = 'Bell Pepper' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.03 FROM menu_items mi, ingredients i WHERE mi.name = 'Vegetables' AND mi.is_active = true AND i.name = 'Vegetable Oil' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.02 FROM menu_items mi, ingredients i WHERE mi.name = 'Vegetables' AND mi.is_active = true AND i.name = 'Garlic' LIMIT 1;
INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe)
SELECT mi.id, i.id, 0.01 FROM menu_items mi, ingredients i WHERE mi.name = 'Vegetables' AND mi.is_active = true AND i.name = 'Salt' LIMIT 1;
