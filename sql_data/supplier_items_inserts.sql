-- ── supplier_items ────────────────────────────────────────────────────────────
-- supplier 1 = Fresh Farms Co.        (produce, vegetables, fruits)
-- supplier 2 = Pacific Seafood        (seafood)
-- supplier 3 = Prime Meats Supply     (meat, poultry)
-- supplier 4 = Golden Grain Wholesale (grains, flour, pasta, rice)
-- supplier 5 = Dairy Direct Inc.      (dairy)
-- supplier 6 = Organic Valley Produce (vegetables, herbs)
-- supplier 7 = Spice World Trading    (spices, condiments)
-- supplier 8 = Continental Beverage   (beverages)
-- supplier 9 = Sunrise Bakery         (baking supplies)
-- supplier 10 = Green Leaf Herbs      (herbs, seasonings)

-- Fresh Farms Co. — produce & fruits
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.20 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Tomato';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 0.80 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Onion';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 0.60 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Garlic';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.50 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Spinach';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.80 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Broccoli';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 0.90 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Carrot';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.10 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Bell Pepper';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.50 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Mango';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.20 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Orange';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.80 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Apple';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.20 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Strawberry';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.40 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Banana';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.60 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Lemon Juice';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.90 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Zucchini';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.30 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Eggplant';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.10 FROM supplier s, ingredients i WHERE s.name='Fresh Farms Co.' AND i.name='Cabbage';

-- Pacific Seafood Distributors — seafood
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 12.50 FROM supplier s, ingredients i WHERE s.name='Pacific Seafood Distributors' AND i.name='Salmon';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 18.00 FROM supplier s, ingredients i WHERE s.name='Pacific Seafood Distributors' AND i.name='Tuna';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 14.00 FROM supplier s, ingredients i WHERE s.name='Pacific Seafood Distributors' AND i.name='Prawns';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 16.00 FROM supplier s, ingredients i WHERE s.name='Pacific Seafood Distributors' AND i.name='Crab';

-- Prime Meats Supply — meat & poultry
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 9.50 FROM supplier s, ingredients i WHERE s.name='Prime Meats Supply' AND i.name='Beef';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 6.50 FROM supplier s, ingredients i WHERE s.name='Prime Meats Supply' AND i.name='Chicken';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 11.00 FROM supplier s, ingredients i WHERE s.name='Prime Meats Supply' AND i.name='Lamb';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 7.50 FROM supplier s, ingredients i WHERE s.name='Prime Meats Supply' AND i.name='Pork';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 3.50 FROM supplier s, ingredients i WHERE s.name='Prime Meats Supply' AND i.name='Bacon';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 8.00 FROM supplier s, ingredients i WHERE s.name='Prime Meats Supply' AND i.name='Turkey';

-- Golden Grain Wholesale — grains
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.20 FROM supplier s, ingredients i WHERE s.name='Golden Grain Wholesale' AND i.name='Flour';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.50 FROM supplier s, ingredients i WHERE s.name='Golden Grain Wholesale' AND i.name='Pasta';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.30 FROM supplier s, ingredients i WHERE s.name='Golden Grain Wholesale' AND i.name='Rice';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 0.80 FROM supplier s, ingredients i WHERE s.name='Golden Grain Wholesale' AND i.name='Sugar';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 0.50 FROM supplier s, ingredients i WHERE s.name='Golden Grain Wholesale' AND i.name='Salt';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.80 FROM supplier s, ingredients i WHERE s.name='Golden Grain Wholesale' AND i.name='Oats';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.60 FROM supplier s, ingredients i WHERE s.name='Golden Grain Wholesale' AND i.name='Wheat';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.20 FROM supplier s, ingredients i WHERE s.name='Golden Grain Wholesale' AND i.name='Quinoa';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.10 FROM supplier s, ingredients i WHERE s.name='Golden Grain Wholesale' AND i.name='Baking Powder';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 0.90 FROM supplier s, ingredients i WHERE s.name='Golden Grain Wholesale' AND i.name='Baking Soda';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.50 FROM supplier s, ingredients i WHERE s.name='Golden Grain Wholesale' AND i.name='Yeast';

