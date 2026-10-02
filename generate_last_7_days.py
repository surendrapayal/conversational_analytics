"""
Generate daily SQL data for 2026-05-19 to 2026-05-25.
Subclasses TestDataGenerator to save files into the correct dated folder.
"""
import os
import sys
from datetime import date, timedelta, datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dotenv import load_dotenv
load_dotenv()

from conversational_analytics.db.test_data_generator import TestDataGenerator


class DatedGenerator(TestDataGenerator):
    def __init__(self, target_date: date, **kwargs):
        super().__init__(**kwargs)
        self._target_date = target_date

    def generate_daily_data(self, orders_count: int = 50):
        print(f"Loading master data IDs...")
        self.load_existing_ids()

        required = ["location", "employee", "customers", "menu_items", "tables", "orders"]
        missing = [t for t in required if t not in self.generated_ids or not self.generated_ids[t]]
        if missing:
            print(f"ERROR: Missing master data: {missing}")
            return

        self.sql_queries = {}
        self.generate_shifts()
        self.generate_orders(orders_count)
        self.generate_order_items()
        self.generate_discounts(3)
        self.generate_order_discounts()
        self.generate_payments()
        self.generate_loyalty_txn()
        self.generate_reservations(15)

        daily_suffix = self._target_date.strftime("%Y%m%d")
        daily_output_dir = os.path.join(self.sql_output_dir, f"daily_{daily_suffix}")
        Path(daily_output_dir).mkdir(exist_ok=True)

        ts = datetime(self._target_date.year, self._target_date.month,
                      self._target_date.day, 10, 0, 0).isoformat()

        combined_file = os.path.join(daily_output_dir, f"daily_inserts_{daily_suffix}.sql")
        with open(combined_file, "w") as f:
            f.write(f"-- Daily Test Data Insert ({ts})\n")
            f.write("-- These tables receive data daily:\n")
            f.write("-- orders, order_items, payments, order_discounts, loyalty_txn, shifts, reservations, inventory\n\n")
            f.write("SET session_replication_role = 'replica';\n\n")
            for table_name in sorted(self.sql_queries.keys()):
                f.write(f"-- {table_name.upper()}\n")
                for query in self.sql_queries[table_name]:
                    f.write(query + ";\n")
                f.write("\n")
            f.write("SET session_replication_role = 'origin';\n")
        print(f"  Saved combined: {combined_file}")

        for table_name, queries in sorted(self.sql_queries.items()):
            file_path = os.path.join(daily_output_dir, f"{table_name}_inserts_{daily_suffix}.sql")
            with open(file_path, "w") as f:
                f.write(f"-- Daily inserts into {table_name} ({ts})\n\n")
                for query in queries:
                    f.write(query + ";\n")
            print(f"  {table_name}: {len(queries)} rows")


START_DATE = date(2026, 5, 19)
DAYS = 7

for i in range(DAYS):
    target_date = START_DATE + timedelta(days=i)
    date_str = target_date.strftime("%Y%m%d")
    print(f"\n{'='*60}")
    print(f"Generating data for {date_str}")
    print(f"{'='*60}")

    generator = DatedGenerator(
        target_date=target_date,
        db_host=os.getenv("ANALYTICS_DB_HOST", "localhost"),
        db_port=int(os.getenv("ANALYTICS_DB_PORT", "5433")),
        db_name=os.getenv("ANALYTICS_DB_NAME", "zenvyra"),
        db_user="admin_user",
        db_password="admin_password",
        sql_output_dir="sql_data",
    )
    generator.generate_daily_data(orders_count=50)
    generator.close()

print("\nAll 7 days generated.")
