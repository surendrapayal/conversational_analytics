import logging
import re
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage
from conversational_analytics.config import get_settings
from conversational_analytics.db.schema_documenter import get_table_descriptions
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


def _resolve_visible_tables(cfg, all_db_tables: list[str]) -> list[str]:
    """Applies include/ignore hierarchy to determine visible tables.

    Hierarchy:
      1. include_tables set → only those tables (whitelist)
      2. ignore_tables set  → all tables except those (blacklist)
      3. neither set        → all tables
    """
    include = cfg.db_include_tables_list
    ignore = cfg.db_ignore_tables_list

    if include:
        visible = [t for t in all_db_tables if t in include]
        logger.info(f"include_tables active: {visible}")
        return visible

    if ignore:
        visible = [t for t in all_db_tables if t not in ignore]
        logger.info(f"ignore_tables active, excluded: {ignore}")
        return visible

    return all_db_tables


def _apply_column_restrictions(descriptions: dict[str, str], restrict_map: dict[str, list[str]]) -> dict[str, str]:
    """Strips restricted columns from table descriptions so the LLM never sees them."""
    for table, restricted_cols in restrict_map.items():
        if table not in descriptions:
            continue
        desc = descriptions[table]
        for col in restricted_cols:
            desc = re.sub(rf",?\s*{re.escape(col)}\s*\([^)]*\)\s*-[^,\n]*", "", desc)
        descriptions[table] = desc.strip()
        logger.info(f"Restricted columns {restricted_cols} from table '{table}'")
    return descriptions


def _build_custom_table_info(visible_tables: list[str]) -> dict[str, str] | None:
    """Reads live DB schema and builds custom_table_info only when column restrictions are set."""
    cfg = get_settings()
    restrict_map = cfg.db_restrict_columns_map

    if not restrict_map:
        return None

    # fetch NLQ-friendly descriptions from live DB for visible tables only
    descriptions = get_table_descriptions(visible_tables)
    if not descriptions:
        return None

    descriptions = _apply_column_restrictions(descriptions, restrict_map)
    logger.info(f"Built custom_table_info for {len(descriptions)} tables")
    return descriptions


def get_db() -> SQLDatabase:
    cfg = get_settings()
    include = cfg.db_include_tables_list or None
    ignore = cfg.db_ignore_tables_list or None

    # build a temporary DB connection to get all table names for hierarchy resolution
    temp_db = SQLDatabase.from_uri(cfg.db_uri)
    all_tables = temp_db.get_usable_table_names()

    visible_tables = _resolve_visible_tables(cfg, list(all_tables))
    custom_table_info = _build_custom_table_info(visible_tables)

    db_kwargs = {
        "ignore_tables": ignore,
        "include_tables": include,
        "sample_rows_in_table_info": cfg.db_sample_rows_in_table_info,
        "view_support": cfg.db_view_support,
    }
    if custom_table_info:
        db_kwargs["custom_table_info"] = custom_table_info

    return SQLDatabase.from_uri(cfg.db_uri, **db_kwargs)


def get_sql_tools() -> list:
    """Returns SQL toolkit tools bound to the database."""
    toolkit = SQLDatabaseToolkit(db=get_db(), llm=get_llm())
    return toolkit.get_tools()


def get_system_message() -> SystemMessage:
    return SystemMessage(content=SYSTEM_PROMPT)
