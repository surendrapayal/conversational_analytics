-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- VECTOR TABLE
--CREATE TABLE IF NOT EXISTS embeddings (
--    id SERIAL PRIMARY KEY,
--    message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
--    embedding vector(1536),
--    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
--);

-- Create index for faster similarity search
--CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);

--RELATIONAL TABLES
-- ============================================================================
-- CORE MASTER DATA TABLES
-- ============================================================================

-- Location: Restaurant branches/locations
CREATE TABLE IF NOT EXISTS location (
  id SERIAL PRIMARY KEY, 
  name TEXT NOT NULL, 
  address TEXT, 
  timezone TEXT NOT NULL DEFAULT 'UTC'
);

COMMENT ON TABLE location IS 'Stores information about restaurant branches/locations';
COMMENT ON COLUMN location.id IS 'Unique identifier for location';
COMMENT ON COLUMN location.name IS 'Name of the restaurant location/branch';
COMMENT ON COLUMN location.address IS 'Physical address of the location';
COMMENT ON COLUMN location.timezone IS 'Timezone for the location (used for order timing)';

-- Roles: Employee job titles
CREATE TABLE IF NOT EXISTS roles (
  id SERIAL PRIMARY KEY, 
  role_name VARCHAR(20) UNIQUE NOT NULL
);

COMMENT ON TABLE roles IS 'Employee roles/job titles (Chef, Waiter, Manager, etc.)';
COMMENT ON COLUMN roles.id IS 'Unique identifier for role';
COMMENT ON COLUMN roles.role_name IS 'Name of the job role (must be unique)';

-- Employee: Staff members
CREATE TABLE IF NOT EXISTS employee (
  id SERIAL PRIMARY KEY, 
  name VARCHAR(100) NOT NULL, 
  role_id INT NOT NULL REFERENCES roles(id), 
  location_id INT NOT NULL REFERENCES location(id), 
  email VARCHAR(100) UNIQUE, 
  hire_date DATE NOT NULL
);

CREATE INDEX ON employee(location_id);

COMMENT ON TABLE employee IS 'Staff members working at restaurant locations';
COMMENT ON COLUMN employee.id IS 'Unique identifier for employee';
COMMENT ON COLUMN employee.name IS 'Full name of employee';
COMMENT ON COLUMN employee.role_id IS 'Foreign key referencing roles table';
COMMENT ON COLUMN employee.location_id IS 'Foreign key referencing location where employee works';
COMMENT ON COLUMN employee.email IS 'Email address (unique per employee)';
COMMENT ON COLUMN employee.hire_date IS 'Date employee was hired';

-- Customers: Customer profiles
CREATE TABLE IF NOT EXISTS customers (
  id SERIAL PRIMARY KEY, 
  name VARCHAR(100) NOT NULL, 
  phone VARCHAR(20), 
  email VARCHAR(100) UNIQUE, 
  address TEXT
);

COMMENT ON TABLE customers IS 'Customer profiles and contact information';
COMMENT ON COLUMN customers.id IS 'Unique identifier for customer';
COMMENT ON COLUMN customers.name IS 'Customer full name';
COMMENT ON COLUMN customers.phone IS 'Customer phone number';
COMMENT ON COLUMN customers.email IS 'Customer email address (unique)';
COMMENT ON COLUMN customers.address IS 'Customer address for delivery/correspondence';

-- ============================================================================
-- MENU & INVENTORY TABLES
-- ============================================================================

-- Menu Categories: Food types/categories
CREATE TABLE IF NOT EXISTS menu_categories (
  id SERIAL PRIMARY KEY, 
  name TEXT UNIQUE NOT NULL
);

COMMENT ON TABLE menu_categories IS 'Menu categories (Appetizers, Entrees, Desserts, Beverages, etc.)';
COMMENT ON COLUMN menu_categories.id IS 'Unique identifier for category';
COMMENT ON COLUMN menu_categories.name IS 'Category name (must be unique)';

