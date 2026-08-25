from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

from workflow_common import PACKAGE_FILES, chapter_number_from_name, load_config, resolve_path


def check_backend() -> dict[str, object]:
    cv2_available = importlib.util.find_spec("cv2") is not None
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    helper = Path(__file__).with_name("playwright_video_backend.cjs")
    bundled_node = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "node" / "bin" / "node.exe"
    playwright = helper.is_file() and (bool(shutil.which("node")) or bundled_node.is_file())
    return {
        "cv2": cv2_available,
        "ffmpeg": ffmpeg,
        "ffprobe": ffprobe,
        "playwright": playwright,
        "usable": cv2_available or bool(ffmpeg) or playwright,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight the web storyboard project without consuming service quota.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--initialize", action="store_true", help="Create workflow, download, rejected, and run directories.")
    parser.add_argument("chapters", nargs="+", type=Path)
    args = parser.parse_args()

    config, project_root = load_config(args.config.resolve())
    errors: list[str] = []
    warnings: list[str] = []
    max_chapters = int(config.get("max_chapters_per_run", 2))
    if not 1 <= len(args.chapters) <= max_chapters:
        errors.append(f"Expected 1-{max_chapters} chapters, received {len(args.chapters)}")

    if not project_root.is_dir():
        errors.append(f"Project root does not exist: {project_root}")

    image_dir = resolve_path(project_root, config["image_dir"])
    if not image_dir.is_dir():
        errors.append(f"Image directory does not exist: {image_dir}")

    workflow_dir = resolve_path(project_root, config["workflow_dir"])
    download_dir = resolve_path(project_root, config["download_dir"])
    rejected_dir = resolve_path(project_root, config["rejected_dir"])
    if args.initialize:
        for path in (workflow_dir, download_dir, rejected_dir, workflow_dir / "runs"):
            path.mkdir(parents=True, exist_ok=True)

    chapter_results = []
    for raw_chapter in args.chapters:
        chapter_dir = raw_chapter.resolve()
        chapter_entry: dict[str, object] = {"path": str(chapter_dir)}
        if not chapter_dir.is_dir():
            errors.append(f"Chapter directory does not exist: {chapter_dir}")
            chapter_results.append(chapter_entry)
            continue
        try:
            number = chapter_number_from_name(chapter_dir.name)
            chapter_entry["number"] = number
        except ValueError as exc:
            errors.append(str(exc))
            chapter_results.append(chapter_entry)
            continue

        source = chapter_dir / f"{chapter_dir.name}.txt"
        chapter_entry["source"] = str(source)
        chapter_entry["source_readable"] = source.is_file() and source.stat().st_size > 0
        if not chapter_entry["source_readable"]:
            errors.append(f"Readable chapter source missing: {source}")

        asset_dir = chapter_dir / config["asset_dir_name"]
        missing_package = [name for name in PACKAGE_FILES if not (asset_dir / name).is_file()]
        chapter_entry["asset_dir"] = str(asset_dir)
        chapter_entry["package_complete"] = not missing_package
        chapter_entry["missing_package_files"] = missing_package
        chapter_results.append(chapter_entry)

    free_bytes = shutil.disk_usage(project_root).free if project_root.exists() else 0
    minimum_free = int(config.get("minimum_free_bytes", 5 * 1024**3))
    if free_bytes < minimum_free:
        errors.append(f"Free space {free_bytes} is below configured minimum {minimum_free}")

    backend = check_backend()
    if not backend["usable"]:
        errors.append("Neither OpenCV, ffmpeg, nor the bundled Playwright video backend is available")
    elif not backend["ffmpeg"] and backend["cv2"]:
        warnings.append("ffmpeg is absent; OpenCV will be used as the video backend")
    elif not backend["ffmpeg"]:
        warnings.append("ffmpeg and OpenCV are absent; bundled Playwright will be used for local video validation and tail extraction")

    report = {
        "ok": not errors,
        "project_root": str(project_root),
        "image_dir": str(image_dir),
        "workflow_dir": str(workflow_dir),
        "download_dir": str(download_dir),
        "free_bytes": free_bytes,
        "video_backend": backend,
        "browser_check": "Run through the Codex browser skill; this script never inspects browser sessions.",
        "chapters": chapter_results,
        "warnings": warnings,
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
