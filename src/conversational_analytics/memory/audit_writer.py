"""
Async audit writer — production-grade fire-and-forget DB logging.

Architecture:
  - Single asyncio.Queue (bounded) as the write buffer
  - One background worker coroutine drains the queue in batches
  - psycopg (async) with AsyncConnectionPool — no threads, no blocking
  - Exponential backoff retry on transient DB errors
  - Graceful drain on shutdown: flushes all queued items before exit
  - Backpressure: queue.put_nowait() drops with a warning if queue is full
    (protects the event loop — audit logs are non-critical)
"""
import asyncio
import json
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

import psycopg
from psycopg_pool import AsyncConnectionPool

from conversational_analytics.config import get_settings

logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
_QUEUE_MAX_SIZE   = 10_000   # max buffered items before backpressure kicks in
_BATCH_SIZE       = 50       # max rows per INSERT batch
_BATCH_TIMEOUT    = 0.5      # seconds to wait for a full batch before flushing partial
_MAX_RETRIES      = 3
_RETRY_BASE_DELAY = 0.5      # seconds, doubles each retry


# ── Event types ───────────────────────────────────────────────────────────────
class _EventType(Enum):
    QUERY_LOG   = auto()
    AGENT_STEP  = auto()


@dataclass
class _AuditEvent:
    event_type: _EventType
    payload: dict[str, Any]


