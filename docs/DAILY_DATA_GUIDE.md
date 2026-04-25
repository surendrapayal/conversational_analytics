# Daily Test Data Generation Guide

## 📊 Database Tables by Update Frequency

### 🔵 MASTER DATA (Setup Once)
These tables are created once and remain relatively static:

| Table | Purpose | Records |
|-------|---------|---------|
| `location` | Restaurant branches/locations | 8 |
| `roles` | Employee job titles | 7 |
| `employee` | Staff members | 50 |
| `customers` | Customer profiles | 150 |
| `menu_categories` | Food categories | 6 |
| `menu_items` | Dishes available | 60 |
| `ingredients` | Raw materials | 40 |
| `supplier` | Food vendors | 5 |
| `tables` | Dining tables at locations | 135 |
| `recipe_items` | Ingredient requirements per dish | 220 |
| `supplier_items` | Pricing from vendors | 105 |
| `loyalty_accounts` | Customer rewards accounts | 105 |

**Setup Command:**
```bash
python src/conversational_analytics/db/test_data_generator.py
```

---

### 🟢 DAILY OPERATIONAL DATA (Updated Daily)
These tables receive new data each day:

| Table | Records/Day | Purpose |
|-------|-------------|---------|
| **orders** | ~50 | Customer orders placed |
| **order_items** | ~150 | Items within orders |
| **payments** | ~28 | Payment transactions |
| **order_discounts** | ~24 | Discounts applied to orders |
| **loyalty_txn** | ~384 | Loyalty points earned/redeemed |
| **shifts** | ~201 | Employee work schedules |
| **reservations** | ~15 | Table bookings |

**Daily Generation Command:**
```bash
python src/conversational_analytics/db/test_data_generator.py daily
```

---

## 📅 Daily Data Generation Details

### Expected Output per Day (Default: 50 orders)

```
✓ Loaded 8 IDs from location
✓ Loaded 50 IDs from employee
✓ Loaded 150 IDs from customers
✓ Loaded 60 IDs from menu_items
✓ Generated 201 shifts
✓ Generated 50 orders
✓ Generated 150 order items
✓ Generated 3 discounts
✓ Generated 24 order discounts
✓ Generated 28 payments
✓ Generated 384 loyalty transactions
✓ Generated 15 reservations

💾 Saved to: sql_data/daily_YYYYMMDD/
```

### SQL Files Generated

**Combined file:** `daily_inserts_YYYYMMDD.sql`
- All daily inserts in chronological order
- Ready for batch import

**Individual files:**
- `orders_inserts_YYYYMMDD.sql` (50 records)
- `order_items_inserts_YYYYMMDD.sql` (150 records)
- `payments_inserts_YYYYMMDD.sql` (28 records)
- `order_discounts_inserts_YYYYMMDD.sql` (24 records)
- `loyalty_txn_inserts_YYYYMMDD.sql` (384 records)
- `shifts_inserts_YYYYMMDD.sql` (201 records)
- `reservations_inserts_YYYYMMDD.sql` (15 records)
- `discounts_inserts_YYYYMMDD.sql` (3 records)

---

## 🔧 Usage Scenarios

### Scenario 1: Initial Setup
```bash
# Generate master data once
python src/conversational_analytics/db/test_data_generator.py

# Expected: ~3,728 records across all tables
```

### Scenario 2: Daily Data Ingestion
```bash
# Run daily to simulate restaurant operations
python src/conversational_analytics/db/test_data_generator.py daily

# Expected: ~1,055 records per day
# Files saved: sql_data/daily_20260419/
```

### Scenario 3: Weekly Batch Load
```bash
# Run 7 times (once per day for a week)
for i in {1..7}; do
    python src/conversational_analytics/db/test_data_generator.py daily
    sleep 3600  # Wait 1 hour between runs
done
```

---

## 📈 Data Growth Over Time

| Period | Master Data | Daily Data | Total Records |
|--------|-------------|-----------|----------------|
| Initial Setup | 3,728 | - | 3,728 |
| After 1 day | 3,728 | 1,055 | 4,783 |
| After 7 days | 3,728 | 7,385 | 11,113 |
| After 30 days | 3,728 | 31,650 | 35,378 |
| After 90 days | 3,728 | 94,950 | 98,678 |

---

## 🔗 Data Relationships for Daily Data

```
Daily data relationships:
├── Orders (50/day)
│   ├── Order Items (3-5 items per order)
│   ├── Payments (80% completion rate)
│   ├── Order Discounts (35% discount rate)
│   └── Loyalty Transactions (linked to customers)
├── Shifts (multiple per employee)
└── Reservations (15/day)
```

---

## ✅ Verification Queries

```sql
-- Check today's orders
SELECT COUNT(*) as today_orders FROM orders WHERE DATE(order_time) = CURRENT_DATE;

-- Check total daily records for this run
SELECT COUNT(*) FROM (
    SELECT COUNT(*) FROM orders
    UNION ALL
    SELECT COUNT(*) FROM order_items
    UNION ALL
    SELECT COUNT(*) FROM payments
    UNION ALL
    SELECT COUNT(*) FROM loyalty_txn
) daily_counts;

-- Check order distribution across locations
SELECT l.name, COUNT(o.id) as order_count 
FROM orders o 
JOIN location l ON o.location_id = l.id 
WHERE DATE(o.order_time) = CURRENT_DATE
GROUP BY l.name
ORDER BY order_count DESC;
```

---

## 📝 Notes

- **Master data** (locations, employees, menu items) setup once via `python test_data_generator.py`
- **Daily data** (orders, payments, loyalty) generated via `python test_data_generator.py daily`
- All SQL files are saved for backup and replay
- Each daily run generates realistic data with proper FK relationships
- Unique constraints are handled automatically (no duplicate key violations)
- Use `sql_data/daily_YYYYMMDD/daily_inserts_YYYYMMDD.sql` for batch replay
