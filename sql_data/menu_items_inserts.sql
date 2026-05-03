-- Insert data into menu_items
-- Generated at: 2026-04-21T14:16:56.348971

-- ── Appetizers ────────────────────────────────────────────────────────────────
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Nachos', 'Crispy tortilla chips loaded with melted cheese, jalapeños, sour cream and salsa', 15.80, true FROM menu_categories WHERE name = 'Appetizers';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Calamari', 'Lightly breaded and fried squid rings served with marinara and lemon aioli', 14.99, true FROM menu_categories WHERE name = 'Appetizers';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Bruschetta', 'Toasted sourdough topped with fresh tomato, basil, garlic and extra virgin olive oil', 9.99, true FROM menu_categories WHERE name = 'Appetizers';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Spring Rolls', 'Crispy vegetable spring rolls served with sweet chilli dipping sauce', 10.44, true FROM menu_categories WHERE name = 'Appetizers';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Shrimp Cocktail', 'Chilled jumbo shrimp served with house-made cocktail sauce and lemon wedges', 14.99, true FROM menu_categories WHERE name = 'Appetizers';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chicken Wings', 'Crispy wings tossed in your choice of buffalo, BBQ, or honey garlic sauce', 13.99, true FROM menu_categories WHERE name = 'Appetizers';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Spinach Artichoke Dip', 'Creamy blend of spinach, artichoke hearts and melted cheese, served with tortilla chips', 11.99, true FROM menu_categories WHERE name = 'Appetizers';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Stuffed Mushrooms', 'Button mushrooms filled with herbed cream cheese, garlic and breadcrumbs, baked golden', 10.99, true FROM menu_categories WHERE name = 'Appetizers';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Beef Sliders', 'Three mini beef patties with cheddar, pickles and special sauce on brioche buns', 12.99, true FROM menu_categories WHERE name = 'Appetizers';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Tuna Tartare', 'Fresh ahi tuna with avocado, sesame oil, soy and wonton crisps', 16.99, true FROM menu_categories WHERE name = 'Appetizers';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Onion Rings', 'Beer-battered thick-cut onion rings served with chipotle dipping sauce', 8.99, true FROM menu_categories WHERE name = 'Appetizers';

-- ── Soups & Salads ────────────────────────────────────────────────────────────
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Caesar Salad', 'Crisp romaine lettuce, parmesan shavings, house croutons and classic Caesar dressing', 15.87, true FROM menu_categories WHERE name = 'Soups & Salads';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Caprese Salad', 'Fresh buffalo mozzarella, heirloom tomatoes, basil and aged balsamic glaze', 13.99, true FROM menu_categories WHERE name = 'Soups & Salads';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Greek Salad', 'Cucumber, tomato, kalamata olives, red onion and feta with oregano vinaigrette', 13.66, true FROM menu_categories WHERE name = 'Soups & Salads';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Minestrone', 'Hearty Italian vegetable soup with cannellini beans, pasta and fresh herbs', 11.89, true FROM menu_categories WHERE name = 'Soups & Salads';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Tomato Soup', 'Slow-roasted tomato and basil soup finished with cream, served with grilled cheese croutons', 10.99, true FROM menu_categories WHERE name = 'Soups & Salads';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'French Onion Soup', 'Slow-cooked caramelised onion broth topped with toasted crouton and melted Gruyère', 10.99, true FROM menu_categories WHERE name = 'Soups & Salads';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Clam Chowder', 'New England style creamy chowder with clams, potatoes and smoky bacon', 11.99, true FROM menu_categories WHERE name = 'Soups & Salads';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chicken Noodle Soup', 'Classic homestyle soup with tender chicken, egg noodles and fresh vegetables', 9.99, true FROM menu_categories WHERE name = 'Soups & Salads';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cobb Salad', 'Romaine, grilled chicken, bacon, hard-boiled egg, avocado, blue cheese and ranch dressing', 15.99, true FROM menu_categories WHERE name = 'Soups & Salads';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Spinach Salad', 'Baby spinach, strawberries, candied walnuts, goat cheese and balsamic vinaigrette', 13.99, true FROM menu_categories WHERE name = 'Soups & Salads';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Wedge Salad', 'Iceberg wedge with blue cheese dressing, crispy bacon, cherry tomatoes and red onion', 12.99, true FROM menu_categories WHERE name = 'Soups & Salads';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Lobster Bisque', 'Rich and velvety bisque with chunks of lobster, finished with cream and sherry', 14.99, true FROM menu_categories WHERE name = 'Soups & Salads';

