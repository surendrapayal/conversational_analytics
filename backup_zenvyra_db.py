"""
Backup script for the `zenvyra-analytics-db` PostgreSQL database.

It runs `pg_dump` *inside* the running Docker container (defined in
docker-compose.yml), so no local Postgres client is required and the dump
tool version always matches the server.

Defaults are taken from docker-compose.yml:
    container : zenvyra-analytics-db
    user      : admin_user
    database  : zenvyra

Usage:
    uv run python backup_zenvyra_db.py
    uv run python backup_zenvyra_db.py --output-dir backups --format custom
    uv run python backup_zenvyra_db.py --format plain

Formats:
    custom (default) -> .dump  (compressed, restore with pg_restore)
    plain            -> .sql   (human-readable, restore with psql)

Restore examples:
    # custom format
    docker exec -i zenvyra-analytics-db pg_restore -U admin_user -d zenvyra --clean < backup.dump
    # plain format
    docker exec -i zenvyra-analytics-db psql -U admin_user -d zenvyra < backup.sql
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

# ── Defaults (match docker-compose.yml) ──────────────────────────────
DEFAULT_CONTAINER = "zenvyra-analytics-db"
DEFAULT_USER = "admin_user"
DEFAULT_DB = "zenvyra"
DEFAULT_OUTPUT_DIR = "backups"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Back up the zenvyra-analytics-db Postgres database via Docker."
    )
    parser.add_argument("--container", default=DEFAULT_CONTAINER, help="Docker container name")
    parser.add_argument("--user", default=DEFAULT_USER, help="Postgres user")
    parser.add_argument("--db", default=DEFAULT_DB, help="Database name to back up")
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to write the backup file into (created if missing)",
    )
    parser.add_argument(
        "--format",
        choices=("custom", "plain"),
        default="custom",
        help="Dump format: custom (.dump, compressed) or plain (.sql)",
    )
    return parser.parse_args()


def ensure_docker_available() -> None:
    if shutil.which("docker") is None:
        sys.exit("ERROR: 'docker' was not found on PATH. Is Docker installed and running?")


def container_is_running(container: str) -> bool:
    result = subprocess.run(
        ["docker", "ps", "--filter", f"name=^{container}$", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    return container in result.stdout.split()


def build_dump_command(args: argparse.Namespace) -> tuple[list[str], str]:
    """Return (command, output_filename) for the chosen format."""
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

    if args.format == "custom":
        ext = "dump"
        fmt_flag = "-Fc"  # custom, compressed
    else:
        ext = "sql"
        fmt_flag = "-Fp"  # plain SQL

    filename = f"{args.db}_{timestamp}.{ext}"

    # pg_dump writes to stdout; we capture it on the host side.
    cmd = [
        "docker", "exec", args.container,
        "pg_dump",
        "-U", args.user,
        "-d", args.db,
        fmt_flag,
    ]
    return cmd, filename


def main() -> int:
    args = parse_args()
    ensure_docker_available()

    if not container_is_running(args.container):
        sys.exit(
            f"ERROR: container '{args.container}' is not running.\n"
            f"Start it first:  docker compose up -d {args.container}"
        )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd, filename = build_dump_command(args)
    out_path = output_dir / filename

    print(f"Backing up database '{args.db}' from container '{args.container}'...")
    print(f"  Format : {args.format}")
    print(f"  Output : {out_path}")

    try:
        with out_path.open("wb") as fh:
            result = subprocess.run(cmd, stdout=fh, stderr=subprocess.PIPE)
    except OSError as e:
        sys.exit(f"ERROR: failed to run pg_dump: {e}")

    if result.returncode != 0:
        # Clean up the (likely empty/partial) file on failure.
        out_path.unlink(missing_ok=True)
        stderr = result.stderr.decode(errors="replace").strip()
        sys.exit(f"ERROR: pg_dump failed (exit {result.returncode}).\n{stderr}")

    size = out_path.stat().st_size
    if size == 0:
        out_path.unlink(missing_ok=True)
        sys.exit("ERROR: backup file is empty — the dump produced no output.")

    print(f"\nSUCCESS: backup written ({size:,} bytes)")
    print(f"  {out_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
