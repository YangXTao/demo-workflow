from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from workflow_common import (
    IMAGE_EXTENSIONS,
    atomic_write_json,
    chapter_number_from_name,
    code_block_after,
    load_config,
    load_json,
    normalize_name,
    read_text,
    resolve_path,
    sanitize_filename,
    split_markdown_h2,
)


PROMPT_HEADING = re.compile(r"^(?P<id>(?:CHAR|LOOK|PROP|LOC)-\d+-P\d+)\s*\|\s*(?P<title>.+)$")
SHOT_HEADING = re.compile(r"^(?P<id>SG-\d+)\s*\|\s*duration=(?P<duration>[0-9.]+)s\b", re.I)
DIRECTOR_SHOT_HEADING = re.compile(
    r"^S(?P<index>\d+)\s*[|｜]\s*(?P<start>\d{2}:\d{2})\s*[—–-]\s*(?P<end>\d{2}:\d{2})\b",
    re.I,
)
REFERENCE_FILE = re.compile(r"`([^`]+\.(?:png|jpe?g|webp|bmp))`", re.I)
SHOT_ID = re.compile(r"SG-\d+", re.I)
BINDING = re.compile(r"(?mi)^\s*-\s*@(?:图片|image)(?P<order>\d+)\s*[：:=＝]\s*(?P<text>.+?)\s*$")
DIRECT_BINDING = re.compile(r"(?mi)^\s*@(?:图片|image)(?P<order>\d+)\s*[：:=＝]\s*(?P<text>.+?)\s*$")
REVERSE_BINDING = re.compile(r"(?mi)(?P<text>[^。\n]{1,100}?)\s*=\s*@(?:图片|image)(?P<order>\d+)\b")
ASSET_ROW = re.compile(
    r"^\|(?P<id>(?:CHAR|LOOK|PROP|LOC)-\d{3})\|(?P<title>[^|]+)\|(?P<source>[^|]+)\|[^|]*\|(?P<shots>[^|]+)\|\s*$",
    re.MULTILINE,
)


def metadata(section: str, label: str) -> str:
    match = re.search(rf"(?m)^\s*-\s*{re.escape(label)}\s*[：:]\s*(.+?)\s*$", section, re.I)
    return match.group(1).strip() if match else ""


def parse_image_prompts(path: Path) -> list[dict[str, Any]]:
    prompts: list[dict[str, Any]] = []
    for heading, section in split_markdown_h2(read_text(path)):
        match = PROMPT_HEADING.match(heading)
        if not match:
            continue
        applicable = sorted(set(value.upper() for value in SHOT_ID.findall(metadata(section, "适用分镜"))))
        reference_text = metadata(section, "输入参考")
        prompts.append(
            {
                "asset_id": match.group("id"),
                "kind": match.group("id").split("-", 1)[0],
                "title": match.group("title").strip(),
                "model": metadata(section, "Model"),
                "quality": metadata(section, "Quality"),
                "size": metadata(section, "Size"),
                "purpose": metadata(section, "用途"),
                "output_filename": metadata(section, "输出文件"),
                "applicable_shots": applicable,
                "reference_text": reference_text,
                "reference_files": REFERENCE_FILE.findall(reference_text),
                "prompt": code_block_after(section, "可直接复制提示词"),
            }
        )
    return prompts


def _expand_shot_scope(value: str) -> list[str]:
    """Expand author-facing SG-001~003 ranges while retaining individual IDs."""
    result: set[str] = set()
    for start_text, end_text in re.findall(r"SG-(\d{3})\s*[~～-]\s*(\d{3})", value, re.I):
        start, end = int(start_text), int(end_text)
        if start <= end:
            result.update(f"SG-{number:03d}" for number in range(start, end + 1))
    result.update(value.upper() for value in SHOT_ID.findall(value))
    return sorted(result)