-- Menu Items: Individual dishes
CREATE TABLE IF NOT EXISTS menu_items (
  id SERIAL PRIMARY KEY, 
  category_id INT REFERENCES menu_categories(id), 
  name VARCHAR(100) NOT NULL, 
  description TEXT, 
  base_price NUMERIC(8, 2) NOT NULL, 
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE menu_items IS 'Menu items/dishes available for ordering';
COMMENT ON COLUMN menu_items.id IS 'Unique identifier for menu item';
COMMENT ON COLUMN menu_items.category_id IS 'Foreign key referencing menu_categories';
COMMENT ON COLUMN menu_items.name IS 'Name of the dish';
COMMENT ON COLUMN menu_items.description IS 'Description of the dish (ingredients, preparation notes)';
COMMENT ON COLUMN menu_items.base_price IS 'Base price of the menu item';
COMMENT ON COLUMN menu_items.is_active IS 'Whether item is currently available (active/inactive)';

-- Ingredients: Raw materials/components
CREATE TABLE IF NOT EXISTS ingredients (
  id SERIAL PRIMARY KEY, 
  name TEXT NOT NULL, 
  unit VARCHAR(20) NOT NULL
);

COMMENT ON TABLE ingredients IS 'Individual ingredients/raw materials used in recipes';
COMMENT ON COLUMN ingredients.id IS 'Unique identifier for ingredient';
COMMENT ON COLUMN ingredients.name IS 'Name of ingredient (flour, chicken, tomato, etc.)';
COMMENT ON COLUMN ingredients.unit IS 'Unit of measurement (kg, liter, pieces, cups, grams)';

-- Recipe Items: Ingredients per dish
CREATE TABLE IF NOT EXISTS recipe_items (
  menu_item_id INT REFERENCES menu_items(id), 
  ingredient_id INT REFERENCES ingredients(id), 
  qty_per_recipe NUMERIC(8, 2) NOT NULL, 
  PRIMARY KEY(menu_item_id, ingredient_id)
);

COMMENT ON TABLE recipe_items IS 'Defines recipes by listing ingredients needed for each menu item';
COMMENT ON COLUMN recipe_items.menu_item_id IS 'Foreign key referencing menu_items';
COMMENT ON COLUMN recipe_items.ingredient_id IS 'Foreign key referencing ingredients';
COMMENT ON COLUMN recipe_items.qty_per_recipe IS 'Quantity of ingredient needed per recipe (in ingredient unit)';

-- Supplier: Ingredient vendors
CREATE TABLE IF NOT EXISTS supplier (
  id SERIAL PRIMARY KEY, 
  name TEXT NOT NULL
);

COMMENT ON TABLE supplier IS 'Ingredient suppliers/vendors';
COMMENT ON COLUMN supplier.id IS 'Unique identifier for supplier';
COMMENT ON COLUMN supplier.name IS 'Supplier company name';

-- Supplier Items: Ingredient pricing from suppliers
CREATE TABLE IF NOT EXISTS supplier_items (
  supplier_id INT REFERENCES supplier(id), 
  ingredient_id INT REFERENCES ingredients(id), 
  unit_cost NUMERIC(8, 2) NOT NULL, 
  PRIMARY KEY(supplier_id, ingredient_id)
);

COMMENT ON TABLE supplier_items IS 'Pricing of ingredients from different suppliers';
COMMENT ON COLUMN supplier_items.supplier_id IS 'Foreign key referencing supplier';
COMMENT ON COLUMN supplier_items.ingredient_id IS 'Foreign key referencing ingredients';
COMMENT ON COLUMN supplier_items.unit_cost IS 'Cost per unit of ingredient from this supplier';

-- Inventory: Stock levels per location
CREATE TABLE IF NOT EXISTS inventory (
  id SERIAL PRIMARY KEY, 
  location_id INT REFERENCES location(id), 
  ingredient_id INT REFERENCES ingredients(id), 
  quantity_on_hand NUMERIC(8, 2) NOT NULL DEFAULT 0, 
  reorder_threshold NUMERIC(8, 2) DEFAULT 0, 
  UNIQUE(location_id, ingredient_id)
);

CREATE INDEX ON inventory(location_id, ingredient_id);

COMMENT ON TABLE inventory IS 'Current stock levels of ingredients at each location';
COMMENT ON COLUMN inventory.id IS 'Unique identifier for inventory record';
COMMENT ON COLUMN inventory.location_id IS 'Foreign key referencing location';
COMMENT ON COLUMN inventory.ingredient_id IS 'Foreign key referencing ingredients';
COMMENT ON COLUMN inventory.quantity_on_hand IS 'Current stock quantity available';
COMMENT ON COLUMN inventory.reorder_threshold IS 'Minimum quantity before reordering is triggered';

-- ============================================================================
-- OPERATIONAL TABLES
-- ============================================================================

-- Tables: Restaurant seating
CREATE TABLE IF NOT EXISTS tables (
  id SERIAL PRIMARY KEY, 
  location_id INT NOT NULL REFERENCES location(id), 
  table_number INT NOT NULL, 
  capacity INT NOT NULL, 
  UNIQUE(location_id, table_number)
);

COMMENT ON TABLE tables IS 'Physical dining tables at restaurant locations';
COMMENT ON COLUMN tables.id IS 'Unique identifier for table';
COMMENT ON COLUMN tables.location_id IS 'Foreign key referencing location';
COMMENT ON COLUMN tables.table_number IS 'Table number within location';
COMMENT ON COLUMN tables.capacity IS 'Number of people the table can seat';

-- Shifts: Employee work schedules
CREATE TABLE IF NOT EXISTS shifts (
  id SERIAL PRIMARY KEY, 
  employee_id INT REFERENCES employee(id), 
  location_id INT REFERENCES location(id), 
  shift_start TIMESTAMP NOT NULL, 
  shift_end TIMESTAMP NOT NULL
);

COMMENT ON TABLE shifts IS 'Employee work shifts/schedules';
COMMENT ON COLUMN shifts.id IS 'Unique identifier for shift';
COMMENT ON COLUMN shifts.employee_id IS 'Foreign key referencing employee';
COMMENT ON COLUMN shifts.location_id IS 'Foreign key referencing location';
COMMENT ON COLUMN shifts.shift_start IS 'Start time of work shift';
COMMENT ON COLUMN shifts.shift_end IS 'End time of work shift';

-- ============================================================================
-- ORDER & SALES TABLES
-- ============================================================================

-- Orders: Customer orders
CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY, 
  location_id INT NOT NULL REFERENCES location(id), 
  customer_id INT REFERENCES customers(id), 
  employee_id INT REFERENCES employee(id), 
  table_id INT REFERENCES tables(id), 
  order_time TIMESTAMP NOT NULL DEFAULT NOW(), 
  total_amount NUMERIC(10, 2) NOT NULL, 
  tax_amount NUMERIC(10, 2) NOT NULL DEFAULT 0, 
  tip_amount NUMERIC(10, 2) NOT NULL DEFAULT 0, 
  status TEXT NOT NULL DEFAULT 'open'
);

