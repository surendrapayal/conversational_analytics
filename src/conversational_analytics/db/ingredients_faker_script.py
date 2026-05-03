from faker import Faker
import random

fake = Faker()

# Ingredient categories with realistic items
ingredient_categories = {
    "Dairy": ["Milk", "Butter", "Cheese", "Yogurt", "Cream", "Mozzarella", "Parmesan"],
    "Meat": ["Chicken", "Beef", "Pork", "Lamb", "Turkey", "Bacon"],
    "Seafood": ["Salmon", "Tuna", "Prawns", "Crab"],
    "Vegetables": [
        "Tomato", "Onion", "Garlic", "Carrot", "Broccoli",
        "Spinach", "Cabbage", "Zucchini", "Eggplant", "Bell Pepper"
    ],
    "Fruits": ["Apple", "Banana", "Mango", "Orange", "Strawberry", "Blueberry"],
    "Grains": ["Rice", "Wheat", "Oats", "Quinoa", "Pasta", "Flour"],
    "Spices": ["Salt", "Pepper", "Turmeric", "Cumin", "Paprika", "Chili Powder"],
    "Herbs": ["Basil", "Oregano", "Thyme", "Coriander", "Parsley"],
    "Oils": ["Olive Oil", "Vegetable Oil", "Sesame Oil"],
    "Liquids": ["Water", "Vinegar", "Soy Sauce", "Stock", "Lemon Juice"],
    "Baking": ["Sugar", "Baking Powder", "Baking Soda", "Yeast", "Vanilla"],
    "Nuts": ["Almonds", "Cashews", "Walnuts", "Pistachios"],
    "Others": ["Chocolate", "Honey", "Ketchup", "Mayonnaise", "Mustard"],
    "Indian": ["Paneer", "Garam Masala", "Dal", "Chana", "Mustard Seeds"]
}

# Unit mapping per category
unit_mapping = {
    "Dairy": ["ml", "grams"],
    "Meat": ["grams"],
    "Seafood": ["grams"],
    "Vegetables": ["grams"],
    "Fruits": ["pieces", "grams"],
    "Grains": ["grams"],
    "Spices": ["grams"],
    "Herbs": ["grams"],
    "Oils": ["ml"],
    "Liquids": ["ml"],
    "Baking": ["grams"],
    "Nuts": ["grams"],
    "Others": ["grams", "ml"]
}

def generate_ingredient_name(existing_names):
    """Generate unique ingredient names"""
    all_items = [item for sublist in ingredient_categories.values() for item in sublist]

    while True:
        name = random.choice(all_items)
        if name not in existing_names:
            return name

def generate_unit(category):
    return random.choice(unit_mapping.get(category, ["grams"]))

def generate_sql(num_records=100):
    queries = []
    used_names = set()

    for _ in range(num_records):
        print(f"Generating ingredient {_ + 1}/{num_records}...")
        category = random.choice(list(ingredient_categories.keys()))
        name = generate_ingredient_name(used_names)
        unit = generate_unit(category)

        used_names.add(name)

        query = f"INSERT INTO ingredients (name, unit) VALUES ('{name}', '{unit}');"
        queries.append(query)

    return "\n".join(queries)


if __name__ == "__main__":
    print("Generating SQL for ingredients...")
    sql_output = generate_sql(75)

    with open("ingredients.sql", "w") as f:
        f.write(sql_output)

    print("✅ ingredients.sql generated successfully!")