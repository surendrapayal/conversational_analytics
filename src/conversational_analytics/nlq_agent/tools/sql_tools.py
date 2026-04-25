import logging
import re
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage
from conversational_analytics.config import get_settings
from conversational_analytics.db.schema_documenter import get_table_descriptions
from conversational_analytics.semantic import build_system_prompt_suffix
from conversational_analytics.llm import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are an expert SQL analyst for a restaurant management system.
You have access to a PostgreSQL database with ONLY the following tables: {tables}

Rules:
- ONLY query the tables listed above. Do NOT attempt to access any other tables.
- Use sql_db_list_tables to confirm available tables, then sql_db_schema before writing queries
- Write efficient, read-only SELECT queries only
- Never modify data (no INSERT, UPDATE, DELETE, DROP)
- If the data needed to answer the question is not available in the listed tables or columns, say so clearly and stop - do NOT retry or look elsewhere
- Always provide a complete, well-formatted text response with tables, observations and insights
- Format numeric results clearly (currency with 2 decimal places)

VISUALIZATION (append after your complete text response):

Generate a Vega-Lite chart ONLY when results contain 2+ rows with at least one numeric column.
Return the spec as JSON inside a markdown code block tagged 'vega'.
Return the spec object directly - do NOT wrap it in a 'vega_spec' key.
Do NOT generate a chart for single scalar values (e.g. a single total count).

REQUIRED FIELDS (always include):
- "$schema": "https://vega.github.io/schema/vega-lite/v5.json"
- "width": 700
- "height": 400
- "title": descriptive title derived from the user query
- "config": {{"view": {{"stroke": "transparent"}}}}

FORMATTING RULES:
- Currency y-axis: use "axis": {{"format": "$,.2f"}} inside the y encoding - NOT "format" at top level of y
- Tooltip format "$,.2f" is correct inside tooltip field definitions
- Always include tooltips showing exact values on hover
- Always sort bar charts descending for ranking queries (Top N) using "sort": "-y" on x-axis
- Use "point": true on line marks to show data points

CHART TYPE SELECTION - choose based on data shape and query intent:

1.  BAR (mark: "bar")
    When: ranking or comparing categories, Top N queries
    Example: top menu items, revenue by location, orders by employee

2.  HORIZONTAL BAR (mark: "bar" with x/y swapped)
    When: 6+ categories or long category names
    Example: ingredient costs, employee performance with long names

3.  LINE (mark: {{"type": "line", "point": true}})
    When: trends over time with a date/timestamp dimension
    Example: daily revenue, monthly orders, weekly customer count

4.  AREA (mark: {{"type": "area", "opacity": 0.7}})
    When: cumulative volume over time or stacked trends
    Example: running total revenue, inventory levels over time

5.  STACKED BAR (mark: "bar" + color encoding on second dimension)
    When: comparing categories broken down by a second dimension
    Example: revenue by location AND category, orders by status per month

6.  GROUPED BAR (mark: "bar" + "xOffset" encoding for dodge)
    When: side-by-side comparison of sub-categories
    Example: revenue vs target by location

7.  PIE / DONUT (mark: {{"type": "arc", "innerRadius": 50}})
    When: part-to-whole with 2-8 categories
    Example: payment method split, order status distribution

8.  SCATTER PLOT (mark: "point")
    When: correlation between two numeric metrics
    Example: price vs quantity sold, tenure vs sales volume

9.  HEATMAP (mark: "rect" + color encoding)
    When: two categorical dimensions with a numeric value
    Example: revenue by location x day of week, orders by hour x day

10. HISTOGRAM (mark: "bar" + bin: true on x field)
    When: distribution of a single numeric field
    Example: order value distribution, tip amount frequency

11. BOX PLOT (mark: "boxplot")
    When: statistical spread and outliers across groups
    Example: order values by location, tip amounts by day of week

12. MULTI-LINE (mark: "line" + color encoding by category)
    When: multiple time series on the same chart
    Example: revenue per location over time, orders by category per month

13. LAYERED (layer: [...])
    When: combining bar + line on the same chart
    Example: monthly revenue bars with trend line overlay