CREATE INDEX idx_orders_loc_time ON orders(location_id, order_time DESC);

COMMENT ON TABLE orders IS 'Customer orders placed at restaurant';
COMMENT ON COLUMN orders.id IS 'Unique identifier for order';
COMMENT ON COLUMN orders.location_id IS 'Foreign key referencing location where order was placed';
COMMENT ON COLUMN orders.customer_id IS 'Foreign key referencing customer (NULL for walk-ins)';
COMMENT ON COLUMN orders.employee_id IS 'Foreign key referencing employee who took the order';
COMMENT ON COLUMN orders.table_id IS 'Foreign key referencing table where customer is seated';
COMMENT ON COLUMN orders.order_time IS 'Timestamp when order was placed';
COMMENT ON COLUMN orders.total_amount IS 'Total order amount (before tax and tip)';
COMMENT ON COLUMN orders.tax_amount IS 'Tax amount for order';
COMMENT ON COLUMN orders.tip_amount IS 'Tip amount for order';
COMMENT ON COLUMN orders.status IS 'Order status (open, completed, cancelled)';

-- Order Items: Individual items in order
CREATE TABLE IF NOT EXISTS order_items (
  id SERIAL PRIMARY KEY, 
  order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE, 
  menu_item_id INT NOT NULL REFERENCES menu_items(id), 
  quantity INT NOT NULL, 
  unit_price NUMERIC(8, 2) NOT NULL
);

CREATE INDEX ON order_items(order_id);

COMMENT ON TABLE order_items IS 'Individual menu items that make up an order';
COMMENT ON COLUMN order_items.id IS 'Unique identifier for order item';
COMMENT ON COLUMN order_items.order_id IS 'Foreign key referencing orders';
COMMENT ON COLUMN order_items.menu_item_id IS 'Foreign key referencing menu_items';
COMMENT ON COLUMN order_items.quantity IS 'Quantity of this menu item ordered';
COMMENT ON COLUMN order_items.unit_price IS 'Price per unit at time of order';

-- Payments: Payment transactions
CREATE TABLE IF NOT EXISTS payments (
  id SERIAL PRIMARY KEY, 
  order_id INT UNIQUE REFERENCES orders(id) ON DELETE CASCADE, 
  payment_time TIMESTAMP NOT NULL DEFAULT NOW(), 
  amount NUMERIC(10, 2) NOT NULL, 
  method TEXT NOT NULL, 
  status TEXT NOT NULL DEFAULT 'paid'
);

COMMENT ON TABLE payments IS 'Payment records for orders';
COMMENT ON COLUMN payments.id IS 'Unique identifier for payment';
COMMENT ON COLUMN payments.order_id IS 'Foreign key referencing orders (one payment per order)';
COMMENT ON COLUMN payments.payment_time IS 'Timestamp when payment was processed';
COMMENT ON COLUMN payments.amount IS 'Payment amount (total + tax + tip)';
COMMENT ON COLUMN payments.method IS 'Payment method (cash, credit_card, debit_card, etc.)';
COMMENT ON COLUMN payments.status IS 'Payment status (paid, pending, failed, refunded)';

