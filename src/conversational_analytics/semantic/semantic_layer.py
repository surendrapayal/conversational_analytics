import json
import logging
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _resolve_path() -> Path | None:
    """Resolves semantic layer path from config. Returns None if not configured."""
    from conversational_analytics.config import get_settings
    raw = get_settings().semantic_layer_path.strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


@lru_cache
def _load() -> dict:
    """Loads semantic_layer.json once and caches it. Returns empty dict if disabled or missing."""
    path = _resolve_path()
    if path is None:
        logger.info("SEMANTIC_LAYER_PATH not set — semantic layer disabled")
        return {}
    if not path.exists():
        logger.warning(f"Semantic layer file not found at {path} — skipping")
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Semantic layer loaded from {path} — domains: {list(data.get('domains', {}).keys())}")
    return data


def _parse_restrict_columns(restricted: list[str]) -> dict[str, list[str]]:
    """Converts ['customers.email', 'employee.email'] → {'customers': ['email'], 'employee': ['email']}"""
    result: dict[str, list[str]] = {}
    for entry in restricted:
        if "." not in entry:
            continue
        table, col = entry.split(".", 1)
        result.setdefault(table.strip(), []).append(col.strip())
    return result


def get_role_config(role: str | None) -> dict:
    """Returns the semantic layer config for a role.

    Backward compatible:
    - If semantic_layer.json missing → returns {}
    - If 'roles' key missing → returns {}
    - If role not found in roles → returns {}
    - If role is None → returns {}
    """
    if not role:
        return {}
    data = _load()
    return data.get("roles", {}).get(role.lower(), {})


def get_global_business_rules() -> list[str]:
    """Returns global business rules from semantic layer. Empty list if not defined."""
    return _load().get("business_rules", [])


def get_domains_for_role(role: str | None) -> dict:
    """Returns domain definitions filtered to the role's allowed domains.

    Backward compatible — returns all domains if role has no domain restriction.
    """
    data = _load()
    all_domains: dict = data.get("domains", {})
    if not all_domains:
        return {}

    role_config = get_role_config(role)
    allowed_domains: list[str] = role_config.get("domains", [])

    if not allowed_domains:
        return all_domains  # no restriction — return all

    return {k: v for k, v in all_domains.items() if k in allowed_domains}


def build_system_prompt_suffix(role: str | None, visible_tables: list[str]) -> str:
    """Builds the semantic layer section to append to the system prompt.

    Backward compatible:
    - Returns empty string if semantic_layer.json is missing
    - Returns only global rules if role has no entry in semantic layer
    - Returns role-specific rules + domains if role is defined
    """
    sections: list[str] = []

    # ── 1. Global business rules (always injected if present) ─────────
    global_rules = get_global_business_rules()
    if global_rules:
        rules_text = "\n".join(f"  - {r}" for r in global_rules)
        sections.append(f"BUSINESS RULES:\n{rules_text}")

    # ── 2. Role-specific context (only if role defined in semantic layer) ──
    role_config = get_role_config(role)
    if role_config:
        role_desc = role_config.get("description", "")
        role_rules = role_config.get("business_rules", [])

        if role_desc:
            sections.append(f"YOUR ROLE ({role}): {role_desc}")

        if role_rules:
            role_rules_text = "\n".join(f"  - {r}" for r in role_rules)
            sections.append(f"ROLE GUIDELINES:\n{role_rules_text}")

    # ── 3. Domain metrics (filtered to role's domains and visible tables) ──
    domains = get_domains_for_role(role)
    if domains:
        metric_lines: list[str] = []
        for domain_name, domain in domains.items():
            domain_desc = domain.get("description", "")
            metrics = domain.get("metrics", {})
            if not metrics:
                continue
            metric_lines.append(f"\n  [{domain_name.upper()}] {domain_desc}")
            for metric_name, metric in metrics.items():
                metric_lines.append(f"    - {metric_name}: {metric.get('description', '')}")
        if metric_lines:
            sections.append("AVAILABLE METRICS:" + "".join(metric_lines))

    return "\n\n".join(sections)
