"""Configurable standard-mode progress narration.

All labels are built from a hardcoded default or an optional JSON override
(``STEP_NARRATION_PATH``). The override file is loaded once and merged over
the defaults, so you only need to include the keys you want to customise.

Safety contract
───────────────
Only values from ``table_domains`` (a hardcoded/configured allow-list) are
ever injected into label templates. No SQL, raw table/column names, or model
reasoning is ever emitted. Unknown tokens in tool args are silently ignored.

JSON schema (all keys optional — omitted = use default)
────────────────────────────────────────────────────────
{
  "table_domains": { "<physical_table>": "<business_domain>" },
  "tool_labels": { "<tool_name>": "Label with {domains} placeholder" },
  "tool_labels_generic": { "<tool_name>": "Fallback label without {domains}" },
  "default_tool_step": "Fallback for any unmapped tool",
  "phases": {
    "understanding": "...",
    "reasoning": "...",
    "formatting": "..."
  }
}
"""

import json
import logging
import re
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# ── Hardcoded defaults ────────────────────────────────────────────────

# Empty by default: table names are schema-specific, so no mapping ships with
# the code. Provide `table_domains` in STEP_NARRATION_PATH to enable
# domain-aware labels (e.g. "Querying sales data"). Without it, tool labels
# fall back to their generic phrasing (no {domains}).
_DEFAULT_TABLE_DOMAINS: dict[str, str] = {}

_DEFAULT_TOOL_LABELS: dict[str, str] = {
    "sql_db_list_tables": "Identifying available data sources",
    "sql_db_schema": "Reviewing the structure of {domains} data",
    "sql_db_query_checker": "Validating the query for {domains} data",
    "sql_db_query": "Querying {domains} data",
}

_DEFAULT_TOOL_LABELS_GENERIC: dict[str, str] = {
    "sql_db_list_tables": "Identifying available data sources",
    "sql_db_schema": "Reviewing the data structure",
    "sql_db_query_checker": "Validating the query",
    "sql_db_query": "Retrieving the data",
}

_DEFAULT_DEFAULT_TOOL_STEP: str = "Working on your request"

_DEFAULT_PHASES: dict[str, str] = {
    "understanding": "Understanding your question",
    "reasoning": "Planning how to answer your question",
    "formatting": "Preparing your answer",
}


# ── Loader ────────────────────────────────────────────────────────────

def _resolve_path() -> Path | None:
    from conversational_analytics.config import get_settings
    raw = get_settings().step_narration_path.strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


@lru_cache
def _load_config() -> dict:
    """Loads the optional JSON override and merges it over defaults.

    Returns a resolved config dict with keys:
        table_domains, tool_labels, tool_labels_generic,
        default_tool_step, phases
    """
    cfg = {
        "table_domains": dict(_DEFAULT_TABLE_DOMAINS),
        "tool_labels": dict(_DEFAULT_TOOL_LABELS),
        "tool_labels_generic": dict(_DEFAULT_TOOL_LABELS_GENERIC),
        "default_tool_step": _DEFAULT_DEFAULT_TOOL_STEP,
        "phases": dict(_DEFAULT_PHASES),
    }

    path = _resolve_path()
    if path is None:
        logger.info("STEP_NARRATION_PATH not set — using built-in defaults")
        return cfg
    if not path.exists():
        logger.warning(f"Step narration file not found at {path} — using built-in defaults")
        return cfg

    try:
        with open(path, encoding="utf-8") as f:
            overrides = json.load(f)
    except Exception as e:
        logger.error(f"Failed to parse step narration JSON at {path}: {e} — using built-in defaults")
        return cfg

    if not isinstance(overrides, dict):
        logger.warning(f"Step narration JSON at {path} is not a dict — using built-in defaults")
        return cfg

    # Merge: override dicts are shallow-merged over defaults so missing keys
    # keep their default value. Scalar keys are replaced outright.
    for dict_key in ("table_domains", "tool_labels", "tool_labels_generic", "phases"):
        if dict_key in overrides and isinstance(overrides[dict_key], dict):
            cfg[dict_key].update(overrides[dict_key])

    if "default_tool_step" in overrides and isinstance(overrides["default_tool_step"], str):
        cfg["default_tool_step"] = overrides["default_tool_step"]

    logger.info(
        f"Step narration loaded from {path} — "
        f"table_domains={len(cfg['table_domains'])}, "
        f"tool_labels={len(cfg['tool_labels'])}"
    )
    return cfg


# ── Public API ────────────────────────────────────────────────────────

def _domains_from_args(args: dict | None) -> list[str]:
    """Extracts safe business-domain words from tool args by matching KNOWN
    table names only. Any token not in the configured table_domains is silently
    ignored — no raw table/column/SQL fragment can leak.
    """
    if not isinstance(args, dict):
        return []
    haystack = " ".join(v.lower() for v in args.values() if isinstance(v, str))
    if not haystack:
        return []
    table_domains = _load_config()["table_domains"]
    seen: list[str] = []
    for table, domain in table_domains.items():
        if re.search(rf"\b{re.escape(table)}\b", haystack) and domain not in seen:
            seen.append(domain)
    return seen


def _format_domains(domains: list[str]) -> str:
    """Joins up to 3 domain words into a human phrase.

    'sales', 'sales and menu', 'sales, menu and payments',
    or 'sales, menu and other' when more than 3.
    """
    if not domains:
        return ""
    shown = domains[:3]
    if len(domains) > len(shown):
        shown = shown + ["other"]
    if len(shown) == 1:
        return shown[0]
    return ", ".join(shown[:-1]) + " and " + shown[-1]


def get_safe_step_label(tool_name: str, args: dict | None = None) -> str:
    """Returns a configured, leak-free progress label for a tool call.

    Enriches the label with safe business-domain words derived from KNOWN table
    names in the args (e.g. 'Querying sales and menu data'). Falls back to a
    generic phrase when the tool is unmapped or no known domain is detected.
    """
    cfg = _load_config()
    tool_labels = cfg["tool_labels"]
    tool_labels_generic = cfg["tool_labels_generic"]

    if tool_name not in tool_labels:
        return cfg["default_tool_step"]

    domains = _format_domains(_domains_from_args(args))
    if domains:
        return tool_labels[tool_name].format(domains=domains)
    return tool_labels_generic.get(tool_name, cfg["default_tool_step"])


def get_phase(phase_key: str) -> str:
    """Returns a configured phase label by key ('understanding', 'reasoning', 'formatting').

    Falls back to the hardcoded default if the key is missing from config.
    """
    return _load_config()["phases"].get(phase_key, _DEFAULT_PHASES.get(phase_key, ""))