-- ============================================================================
-- DISCOUNT & PROMOTION TABLES
-- ============================================================================

-- Discounts: Promotional codes and discounts
CREATE TABLE IF NOT EXISTS discounts (
  id SERIAL PRIMARY KEY, 
  code TEXT UNIQUE, 
  description TEXT, 
  type TEXT NOT NULL, 
  amount NUMERIC(8, 2) NOT NULL, 
  start_date DATE, 
  end_date DATE
);

COMMENT ON TABLE discounts IS 'Discount codes and promotional offers';
COMMENT ON COLUMN discounts.id IS 'Unique identifier for discount';
COMMENT ON COLUMN discounts.code IS 'Discount code (unique)';
COMMENT ON COLUMN discounts.description IS 'Description of the discount/promotion';
COMMENT ON COLUMN discounts.type IS 'Discount type (percent for percentage, fixed for dollar amount)';
COMMENT ON COLUMN discounts.amount IS 'Discount amount (percentage value or dollar amount)';
COMMENT ON COLUMN discounts.start_date IS 'Start date when discount becomes valid';
COMMENT ON COLUMN discounts.end_date IS 'End date when discount expires';

-- Order Discounts: Discounts applied to orders
CREATE TABLE IF NOT EXISTS order_discounts (
  order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE, 
  discount_id INT REFERENCES discounts(id), 
  PRIMARY KEY(order_id, discount_id)
);

COMMENT ON TABLE order_discounts IS 'Links discounts applied to specific orders';
COMMENT ON COLUMN order_discounts.order_id IS 'Foreign key referencing orders';
COMMENT ON COLUMN order_discounts.discount_id IS 'Foreign key referencing discounts';

-- ============================================================================
-- LOYALTY & RESERVATION TABLES
-- ============================================================================

-- Loyalty Accounts: Customer reward programs
CREATE TABLE IF NOT EXISTS loyalty_accounts (
  id SERIAL PRIMARY KEY, 
  customer_id INT REFERENCES customers(id), 
  points_balance INT NOT NULL DEFAULT 0
);

COMMENT ON TABLE loyalty_accounts IS 'Customer loyalty/rewards program accounts';
COMMENT ON COLUMN loyalty_accounts.id IS 'Unique identifier for loyalty account';
COMMENT ON COLUMN loyalty_accounts.customer_id IS 'Foreign key referencing customers';
COMMENT ON COLUMN loyalty_accounts.points_balance IS 'Current loyalty points balance';

-- Loyalty Transactions: Points earned and redeemed
CREATE TABLE IF NOT EXISTS loyalty_txn (
  id SERIAL PRIMARY KEY, 
  loyalty_id INT REFERENCES loyalty_accounts(id), 
  points_change INT NOT NULL, 
  txn_type TEXT, 
  txn_time TIMESTAMP NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE loyalty_txn IS 'Transaction history for loyalty points (earned/redeemed)';
COMMENT ON COLUMN loyalty_txn.id IS 'Unique identifier for loyalty transaction';
COMMENT ON COLUMN loyalty_txn.loyalty_id IS 'Foreign key referencing loyalty_accounts';
COMMENT ON COLUMN loyalty_txn.points_change IS 'Number of points earned (positive) or redeemed (negative)';
COMMENT ON COLUMN loyalty_txn.txn_type IS 'Transaction type (earn or redeem)';
COMMENT ON COLUMN loyalty_txn.txn_time IS 'Timestamp when transaction occurred';

-- Reservations: Table bookings
CREATE TABLE IF NOT EXISTS reservations (
  id SERIAL PRIMARY KEY, 
  table_id INT REFERENCES tables(id), 
  customer_id INT REFERENCES customers(id), 
  start_time TIMESTAMP NOT NULL, 
  end_time TIMESTAMP NOT NULL, 
  status TEXT NOT NULL DEFAULT 'booked'
);

COMMENT ON TABLE reservations IS 'Table reservations/bookings by customers';
COMMENT ON COLUMN reservations.id IS 'Unique identifier for reservation';
COMMENT ON COLUMN reservations.table_id IS 'Foreign key referencing tables';
COMMENT ON COLUMN reservations.customer_id IS 'Foreign key referencing customers';
COMMENT ON COLUMN reservations.start_time IS 'Reservation start time';
COMMENT ON COLUMN reservations.end_time IS 'Reservation end time';
COMMENT ON COLUMN reservations.status IS 'Reservation status (booked, checked_in, no_show, cancelled)';