def parse_reusable_assets(path: Path, image_dir: Path, prompt_assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Expose explicit 03-assets.md reuse rows to the manifest binding resolver."""
    prompt_base_ids = {str(item["asset_id"]).rsplit("-P", 1)[0] for item in prompt_assets}
    reusable: list[dict[str, Any]] = []
    for match in ASSET_ROW.finditer(read_text(path)):
        asset_id = match.group("id")
        if asset_id in prompt_base_ids:
            continue
        source_match = REFERENCE_FILE.search(match.group("source"))
        if not source_match:
            continue
        filename = Path(source_match.group(1)).name
        resolved = image_dir / filename
        if not resolved.is_file():
            continue
        title = match.group("title").strip()
        reusable.append(
            {
                "asset_id": asset_id,
                "kind": asset_id.split("-", 1)[0],
                "title": f"{title} {Path(filename).stem}",
                "model": "",
                "quality": "",
                "size": "",
                "purpose": "existing accepted reusable asset",
                "applicable_shots": _expand_shot_scope(match.group("shots")),
                "reference_text": match.group("source").strip(),
                "reference_files": [filename],
                "prompt": "",
                "existing_path": str(resolved),
                "output_path": str(resolved),
                "status": "reused",
                "fresh_chat_required": False,
            }
        )
    return reusable


def _transition(prompt: str) -> str:
    block = prompt.split("【首帧与上镜承接】", 1)[-1].split("【", 1)[0]
    if "【首帧与上镜承接】" not in prompt:
        block = prompt.split("【上一镜尾帧衔接】", 1)[-1].split("【", 1)[0]
    for value in ("尾帧直续", "章节开场", "匹配切", "时空硬切"):
        if value in block:
            return value
    if "无上一镜" in block or "开场第一镜" in block:
        return "章节开场"
    if "上一镜结尾" in block or "尾帧" in block:
        return "尾帧直续"
    return "未声明"


def _clock_seconds(value: str) -> float:
    minutes, seconds = value.split(":", 1)
    return float(int(minutes) * 60 + int(seconds))


def _bindings(prompt: str) -> list[dict[str, Any]]:
    """Read both legacy @图片N bullets and the canonical S01 file style."""
    chosen: dict[int, str] = {}
    for pattern in (BINDING, DIRECT_BINDING, REVERSE_BINDING):
        for item in pattern.finditer(prompt):
            order = int(item.group("order"))
            text = item.group("text").strip()
            if order not in chosen and text:
                chosen[order] = text
    return [{"order": order, "description": chosen[order]} for order in sorted(chosen)]


def parse_shots(path: Path) -> list[dict[str, Any]]:
    shots: list[dict[str, Any]] = []
    for heading, section in split_markdown_h2(read_text(path)):
        match = SHOT_HEADING.match(heading)
        director_match = DIRECTOR_SHOT_HEADING.match(heading) if not match else None
        if not match and not director_match:
            continue
        if match:
            shot_id = match.group("id").upper()
            duration = float(match.group("duration"))
        else:
            assert director_match is not None
            shot_id = f"SG-{int(director_match.group('index')):03d}"
            duration = _clock_seconds(director_match.group("end")) - _clock_seconds(director_match.group("start"))
            if duration <= 0:
                raise ValueError(f"{heading} has a non-positive canonical S-shot duration")
            if abs(duration - 10.0) > 0.001:
                raise ValueError(f"{heading} must be exactly 10 seconds in canonical director mode")
        prompt = code_block_after(section) or section
        shots.append(
            {
                "shot_id": shot_id,
                "duration_seconds": duration,
                "transition": _transition(prompt),
                "bindings": _bindings(prompt),
                "prompt": prompt,
            }
        )
    return shots


def _index_candidates(index: dict[str, Any]) -> list[dict[str, Any]]:
    value = index.get("assets", index.get("files", []))
    return value if isinstance(value, list) else []


def _candidate_name(item: dict[str, Any]) -> str:
    value = str(item.get("name") or item.get("filename") or item.get("path", ""))
    return Path(value).stem


def _candidate_path(item: dict[str, Any]) -> str:
    return str(item.get("path") or "")


def _best_existing(asset: dict[str, Any], index: dict[str, Any], aliases: dict[str, str]) -> str | None:
    candidates = _index_candidates(index)
    title_key = normalize_name(asset["title"], aliases)
    exact: list[str] = []
    contains: list[str] = []
    for item in candidates:
        key = normalize_name(_candidate_name(item), aliases)
        path = _candidate_path(item)
        if not path or not key:
            continue
        if key == title_key:
            exact.append(path)
        elif title_key and (title_key in key or key in title_key) and min(len(key), len(title_key)) >= 3:
            contains.append(path)
    if exact:
        return sorted(exact)[0]
    # A new clothing/state LOOK needs an exact accepted match.  A character
    # identity master with the same name must never satisfy that new visible state.
    if contains and asset["kind"] != "LOOK":
        return sorted(contains, key=len)[0]
    # A CHAR task may directly reuse the named identity image. LOOK/PROP/LOC references
    # remain generation inputs unless a title-matching finished asset exists.
    if asset["kind"] == "CHAR":
        reference_names = {Path(value).name.lower() for value in asset["reference_files"]}
        for item in candidates:
            path = _candidate_path(item)
            if Path(path).name.lower() in reference_names:
                return path
    return None


def _output_name(asset: dict[str, Any], chapter_number: int) -> str:
    explicit = str(asset.get("output_filename") or "").strip()
    if explicit:
        return sanitize_filename(explicit)
    title = sanitize_filename(asset["title"].replace("·", "-"))
    if asset["kind"] == "CHAR":
        return f"{title}-三视图.png"
    if asset["kind"] == "LOOK":
        return f"{title}-第{chapter_number}章-三视图.png"
    if asset["kind"] == "PROP":
        return f"第{chapter_number}章道具-{title}.png"
    return f"第{chapter_number}章场景-{title}.png"


def _tokens(value: str, aliases: dict[str, str]) -> set[str]:
    value = normalize_name(value, aliases)
    if len(value) < 2:
        return {value} if value else set()
    return {value[index:index + 2] for index in range(len(value) - 1)}


def _match_binding(description: str, eligible: list[dict[str, Any]], aliases: dict[str, str]) -> dict[str, Any] | None:
    target = _tokens(description, aliases)
    normalized_description = normalize_name(description, aliases)
    scored: list[tuple[float, dict[str, Any]]] = []
    for asset in eligible:
        source = _tokens(asset["title"] + asset.get("purpose", ""), aliases)
        if not target or not source:
            continue
        score = len(target & source) / max(1, min(len(target), len(source)))
        # Chinese binding descriptions often share generic words such as
        # "三视图" and "场景图".  A direct mention of the authored asset
        # identity (the first title component) must win over that generic
        # overlap; otherwise a later monster/prop can be bound as a pet or
        # a different character solely because both are reference sheets.
        # Reusable rows append the accepted filename after a space.  Keep
        # only the authored identity before that suffix as well.
        primary_title = re.split(r"[\s，,、（(]", asset["title"], maxsplit=1)[0].strip()
        primary_key = normalize_name(primary_title, aliases)
        if len(primary_key) >= 2 and primary_key in normalized_description:
            score += 2.0
        scored.append((score, asset))
    if not scored:
        return None
    score, result = max(scored, key=lambda item: item[0])
    return result if score >= 0.05 else None


def _eligible_assets_for_shot(assets: list[dict[str, Any]], shot_id: str) -> list[dict[str, Any]]:
    """Keep bindings inside the asset authoring scope declared for the shot."""
    return [
        asset
        for asset in assets
        if not asset.get("applicable_shots") or shot_id in asset["applicable_shots"]
    ]


def build_manifest(config_path: Path, chapter_dir: Path, asset_index_path: Path | None = None) -> dict[str, Any]:
    config, project_root = load_config(config_path)
    chapter_dir = chapter_dir.resolve()
    chapter_number = chapter_number_from_name(chapter_dir.name)
    asset_dir = chapter_dir / config.get("asset_dir_name", "资产")
    image_dir = resolve_path(project_root, config["image_dir"])
    workflow_dir = resolve_path(project_root, config.get("workflow_dir", ".workflow"))
    index_path = asset_index_path or workflow_dir / "asset-index.json"
    index = load_json(index_path) if index_path.exists() else {"assets": []}
    aliases = config.get("aliases", {})

    prompt_assets = parse_image_prompts(asset_dir / "04-gpt-image-2-prompts.md")
    assets = list(prompt_assets)
    if not assets:
        raise ValueError("No image prompt sections were found")
    for asset in prompt_assets:
        expected_output = image_dir / _output_name(asset, chapter_number)
        generated_output = str(expected_output) if expected_output.is_file() else None
        existing = generated_output or _best_existing(asset, index, aliases)
        asset["existing_path"] = existing
        asset["output_path"] = existing or str(image_dir / _output_name(asset, chapter_number))
        asset["status"] = "generated" if generated_output else "reused" if existing else "pending_generation"
        asset["fresh_chat_required"] = asset["kind"] in {"CHAR", "LOOK"}

    assets.extend(parse_reusable_assets(asset_dir / "03-assets.md", image_dir, prompt_assets))

    shots = parse_shots(asset_dir / "07-seedance-2-fast-prompts.md")
    if not shots:
        raise ValueError("No Seedance shot sections were found")
    max_images = int(config.get("doubao", {}).get("max_images_per_shot", 9))
    shot_dir = chapter_dir / config.get("shot_dir_name", "镜头")
    for position, shot in enumerate(shots, start=1):
        if len(shot["bindings"]) > max_images:
            raise ValueError(f"{shot['shot_id']} requests {len(shot['bindings'])} images; limit is {max_images}")
        used_asset_ids: set[str] = set()
        shot_assets = _eligible_assets_for_shot(assets, shot["shot_id"])
        for binding in shot["bindings"]:
            if binding["order"] == 1 and shot["transition"] == "尾帧直续":
                previous = shots[position - 2] if position > 1 else None
                binding.update(
                    {
                        "source": "previous_tail_frame",
                        "asset_id": None,
                        "path": str(shot_dir / f"{chapter_number}-{position - 1}-尾帧.png") if previous else None,
                    }
                )
                continue
            unused = [asset for asset in shot_assets if asset["asset_id"] not in used_asset_ids]
            matched = _match_binding(binding["description"], unused, aliases)
            if matched is None:
                matched = _match_binding(binding["description"], shot_assets, aliases)
            # A storyboard can explicitly request an existing asset that was
            # omitted from its authored applicable-shot list. Resolve that
            # conservative text match before emitting a broken null binding.
            if matched is None:
                all_unused = [asset for asset in assets if asset["asset_id"] not in used_asset_ids]
                matched = _match_binding(binding["description"], all_unused, aliases)
            if matched is None:
                matched = _match_binding(binding["description"], assets, aliases)
            if matched:
                used_asset_ids.add(matched["asset_id"])
            binding.update(
                {
                    "source": "asset",
                    "asset_id": matched["asset_id"] if matched else None,
                    "path": matched["output_path"] if matched else None,
                }
            )
        shot["sequence"] = position
        shot["video_path"] = str(shot_dir / f"{chapter_number}-{position}.mp4")
        shot["tail_frame_path"] = str(shot_dir / f"{chapter_number}-{position}-尾帧.png")
        shot["tail_frame_required"] = position < len(shots) and shots[position]["transition"] == "尾帧直续"
        shot["status"] = "pending"

    return {
        "schema_version": 1,
        "chapter": {"number": chapter_number, "name": chapter_dir.name, "path": str(chapter_dir)},
        "settings": {
            "chatgpt_model": config.get("chatgpt", {}).get("model"),
            "doubao_model": config.get("doubao", {}).get("model"),
            "ratio": config.get("doubao", {}).get("ratio"),
            "duration_seconds": config.get("doubao", {}).get("duration_seconds", 10),
            "account_generation_limit": config.get("account_generation_limit", 3),
            "start_video_with_director_account": config.get("start_video_with_director_account", True),
            "default_director_account": config.get("director_prompt", {}).get(
                "default_account_label", "用户867998"
            ),
            "reserved_last_account": config.get("reserved_last_account", "fei-1"),
            "reserved_tail_accounts": config.get(
                "reserved_tail_accounts", ["yindu-1", "yindu-2", config.get("reserved_last_account", "fei-1")]
            ),
            "download_dir": str(resolve_path(project_root, config.get("download_dir", ".workflow/downloads"))),
        },
        "assets": assets,
        "shots": shots,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic browser-workflow manifest for one chapter.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--chapter-dir", required=True, type=Path)
    parser.add_argument("--asset-index", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest = build_manifest(args.config.resolve(), args.chapter_dir, args.asset_index)
    if args.output:
        output = args.output.resolve()
    else:
        config, root = load_config(args.config.resolve())
        workflow = resolve_path(root, config.get("workflow_dir", ".workflow"))
        output = workflow / "runs" / f"chapter-{manifest['chapter']['number']}" / "manifest.json"
    atomic_write_json(output, manifest)
    print(json.dumps({"ok": True, "output": str(output), "assets": len(manifest["assets"]), "shots": len(manifest["shots"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
