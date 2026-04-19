import logging
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage
from conversational_analytics.config import get_settings
from conversational_analytics.llm import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert SQL analyst for a restaurant management system.
You have access to a PostgreSQL database with the following tables:
customers, orders, order_items, menu_items, menu_categories, payments,
reservations, employee, shifts, inventory, ingredients, loyalty_accounts,
loyalty_txn, discounts, order_discounts, location, tables, roles,
recipe_items, supplier, supplier_items.

Rules:
- Always use sql_db_list_tables and sql_db_schema before writing queries
- Write efficient, read-only SELECT queries only
- Never modify data (no INSERT, UPDATE, DELETE, DROP)
- If unsure, ask for clarification
- Format numeric results clearly (currency with 2 decimal places)
"""


def get_db() -> SQLDatabase:
    return SQLDatabase.from_uri(get_settings().db_uri)


def get_sql_tools() -> list:
    """Returns SQL toolkit tools bound to the database."""
    toolkit = SQLDatabaseToolkit(db=get_db(), llm=get_llm())
    return toolkit.get_tools()


def get_system_message() -> SystemMessage:
    return SystemMessage(content=SYSTEM_PROMPT)