# ── Singleton writer ──────────────────────────────────────────────────────────
class AuditWriter:
    """
    Singleton async audit writer.
    Call start() on app startup and stop() on shutdown.
    Use enqueue_query_log() and enqueue_agent_step() to submit events.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[_AuditEvent] = asyncio.Queue(maxsize=_QUEUE_MAX_SIZE)
        self._pool: AsyncConnectionPool | None = None
        self._worker_task: asyncio.Task | None = None
        self._stopped = False

    async def start(self) -> None:
        cfg = get_settings()
        logger.info("Starting AuditWriter — connecting to DB...")
        self._pool = AsyncConnectionPool(
            cfg.long_term_memory_db_uri,
            min_size=2,
            max_size=10,
            kwargs={"autocommit": True, "prepare_threshold": 0},
            open=False,
        )
        await self._pool.open()
        self._stopped = False
        self._worker_task = asyncio.create_task(self._worker(), name="audit-writer")
        logger.info("AuditWriter started")

    async def stop(self) -> None:
        """Graceful shutdown — drains the queue before closing the pool."""
        logger.info(f"AuditWriter stopping — draining {self._queue.qsize()} queued items...")
        self._stopped = True
        if self._worker_task:
            # signal worker to finish by waiting for queue to drain
            try:
                await asyncio.wait_for(self._queue.join(), timeout=30.0)
            except asyncio.TimeoutError:
                logger.warning("AuditWriter drain timed out after 30s — some audit records may be lost")
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        if self._pool:
            await self._pool.close()
        logger.info("AuditWriter stopped")

    def enqueue_query_log(self, **kwargs: Any) -> None:
        """Non-blocking enqueue — drops with warning if queue is full."""
        self._enqueue(_EventType.QUERY_LOG, kwargs)

    def enqueue_agent_step(self, **kwargs: Any) -> None:
        """Non-blocking enqueue — drops with warning if queue is full."""
        self._enqueue(_EventType.AGENT_STEP, kwargs)

    def _enqueue(self, event_type: _EventType, payload: dict) -> None:
        try:
            self._queue.put_nowait(_AuditEvent(event_type=event_type, payload=payload))
        except asyncio.QueueFull:
            logger.warning(
                f"AuditWriter queue full ({_QUEUE_MAX_SIZE}) — dropping {event_type.name} "
                f"for conversation={payload.get('conversation_id')}"
            )

    # ── Worker ────────────────────────────────────────────────────────────────

    async def _worker(self) -> None:
        """Drains the queue in batches, retrying on transient errors."""
        logger.debug("AuditWriter worker started")
        while not self._stopped or not self._queue.empty():
            batch = await self._collect_batch()
            if not batch:
                continue
            await self._flush_with_retry(batch)
        logger.debug("AuditWriter worker exiting")

    async def _collect_batch(self) -> list[_AuditEvent]:
        """Collects up to _BATCH_SIZE items, waiting up to _BATCH_TIMEOUT seconds."""
        batch: list[_AuditEvent] = []
        deadline = asyncio.get_event_loop().time() + _BATCH_TIMEOUT
        while len(batch) < _BATCH_SIZE:
            timeout = deadline - asyncio.get_event_loop().time()
            if timeout <= 0:
                break
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=timeout)
                batch.append(event)
            except asyncio.TimeoutError:
                break
        return batch

    async def _flush_with_retry(self, batch: list[_AuditEvent]) -> None:
        """Writes a batch to DB with exponential backoff retry."""
        query_logs  = [e.payload for e in batch if e.event_type == _EventType.QUERY_LOG]
        agent_steps = [e.payload for e in batch if e.event_type == _EventType.AGENT_STEP]

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                async with self._pool.connection() as conn:
                    if query_logs:
                        await self._insert_query_logs(conn, query_logs)
                    if agent_steps:
                        await self._insert_agent_steps(conn, agent_steps)
                # mark all items done after successful write
                for _ in batch:
                    self._queue.task_done()
                logger.debug(f"AuditWriter flushed batch — query_logs={len(query_logs)} agent_steps={len(agent_steps)}")
                return
            except Exception as e:
                if attempt == _MAX_RETRIES:
                    logger.error(
                        f"AuditWriter failed after {_MAX_RETRIES} retries — "
                        f"dropping batch of {len(batch)} items: {e}"
                    )
                    for _ in batch:
                        self._queue.task_done()
                else:
                    delay = _RETRY_BASE_DELAY * (2 ** (attempt - 1))
                    logger.warning(f"AuditWriter DB error (attempt {attempt}/{_MAX_RETRIES}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)

    @staticmethod
    async def _insert_query_logs(conn: psycopg.AsyncConnection, rows: list[dict]) -> None:
        async with conn.cursor() as cur:
            await cur.executemany(
                """
                INSERT INTO memory.query_log
                    (conversation_id, session_id, user_id, role, user_query, prompt,
                     sql_generated, tools_invoked, agent_response, vega_spec,
                     token_usage, stream_events, has_vega, execution_ms)
                VALUES (%(conversation_id)s, %(session_id)s, %(user_id)s, %(role)s,
                        %(user_query)s, %(prompt)s, %(sql_generated)s, %(tools_invoked)s,
                        %(agent_response)s, %(vega_spec)s, %(token_usage)s,
                        %(stream_events)s, %(has_vega)s, %(execution_ms)s)
                """,
                [_serialise_query_log(r) for r in rows],
            )

    @staticmethod
    async def _insert_agent_steps(conn: psycopg.AsyncConnection, rows: list[dict]) -> None:
        async with conn.cursor() as cur:
            await cur.executemany(
                """
                INSERT INTO memory.agent_steps
                    (conversation_id, session_id, user_id, step_number, step_type,
                     tool_name, input, output, token_usage, duration_ms)
                VALUES (%(conversation_id)s, %(session_id)s, %(user_id)s, %(step_number)s,
                        %(step_type)s, %(tool_name)s, %(input)s, %(output)s,
                        %(token_usage)s, %(duration_ms)s)
                """,
                [_serialise_agent_step(r) for r in rows],
            )


# ── Serialisers ───────────────────────────────────────────────────────────────

def _serialise_query_log(r: dict) -> dict:
    return {
        "conversation_id": r["conversation_id"],
        "session_id":      r["session_id"],
        "user_id":         r["user_id"],
        "role":            r.get("role"),
        "user_query":      r["user_query"],
        "prompt":          r.get("prompt"),
        "sql_generated":   r.get("sql_generated"),
        "tools_invoked":   r.get("tools_invoked"),
        "agent_response":  r.get("agent_response"),
        "vega_spec":       json.dumps(r["vega_spec"])     if r.get("vega_spec")     else None,
        "token_usage":     json.dumps(r["token_usage"])   if r.get("token_usage")   else None,
        "stream_events":   json.dumps(r["stream_events"]) if r.get("stream_events") else None,
        "has_vega":        r.get("has_vega", False),
        "execution_ms":    r.get("execution_ms"),
    }


def _serialise_agent_step(r: dict) -> dict:
    return {
        "conversation_id": r["conversation_id"],
        "session_id":      r["session_id"],
        "user_id":         r["user_id"],
        "step_number":     r["step_number"],
        "step_type":       r["step_type"],
        "tool_name":       r.get("tool_name"),
        "input":           r.get("input"),
        "output":          r.get("output"),
        "token_usage":     json.dumps(r["token_usage"]) if r.get("token_usage") else None,
        "duration_ms":     r.get("duration_ms"),
    }


# ── Module-level singleton ────────────────────────────────────────────────────
audit_writer = AuditWriter()