-- ── Main Courses ──────────────────────────────────────────────────────────────
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Pasta Carbonara', 'Spaghetti with crispy pancetta, egg yolk, pecorino romano and black pepper', 18.99, true FROM menu_categories WHERE name = 'Main Courses';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Fish Tacos', 'Grilled mahi-mahi in corn tortillas with cabbage slaw, pico de gallo and chipotle crema', 16.99, true FROM menu_categories WHERE name = 'Main Courses';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chicken Parmesan', 'Breaded chicken breast with marinara, melted mozzarella and parmesan over spaghetti', 19.99, true FROM menu_categories WHERE name = 'Main Courses';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Beef Steak', '10oz sirloin grilled to order with herb butter, seasonal vegetables and fries', 28.99, true FROM menu_categories WHERE name = 'Main Courses';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Grilled Salmon', 'Atlantic salmon fillet with lemon dill butter, wild rice and seasonal vegetables', 26.99, true FROM menu_categories WHERE name = 'Main Courses';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Ribeye Steak', '12oz prime ribeye grilled to order, served with roasted garlic mashed potatoes', 42.99, true FROM menu_categories WHERE name = 'Main Courses';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Rack of Lamb', 'French-trimmed rack with herb crust, served with mint jelly and roasted vegetables', 38.99, true FROM menu_categories WHERE name = 'Main Courses';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Lobster Tail', 'Butter-poached 8oz lobster tail with drawn butter, lemon and seasonal vegetables', 49.99, true FROM menu_categories WHERE name = 'Main Courses';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'BBQ Baby Back Ribs', 'Full rack slow-smoked ribs glazed with house BBQ sauce, served with coleslaw and fries', 32.99, true FROM menu_categories WHERE name = 'Main Courses';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mushroom Risotto', 'Creamy Arborio rice with wild mushrooms, truffle oil, parmesan and fresh thyme', 22.99, true FROM menu_categories WHERE name = 'Main Courses';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Duck Confit', 'Slow-cooked duck leg with cherry reduction, roasted fingerling potatoes and haricots verts', 34.99, true FROM menu_categories WHERE name = 'Main Courses';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Shrimp Scampi', 'Sautéed jumbo shrimp in garlic butter white wine sauce over linguine', 26.99, true FROM menu_categories WHERE name = 'Main Courses';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Roast Chicken', 'Half roasted free-range chicken with pan jus, roasted root vegetables and mashed potatoes', 24.99, true FROM menu_categories WHERE name = 'Main Courses';

-- ── Desserts ──────────────────────────────────────────────────────────────────
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Ice Cream', 'Three scoops of house-churned ice cream — vanilla, chocolate or strawberry', 7.99, true FROM menu_categories WHERE name = 'Desserts';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Crème Brûlée', 'Classic vanilla custard with caramelised sugar crust and fresh berries', 9.80, true FROM menu_categories WHERE name = 'Desserts';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cheesecake', 'New York style cheesecake on graham cracker crust with seasonal berry compote', 8.99, true FROM menu_categories WHERE name = 'Desserts';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Tiramisu', 'Espresso-soaked ladyfingers layered with mascarpone cream and dusted with cocoa', 9.99, true FROM menu_categories WHERE name = 'Desserts';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chocolate Cake', 'Rich triple-layer dark chocolate cake with ganache frosting and raspberry coulis', 8.99, true FROM menu_categories WHERE name = 'Desserts';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Lava Cake', 'Warm dark chocolate cake with molten centre, served with vanilla bean ice cream', 9.99, true FROM menu_categories WHERE name = 'Desserts';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Banana Foster', 'Caramelised bananas in rum butter sauce flambéed tableside, served over vanilla ice cream', 10.99, true FROM menu_categories WHERE name = 'Desserts';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Panna Cotta', 'Silky vanilla panna cotta with seasonal berry coulis and fresh mint', 8.49, true FROM menu_categories WHERE name = 'Desserts';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Apple Pie', 'Warm house-baked apple pie with cinnamon streusel topping and whipped cream', 7.99, true FROM menu_categories WHERE name = 'Desserts';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Sorbet Trio', 'Three scoops of rotating seasonal sorbets served with fresh berries', 7.49, true FROM menu_categories WHERE name = 'Desserts';

-- ── Beverages ─────────────────────────────────────────────────────────────────
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Coca Cola', 'Chilled Coca-Cola served over ice with a lemon wedge', 3.99, true FROM menu_categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Lemonade', 'House-made fresh squeezed lemonade with mint and a hint of ginger', 4.49, true FROM menu_categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Coffee', 'Freshly brewed house blend coffee, served with cream and sugar', 3.49, true FROM menu_categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Wine', 'Rotating selection of red and white wines by the glass — ask your server', 9.99, true FROM menu_categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Fresh Orange Juice', 'Freshly squeezed orange juice served chilled', 4.99, true FROM menu_categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Sparkling Water', 'San Pellegrino sparkling mineral water 500ml', 3.99, true FROM menu_categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Iced Tea', 'House-brewed black tea served over ice with lemon and simple syrup on the side', 3.49, true FROM menu_categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cappuccino', 'Double espresso with steamed milk and thick foam, dusted with cocoa', 5.49, true FROM menu_categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Hot Chocolate', 'Rich Belgian chocolate with steamed whole milk and whipped cream', 5.49, true FROM menu_categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Craft Beer', 'Rotating selection of local craft beers on tap — ask your server for today''s options', 7.99, true FROM menu_categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'House Red Wine', 'Smooth Cabernet Sauvignon by the glass', 9.99, true FROM menu_categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'House White Wine', 'Crisp Chardonnay by the glass', 9.99, true FROM menu_categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mango Lassi', 'Chilled blend of fresh mango, yogurt and a hint of cardamom', 5.99, true FROM menu_categories WHERE name = 'Beverages';

