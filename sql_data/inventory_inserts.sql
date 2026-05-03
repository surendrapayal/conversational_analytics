-- ── inventory (stock levels per location per ingredient) ─────────────────────
-- Covers key ingredients across all 20 locations
-- quantity_on_hand in kg/liters/units, reorder_threshold = 20% of typical stock

INSERT INTO inventory (location_id, ingredient_id, quantity_on_hand, reorder_threshold)
SELECT l.id, i.id,
    ROUND((RANDOM() * 40 + 10)::numeric, 2),
    ROUND((RANDOM() * 5 + 2)::numeric, 2)
FROM location l, ingredients i
WHERE i.name IN (
    'Chicken','Beef','Salmon','Prawns','Pork','Lamb','Bacon',
    'Pasta','Rice','Flour','Sugar','Salt','Butter','Milk','Cream','Cheese','Mozzarella','Parmesan',
    'Tomato','Onion','Garlic','Spinach','Broccoli','Carrot','Bell Pepper','Cabbage','Zucchini',
    'Basil','Thyme','Parsley','Oregano','Paprika','Cumin','Pepper','Chili Powder',
    'Vegetable Oil','Sesame Oil','Soy Sauce','Honey','Vinegar','Ketchup','Mayonnaise',
    'Lemon Juice','Mango','Orange','Apple','Strawberry','Banana',
    'Chocolate','Vanilla','Yeast','Baking Powder','Stock','Yogurt','Eggs'
)
ON CONFLICT (location_id, ingredient_id) DO NOTHING;
