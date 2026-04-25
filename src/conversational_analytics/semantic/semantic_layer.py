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


def get_role_config(role: str | None) -> dict:
    """Returns the semantic layer config for a role. Returns {} if not found."""
    if not role:
        return {}
    return _load().get("roles", {}).get(role.lower(), {})


def get_global_business_rules() -> list[str]:
    """Returns global business rules. Empty list if not defined."""
    return _load().get("business_rules", [])


def get_domains_for_role(role: str | None) -> dict:
    """Returns domain definitions filtered to the role's allowed domains."""
    data = _load()
    all_domains: dict = data.get("domains", {})
    if not all_domains:
        return {}
    allowed_domains: list[str] = get_role_config(role).get("domains", [])
    if not allowed_domains:
        return all_domains
    return {k: v for k, v in all_domains.items() if k in allowed_domains}


def build_system_prompt_suffix(role: str | None, visible_tables: list[str]) -> str:
    """Builds the semantic layer section to append to the system prompt.

    Reads all content directly from semantic_layer.json:
    1. Global business rules          — from business_rules[]
    2. Role description + guidelines  — from roles.<role>
    3. Critical SQL filter patterns   — from sql_patterns[]
    4. Join guide with notes          — from relationships[] + join_notes{}
    5. Available metrics with units   — from domains.<domain>.metrics

    Backward compatible — returns empty string if semantic_layer.json is missing.
    """
    data = _load()
    if not data:
        return ""

    sections: list[str] = []

    # ── 1. Global business rules ──────────────────────────────────────
    global_rules = data.get("business_rules", [])
    if global_rules:
        rules_text = "\n".join(f"  - {r}" for r in global_rules)
        sections.append(f"BUSINESS RULES:\n{rules_text}")

    # ── 2. Role-specific context ──────────────────────────────────────
    role_config = get_role_config(role)
    if role_config:
        role_desc = role_config.get("description", "")
        role_rules = role_config.get("business_rules", [])
        if role_desc:
            sections.append(f"YOUR ROLE ({role}): {role_desc}")
        if role_rules:
            role_rules_text = "\n".join(f"  - {r}" for r in role_rules)
            sections.append(f"ROLE GUIDELINES:\n{role_rules_text}")

    # ── 3. Critical SQL filter patterns — read directly from json ─────
    sql_patterns = data.get("sql_patterns", [])
    if sql_patterns:
        patterns_text = "\n".join(f"  - {p}" for p in sql_patterns)
        sections.append(f"CRITICAL SQL PATTERNS (always use these exact filters):\n{patterns_text}")

    # ── 4. Join guide — read relationships + join_notes from json ─────
    relationships = data.get("relationships", [])
    join_notes: dict = data.get("join_notes", {})
    if relationships:
        by_source: dict[str, list[str]] = {}
        for rel in relationships:
            src = rel.get("from", "")
            tgt = rel.get("to", "")
            join = rel.get("join", "")
            if not src or not tgt or not join:
                continue
            note = join_notes.get(f"{src}->{tgt}", "")
            note_str = f" [{note}]" if note else ""
            by_source.setdefault(src, []).append(f"{tgt} ON {join}{note_str}")

        if by_source:
            join_lines = "\n".join(
                f"  {src}: " + " | ".join(targets)
                for src, targets in sorted(by_source.items())
            )
            sections.append(f"KEY JOIN PATTERNS:\n{join_lines}")

    # ── 5. Available metrics with unit labels ─────────────────────────
    domains = get_domains_for_role(role)
    if domains:
        metric_lines: list[str] = []
        for domain_name, domain in domains.items():
            metrics = domain.get("metrics", {})
            if not metrics:
                continue
            metric_lines.append(f"\n  [{domain_name.upper()}] {domain.get('description', '')}")
            for metric_name, metric in metrics.items():
                unit = metric.get("unit", "")
                unit_label = f" ({unit})" if unit else ""
                metric_lines.append(f"    - {metric_name}{unit_label}: {metric.get('description', '')}")
        if metric_lines:
            sections.append("AVAILABLE METRICS:" + "".join(metric_lines))

    return "\n\n".join(sections)
