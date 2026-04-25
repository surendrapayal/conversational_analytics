import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import json
from typing import Dict, List, Any

load_dotenv()

class SchemaDocumenter:
    """Extracts and documents PostgreSQL schema for NLQ agents"""
    
    def __init__(self, db_host: str, db_name: str, db_user: str, db_password: str, db_port: int = 5432):
        self.connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        self.cursor = self.connection.cursor()
    
    def get_all_tables(self) -> List[str]:
        """Get all table names from current database"""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
        """
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_table_description(self, table_name: str) -> str:
        """Get table description/comment"""
        desc_query = """
        SELECT description
        FROM pg_description
        WHERE objoid = (
            SELECT oid FROM pg_class 
            WHERE relname = %s 
            AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
        )
        AND objsubid = 0
        """
        self.cursor.execute(desc_query, (table_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_column_description(self, table_name: str, column_name: str) -> str:
        """Get column description/comment"""
        desc_query = """
        SELECT description
        FROM pg_description
        WHERE objoid = (
            SELECT oid FROM pg_class 
            WHERE relname = %s 
            AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
        )
        AND objsubid = (
            SELECT attnum FROM pg_attribute 
            WHERE attrelid = (
                SELECT oid FROM pg_class 
                WHERE relname = %s 
                AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            ) 
            AND attname = %s
        )
        """
        self.cursor.execute(desc_query, (table_name, table_name, column_name))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed info about a specific table"""
        # Get columns and their details
        column_query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
        """
        self.cursor.execute(column_query, (table_name,))
        columns = self.cursor.fetchall()
        
        # Get primary keys using information_schema
        pk_query = """
        SELECT kcu.column_name
        FROM information_schema.key_column_usage kcu
        JOIN information_schema.table_constraints tc
          ON kcu.constraint_name = tc.constraint_name
        WHERE kcu.table_name = %s
        AND tc.constraint_type = 'PRIMARY KEY'
        """
        self.cursor.execute(pk_query, (table_name,))
        primary_keys = [row[0] for row in self.cursor.fetchall()]
        
        # Get foreign keys
        fk_query = """
        SELECT
            kcu.column_name,
            ccu.table_name AS referenced_table,
            ccu.column_name AS referenced_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s
        """
        self.cursor.execute(fk_query, (table_name,))
        foreign_keys = self.cursor.fetchall()
        
        # Get table description
        table_desc = self.get_table_description(table_name)
        
        return {
            "table_name": table_name,
            "description": table_desc,
            "columns": [
                {
                    "name": col[0],
                    "type": col[1],
                    "nullable": col[2],
                    "default": col[3],
                    "is_primary_key": col[0] in primary_keys,
                    "description": self.get_column_description(table_name, col[0])
                }
                for col in columns
            ],
            "foreign_keys": [
                {
                    "column": fk[0],
                    "column_description": self.get_column_description(table_name, fk[0]),
                    "references_table": fk[1],
                    "references_table_description": self.get_table_description(fk[1]),
                    "references_column": fk[2],
                    "references_column_description": self.get_column_description(fk[1], fk[2])
                }
                for fk in foreign_keys
            ]
        }
    
    def generate_schema_documentation(self) -> Dict[str, Any]:
        """Generate complete schema documentation"""
        tables = self.get_all_tables()
        schema_doc = {
            "database": self.connection.get_dsn_parameters()['dbname'],
            "tables": []
        }
        
        for table in tables:
            table_info = self.get_table_info(table)
            schema_doc["tables"].append(table_info)
        
        return schema_doc
    
    def generate_natural_language_descriptions(self) -> Dict[str, str]:
        """Generate NLQ-friendly descriptions"""
        tables = self.get_all_tables()
        descriptions = {}
        
        for table in tables:
            info = self.get_table_info(table)
            
            # Build table description
            table_desc = info.get("description", "No description available")
            
            # Build column descriptions
            columns_desc = ", ".join([
                f"{col['name']} ({col['type']}) - {col.get('description', 'No description')}"
                for col in info['columns']
            ])
            
            # Build FK descriptions
            fk_desc = ""
            if info['foreign_keys']:
                fk_desc = ". Foreign keys: " + ", ".join([
                    f"{fk['column']} references {fk['references_table']}.{fk['references_column']}"
                    for fk in info['foreign_keys']
                ])
            
            descriptions[table] = f"Table: {table_desc}\nColumns: {columns_desc}{fk_desc}"
        
        return descriptions
    
    def save_to_json(self, output_file: str):
        """Save schema documentation to JSON"""
        schema_doc = self.generate_schema_documentation()
        with open(output_file, 'w') as f:
            json.dump(schema_doc, f, indent=2)
        print(f"Schema documentation saved to {output_file}")
    
    def save_nlq_descriptions(self, output_file: str):
        """Save NLQ descriptions to JSON"""
        descriptions = self.generate_natural_language_descriptions()
        with open(output_file, 'w') as f:
            json.dump(descriptions, f, indent=2)
        print(f"NLQ descriptions saved to {output_file}")
    
    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.connection.close()


def get_table_descriptions(visible_tables: list[str] | None = None) -> dict[str, str]:
    """Reads live DB schema and returns NLQ-friendly descriptions per table.

    Args:
        visible_tables: if provided, only return descriptions for these tables.
    """
    from conversational_analytics.config import get_settings
    cfg = get_settings()
    documenter = SchemaDocumenter(
        db_host=cfg.analytics_db_host,
        db_port=cfg.analytics_db_port,
        db_name=cfg.analytics_db_name,
        db_user=cfg.analytics_db_user,
        db_password=cfg.analytics_db_password,
    )
    try:
        all_descriptions = documenter.generate_natural_language_descriptions()
        if visible_tables is not None:
            return {t: d for t, d in all_descriptions.items() if t in visible_tables}
        return all_descriptions
    finally:
        documenter.close()


# Usage example
if __name__ == "__main__":
    documenter = SchemaDocumenter(
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5433")),
        db_name=os.getenv("DB_NAME", "zenvyra"),
        db_user=os.getenv("DB_USER", "admin_user"),
        db_password=os.getenv("DB_PASSWORD", "admin_password")
    )
    
    # Generate and save documentation
    documenter.save_to_json("schema_documentation.json")
    documenter.save_nlq_descriptions("nlq_descriptions.json")
    
    # Print to console
    docs = documenter.generate_natural_language_descriptions()
    for table, description in docs.items():
        print(f"\n{description}")
    
    documenter.close()