DECISION GUIDE:
- 1 category + 1 number                    → BAR
- 1 category + 1 number (6+ or long names) → HORIZONTAL BAR
- 1 date + 1 number                        → LINE
- 1 date + 1 number (cumulative)           → AREA
- 2 categories + 1 number                  → STACKED BAR or HEATMAP
- 1 category + 2 numbers (comparison)      → GROUPED BAR
- 1 category + 2 numbers (correlation)     → SCATTER
- 1 category (2-8 values, part-of-whole)   → PIE/DONUT
- 1 number (distribution)                  → HISTOGRAM
- 1 category + 1 number (spread/outliers)  → BOX PLOT
- 1 date + multiple numeric series         → MULTI-LINE
- bar + trend overlay                      → LAYERED
{semantic_section}"""

_role_cache: dict[str, dict] = {}
_default_context: dict = {}


def _apply_column_restrictions(descriptions: dict[str, str], restrict_map: dict[str, list[str]]) -> dict[str, str]:
    """Strips restricted columns from table descriptions so the LLM never sees them."""
    for table, restricted_cols in restrict_map.items():
        if table not in descriptions:
            logger.debug(f"Table '{table}' not found in descriptions — skipping column restriction")
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
        logger.debug("No column restrictions configured — skipping custom_table_info")
        return None
    logger.debug(f"Building custom_table_info for {len(visible_tables)} tables with restrictions: {restrict_map}")
    descriptions = get_table_descriptions(visible_tables)
    if not descriptions:
        logger.warning("Could not retrieve table descriptions from DB — custom_table_info will be empty")
        return None
    result = _apply_column_restrictions(descriptions, restrict_map)
    logger.info(f"Built custom_table_info for {len(result)} tables")
    return result


def _build_system_message(visible_tables: list[str], role: str | None) -> SystemMessage:
    """Builds system message with semantic layer injected if available."""
    logger.debug(f"Building system message for role={role}, tables={len(visible_tables)}")
    semantic_suffix = build_system_prompt_suffix(role, visible_tables)
    semantic_section = f"\n\n{semantic_suffix}" if semantic_suffix else ""
    if semantic_suffix:
        logger.debug(f"Semantic layer injected into system prompt ({len(semantic_suffix)} chars)")
    content = SYSTEM_PROMPT_TEMPLATE.format(
        tables=", ".join(sorted(visible_tables)),
        semantic_section=semantic_section,
    )
    return SystemMessage(content=content)


def _build_context(include_tables: list[str] | None, ignore_tables: list[str] | None,
                   restrict_map: dict[str, list[str]], role: str | None = None) -> dict:
    """Builds and returns a context dict {db, tools, system_message} for a given table filter."""
    cfg = get_settings()
    logger.debug(f"Building context for role={role}, include={include_tables}, ignore={ignore_tables}")

    base_db = SQLDatabase.from_uri(cfg.db_uri)
    all_tables = list(base_db.get_usable_table_names())
    logger.debug(f"Found {len(all_tables)} tables in database")

    if include_tables:
        visible_tables = [t for t in all_tables if t in include_tables]
        logger.debug(f"include_tables filter applied: {len(visible_tables)} visible tables")
    elif ignore_tables:
        visible_tables = [t for t in all_tables if t not in ignore_tables]
        logger.debug(f"ignore_tables filter applied: excluded {len(ignore_tables)}, {len(visible_tables)} visible tables")
    else:
        visible_tables = all_tables
        logger.debug(f"No table filter — all {len(visible_tables)} tables visible")

    custom_table_info = _build_custom_table_info(visible_tables, restrict_map)
    db_kwargs = {
        "include_tables": include_tables or None,
        "ignore_tables": ignore_tables or None,
        "sample_rows_in_table_info": cfg.db_sample_rows_in_table_info,
        "view_support": cfg.db_view_support,
    }
    if custom_table_info:
        db_kwargs["custom_table_info"] = custom_table_info

    logger.debug(f"Creating SQLDatabase with kwargs: include={include_tables}, ignore={ignore_tables}, view_support={cfg.db_view_support}")
    db = SQLDatabase.from_uri(cfg.db_uri, **db_kwargs)
    tools = SQLDatabaseToolkit(db=db, llm=get_llm()).get_tools()
    logger.debug(f"SQL toolkit created with {len(tools)} tools")
    system_message = _build_system_message(visible_tables, role)

    return {"db": db, "tools": tools, "system_message": system_message}


def _init():
    """Runs once at startup - builds context for each role and the default context."""
    cfg = get_settings()
    logger.info("Initialising SQL contexts at startup...")

    global _default_context
    logger.info("Building default SQL context (no role)...")
    _default_context = _build_context(
        include_tables=cfg.db_include_tables_list or None,
        ignore_tables=cfg.db_ignore_tables_list or None,
        restrict_map=cfg.db_restrict_columns_map,
        role=None,
    )
    logger.info("Default SQL context initialised")

    roles = cfg.role_tables_map
    if not roles:
        logger.warning("No roles defined in .env — only default context available")
    else:
        logger.info(f"Building SQL context for {len(roles)} roles: {list(roles.keys())}")
        for role, tables in roles.items():
            logger.info(f"Building context for role='{role}' ({len(tables)} tables)...")
            restrict_map = cfg.get_restrict_columns_for_role(role)
            if restrict_map:
                logger.debug(f"Role '{role}' has column restrictions: {restrict_map}")
            _role_cache[role] = _build_context(
                include_tables=tables,
                ignore_tables=None,
                restrict_map=restrict_map,
                role=role,
            )
            logger.info(f"Role '{role}' SQL context initialised — tables: {', '.join(sorted(tables))}")

    logger.info(f"SQL context initialisation complete — default + {len(_role_cache)} role(s) ready")


# initialise everything at module load
_init()


def _get_context(role: str | None) -> dict:
    """Returns the cached context for the given role, or default if role is None/unknown."""
    if role:
        role = role.lower()
        if role not in _role_cache:
            logger.error(f"Unknown role '{role}' requested. Defined roles: {list(_role_cache.keys())}")
            raise ValueError(f"Unknown role '{role}'. Defined roles: {list(_role_cache.keys())}")
        logger.debug(f"Returning cached context for role='{role}'")
        logger.debug(f"Context for role='{role}': db={_role_cache[role]['db']}, tools={len(_role_cache[role]['tools'])} tools, system_message_length={len(_role_cache[role]['system_message'].content)} chars")
        logger.debug(f"System message for role='{role}': {_role_cache[role]['system_message'].content}")
        return _role_cache[role]
    logger.debug("No role specified — returning default context")
    return _default_context


def get_db(role: str | None = None) -> SQLDatabase:
    return _get_context(role)["db"]


def get_sql_tools(role: str | None = None) -> list:
    return _get_context(role)["tools"]


def get_system_message(role: str | None = None) -> SystemMessage:
    return _get_context(role)["system_message"]
