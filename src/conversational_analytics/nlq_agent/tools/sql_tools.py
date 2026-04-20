import logging
import re
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage
from conversational_analytics.config import get_settings
from conversational_analytics.db.schema_documenter import get_table_descriptions
from conversational_analytics.db.row_access import create_row_filter_views
from conversational_analytics.llm import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are an expert SQL analyst for a restaurant management system.
You have access to a PostgreSQL database with ONLY the following tables: {tables}

Rules:
- ONLY query the tables listed above. Do NOT attempt to access any other tables.
- Use sql_db_list_tables to confirm available tables, then sql_db_schema before writing queries
- Write efficient, read-only SELECT queries only
- Never modify data (no INSERT, UPDATE, DELETE, DROP)
- If the data needed to answer the question is not available in the listed tables or columns, say so clearly and stop — do NOT retry or look elsewhere
- Format numeric results clearly (currency with 2 decimal places)
"""

# Role context holds everything needed per role
_role_cache: dict[str, dict] = {}  # {role: {db, tools, system_message}}
_default_context: dict = {}         # used when no role is specified


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


def _build_custom_table_info(visible_tables: list[str], restrict_map: dict[str, list[str]]) -> dict[str, str] | None:
    """Builds custom_table_info from live DB only when column restrictions are set."""
    if not restrict_map:
        return None
    descriptions = get_table_descriptions(visible_tables)
    if not descriptions:
        return None
    return _apply_column_restrictions(descriptions, restrict_map)


def _build_context(include_tables: list[str] | None, ignore_tables: list[str] | None,
                   restrict_map: dict[str, list[str]], row_filters: dict[str, str] | None = None) -> dict:
    """Builds and returns a context dict {db, tools, system_message} for a given table filter."""
    cfg = get_settings()

    base_db = SQLDatabase.from_uri(cfg.db_uri)
    all_tables = list(base_db.get_usable_table_names())

    # resolve visible tables
    if include_tables:
        visible_tables = [t for t in all_tables if t in include_tables]
    elif ignore_tables:
        visible_tables = [t for t in all_tables if t not in ignore_tables]
    else:
        visible_tables = all_tables

    # apply row-level filters — create views and swap table names with view names
    if row_filters:
        role_name = "role"  # placeholder, overridden in _init
        view_map = create_row_filter_views(role_name, row_filters)
        # replace filtered tables with their views in visible_tables
        visible_tables = [view_map.get(t, t) for t in visible_tables]
        include_tables = visible_tables  # point DB to views

    # enable view_support if any views are in visible_tables
    view_support = cfg.db_view_support or bool(row_filters)

    # build DB with role-specific restrict map
    custom_table_info = _build_custom_table_info(visible_tables, restrict_map)
    db_kwargs = {
        "include_tables": include_tables or None,
        "ignore_tables": ignore_tables or None,
        "sample_rows_in_table_info": cfg.db_sample_rows_in_table_info,
        "view_support": view_support,
    }
    if custom_table_info:
        db_kwargs["custom_table_info"] = custom_table_info

    db = SQLDatabase.from_uri(cfg.db_uri, **db_kwargs)
    tools = SQLDatabaseToolkit(db=db, llm=get_llm()).get_tools()
    system_message = SystemMessage(
        content=SYSTEM_PROMPT_TEMPLATE.format(tables=", ".join(sorted(visible_tables)))
    )
    return {"db": db, "tools": tools, "system_message": system_message}


def _init():
    """Runs once at startup — builds context for each role and the default context."""
    cfg = get_settings()

    # build default context using global DB_RESTRICT_COLUMNS, no row filters
    global _default_context
    _default_context = _build_context(
        include_tables=cfg.db_include_tables_list or None,
        ignore_tables=cfg.db_ignore_tables_list or None,
        restrict_map=cfg.db_restrict_columns_map,
        row_filters=None,
    )
    logger.info("Default SQL context initialised")

    # build one context per role
    for role, tables in cfg.role_tables_map.items():
        restrict_map = cfg.get_restrict_columns_for_role(role)
        row_filters = cfg.get_row_filters_for_role(role) or None

        # patch _build_context to use correct role name for view creation
        if row_filters:
            view_map = create_row_filter_views(role, row_filters)
            # replace filtered tables with view names in include list
            resolved = [view_map.get(t, t) for t in tables]
            _role_cache[role] = _build_context(
                include_tables=resolved,
                ignore_tables=None,
                restrict_map=restrict_map,
                row_filters=None,  # views already created, no need to recreate
            )
        else:
            _role_cache[role] = _build_context(
                include_tables=tables,
                ignore_tables=None,
                restrict_map=restrict_map,
                row_filters=None,
            )
        logger.info(
            f"Role '{role}' initialised — tables: {', '.join(sorted(tables))}"
            + (f", row filters: {row_filters}" if row_filters else "")
            + (f", restricted columns: {restrict_map}" if restrict_map else "")
        )


# ── initialise everything at module load ─────────────────────────────
_init()


def _get_context(role: str | None) -> dict:
    """Returns the cached context for the given role, or default if role is None/unknown."""
    if role:
        role = role.lower()
        if role not in _role_cache:
            raise ValueError(f"Unknown role '{role}'. Defined roles: {list(_role_cache.keys())}")
        return _role_cache[role]
    return _default_context


def get_db(role: str | None = None) -> SQLDatabase:
    return _get_context(role)["db"]


def get_sql_tools(role: str | None = None) -> list:
    return _get_context(role)["tools"]


def get_system_message(role: str | None = None) -> SystemMessage:
    return _get_context(role)["system_message"]
