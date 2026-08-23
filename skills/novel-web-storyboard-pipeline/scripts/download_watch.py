from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path
from typing import Any

from workflow_common import atomic_write_json, load_json, versioned_path


PARTIAL_SUFFIXES = {".crdownload", ".part", ".tmp"}


def snapshot(directory: Path) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=True)
    return {
        "directory": str(directory.resolve()),
        "files": {
            str(path.resolve()): {"size": path.stat().st_size, "mtime_ns": path.stat().st_mtime_ns}
            for path in directory.iterdir()
            if path.is_file()
        },
    }


def wait_for_download(directory: Path, before: dict[str, Any], timeout: float, extensions: set[str]) -> Path:
    deadline = time.monotonic() + timeout
    previous_size: dict[Path, int] = {}
    stable_count: dict[Path, int] = {}
    old = before.get("files", {})
    while time.monotonic() < deadline:
        partial_names = {path.stem for path in directory.iterdir() if path.is_file() and path.suffix.lower() in PARTIAL_SUFFIXES}
        candidates = []
        for path in directory.iterdir():
            if not path.is_file() or path.suffix.lower() not in extensions:
                continue
            resolved = str(path.resolve())
            stat = path.stat()
            if resolved in old and old[resolved].get("mtime_ns") == stat.st_mtime_ns and old[resolved].get("size") == stat.st_size:
                continue
            if path.stem in partial_names:
                continue
            candidates.append(path)
        for path in sorted(candidates, key=lambda value: value.stat().st_mtime_ns, reverse=True):
            size = path.stat().st_size
            stable_count[path] = stable_count.get(path, 0) + 1 if previous_size.get(path) == size and size > 0 else 0
            previous_size[path] = size
            if stable_count[path] >= 2:
                return path.resolve()
        time.sleep(1.0)
    raise TimeoutError(f"No completed new download appeared in {directory} within {timeout}s")


def promote(source: Path, destination: Path, overwrite: bool = False) -> Path:
    if source.suffix.lower() in PARTIAL_SUFFIXES:
        raise ValueError(f"Partial download cannot be promoted: {source}")
    if not source.is_file() or source.stat().st_size == 0:
        raise ValueError(f"Download is missing or empty: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    target = destination if overwrite else versioned_path(destination)
    shutil.move(str(source), str(target))
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect the newest completed browser download and move it to its deterministic name.")
    sub = parser.add_subparsers(dest="command", required=True)
    snap = sub.add_parser("snapshot")
    snap.add_argument("--dir", required=True, type=Path)
    snap.add_argument("--output", required=True, type=Path)
    wait = sub.add_parser("wait")
    wait.add_argument("--dir", required=True, type=Path)
    wait.add_argument("--snapshot", required=True, type=Path)
    wait.add_argument("--timeout", type=float, default=1800)
    wait.add_argument("--extensions", default=".mp4,.png,.jpg,.jpeg,.webp")
    move = sub.add_parser("promote")
    move.add_argument("--source", required=True, type=Path)
    move.add_argument("--destination", required=True, type=Path)
    move.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.command == "snapshot":
        payload = snapshot(args.dir.resolve())
        atomic_write_json(args.output.resolve(), payload)
        result = {"ok": True, "snapshot": str(args.output.resolve()), "files": len(payload["files"])}
    elif args.command == "wait":
        extensions = {value.strip().lower() for value in args.extensions.split(",") if value.strip()}
        result = {"ok": True, "path": str(wait_for_download(args.dir.resolve(), load_json(args.snapshot.resolve()), args.timeout, extensions))}
    else:
        result = {"ok": True, "path": str(promote(args.source.resolve(), args.destination.resolve(), args.overwrite))}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