-- ── Sides ─────────────────────────────────────────────────────────────────────
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'French Fries', 'Golden crispy fries seasoned with sea salt, served with ketchup and aioli', 5.99, true FROM menu_categories WHERE name = 'Sides';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Bread Basket', 'Warm assorted rolls and sourdough with whipped butter and sea salt', 4.99, true FROM menu_categories WHERE name = 'Sides';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Coleslaw', 'Creamy house coleslaw with shredded cabbage, carrot and apple cider dressing', 4.49, true FROM menu_categories WHERE name = 'Sides';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Rice Pilaf', 'Fragrant basmati rice toasted with butter, onion and fresh herbs', 4.99, true FROM menu_categories WHERE name = 'Sides';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Vegetables', 'Seasonal roasted vegetables with olive oil, garlic and fresh thyme', 5.49, true FROM menu_categories WHERE name = 'Sides';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mashed Potatoes', 'Creamy Yukon Gold mashed potatoes with butter and chives', 5.99, true FROM menu_categories WHERE name = 'Sides';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Roasted Asparagus', 'Oven-roasted asparagus spears with lemon zest and shaved parmesan', 6.99, true FROM menu_categories WHERE name = 'Sides';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mac and Cheese', 'House-made three-cheese macaroni with crispy breadcrumb topping', 7.99, true FROM menu_categories WHERE name = 'Sides';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Sweet Potato Fries', 'Crispy sweet potato fries seasoned with sea salt, served with chipotle aioli', 6.49, true FROM menu_categories WHERE name = 'Sides';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Garlic Bread', 'Toasted sourdough with roasted garlic butter and fresh parsley', 4.49, true FROM menu_categories WHERE name = 'Sides';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Corn on the Cob', 'Grilled corn with herb butter and sea salt', 4.99, true FROM menu_categories WHERE name = 'Sides';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Side Salad', 'Mixed greens, cherry tomatoes, cucumber and house vinaigrette', 4.99, true FROM menu_categories WHERE name = 'Sides';
INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Steamed Broccoli', 'Fresh broccoli florets steamed and finished with garlic butter', 5.49, true FROM menu_categories WHERE name = 'Sides';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Bruschetta', 'Bruschetta prepared with fresh ingredients and chef special seasoning.', 8.57, true
FROM menu_categories WHERE name = 'Appetizers';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Bruschetta', 'Bruschetta prepared with fresh ingredients and chef special seasoning.', 5.87, false
FROM menu_categories WHERE name = 'Appetizers';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Spring Rolls', 'Spring Rolls prepared with fresh ingredients and chef special seasoning.', 10.17, true
FROM menu_categories WHERE name = 'Appetizers';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Nachos', 'Nachos prepared with fresh ingredients and chef special seasoning.', 9.11, true
FROM menu_categories WHERE name = 'Appetizers';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Garlic Bread', 'Garlic Bread prepared with fresh ingredients and chef special seasoning.', 6.32, true
FROM menu_categories WHERE name = 'Appetizers';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Minestrone', 'Minestrone prepared with fresh ingredients and chef special seasoning.', 9.75, false
FROM menu_categories WHERE name = 'Soups & Salads';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Caesar Salad', 'Caesar Salad prepared with fresh ingredients and chef special seasoning.', 9.76, true
FROM menu_categories WHERE name = 'Soups & Salads';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Tomato Soup', 'Tomato Soup prepared with fresh ingredients and chef special seasoning.', 14.16, true
FROM menu_categories WHERE name = 'Soups & Salads';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Caesar Salad', 'Caesar Salad prepared with fresh ingredients and chef special seasoning.', 13.87, true
FROM menu_categories WHERE name = 'Soups & Salads';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Minestrone', 'Minestrone prepared with fresh ingredients and chef special seasoning.', 14.23, true
FROM menu_categories WHERE name = 'Soups & Salads';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Grilled Chicken', 'Grilled Chicken prepared with fresh ingredients and chef special seasoning.', 17.57, true
FROM menu_categories WHERE name = 'Main Courses';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Paneer Butter Masala', 'Paneer Butter Masala prepared with fresh ingredients and chef special seasoning.', 12.94, true
FROM menu_categories WHERE name = 'Main Courses';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Grilled Chicken', 'Grilled Chicken prepared with fresh ingredients and chef special seasoning.', 16.44, true
FROM menu_categories WHERE name = 'Main Courses';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Grilled Chicken', 'Grilled Chicken prepared with fresh ingredients and chef special seasoning.', 15.04, false
FROM menu_categories WHERE name = 'Main Courses';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Grilled Chicken', 'Grilled Chicken prepared with fresh ingredients and chef special seasoning.', 20.88, true
FROM menu_categories WHERE name = 'Main Courses';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Brownie', 'Brownie prepared with fresh ingredients and chef special seasoning.', 7.74, true
FROM menu_categories WHERE name = 'Desserts';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cheesecake', 'Cheesecake prepared with fresh ingredients and chef special seasoning.', 6.21, true
FROM menu_categories WHERE name = 'Desserts';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chocolate Lava Cake', 'Chocolate Lava Cake prepared with fresh ingredients and chef special seasoning.', 6.44, false
FROM menu_categories WHERE name = 'Desserts';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chocolate Lava Cake', 'Chocolate Lava Cake prepared with fresh ingredients and chef special seasoning.', 7.79, true
FROM menu_categories WHERE name = 'Desserts';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chocolate Lava Cake', 'Chocolate Lava Cake prepared with fresh ingredients and chef special seasoning.', 8.0, true
FROM menu_categories WHERE name = 'Desserts';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Coca Cola', 'Coca Cola prepared with fresh ingredients and chef special seasoning.', 6.29, true
FROM menu_categories WHERE name = 'Beverages';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Lemonade', 'Lemonade prepared with fresh ingredients and chef special seasoning.', 5.34, true
FROM menu_categories WHERE name = 'Beverages';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Orange Juice', 'Orange Juice prepared with fresh ingredients and chef special seasoning.', 3.76, true
FROM menu_categories WHERE name = 'Beverages';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Iced Tea', 'Iced Tea prepared with fresh ingredients and chef special seasoning.', 3.3, true
FROM menu_categories WHERE name = 'Beverages';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Lemonade', 'Lemonade prepared with fresh ingredients and chef special seasoning.', 3.49, false
FROM menu_categories WHERE name = 'Beverages';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'French Fries', 'French Fries prepared with fresh ingredients and chef special seasoning.', 7.84, false
FROM menu_categories WHERE name = 'Sides';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Garlic Bread', 'Garlic Bread prepared with fresh ingredients and chef special seasoning.', 16.99, true
FROM menu_categories WHERE name = 'Sides';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Garlic Bread', 'Garlic Bread prepared with fresh ingredients and chef special seasoning.', 17.97, true
FROM menu_categories WHERE name = 'Sides';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Garlic Bread', 'Garlic Bread prepared with fresh ingredients and chef special seasoning.', 14.51, false
FROM menu_categories WHERE name = 'Sides';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Garlic Bread', 'Garlic Bread prepared with fresh ingredients and chef special seasoning.', 7.77, true
FROM menu_categories WHERE name = 'Sides';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Waffles', 'Waffles prepared with fresh ingredients and chef special seasoning.', 8.27, false
FROM menu_categories WHERE name = 'Breakfast';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Pancakes', 'Pancakes prepared with fresh ingredients and chef special seasoning.', 15.97, true
FROM menu_categories WHERE name = 'Breakfast';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Waffles', 'Waffles prepared with fresh ingredients and chef special seasoning.', 12.96, true
FROM menu_categories WHERE name = 'Breakfast';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'French Toast', 'French Toast prepared with fresh ingredients and chef special seasoning.', 10.78, true
FROM menu_categories WHERE name = 'Breakfast';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Pancakes', 'Pancakes prepared with fresh ingredients and chef special seasoning.', 7.85, false
FROM menu_categories WHERE name = 'Breakfast';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Brunch Platter', 'Brunch Platter prepared with fresh ingredients and chef special seasoning.', 13.61, true
FROM menu_categories WHERE name = 'Brunch Specials';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Brunch Platter', 'Brunch Platter prepared with fresh ingredients and chef special seasoning.', 8.74, true
FROM menu_categories WHERE name = 'Brunch Specials';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Egg Benedict', 'Egg Benedict prepared with fresh ingredients and chef special seasoning.', 11.09, true
FROM menu_categories WHERE name = 'Brunch Specials';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Avocado Toast', 'Avocado Toast prepared with fresh ingredients and chef special seasoning.', 15.79, true
FROM menu_categories WHERE name = 'Brunch Specials';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Avocado Toast', 'Avocado Toast prepared with fresh ingredients and chef special seasoning.', 8.54, true
FROM menu_categories WHERE name = 'Brunch Specials';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Masala Omelette', 'Masala Omelette prepared with fresh ingredients and chef special seasoning.', 15.53, true
FROM menu_categories WHERE name = 'Eggs & Omelettes';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Boiled Eggs', 'Boiled Eggs prepared with fresh ingredients and chef special seasoning.', 14.38, true
FROM menu_categories WHERE name = 'Eggs & Omelettes';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cheese Omelette', 'Cheese Omelette prepared with fresh ingredients and chef special seasoning.', 11.62, true
FROM menu_categories WHERE name = 'Eggs & Omelettes';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Boiled Eggs', 'Boiled Eggs prepared with fresh ingredients and chef special seasoning.', 9.26, true
FROM menu_categories WHERE name = 'Eggs & Omelettes';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cheese Omelette', 'Cheese Omelette prepared with fresh ingredients and chef special seasoning.', 13.5, true
FROM menu_categories WHERE name = 'Eggs & Omelettes';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Margherita Pizza', 'Margherita Pizza prepared with fresh ingredients and chef special seasoning.', 14.84, false
FROM menu_categories WHERE name = 'Flatbreads & Pizzas';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Pepperoni Pizza', 'Pepperoni Pizza prepared with fresh ingredients and chef special seasoning.', 12.58, true
FROM menu_categories WHERE name = 'Flatbreads & Pizzas';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Veggie Pizza', 'Veggie Pizza prepared with fresh ingredients and chef special seasoning.', 15.99, false
FROM menu_categories WHERE name = 'Flatbreads & Pizzas';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Veggie Pizza', 'Veggie Pizza prepared with fresh ingredients and chef special seasoning.', 11.49, true
FROM menu_categories WHERE name = 'Flatbreads & Pizzas';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Margherita Pizza', 'Margherita Pizza prepared with fresh ingredients and chef special seasoning.', 12.35, true
FROM menu_categories WHERE name = 'Flatbreads & Pizzas';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chicken Sliders', 'Chicken Sliders prepared with fresh ingredients and chef special seasoning.', 10.38, false
FROM menu_categories WHERE name = 'Sliders & Small Bites';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chicken Sliders', 'Chicken Sliders prepared with fresh ingredients and chef special seasoning.', 12.77, true
FROM menu_categories WHERE name = 'Sliders & Small Bites';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mini Burgers', 'Mini Burgers prepared with fresh ingredients and chef special seasoning.', 12.95, true
FROM menu_categories WHERE name = 'Sliders & Small Bites';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Veg Sliders', 'Veg Sliders prepared with fresh ingredients and chef special seasoning.', 13.72, true
FROM menu_categories WHERE name = 'Sliders & Small Bites';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chicken Sliders', 'Chicken Sliders prepared with fresh ingredients and chef special seasoning.', 10.28, true
FROM menu_categories WHERE name = 'Sliders & Small Bites';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cold Cuts Board', 'Cold Cuts Board prepared with fresh ingredients and chef special seasoning.', 13.09, true
FROM menu_categories WHERE name = 'Charcuterie & Cheese';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cold Cuts Board', 'Cold Cuts Board prepared with fresh ingredients and chef special seasoning.', 10.04, false
FROM menu_categories WHERE name = 'Charcuterie & Cheese';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cold Cuts Board', 'Cold Cuts Board prepared with fresh ingredients and chef special seasoning.', 16.63, true
FROM menu_categories WHERE name = 'Charcuterie & Cheese';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cheese Platter', 'Cheese Platter prepared with fresh ingredients and chef special seasoning.', 12.04, false
FROM menu_categories WHERE name = 'Charcuterie & Cheese';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cheese Platter', 'Cheese Platter prepared with fresh ingredients and chef special seasoning.', 7.03, true
FROM menu_categories WHERE name = 'Charcuterie & Cheese';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Veg Sandwich', 'Veg Sandwich prepared with fresh ingredients and chef special seasoning.', 11.61, true
FROM menu_categories WHERE name = 'Burgers & Sandwiches';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Veg Sandwich', 'Veg Sandwich prepared with fresh ingredients and chef special seasoning.', 9.21, true
FROM menu_categories WHERE name = 'Burgers & Sandwiches';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Veg Sandwich', 'Veg Sandwich prepared with fresh ingredients and chef special seasoning.', 11.53, false
FROM menu_categories WHERE name = 'Burgers & Sandwiches';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chicken Burger', 'Chicken Burger prepared with fresh ingredients and chef special seasoning.', 16.09, false
FROM menu_categories WHERE name = 'Burgers & Sandwiches';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chicken Burger', 'Chicken Burger prepared with fresh ingredients and chef special seasoning.', 16.31, false
FROM menu_categories WHERE name = 'Burgers & Sandwiches';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Ribeye Steak', 'Ribeye Steak prepared with fresh ingredients and chef special seasoning.', 16.01, true
FROM menu_categories WHERE name = 'Steaks & Grills';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Grilled Lamb', 'Grilled Lamb prepared with fresh ingredients and chef special seasoning.', 16.18, true
FROM menu_categories WHERE name = 'Steaks & Grills';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Ribeye Steak', 'Ribeye Steak prepared with fresh ingredients and chef special seasoning.', 9.43, true
FROM menu_categories WHERE name = 'Steaks & Grills';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Grilled Lamb', 'Grilled Lamb prepared with fresh ingredients and chef special seasoning.', 10.02, true
FROM menu_categories WHERE name = 'Steaks & Grills';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Ribeye Steak', 'Ribeye Steak prepared with fresh ingredients and chef special seasoning.', 17.89, true
FROM menu_categories WHERE name = 'Steaks & Grills';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Prawn Curry', 'Prawn Curry prepared with fresh ingredients and chef special seasoning.', 10.62, true
FROM menu_categories WHERE name = 'Seafood';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Fish Tacos', 'Fish Tacos prepared with fresh ingredients and chef special seasoning.', 6.9, false
FROM menu_categories WHERE name = 'Seafood';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Prawn Curry', 'Prawn Curry prepared with fresh ingredients and chef special seasoning.', 8.49, false
FROM menu_categories WHERE name = 'Seafood';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Prawn Curry', 'Prawn Curry prepared with fresh ingredients and chef special seasoning.', 13.31, true
FROM menu_categories WHERE name = 'Seafood';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Fish Tacos', 'Fish Tacos prepared with fresh ingredients and chef special seasoning.', 13.4, true
FROM menu_categories WHERE name = 'Seafood';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mushroom Risotto', 'Mushroom Risotto prepared with fresh ingredients and chef special seasoning.', 9.86, false
FROM menu_categories WHERE name = 'Pasta & Risotto';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mushroom Risotto', 'Mushroom Risotto prepared with fresh ingredients and chef special seasoning.', 6.4, true
FROM menu_categories WHERE name = 'Pasta & Risotto';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mushroom Risotto', 'Mushroom Risotto prepared with fresh ingredients and chef special seasoning.', 10.49, false
FROM menu_categories WHERE name = 'Pasta & Risotto';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Pasta Carbonara', 'Pasta Carbonara prepared with fresh ingredients and chef special seasoning.', 7.03, false
FROM menu_categories WHERE name = 'Pasta & Risotto';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Pasta Carbonara', 'Pasta Carbonara prepared with fresh ingredients and chef special seasoning.', 12.92, true
FROM menu_categories WHERE name = 'Pasta & Risotto';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Tofu Stir Fry', 'Tofu Stir Fry prepared with fresh ingredients and chef special seasoning.', 7.67, true
FROM menu_categories WHERE name = 'Vegetarian & Vegan';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Veg Curry', 'Veg Curry prepared with fresh ingredients and chef special seasoning.', 12.68, true
FROM menu_categories WHERE name = 'Vegetarian & Vegan';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Tofu Stir Fry', 'Tofu Stir Fry prepared with fresh ingredients and chef special seasoning.', 10.85, true
FROM menu_categories WHERE name = 'Vegetarian & Vegan';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Veg Curry', 'Veg Curry prepared with fresh ingredients and chef special seasoning.', 12.97, true
FROM menu_categories WHERE name = 'Vegetarian & Vegan';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Tofu Stir Fry', 'Tofu Stir Fry prepared with fresh ingredients and chef special seasoning.', 8.07, true
FROM menu_categories WHERE name = 'Vegetarian & Vegan';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Falafel Wrap', 'Falafel Wrap prepared with fresh ingredients and chef special seasoning.', 6.72, true
FROM menu_categories WHERE name = 'Tacos & Wraps';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chicken Wrap', 'Chicken Wrap prepared with fresh ingredients and chef special seasoning.', 17.52, true
FROM menu_categories WHERE name = 'Tacos & Wraps';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Veg Tacos', 'Veg Tacos prepared with fresh ingredients and chef special seasoning.', 9.12, true
FROM menu_categories WHERE name = 'Tacos & Wraps';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chicken Wrap', 'Chicken Wrap prepared with fresh ingredients and chef special seasoning.', 11.34, true
FROM menu_categories WHERE name = 'Tacos & Wraps';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chicken Wrap', 'Chicken Wrap prepared with fresh ingredients and chef special seasoning.', 15.36, true
FROM menu_categories WHERE name = 'Tacos & Wraps';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Hakka Noodles', 'Hakka Noodles prepared with fresh ingredients and chef special seasoning.', 8.17, true
FROM menu_categories WHERE name = 'Rice & Noodles';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Fried Rice', 'Fried Rice prepared with fresh ingredients and chef special seasoning.', 16.59, true
FROM menu_categories WHERE name = 'Rice & Noodles';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Fried Rice', 'Fried Rice prepared with fresh ingredients and chef special seasoning.', 16.31, true
FROM menu_categories WHERE name = 'Rice & Noodles';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Hakka Noodles', 'Hakka Noodles prepared with fresh ingredients and chef special seasoning.', 12.65, false
FROM menu_categories WHERE name = 'Rice & Noodles';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Fried Rice', 'Fried Rice prepared with fresh ingredients and chef special seasoning.', 8.37, true
FROM menu_categories WHERE name = 'Rice & Noodles';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mac & Cheese', 'Mac & Cheese prepared with fresh ingredients and chef special seasoning.', 8.94, false
FROM menu_categories WHERE name = 'Kids Menu';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mac & Cheese', 'Mac & Cheese prepared with fresh ingredients and chef special seasoning.', 8.33, true
FROM menu_categories WHERE name = 'Kids Menu';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chicken Nuggets', 'Chicken Nuggets prepared with fresh ingredients and chef special seasoning.', 7.77, false
FROM menu_categories WHERE name = 'Kids Menu';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mini Burger', 'Mini Burger prepared with fresh ingredients and chef special seasoning.', 8.36, false
FROM menu_categories WHERE name = 'Kids Menu';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mini Burger', 'Mini Burger prepared with fresh ingredients and chef special seasoning.', 12.53, true
FROM menu_categories WHERE name = 'Kids Menu';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Strawberry Scoop', 'Strawberry Scoop prepared with fresh ingredients and chef special seasoning.', 9.99, true
FROM menu_categories WHERE name = 'Ice Cream & Gelato';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Vanilla Ice Cream', 'Vanilla Ice Cream prepared with fresh ingredients and chef special seasoning.', 11.85, true
FROM menu_categories WHERE name = 'Ice Cream & Gelato';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chocolate Gelato', 'Chocolate Gelato prepared with fresh ingredients and chef special seasoning.', 8.55, true
FROM menu_categories WHERE name = 'Ice Cream & Gelato';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Strawberry Scoop', 'Strawberry Scoop prepared with fresh ingredients and chef special seasoning.', 13.83, true
FROM menu_categories WHERE name = 'Ice Cream & Gelato';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Vanilla Ice Cream', 'Vanilla Ice Cream prepared with fresh ingredients and chef special seasoning.', 14.43, true
FROM menu_categories WHERE name = 'Ice Cream & Gelato';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cupcake', 'Cupcake prepared with fresh ingredients and chef special seasoning.', 12.62, true
FROM menu_categories WHERE name = 'Cakes & Pastries';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cupcake', 'Cupcake prepared with fresh ingredients and chef special seasoning.', 17.83, true
FROM menu_categories WHERE name = 'Cakes & Pastries';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cupcake', 'Cupcake prepared with fresh ingredients and chef special seasoning.', 8.91, false
FROM menu_categories WHERE name = 'Cakes & Pastries';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chocolate Cake', 'Chocolate Cake prepared with fresh ingredients and chef special seasoning.', 16.03, false
FROM menu_categories WHERE name = 'Cakes & Pastries';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chocolate Cake', 'Chocolate Cake prepared with fresh ingredients and chef special seasoning.', 11.23, true
FROM menu_categories WHERE name = 'Cakes & Pastries';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cosmopolitan', 'Cosmopolitan prepared with fresh ingredients and chef special seasoning.', 8.19, true
FROM menu_categories WHERE name = 'Cocktails';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Margarita', 'Margarita prepared with fresh ingredients and chef special seasoning.', 10.61, true
FROM menu_categories WHERE name = 'Cocktails';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cosmopolitan', 'Cosmopolitan prepared with fresh ingredients and chef special seasoning.', 10.54, true
FROM menu_categories WHERE name = 'Cocktails';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cosmopolitan', 'Cosmopolitan prepared with fresh ingredients and chef special seasoning.', 14.86, false
FROM menu_categories WHERE name = 'Cocktails';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Margarita', 'Margarita prepared with fresh ingredients and chef special seasoning.', 12.51, true
FROM menu_categories WHERE name = 'Cocktails';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mint Cooler', 'Mint Cooler prepared with fresh ingredients and chef special seasoning.', 16.48, true
FROM menu_categories WHERE name = 'Mocktails';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Fruit Punch', 'Fruit Punch prepared with fresh ingredients and chef special seasoning.', 11.7, true
FROM menu_categories WHERE name = 'Mocktails';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Virgin Mojito', 'Virgin Mojito prepared with fresh ingredients and chef special seasoning.', 11.98, true
FROM menu_categories WHERE name = 'Mocktails';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Fruit Punch', 'Fruit Punch prepared with fresh ingredients and chef special seasoning.', 10.83, true
FROM menu_categories WHERE name = 'Mocktails';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Virgin Mojito', 'Virgin Mojito prepared with fresh ingredients and chef special seasoning.', 8.86, true
FROM menu_categories WHERE name = 'Mocktails';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Red Wine', 'Red Wine prepared with fresh ingredients and chef special seasoning.', 7.3, false
FROM menu_categories WHERE name = 'Wine & Beer';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'White Wine', 'White Wine prepared with fresh ingredients and chef special seasoning.', 10.56, true
FROM menu_categories WHERE name = 'Wine & Beer';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'White Wine', 'White Wine prepared with fresh ingredients and chef special seasoning.', 11.31, true
FROM menu_categories WHERE name = 'Wine & Beer';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Red Wine', 'Red Wine prepared with fresh ingredients and chef special seasoning.', 16.75, false
FROM menu_categories WHERE name = 'Wine & Beer';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Red Wine', 'Red Wine prepared with fresh ingredients and chef special seasoning.', 14.81, true
FROM menu_categories WHERE name = 'Wine & Beer';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cappuccino', 'Cappuccino prepared with fresh ingredients and chef special seasoning.', 7.18, true
FROM menu_categories WHERE name = 'Coffee & Tea';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cappuccino', 'Cappuccino prepared with fresh ingredients and chef special seasoning.', 17.11, true
FROM menu_categories WHERE name = 'Coffee & Tea';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cappuccino', 'Cappuccino prepared with fresh ingredients and chef special seasoning.', 7.83, false
FROM menu_categories WHERE name = 'Coffee & Tea';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Espresso', 'Espresso prepared with fresh ingredients and chef special seasoning.', 14.45, false
FROM menu_categories WHERE name = 'Coffee & Tea';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Cappuccino', 'Cappuccino prepared with fresh ingredients and chef special seasoning.', 16.91, true
FROM menu_categories WHERE name = 'Coffee & Tea';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Mango Smoothie', 'Mango Smoothie prepared with fresh ingredients and chef special seasoning.', 17.9, false
FROM menu_categories WHERE name = 'Fresh Juices & Smoothies';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Berry Blast', 'Berry Blast prepared with fresh ingredients and chef special seasoning.', 6.46, true
FROM menu_categories WHERE name = 'Fresh Juices & Smoothies';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Berry Blast', 'Berry Blast prepared with fresh ingredients and chef special seasoning.', 7.05, false
FROM menu_categories WHERE name = 'Fresh Juices & Smoothies';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Orange Juice', 'Orange Juice prepared with fresh ingredients and chef special seasoning.', 14.72, true
FROM menu_categories WHERE name = 'Fresh Juices & Smoothies';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Berry Blast', 'Berry Blast prepared with fresh ingredients and chef special seasoning.', 15.09, true
FROM menu_categories WHERE name = 'Fresh Juices & Smoothies';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Vanilla Shake', 'Vanilla Shake prepared with fresh ingredients and chef special seasoning.', 15.62, true
FROM menu_categories WHERE name = 'Milkshakes';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Oreo Shake', 'Oreo Shake prepared with fresh ingredients and chef special seasoning.', 15.05, true
FROM menu_categories WHERE name = 'Milkshakes';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Oreo Shake', 'Oreo Shake prepared with fresh ingredients and chef special seasoning.', 12.37, true
FROM menu_categories WHERE name = 'Milkshakes';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Oreo Shake', 'Oreo Shake prepared with fresh ingredients and chef special seasoning.', 13.34, true
FROM menu_categories WHERE name = 'Milkshakes';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chocolate Shake', 'Chocolate Shake prepared with fresh ingredients and chef special seasoning.', 12.01, true
FROM menu_categories WHERE name = 'Milkshakes';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chef Special Chicken', 'Chef Special Chicken prepared with fresh ingredients and chef special seasoning.', 10.75, true
FROM menu_categories WHERE name = 'Chef Specials';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Signature Dish', 'Signature Dish prepared with fresh ingredients and chef special seasoning.', 8.47, true
FROM menu_categories WHERE name = 'Chef Specials';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chef Special Chicken', 'Chef Special Chicken prepared with fresh ingredients and chef special seasoning.', 14.69, false
FROM menu_categories WHERE name = 'Chef Specials';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Chef Special Chicken', 'Chef Special Chicken prepared with fresh ingredients and chef special seasoning.', 16.68, false
FROM menu_categories WHERE name = 'Chef Specials';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Signature Dish', 'Signature Dish prepared with fresh ingredients and chef special seasoning.', 11.39, false
FROM menu_categories WHERE name = 'Chef Specials';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Summer Salad', 'Summer Salad prepared with fresh ingredients and chef special seasoning.', 13.88, true
FROM menu_categories WHERE name = 'Seasonal Menu';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Summer Salad', 'Summer Salad prepared with fresh ingredients and chef special seasoning.', 14.62, true
FROM menu_categories WHERE name = 'Seasonal Menu';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Winter Soup', 'Winter Soup prepared with fresh ingredients and chef special seasoning.', 17.44, false
FROM menu_categories WHERE name = 'Seasonal Menu';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Summer Salad', 'Summer Salad prepared with fresh ingredients and chef special seasoning.', 14.97, true
FROM menu_categories WHERE name = 'Seasonal Menu';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Summer Salad', 'Summer Salad prepared with fresh ingredients and chef special seasoning.', 14.57, true
FROM menu_categories WHERE name = 'Seasonal Menu';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Beer Combo', 'Beer Combo prepared with fresh ingredients and chef special seasoning.', 11.58, true
FROM menu_categories WHERE name = 'Happy Hour';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Beer Combo', 'Beer Combo prepared with fresh ingredients and chef special seasoning.', 12.6, true
FROM menu_categories WHERE name = 'Happy Hour';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Snack Platter', 'Snack Platter prepared with fresh ingredients and chef special seasoning.', 13.14, true
FROM menu_categories WHERE name = 'Happy Hour';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Beer Combo', 'Beer Combo prepared with fresh ingredients and chef special seasoning.', 15.2, true
FROM menu_categories WHERE name = 'Happy Hour';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Snack Platter', 'Snack Platter prepared with fresh ingredients and chef special seasoning.', 9.97, true
FROM menu_categories WHERE name = 'Happy Hour';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Party Pack', 'Party Pack prepared with fresh ingredients and chef special seasoning.', 13.42, true
FROM menu_categories WHERE name = 'Catering Packages';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Party Pack', 'Party Pack prepared with fresh ingredients and chef special seasoning.', 8.13, true
FROM menu_categories WHERE name = 'Catering Packages';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Family Pack', 'Family Pack prepared with fresh ingredients and chef special seasoning.', 14.26, true
FROM menu_categories WHERE name = 'Catering Packages';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Family Pack', 'Family Pack prepared with fresh ingredients and chef special seasoning.', 17.92, true
FROM menu_categories WHERE name = 'Catering Packages';

INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, 'Party Pack', 'Party Pack prepared with fresh ingredients and chef special seasoning.', 16.64, true
FROM menu_categories WHERE name = 'Catering Packages';