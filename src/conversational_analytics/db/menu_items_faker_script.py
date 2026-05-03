from faker import Faker
import random

fake = Faker()

# Categories (same as your DB)
categories = [
    'Appetizers', 'Soups & Salads', 'Main Courses', 'Desserts', 'Beverages', 'Sides',
    'Breakfast', 'Brunch Specials', 'Eggs & Omelettes',
    'Flatbreads & Pizzas', 'Sliders & Small Bites', 'Charcuterie & Cheese',
    'Burgers & Sandwiches', 'Steaks & Grills', 'Seafood', 'Pasta & Risotto',
    'Vegetarian & Vegan', 'Tacos & Wraps', 'Rice & Noodles',
    'Kids Menu', 'Ice Cream & Gelato', 'Cakes & Pastries',
    'Cocktails', 'Mocktails', 'Wine & Beer', 'Coffee & Tea',
    'Fresh Juices & Smoothies', 'Milkshakes',
    'Chef Specials', 'Seasonal Menu', 'Happy Hour', 'Catering Packages'
]

# Predefined items per category (to keep it realistic)
menu_items_map = {
    'Appetizers': ['Bruschetta', 'Spring Rolls', 'Garlic Bread', 'Nachos'],
    'Soups & Salads': ['Tomato Soup', 'Caesar Salad', 'Greek Salad', 'Minestrone'],
    'Main Courses': ['Grilled Chicken', 'Veg Stir Fry', 'Paneer Butter Masala', 'BBQ Chicken'],
    'Desserts': ['Cheesecake', 'Chocolate Lava Cake', 'Tiramisu', 'Brownie'],
    'Beverages': ['Coca Cola', 'Lemonade', 'Iced Tea', 'Orange Juice'],
    'Sides': ['French Fries', 'Coleslaw', 'Garlic Bread', 'Onion Rings'],
    'Breakfast': ['Pancakes', 'Waffles', 'French Toast', 'Oatmeal'],
    'Brunch Specials': ['Avocado Toast', 'Egg Benedict', 'Brunch Platter'],
    'Eggs & Omelettes': ['Cheese Omelette', 'Masala Omelette', 'Boiled Eggs'],
    'Flatbreads & Pizzas': ['Margherita Pizza', 'Pepperoni Pizza', 'Veggie Pizza'],
    'Sliders & Small Bites': ['Chicken Sliders', 'Veg Sliders', 'Mini Burgers'],
    'Charcuterie & Cheese': ['Cheese Platter', 'Cold Cuts Board'],
    'Burgers & Sandwiches': ['Beef Burger', 'Chicken Burger', 'Veg Sandwich'],
    'Steaks & Grills': ['Ribeye Steak', 'Grilled Lamb', 'T-Bone Steak'],
    'Seafood': ['Grilled Salmon', 'Fish Tacos', 'Prawn Curry'],
    'Pasta & Risotto': ['Pasta Carbonara', 'Alfredo Pasta', 'Mushroom Risotto'],
    'Vegetarian & Vegan': ['Vegan Bowl', 'Tofu Stir Fry', 'Veg Curry'],
    'Tacos & Wraps': ['Chicken Wrap', 'Veg Tacos', 'Falafel Wrap'],
    'Rice & Noodles': ['Fried Rice', 'Hakka Noodles', 'Biryani'],
    'Kids Menu': ['Mini Burger', 'Mac & Cheese', 'Chicken Nuggets'],
    'Ice Cream & Gelato': ['Vanilla Ice Cream', 'Chocolate Gelato', 'Strawberry Scoop'],
    'Cakes & Pastries': ['Chocolate Cake', 'Croissant', 'Cupcake'],
    'Cocktails': ['Mojito', 'Margarita', 'Cosmopolitan'],
    'Mocktails': ['Virgin Mojito', 'Fruit Punch', 'Mint Cooler'],
    'Wine & Beer': ['Red Wine', 'White Wine', 'Craft Beer'],
    'Coffee & Tea': ['Espresso', 'Cappuccino', 'Green Tea'],
    'Fresh Juices & Smoothies': ['Mango Smoothie', 'Orange Juice', 'Berry Blast'],
    'Milkshakes': ['Chocolate Shake', 'Vanilla Shake', 'Oreo Shake'],
    'Chef Specials': ['Chef Special Chicken', 'Signature Dish'],
    'Seasonal Menu': ['Summer Salad', 'Winter Soup'],
    'Happy Hour': ['Beer Combo', 'Snack Platter'],
    'Catering Packages': ['Family Pack', 'Party Pack']
}

def generate_description(item):
    return f"{item} prepared with fresh ingredients and chef special seasoning."

def generate_price(category):
    base_prices = {
        'Appetizers': (5, 12),
        'Main Courses': (12, 25),
        'Desserts': (5, 10),
        'Beverages': (3, 8),
        'default': (6, 18)
    }
    low, high = base_prices.get(category, base_prices['default'])
    return round(random.uniform(low, high), 2)

def generate_sql(num_items_per_category=5):
    queries = []

    for category in categories:
        items = menu_items_map.get(category, [fake.word().title() for _ in range(3)])

        for _ in range(num_items_per_category):
            item_name = random.choice(items)
            description = generate_description(item_name)
            price = generate_price(category)
            is_active = random.choice(['true', 'true', 'true', 'false'])  # mostly active

            query = f"""INSERT INTO menu_items (category_id, name, description, base_price, is_active)
SELECT id, '{item_name}', '{description}', {price}, {is_active}
FROM menu_categories WHERE name = '{category}';"""

            queries.append(query)

    return "\n\n".join(queries)


if __name__ == "__main__":
    sql_output = generate_sql(num_items_per_category=5)

    with open("menu_items.sql", "w") as f:
        f.write(sql_output)

    print("✅ SQL file 'menu_items.sql' generated successfully!")