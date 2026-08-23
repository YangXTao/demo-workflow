from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from workflow_common import IMAGE_EXTENSIONS, atomic_write_json, image_dimensions, load_config, normalize_name, resolve_path, sha256_file


def classify(name: str) -> str:
    lowered = name.lower()
    if "场景" in name or any(token in lowered for token in ("location", "environment")):
        return "scene"
    if "道具" in name or any(token in lowered for token in ("prop", "weapon", "token")):
        return "prop"
    if any(token in name for token in ("群体", "群像", "百姓", "弟子群", "修士群", "二人组")):
        return "group"
    if any(token in name for token in ("三视图", "四视图", "角色")):
        return "character"
    return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a regenerable asset inventory from the global image directory.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    config, project_root = load_config(args.config.resolve())
    aliases = config.get("aliases", {})
    image_dir = resolve_path(project_root, config["image_dir"])
    output = args.output or resolve_path(project_root, config["workflow_dir"]) / "asset-index.json"
    if not image_dir.is_dir():
        raise SystemExit(f"Image directory does not exist: {image_dir}")

    assets = []
    hash_groups: dict[str, list[str]] = defaultdict(list)
    for path in sorted(image_dir.rglob("*"), key=lambda item: str(item).casefold()):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        digest = sha256_file(path)
        width, height = image_dimensions(path)
        relative = path.relative_to(image_dir)
        entry = {
            "path": str(path.resolve()),
            "relative_path": str(relative),
            "filename": path.name,
            "kind": classify(path.stem),
            "canonical_key": normalize_name(path.stem, aliases),
            "sha256": digest,
            "bytes": path.stat().st_size,
            "width": width,
            "height": height,
            "modified_ns": path.stat().st_mtime_ns,
        }
        assets.append(entry)
        hash_groups[digest].append(str(relative))

    duplicates = [paths for paths in hash_groups.values() if len(paths) > 1]
    payload = {
        "schema_version": 1,
        "project_root": str(project_root),
        "image_dir": str(image_dir),
        "aliases": aliases,
        "asset_count": len(assets),
        "exact_duplicate_groups": duplicates,
        "assets": assets,
    }
    atomic_write_json(output.resolve(), payload)
    print(json.dumps({"ok": True, "output": str(output.resolve()), "asset_count": len(assets), "exact_duplicate_groups": len(duplicates)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
