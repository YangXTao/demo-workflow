from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
PACKAGE_FILES = [
    "01-adaptation.md",
    "02-screenplay.md",
    "03-assets.md",
    "04-gpt-image-2-prompts.md",
    "05-storyboard-video-prompts.md",
    "06-qc.md",
    "07-seedance-2-fast-prompts.md",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def resolve_path(project_root: Path, configured: str) -> Path:
    candidate = Path(configured)
    return candidate if candidate.is_absolute() else project_root / candidate


def load_config(config_path: Path) -> tuple[dict[str, Any], Path]:
    config = load_json(config_path)
    if config.get("schema_version") != 1:
        raise ValueError(f"Unsupported config schema: {config.get('schema_version')!r}")
    project_root = Path(config["project_root"]).expanduser().resolve()
    return config, project_root


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        from PIL import Image

        with Image.open(path) as image:
            return int(image.width), int(image.height)
    except Exception:
        try:
            import cv2

            image = cv2.imdecode(_read_numpy_bytes(path), cv2.IMREAD_UNCHANGED)
            if image is None:
                return None, None
            return int(image.shape[1]), int(image.shape[0])
        except Exception:
            return None, None


def _read_numpy_bytes(path: Path):
    import numpy as np

    return np.fromfile(str(path), dtype=np.uint8)


_CHINESE_DIGITS = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_CHINESE_UNITS = {"十": 10, "百": 100, "千": 1000}


def chinese_number_to_int(value: str) -> int:
    if value.isdigit():
        return int(value)
    total = 0
    current = 0
    for char in value:
        if char in _CHINESE_DIGITS:
            current = _CHINESE_DIGITS[char]
        elif char in _CHINESE_UNITS:
            unit = _CHINESE_UNITS[char]
            total += (current or 1) * unit
            current = 0
        else:
            raise ValueError(f"Unsupported Chinese numeral: {value}")
    return total + current


def chapter_number_from_name(name: str) -> int:
    match = re.search(r"第([0-9〇零一二两三四五六七八九十百千]+)章", name)
    if not match:
        raise ValueError(f"Cannot infer chapter number from: {name}")
    return chinese_number_to_int(match.group(1))


def canonical_alias(value: str, aliases: dict[str, str]) -> str:
    result = value
    for source, target in aliases.items():
        result = result.replace(source, target)
    return result


def normalize_name(value: str, aliases: dict[str, str] | None = None) -> str:
    if aliases:
        value = canonical_alias(value, aliases)
    value = value.lower()
    value = re.sub(r"第[0-9〇零一二两三四五六七八九十百千]+章", "", value)
    value = re.sub(r"(三视图|四视图|形象|设定图|概念图|图片|资产|道具|场景)", "", value)
    value = re.sub(r"[\s\-_—–·|()（）\[\]【】,，.。:：'\"]+", "", value)
    return value


def sanitize_filename(value: str) -> str:
    value = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "-", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value or "unnamed"


def versioned_path(path: Path) -> Path:
    if not path.exists():
        return path
    index = 2
    while True:
        candidate = path.with_name(f"{path.stem}-v{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def code_block_after(section: str, heading: str | None = None) -> str:
    source = section
    if heading and heading in source:
        source = source.split(heading, 1)[1]
    match = re.search(r"```(?:text)?\s*\n(.*?)\n```", source, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def split_markdown_h2(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", text))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group(1).strip(), text[match.end():end].strip()))
    return sections
