"""
Test search_similar_conversations against the live agent-memory-db.

Run:
    uv run pytest tests/test_long_term_memory.py -v -s
"""
import uuid
import psycopg
from conversational_analytics.config import get_settings
from conversational_analytics.memory.long_term_memory import (
    save_conversation_summary,
    search_similar_conversations,
)

USER_ID = "admin"
QUERY   = "What is the net sales in each location?"


def test_db_connectivity():
    """Step 1 — verify raw TCP connection to agent-memory-db."""
    cfg = get_settings()
    print(f"\nConnecting to: {cfg.long_term_memory_db_uri}")
    conn = psycopg.connect(
        f"host={cfg.long_term_memory_db_host} "
        f"port={cfg.long_term_memory_db_port} "
        f"dbname={cfg.long_term_memory_db_name} "
        f"user={cfg.long_term_memory_db_user} "
        f"password={cfg.long_term_memory_db_password}"
    )
    cur = conn.execute("SELECT COUNT(*) FROM store_vectors")
    count = cur.fetchone()[0]
    print(f"Total store_vectors rows: {count}")
    conn.close()
    print("DB connection OK")


async def test_search_similar_conversations_round_trip():
    """Step 2 — save a summary then verify semantic search finds it."""
    conversation_id = str(uuid.uuid4())
    session_id      = str(uuid.uuid4())

    # ── Save a known summary first ────────────────────────────────────────────
    print(f"\nSaving test summary — conversation_id={conversation_id}")
    await save_conversation_summary(
        user_id=USER_ID,
        session_id=session_id,
        conversation_id=conversation_id,
        user_query=QUERY,
        response_text="The net sales per location are: Downtown $45,000, Uptown $38,000, Riverside $29,500.",
        role="admin",
    )
    print("Summary saved — running semantic search...")

    # ── Search for it ─────────────────────────────────────────────────────────
    results = await search_similar_conversations(user_id=USER_ID, query=QUERY, limit=3)

    print(f"\n--- search_similar_conversations results ({len(results)}) ---")
    for r in results:
        print(f"  conversation_id : {r['conversation_id']}")
        print(f"  similarity      : {r['similarity']:.4f}")
        print(f"  summary         : {r['summary'][:120]}")
        print(f"  session_id      : {r['session_id']}")
        print()

    assert len(results) > 0, "Expected at least 1 result after saving a summary"
    assert results[0]["similarity"] is not None
    assert results[0]["summary"]
    assert results[0]["conversation_id"]
