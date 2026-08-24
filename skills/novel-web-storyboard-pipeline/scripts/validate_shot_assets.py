from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from workflow_common import load_json


def validate_shot_assets(manifest: dict[str, Any], shot_id: str) -> dict[str, Any]:
    normalized = shot_id.upper()
    shot = next((item for item in manifest.get("shots", []) if str(item.get("shot_id", "")).upper() == normalized), None)
    if shot is None:
        return {"ok": False, "shot_id": normalized, "errors": [f"Shot not found in manifest: {normalized}"]}

    assets = {str(item.get("asset_id")): item for item in manifest.get("assets", [])}
    errors: list[str] = []
    bindings = sorted(shot.get("bindings", []), key=lambda item: int(item.get("order", 0)))
    expected_orders = list(range(1, len(bindings) + 1))
    actual_orders = [int(item.get("order", 0)) for item in bindings]
    if actual_orders != expected_orders:
        errors.append(f"Binding order must be contiguous from 1: {actual_orders}")

    checked: list[dict[str, Any]] = []
    for binding in bindings:
        order = int(binding.get("order", 0))
        path_value = binding.get("path")
        path = Path(str(path_value)) if path_value else None
        source = str(binding.get("source") or "")
        asset_id = binding.get("asset_id")
        entry = {
            "order": order,
            "source": source,
            "asset_id": asset_id,
            "path": str(path) if path else None,
            "exists": bool(path and path.is_file()),
        }

        if source not in {"asset", "previous_tail_frame"}:
            errors.append(f"@图片{order} has unresolved source: {source or '<empty>'}")
        if not path:
            errors.append(f"@图片{order} has no resolved path")
        elif not path.is_file():
            errors.append(f"@图片{order} file does not exist: {path}")

        if source == "asset":
            asset = assets.get(str(asset_id)) if asset_id else None
            if asset is None:
                errors.append(f"@图片{order} has no valid manifest asset: {asset_id!r}")
            else:
                status = str(asset.get("status") or "")
                entry["asset_status"] = status
                if status == "pending_generation":
                    errors.append(f"@图片{order} asset {asset_id} is still pending_generation")
        checked.append(entry)

    return {"ok": not errors, "shot_id": normalized, "bindings": checked, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description="Hard-gate one manifest shot before Doubao upload.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--shot", required=True)
    args = parser.parse_args()
    report = validate_shot_assets(load_json(args.manifest.resolve()), args.shot)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
