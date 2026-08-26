from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workflow_common import load_json


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


SCHEMA = """
CREATE TABLE IF NOT EXISTS assets (
  asset_id TEXT PRIMARY KEY,
  chapter INTEGER NOT NULL,
  title TEXT NOT NULL,
  kind TEXT NOT NULL,
  status TEXT NOT NULL,
  output_path TEXT,
  error TEXT,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS shots (
  shot_id TEXT PRIMARY KEY,
  chapter INTEGER NOT NULL,
  sequence INTEGER NOT NULL,
  status TEXT NOT NULL,
  account TEXT,
  artifact_path TEXT,
  error TEXT,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS accounts (
  account TEXT PRIMARY KEY,
  used INTEGER NOT NULL DEFAULT 0,
  exhausted INTEGER NOT NULL DEFAULT 0,
  reserved INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  kind TEXT NOT NULL,
  chapter INTEGER,
  shot_id TEXT,
  message TEXT NOT NULL
);
"""


def initialize(db: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    chapter = int(manifest["chapter"]["number"])
    stamp = now()
    with closing(connect(db)) as connection:
        connection.executescript(SCHEMA)
        for asset in manifest["assets"]:
            key = f"{chapter}:{asset['asset_id']}"
            connection.execute(
                """INSERT INTO assets(asset_id, chapter, title, kind, status, output_path, updated_at)
                   VALUES(?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(asset_id) DO UPDATE SET title=excluded.title, kind=excluded.kind,
                     output_path=excluded.output_path, updated_at=excluded.updated_at""",
                (key, chapter, asset["title"], asset["kind"], asset["status"], asset["output_path"], stamp),
            )
        for shot in manifest["shots"]:
            key = f"{chapter}:{shot['shot_id']}"
            connection.execute(
                """INSERT INTO shots(shot_id, chapter, sequence, status, artifact_path, updated_at)
                   VALUES(?, ?, ?, ?, ?, ?)
                   ON CONFLICT(shot_id) DO UPDATE SET sequence=excluded.sequence,
                     artifact_path=COALESCE(shots.artifact_path, excluded.artifact_path), updated_at=excluded.updated_at""",
                (key, chapter, shot["sequence"], shot["status"], shot["video_path"], stamp),
            )
        reserved = manifest.get("settings", {}).get("reserved_last_account")
        if reserved:
            connection.execute(
                """INSERT INTO accounts(account, used, exhausted, reserved, updated_at) VALUES(?, 0, 0, 1, ?)
                   ON CONFLICT(account) DO UPDATE SET reserved=1, updated_at=excluded.updated_at""",
                (reserved, stamp),
            )
        connection.execute(
            "INSERT INTO events(created_at, kind, chapter, message) VALUES(?, 'manifest_initialized', ?, ?)",
            (stamp, chapter, str(manifest_path)),
        )
        connection.commit()
    return {"ok": True, "db": str(db), "chapter": chapter}


def resolve_key(connection: sqlite3.Connection, table: str, key_column: str, short_id: str, chapter: int | None) -> str:
    if chapter is not None:
        key = f"{chapter}:{short_id}"
        rows = connection.execute(f"SELECT {key_column} FROM {table} WHERE {key_column}=?", (key,)).fetchall()
    elif ":" in short_id:
        rows = connection.execute(f"SELECT {key_column} FROM {table} WHERE {key_column}=?", (short_id,)).fetchall()
    else:
        rows = connection.execute(
            f"SELECT {key_column} FROM {table} WHERE {key_column}=? OR {key_column} LIKE ?",
            (short_id, f"%:{short_id}"),
        ).fetchall()
    if len(rows) != 1:
        scope = f" in chapter {chapter}" if chapter is not None else ""
        raise KeyError(f"{table} must resolve exactly once{scope}: {short_id}")
    return rows[0][key_column]


def set_asset(db: Path, asset_id: str, status: str, path: str | None, error: str | None, chapter: int | None) -> None:
    with closing(connect(db)) as connection:
        key = resolve_key(connection, "assets", "asset_id", asset_id, chapter)
        cursor = connection.execute(
            "UPDATE assets SET status=?, output_path=COALESCE(?, output_path), error=?, updated_at=? WHERE asset_id=?",
            (status, path, error, now(), key),
        )
        if cursor.rowcount != 1:
            raise KeyError(f"Unknown asset: {asset_id}")
        connection.commit()


def set_shot(db: Path, shot_id: str, status: str, account: str | None, artifact: str | None, error: str | None, chapter: int | None) -> None:
    with closing(connect(db)) as connection:
        key = resolve_key(connection, "shots", "shot_id", shot_id, chapter)
        connection.execute(
            "UPDATE shots SET status=?, account=COALESCE(?, account), artifact_path=COALESCE(?, artifact_path), error=?, updated_at=? WHERE shot_id=?",
            (status, account, artifact, error, now(), key),
        )
        connection.commit()


def record_account(db: Path, account: str, delta: int, exhausted: bool, reserved: bool) -> None:
    stamp = now()
    with closing(connect(db)) as connection:
        connection.execute(
            """INSERT INTO accounts(account, used, exhausted, reserved, updated_at) VALUES(?, ?, ?, ?, ?)
               ON CONFLICT(account) DO UPDATE SET used=MAX(0, accounts.used + excluded.used),
                 exhausted=MAX(accounts.exhausted, excluded.exhausted),
                 reserved=MAX(accounts.reserved, excluded.reserved), updated_at=excluded.updated_at""",
            (account, delta, int(exhausted), int(reserved), stamp),
        )
        connection.commit()


def add_event(db: Path, kind: str, message: str, chapter: int | None, shot: str | None) -> None:
    with closing(connect(db)) as connection:
        connection.execute(
            "INSERT INTO events(created_at, kind, chapter, shot_id, message) VALUES(?, ?, ?, ?, ?)",
            (now(), kind, chapter, shot, message),
        )
        connection.commit()


def summary(db: Path) -> dict[str, Any]:
    with closing(connect(db)) as connection:
        connection.executescript(SCHEMA)
        assets = [dict(row) for row in connection.execute("SELECT status, COUNT(*) count FROM assets GROUP BY status ORDER BY status")]
        shots = [dict(row) for row in connection.execute("SELECT status, COUNT(*) count FROM shots GROUP BY status ORDER BY status")]
        accounts = [dict(row) for row in connection.execute("SELECT account, used, exhausted, reserved FROM accounts ORDER BY reserved, account")]
        recent = [dict(row) for row in connection.execute("SELECT * FROM events ORDER BY id DESC LIMIT 20")]
    return {"assets": assets, "shots": shots, "accounts": accounts, "recent_events": recent}


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist resumable workflow state in SQLite.")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--db", required=True, type=Path)
    init.add_argument("--manifest", required=True, type=Path)

    asset = sub.add_parser("set-asset")
    asset.add_argument("--db", required=True, type=Path)
    asset.add_argument("--asset", required=True)
    asset.add_argument("--status", required=True)
    asset.add_argument("--path")
    asset.add_argument("--error")
    asset.add_argument("--chapter", type=int, help="Required when the short asset ID exists in more than one chapter.")

    shot = sub.add_parser("set-shot")
    shot.add_argument("--db", required=True, type=Path)
    shot.add_argument("--shot", required=True)
    shot.add_argument("--status", required=True)
    shot.add_argument("--account")
    shot.add_argument("--artifact")
    shot.add_argument("--error")
    shot.add_argument("--chapter", type=int, help="Required when the short shot ID exists in more than one chapter.")

    account = sub.add_parser("record-account")
    account.add_argument("--db", required=True, type=Path)
    account.add_argument("--account", required=True)
    account.add_argument("--delta", type=int, default=1)
    account.add_argument("--exhausted", action="store_true")
    account.add_argument("--reserved", action="store_true")

    event = sub.add_parser("event")
    event.add_argument("--db", required=True, type=Path)
    event.add_argument("--kind", required=True)
    event.add_argument("--message", required=True)
    event.add_argument("--chapter", type=int)
    event.add_argument("--shot")

    report = sub.add_parser("summary")
    report.add_argument("--db", required=True, type=Path)
    args = parser.parse_args()

    if args.command == "init":
        result = initialize(args.db.resolve(), args.manifest.resolve())
    elif args.command == "set-asset":
        set_asset(args.db.resolve(), args.asset, args.status, args.path, args.error, args.chapter)
        result = {"ok": True}
    elif args.command == "set-shot":
        set_shot(args.db.resolve(), args.shot, args.status, args.account, args.artifact, args.error, args.chapter)
        result = {"ok": True}
    elif args.command == "record-account":
        record_account(args.db.resolve(), args.account, args.delta, args.exhausted, args.reserved)
        result = {"ok": True}
    elif args.command == "event":
        add_event(args.db.resolve(), args.kind, args.message, args.chapter, args.shot)
        result = {"ok": True}
    else:
        result = summary(args.db.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