-- Dairy Direct Inc. — dairy
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.20 FROM supplier s, ingredients i WHERE s.name='Dairy Direct Inc.' AND i.name='Milk';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 3.50 FROM supplier s, ingredients i WHERE s.name='Dairy Direct Inc.' AND i.name='Cream';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 4.50 FROM supplier s, ingredients i WHERE s.name='Dairy Direct Inc.' AND i.name='Butter';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 5.00 FROM supplier s, ingredients i WHERE s.name='Dairy Direct Inc.' AND i.name='Cheese';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 6.50 FROM supplier s, ingredients i WHERE s.name='Dairy Direct Inc.' AND i.name='Mozzarella';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 7.00 FROM supplier s, ingredients i WHERE s.name='Dairy Direct Inc.' AND i.name='Parmesan';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.80 FROM supplier s, ingredients i WHERE s.name='Dairy Direct Inc.' AND i.name='Yogurt';

-- Organic Valley Produce — organic vegetables
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.80 FROM supplier s, ingredients i WHERE s.name='Organic Valley Produce' AND i.name='Tomato';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.20 FROM supplier s, ingredients i WHERE s.name='Organic Valley Produce' AND i.name='Onion';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.20 FROM supplier s, ingredients i WHERE s.name='Organic Valley Produce' AND i.name='Spinach';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.50 FROM supplier s, ingredients i WHERE s.name='Organic Valley Produce' AND i.name='Broccoli';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.40 FROM supplier s, ingredients i WHERE s.name='Organic Valley Produce' AND i.name='Carrot';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 3.50 FROM supplier s, ingredients i WHERE s.name='Organic Valley Produce' AND i.name='Blueberry';

-- Spice World Trading — spices & condiments
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 3.50 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Paprika';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 4.00 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Cumin';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 4.50 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Turmeric';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 3.80 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Coriander';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 5.00 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Garam Masala';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 3.20 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Chili Powder';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.80 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Pepper';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 3.00 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Mustard Seeds';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.50 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Oregano';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.80 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Ketchup';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.20 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Soy Sauce';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.50 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Mustard';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 3.50 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Sesame Oil';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 4.50 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Honey';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.00 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Vinegar';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.80 FROM supplier s, ingredients i WHERE s.name='Spice World Trading' AND i.name='Mayonnaise';

-- Continental Beverage Supply — beverages
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 0.50 FROM supplier s, ingredients i WHERE s.name='Continental Beverage Supply' AND i.name='Water';

-- Sunrise Bakery Supplies — baking
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 5.50 FROM supplier s, ingredients i WHERE s.name='Sunrise Bakery Supplies' AND i.name='Vanilla';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 8.00 FROM supplier s, ingredients i WHERE s.name='Sunrise Bakery Supplies' AND i.name='Chocolate';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 1.00 FROM supplier s, ingredients i WHERE s.name='Sunrise Bakery Supplies' AND i.name='Flour';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 0.70 FROM supplier s, ingredients i WHERE s.name='Sunrise Bakery Supplies' AND i.name='Sugar';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 4.20 FROM supplier s, ingredients i WHERE s.name='Sunrise Bakery Supplies' AND i.name='Butter';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.30 FROM supplier s, ingredients i WHERE s.name='Sunrise Bakery Supplies' AND i.name='Yeast';

-- Green Leaf Herbs — herbs
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.50 FROM supplier s, ingredients i WHERE s.name='Green Leaf Herbs' AND i.name='Basil';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.80 FROM supplier s, ingredients i WHERE s.name='Green Leaf Herbs' AND i.name='Thyme';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 2.20 FROM supplier s, ingredients i WHERE s.name='Green Leaf Herbs' AND i.name='Parsley';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 3.00 FROM supplier s, ingredients i WHERE s.name='Green Leaf Herbs' AND i.name='Coriander';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 4.50 FROM supplier s, ingredients i WHERE s.name='Green Leaf Herbs' AND i.name='Walnuts';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 5.50 FROM supplier s, ingredients i WHERE s.name='Green Leaf Herbs' AND i.name='Cashews';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 6.00 FROM supplier s, ingredients i WHERE s.name='Green Leaf Herbs' AND i.name='Pistachios';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 3.80 FROM supplier s, ingredients i WHERE s.name='Green Leaf Herbs' AND i.name='Vegetable Oil';
INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) SELECT s.id, i.id, 0.30 FROM supplier s, ingredients i WHERE s.name='Green Leaf Herbs' AND i.name='Stock';
