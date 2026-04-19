import os
import json
import psycopg2
from faker import Faker
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
from typing import Dict, List, Any
from pathlib import Path

load_dotenv()

class TestDataGenerator:
    """Generates realistic test data for restaurant database using Faker"""
    
    def __init__(self, db_host: str, db_name: str, db_user: str, db_password: str, db_port: int = 5433, sql_output_dir: str = "sql_data"):
        self.connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        self.cursor = self.connection.cursor()
        self.fake = Faker()
        self.generated_ids = {}  # Track generated IDs for FK relationships
        self.sql_queries = {}  # Store SQL queries by table
        self.sql_output_dir = sql_output_dir
        
        # Create output directory
        Path(self.sql_output_dir).mkdir(exist_ok=True)
    
    def add_query(self, table_name: str, query: str):
        """Add a query to the SQL collection"""
        if table_name not in self.sql_queries:
            self.sql_queries[table_name] = []
        self.sql_queries[table_name].append(query)
    
    def execute_and_save(self, query: str, params: tuple = None, table_name: str = None, return_id: bool = False):
        """Execute query and save SQL version"""
        # Execute the query
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        
        # Save SQL version
        if table_name and params:
            # Format the query with parameters for SQL file
            sql_query = self.cursor.mogrify(query, params).decode('utf-8')
            self.add_query(table_name, sql_query)
        
        # Return ID if requested
        if return_id:
            return self.cursor.fetchone()[0]
    
    def save_sql_files(self):
        """Save all collected SQL queries to files"""
        # Save combined file
        combined_file = os.path.join(self.sql_output_dir, "01_all_inserts.sql")
        with open(combined_file, 'w') as f:
            f.write("-- Generated Test Data for Restaurant Database\n")
            f.write(f"-- Generated at: {datetime.now().isoformat()}\n")
            f.write("-- Disable foreign key checks temporarily\n\n")
            f.write("SET session_replication_role = 'replica';\n\n")
            
            # Write all queries in order
            for table_name in sorted(self.sql_queries.keys()):
                f.write(f"-- {table_name.upper()}\n")
                for query in self.sql_queries[table_name]:
                    f.write(query + ";\n")
                f.write("\n")
            
            f.write("SET session_replication_role = 'origin';\n")
        
        print(f"✓ Saved combined SQL to {combined_file}")
        
        # Save individual table files
        for table_name, queries in sorted(self.sql_queries.items()):
            file_path = os.path.join(self.sql_output_dir, f"{table_name}_inserts.sql")
            with open(file_path, 'w') as f:
                f.write(f"-- Insert data into {table_name}\n")
                f.write(f"-- Generated at: {datetime.now().isoformat()}\n\n")
                for query in queries:
                    f.write(query + ";\n")
            print(f"✓ Saved {len(queries)} queries to {file_path}")
    
    def clear_data(self):
        """Clear all data from tables (respecting FK constraints)"""
        tables = [
            'loyalty_txn', 'order_discounts', 'order_items', 'payments', 'reservations',
            'shifts', 'orders', 'recipe_items', 'supplier_items', 'inventory',
            'loyalty_accounts', 'menu_items', 'menu_categories', 'ingredients', 'supplier',
            'employee', 'roles', 'tables', 'customers', 'location'
        ]
        for table in tables:
            self.cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")
        self.connection.commit()
        print("✓ Cleared all tables")
    
    def generate_locations(self, count: int = 5) -> List[int]:
        """Generate restaurant locations"""
        location_ids = []
        location_names = [
            "Downtown Diner", "Uptown Bistro", "Riverside Cafe",
            "Mountain View Restaurant", "Lakeside Grill", "Harbor Point Eatery",
            "Sunset Plaza Restaurant", "Garden District Cafe", "Old Town Steakhouse",
            "Beachfront Seafood Grill"
        ]
        
        for i in range(min(count, len(location_names))):
            name = location_names[i]
            address = self.fake.address().replace('\n', ', ')
            timezone = random.choice(['UTC', 'EST', 'CST', 'MST', 'PST'])
            
            query = "INSERT INTO location (name, address, timezone) VALUES (%s, %s, %s) RETURNING id"
            location_id = self.execute_and_save(query, (name, address, timezone), "location", return_id=True)
            location_ids.append(location_id)
        
        self.connection.commit()
        self.generated_ids['location'] = location_ids
        print(f"✓ Generated {len(location_ids)} locations")
        return location_ids
    
    def generate_roles(self) -> List[int]:
        """Generate employee roles"""
        role_names = ['Chef', 'Waiter', 'Manager', 'Bartender', 'Cashier', 'Host', 'Busser']
        role_ids = []
        
        for role_name in role_names:
            query = "INSERT INTO roles (role_name) VALUES (%s) RETURNING id"
            role_id = self.execute_and_save(query, (role_name,), "roles", return_id=True)
            role_ids.append(role_id)
        
        self.connection.commit()
        self.generated_ids['roles'] = role_ids
        print(f"✓ Generated {len(role_ids)} roles")
        return role_ids
    
    def generate_employees(self, count: int = 50) -> List[int]:
        """Generate employees"""
        employee_ids = []
        location_ids = self.generated_ids['location']
        role_ids = self.generated_ids['roles']
        
        for _ in range(count):
            name = self.fake.name()
            role_id = random.choice(role_ids)
            location_id = random.choice(location_ids)
            email = self.fake.email()
            hire_date = self.fake.date_between(start_date='-5y')
            
            query = "INSERT INTO employee (name, role_id, location_id, email, hire_date) VALUES (%s, %s, %s, %s, %s) RETURNING id"
            employee_id = self.execute_and_save(query, (name, role_id, location_id, email, hire_date), "employee", return_id=True)
            employee_ids.append(employee_id)
        
        self.connection.commit()
        self.generated_ids['employee'] = employee_ids
        print(f"✓ Generated {len(employee_ids)} employees")
        return employee_ids
    
    def generate_customers(self, count: int = 150) -> List[int]:
        """Generate customers"""
        customer_ids = []
        
        for _ in range(count):
            name = self.fake.name()
            phone = self.fake.phone_number()[:20]  # Truncate to fit VARCHAR(20)
            email = self.fake.email()
            address = self.fake.address().replace('\n', ', ')
            
            query = "INSERT INTO customers (name, phone, email, address) VALUES (%s, %s, %s, %s) RETURNING id"
            customer_id = self.execute_and_save(query, (name, phone, email, address), "customers", return_id=True)
            customer_ids.append(customer_id)
        
        self.connection.commit()
        self.generated_ids['customers'] = customer_ids
        print(f"✓ Generated {len(customer_ids)} customers")
        return customer_ids
    
    def generate_menu_categories(self) -> List[int]:
        """Generate menu categories"""
        categories = ['Appetizers', 'Soups & Salads', 'Main Courses', 'Desserts', 'Beverages', 'Sides']
        category_ids = []
        
        for category in categories:
            query = "INSERT INTO menu_categories (name) VALUES (%s) RETURNING id"
            category_id = self.execute_and_save(query, (category,), "menu_categories", return_id=True)
            category_ids.append(category_id)
        
        self.connection.commit()
        self.generated_ids['menu_categories'] = category_ids
        print(f"✓ Generated {len(category_ids)} menu categories")
        return category_ids
    
    def generate_menu_items(self, count: int = 60) -> List[int]:
        """Generate menu items"""
        menu_item_ids = []
        category_ids = self.generated_ids['menu_categories']
        
        dishes = {
            'Appetizers': ['Bruschetta', 'Calamari', 'Spring Rolls', 'Nachos', 'Mozzarella Sticks'],
            'Soups & Salads': ['Tomato Soup', 'Caesar Salad', 'Greek Salad', 'Minestrone', 'Caprese Salad'],
            'Main Courses': ['Grilled Salmon', 'Beef Steak', 'Chicken Parmesan', 'Pasta Carbonara', 'Fish Tacos'],
            'Desserts': ['Tiramisu', 'Chocolate Cake', 'Cheesecake', 'Crème Brûlée', 'Ice Cream'],
            'Beverages': ['Coca Cola', 'Iced Tea', 'Lemonade', 'Coffee', 'Wine'],
            'Sides': ['French Fries', 'Rice Pilaf', 'Vegetables', 'Bread Basket', 'Coleslaw']
        }
        
        category_idx = 0
        for _ in range(count):
            category_id = category_ids[category_idx % len(category_ids)]
            category_name = list(dishes.keys())[category_idx % len(category_ids)]
            name = random.choice(dishes[category_name])
            description = self.fake.sentence(nb_words=10)
            base_price = round(random.uniform(5.99, 29.99), 2)
            is_active = random.choice([True, False])
            
            query = "INSERT INTO menu_items (category_id, name, description, base_price, is_active) VALUES (%s, %s, %s, %s, %s) RETURNING id"
            menu_item_id = self.execute_and_save(query, (category_id, name, description, base_price, is_active), "menu_items", return_id=True)
            menu_item_ids.append(menu_item_id)
            category_idx += 1
        
        self.connection.commit()
        self.generated_ids['menu_items'] = menu_item_ids
        print(f"✓ Generated {len(menu_item_ids)} menu items")
        return menu_item_ids
    
    def generate_ingredients(self, count: int = 40) -> List[int]:
        """Generate ingredients"""
        ingredient_ids = []
        ingredient_names = [
            'Flour', 'Sugar', 'Salt', 'Pepper', 'Olive Oil', 'Butter', 'Eggs',
            'Chicken', 'Beef', 'Salmon', 'Tomato', 'Lettuce', 'Cucumber', 'Onion',
            'Garlic', 'Cheese', 'Milk', 'Pasta', 'Rice', 'Bread', 'Potatoes',
            'Carrots', 'Broccoli', 'Spinach', 'Mushrooms', 'Bell Pepper', 'Lemon',
            'Lime', 'Ginger', 'Basil', 'Oregano', 'Thyme', 'Cinnamon', 'Vanilla',
            'Chocolate', 'Honey', 'Vinegar', 'Wine', 'Beer', 'Coffee'
        ]
        units = ['kg', 'liter', 'pieces', 'cups', 'grams', 'ml', 'oz']
        
        for ingredient_name in ingredient_names[:count]:
            unit = random.choice(units)
            query = "INSERT INTO ingredients (name, unit) VALUES (%s, %s) RETURNING id"
            ingredient_id = self.execute_and_save(query, (ingredient_name, unit), "ingredients", return_id=True)
            ingredient_ids.append(ingredient_id)
        
        self.connection.commit()
        self.generated_ids['ingredients'] = ingredient_ids
        print(f"✓ Generated {len(ingredient_ids)} ingredients")
        return ingredient_ids
    
    def generate_recipe_items(self) -> None:
        """Generate recipe items (linking menu items to ingredients)"""
        menu_item_ids = self.generated_ids['menu_items']
        ingredient_ids = self.generated_ids['ingredients']
        recipe_count = 0
        
        for menu_item_id in menu_item_ids:
            # Each menu item gets 2-5 ingredients
            num_ingredients = random.randint(2, 5)
            selected_ingredients = random.sample(ingredient_ids, min(num_ingredients, len(ingredient_ids)))
            
            for ingredient_id in selected_ingredients:
                qty = round(random.uniform(0.5, 5.0), 2)
                try:
                    query = "INSERT INTO recipe_items (menu_item_id, ingredient_id, qty_per_recipe) VALUES (%s, %s, %s)"
                    self.execute_and_save(query, (menu_item_id, ingredient_id, qty), "recipe_items")
                    recipe_count += 1
                except psycopg2.IntegrityError:
                    self.connection.rollback()
                    continue
        
        self.connection.commit()
        print(f"✓ Generated {recipe_count} recipe items")
    
    def generate_supplier(self, count: int = 8) -> List[int]:
        """Generate suppliers"""
        supplier_ids = []
        supplier_names = [
            "Fresh Farms Co.", "Global Ingredients Ltd.", "Local Produce Market",
            "Premium Suppliers Inc.", "Quality Foods Wholesale"
        ]
        
        for name in supplier_names[:count]:
            query = "INSERT INTO supplier (name) VALUES (%s) RETURNING id"
            supplier_id = self.execute_and_save(query, (name,), "supplier", return_id=True)
            supplier_ids.append(supplier_id)
        
        self.connection.commit()
        self.generated_ids['supplier'] = supplier_ids
        print(f"✓ Generated {len(supplier_ids)} suppliers")
        return supplier_ids
    
    def generate_supplier_items(self) -> None:
        """Generate supplier items (ingredient pricing)"""
        supplier_ids = self.generated_ids['supplier']
        ingredient_ids = self.generated_ids['ingredients']
        supplier_item_count = 0
        
        for ingredient_id in ingredient_ids:
            # Each ingredient from 2-3 suppliers
            num_suppliers = random.randint(2, 3)
            selected_suppliers = random.sample(supplier_ids, min(num_suppliers, len(supplier_ids)))
            
            for supplier_id in selected_suppliers:
                unit_cost = round(random.uniform(1.0, 50.0), 2)
                try:
                    query = "INSERT INTO supplier_items (supplier_id, ingredient_id, unit_cost) VALUES (%s, %s, %s)"
                    self.execute_and_save(query, (supplier_id, ingredient_id, unit_cost), "supplier_items")
                    supplier_item_count += 1
                except psycopg2.IntegrityError:
                    self.connection.rollback()
                    continue
        
        self.connection.commit()
        print(f"✓ Generated {supplier_item_count} supplier items")
    
    def generate_inventory(self) -> None:
        """Generate inventory records"""
        location_ids = self.generated_ids['location']
        ingredient_ids = self.generated_ids['ingredients']
        inventory_count = 0
        
        for location_id in location_ids:
            for ingredient_id in ingredient_ids:
                quantity = round(random.uniform(10.0, 100.0), 2)
                reorder_threshold = round(random.uniform(5.0, 20.0), 2)
                
                query = "INSERT INTO inventory (location_id, ingredient_id, quantity_on_hand, reorder_threshold) VALUES (%s, %s, %s, %s)"
                self.execute_and_save(query, (location_id, ingredient_id, quantity, reorder_threshold), "inventory")
                inventory_count += 1
        
        self.connection.commit()
        print(f"✓ Generated {inventory_count} inventory records")
    
    def generate_tables(self) -> List[int]:
        """Generate restaurant tables"""
        table_ids = []
        location_ids = self.generated_ids['location']
        
        for location_id in location_ids:
            num_tables = random.randint(10, 20)
            for table_num in range(1, num_tables + 1):
                capacity = random.choice([2, 4, 6, 8])
                query = "INSERT INTO tables (location_id, table_number, capacity) VALUES (%s, %s, %s) RETURNING id"
                table_id = self.execute_and_save(query, (location_id, table_num, capacity), "tables", return_id=True)
                table_ids.append(table_id)
        
        self.connection.commit()
        self.generated_ids['tables'] = table_ids
        print(f"✓ Generated {len(table_ids)} tables")
        return table_ids
    
    def generate_shifts(self) -> None:
        """Generate employee shifts"""
        employee_ids = self.generated_ids['employee']
        location_ids = self.generated_ids['location']
        shift_count = 0
        
        for employee_id in employee_ids:
            num_shifts = random.randint(3, 5)
            for _ in range(num_shifts):
                location_id = random.choice(location_ids)
                shift_date = self.fake.date_time_between(start_date='-7d')
                shift_start = shift_date.replace(hour=random.choice([8, 11, 15]))
                shift_end = shift_start + timedelta(hours=random.randint(4, 8))
                
                query = "INSERT INTO shifts (employee_id, location_id, shift_start, shift_end) VALUES (%s, %s, %s, %s)"
                self.execute_and_save(query, (employee_id, location_id, shift_start, shift_end), "shifts")
                shift_count += 1
        
        self.connection.commit()
        print(f"✓ Generated {shift_count} shifts")
    
    def generate_orders(self, count: int = 300) -> List[int]:
        """Generate orders"""
        order_ids = []
        location_ids = self.generated_ids['location']
        customer_ids = self.generated_ids['customers']
        employee_ids = self.generated_ids['employee']
        table_ids = self.generated_ids['tables']
        
        for _ in range(count):
            location_id = random.choice(location_ids)
            customer_id = random.choice(customer_ids) if random.random() > 0.2 else None
            employee_id = random.choice(employee_ids)
            table_id = random.choice(table_ids) if random.random() > 0.3 else None
            order_time = self.fake.date_time_this_month()
            total_amount = round(random.uniform(15.0, 150.0), 2)
            tax_amount = round(total_amount * 0.08, 2)
            tip_amount = round(random.uniform(0, total_amount * 0.2), 2)
            status = random.choice(['open', 'completed', 'cancelled'])
            
            query = "INSERT INTO orders (location_id, customer_id, employee_id, table_id, order_time, total_amount, tax_amount, tip_amount, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"
            order_id = self.execute_and_save(query, (location_id, customer_id, employee_id, table_id, order_time, total_amount, tax_amount, tip_amount, status), "orders", return_id=True)
            order_ids.append(order_id)
        
        self.connection.commit()
        self.generated_ids['orders'] = order_ids
        print(f"✓ Generated {len(order_ids)} orders")
        return order_ids
    
    def generate_order_items(self) -> None:
        """Generate order items"""
        order_ids = self.generated_ids['orders']
        menu_item_ids = self.generated_ids['menu_items']
        order_item_count = 0
        
        for order_id in order_ids:
            num_items = random.randint(1, 5)
            selected_items = random.sample(menu_item_ids, min(num_items, len(menu_item_ids)))
            
            for menu_item_id in selected_items:
                quantity = random.randint(1, 3)
                unit_price = round(random.uniform(5.99, 29.99), 2)
                
                query = "INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price) VALUES (%s, %s, %s, %s)"
                self.execute_and_save(query, (order_id, menu_item_id, quantity, unit_price), "order_items")
                order_item_count += 1
        
        self.connection.commit()
        print(f"✓ Generated {order_item_count} order items")
    
    def generate_payments(self) -> None:
        """Generate payments"""
        order_ids = self.generated_ids['orders']
        payment_count = 0
        
        for order_id in order_ids:
            if random.random() > 0.2:
                payment_time = self.fake.date_time_this_month()
                amount = round(random.uniform(20.0, 200.0), 2)
                method = random.choice(['cash', 'credit_card', 'debit_card', 'digital_wallet'])
                status = random.choice(['paid', 'pending', 'failed']) if random.random() > 0.9 else 'paid'
                
                try:
                    query = "INSERT INTO payments (order_id, payment_time, amount, method, status) VALUES (%s, %s, %s, %s, %s)"
                    self.execute_and_save(query, (order_id, payment_time, amount, method, status), "payments")
                    payment_count += 1
                except psycopg2.IntegrityError:
                    self.connection.rollback()
                    continue
        
        self.connection.commit()
        print(f"✓ Generated {payment_count} payments")
    
    def generate_discounts(self, count: int = 20) -> List[int]:
        """Generate discounts"""
        discount_ids = []
        discount_types = ['percent', 'fixed']
        
        for i in range(count):
            code = f"PROMO{i+1:03d}_{random.randint(1000, 9999)}"
            description = self.fake.sentence(nb_words=5)
            discount_type = random.choice(discount_types)
            amount = round(random.uniform(5, 50), 2) if discount_type == 'fixed' else round(random.uniform(5, 30), 2)
            start_date = self.fake.date_object()
            end_date = start_date + timedelta(days=random.randint(7, 90))
            
            query = "INSERT INTO discounts (code, description, type, amount, start_date, end_date) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id"
            discount_id = self.execute_and_save(query, (code, description, discount_type, amount, start_date, end_date), "discounts", return_id=True)
            discount_ids.append(discount_id)
        
        self.connection.commit()
        self.generated_ids['discounts'] = discount_ids
        print(f"✓ Generated {len(discount_ids)} discounts")
        return discount_ids
    
    def generate_order_discounts(self) -> None:
        """Generate order discounts"""
        order_ids = self.generated_ids['orders']
        discount_ids = self.generated_ids['discounts']
        order_discount_count = 0
        
        for order_id in order_ids:
            if random.random() > 0.7:
                num_discounts = random.randint(1, 2)
                selected_discounts = random.sample(discount_ids, min(num_discounts, len(discount_ids)))
                
                for discount_id in selected_discounts:
                    try:
                        query = "INSERT INTO order_discounts (order_id, discount_id) VALUES (%s, %s)"
                        self.execute_and_save(query, (order_id, discount_id), "order_discounts")
                        order_discount_count += 1
                    except psycopg2.IntegrityError:
                        self.connection.rollback()
                        continue
        
        self.connection.commit()
        print(f"✓ Generated {order_discount_count} order discounts")
    
    def generate_loyalty_accounts(self) -> List[int]:
        """Generate loyalty accounts"""
        loyalty_ids = []
        customer_ids = self.generated_ids['customers']
        
        loyalty_customers = random.sample(customer_ids, int(len(customer_ids) * 0.7))
        
        for customer_id in loyalty_customers:
            points_balance = random.randint(0, 1000)
            query = "INSERT INTO loyalty_accounts (customer_id, points_balance) VALUES (%s, %s) RETURNING id"
            loyalty_id = self.execute_and_save(query, (customer_id, points_balance), "loyalty_accounts", return_id=True)
            loyalty_ids.append(loyalty_id)
        
        self.connection.commit()
        self.generated_ids['loyalty_accounts'] = loyalty_ids
        print(f"✓ Generated {len(loyalty_ids)} loyalty accounts")
        return loyalty_ids
    
    def generate_loyalty_txn(self) -> None:
        """Generate loyalty transactions"""
        loyalty_ids = self.generated_ids['loyalty_accounts']
        txn_count = 0
        
        for loyalty_id in loyalty_ids:
            num_txns = random.randint(2, 5)
            for _ in range(num_txns):
                points_change = random.randint(-100, 200)
                txn_type = 'redeem' if points_change < 0 else 'earn'
                txn_time = self.fake.date_time_this_month()
                
                query = "INSERT INTO loyalty_txn (loyalty_id, points_change, txn_type, txn_time) VALUES (%s, %s, %s, %s)"
                self.execute_and_save(query, (loyalty_id, points_change, txn_type, txn_time), "loyalty_txn")
                txn_count += 1
        
        self.connection.commit()
        print(f"✓ Generated {txn_count} loyalty transactions")
    
    def generate_reservations(self, count: int = 100) -> None:
        """Generate reservations"""
        table_ids = self.generated_ids['tables']
        customer_ids = self.generated_ids['customers']
        reservation_count = 0
        
        for _ in range(count):
            table_id = random.choice(table_ids)
            customer_id = random.choice(customer_ids)
            start_time = self.fake.future_datetime(end_date='+30d')
            end_time = start_time + timedelta(hours=random.randint(1, 3))
            status = random.choice(['booked', 'checked_in', 'no_show', 'cancelled'])
            
            query = "INSERT INTO reservations (table_id, customer_id, start_time, end_time, status) VALUES (%s, %s, %s, %s, %s)"
            self.execute_and_save(query, (table_id, customer_id, start_time, end_time, status), "reservations")
            reservation_count += 1
        
        self.connection.commit()
        print(f"✓ Generated {reservation_count} reservations")
    
    def load_existing_ids(self):
        """Load IDs from existing master data in the database"""
        print("📂 Loading existing master data IDs from database...\n")
        
        tables_to_load = {
            'location': 'SELECT id FROM location ORDER BY id',
            'roles': 'SELECT id FROM roles ORDER BY id',
            'employee': 'SELECT id FROM employee ORDER BY id',
            'customers': 'SELECT id FROM customers ORDER BY id',
            'menu_categories': 'SELECT id FROM menu_categories ORDER BY id',
            'menu_items': 'SELECT id FROM menu_items ORDER BY id',
            'ingredients': 'SELECT id FROM ingredients ORDER BY id',
            'supplier': 'SELECT id FROM supplier ORDER BY id',
            'tables': 'SELECT id FROM tables ORDER BY id',
            'discounts': 'SELECT id FROM discounts ORDER BY id',
            'orders': 'SELECT id FROM orders ORDER BY id',
            'loyalty_accounts': 'SELECT id FROM loyalty_accounts ORDER BY id'
        }
        
        for table_name, query in tables_to_load.items():
            try:
                self.cursor.execute(query)
                ids = [row[0] for row in self.cursor.fetchall()]
                if ids:
                    self.generated_ids[table_name] = ids
                    print(f"✓ Loaded {len(ids)} IDs from {table_name}")
                else:
                    print(f"⚠ No data found in {table_name} - run master data generation first")
            except Exception as e:
                print(f"⚠ Could not load {table_name}: {str(e)}")
    
    def generate_daily_data(self, orders_count: int = 50):
        """
        Generate daily operational data for recurring insertion.
        This should be run daily to simulate actual restaurant operations.
        
        Daily tables generated:
        - orders: New customer orders
        - order_items: Items within orders
        - payments: Payment transactions
        - order_discounts: Discounts applied to orders
        - loyalty_txn: Loyalty points transactions
        - shifts: Employee work schedules
        - reservations: Table bookings
        - inventory: Stock level updates (after order consumption)
        """
        print("\n📅 Starting daily test data generation...\n")
        
        # Load existing master data IDs from database
        self.load_existing_ids()
        
        # Check if we have required master data
        required_tables = ['location', 'employee', 'customers', 'menu_items', 'tables', 'orders']
        missing = [t for t in required_tables if t not in self.generated_ids or not self.generated_ids[t]]
        if missing:
            print(f"\n❌ ERROR: Missing master data in: {', '.join(missing)}")
            print("   Please run master data generation first: python test_data_generator.py")
            self.close()
            return
        
        self.sql_queries = {}  # Reset queries for daily generation
        
        self.generate_shifts()                  # Employee shifts for today
        self.generate_orders(orders_count)      # New orders (~50 per day)
        self.generate_order_items()             # Items within orders
        self.generate_discounts(3)              # New promotional codes (3-5 daily)
        self.generate_order_discounts()         # Apply discounts to orders
        self.generate_payments()                # Process payments
        self.generate_loyalty_txn()             # Loyalty point transactions
        self.generate_reservations(15)          # New table reservations (~15 daily)
        # Note: inventory is typically updated via consumption logic in separate process
        
        print("\n✅ Daily data generation completed successfully!")
        print("\n💾 Saving daily SQL files...\n")
        
        # Save with daily timestamp
        from datetime import datetime
        daily_suffix = datetime.now().strftime("%Y%m%d")
        daily_output_dir = os.path.join(self.sql_output_dir, f"daily_{daily_suffix}")
        Path(daily_output_dir).mkdir(exist_ok=True)
        
        # Save combined daily file
        combined_file = os.path.join(daily_output_dir, f"daily_inserts_{daily_suffix}.sql")
        with open(combined_file, 'w') as f:
            f.write(f"-- Daily Test Data Insert ({datetime.now().isoformat()})\n")
            f.write("-- These tables receive data daily:\n")
            f.write("-- orders, order_items, payments, order_discounts, loyalty_txn, shifts, reservations, inventory\n\n")
            f.write("SET session_replication_role = 'replica';\n\n")
            
            for table_name in sorted(self.sql_queries.keys()):
                f.write(f"-- {table_name.upper()}\n")
                for query in self.sql_queries[table_name]:
                    f.write(query + ";\n")
                f.write("\n")
            
            f.write("SET session_replication_role = 'origin';\n")
        
        print(f"✓ Saved daily combined SQL to {combined_file}")
        
        # Save individual table files
        for table_name, queries in sorted(self.sql_queries.items()):
            file_path = os.path.join(daily_output_dir, f"{table_name}_inserts_{daily_suffix}.sql")
            with open(file_path, 'w') as f:
                f.write(f"-- Daily inserts into {table_name} ({datetime.now().isoformat()})\n\n")
                for query in queries:
                    f.write(query + ";\n")
            print(f"✓ Saved {len(queries)} daily queries to {file_path}")
    
    
    def generate_all_data(self):
        """Generate all test data in the correct order"""
        print("\n🔄 Starting test data generation...\n")
        
        self.generate_locations(8)              # 8 restaurant locations
        self.generate_roles()                   # 7 roles
        self.generate_employees(50)             # 50 employees (more staff for multiple locations)
        self.generate_customers(150)            # 150 customers
        self.generate_menu_categories()         # 6 categories
        self.generate_menu_items(60)            # 60 menu items
        self.generate_ingredients(40)           # 40 ingredients
        self.generate_recipe_items()            # Links ingredients to menu items
        self.generate_supplier(8)               # 8 suppliers
        self.generate_supplier_items()          # Links suppliers to ingredients
        self.generate_inventory()               # Inventory for each location
        self.generate_tables()                  # Tables for each location
        self.generate_shifts()                  # Employee shifts
        self.generate_orders(300)               # 300 orders
        self.generate_order_items()             # Items within orders
        self.generate_discounts(20)             # 20 discount codes
        self.generate_order_discounts()         # Links discounts to orders
        self.generate_payments()                # Payment records
        self.generate_loyalty_accounts()        # Loyalty accounts for customers
        self.generate_loyalty_txn()             # Loyalty transactions
        self.generate_reservations(100)         # 100 table reservations
        
        print("\n✅ Test data generation completed successfully!")
        print("\n💾 Saving SQL files...\n")
        self.save_sql_files()
    
    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.connection.close()


# Usage example
if __name__ == "__main__":
    import sys
    
    generator = TestDataGenerator(
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5433")),
        db_name=os.getenv("DB_NAME", "zenvyra"),
        db_user=os.getenv("DB_USER", "admin_user"),
        db_password=os.getenv("DB_PASSWORD", "admin_password"),
        sql_output_dir="sql_data"
    )
    
    # Check if daily mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "daily":
        # Daily data generation (run this every day)
        generator.generate_daily_data(orders_count=50)
    else:
        # Master data setup (run once)
        generator.clear_data()
        generator.generate_all_data()
    
    generator.close()
