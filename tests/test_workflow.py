from __future__ import annotations

import base64
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills" / "novel-web-storyboard-pipeline" / "scripts"
SKILL_ROOT = REPO / "skills" / "novel-web-storyboard-pipeline"
sys.path.insert(0, str(SCRIPTS))

from build_run_manifest import _best_existing, _eligible_assets_for_shot, _match_binding, build_manifest  # noqa: E402
from download_watch import promote, snapshot  # noqa: E402
from image_tools import normalize_png  # noqa: E402
from media_tools import extract_tail, inspect_video  # noqa: E402
from state_cli import initialize, record_account, set_shot, summary  # noqa: E402
from validate_shot_assets import validate_shot_assets  # noqa: E402
from workflow_common import chapter_number_from_name, chinese_number_to_int  # noqa: E402


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class WorkflowTests(unittest.TestCase):
    def test_chinese_chapter_numbers(self) -> None:
        self.assertEqual(chinese_number_to_int("二十八"), 28)
        self.assertEqual(chinese_number_to_int("一百零二"), 102)
        self.assertEqual(chapter_number_from_name("第二十八章"), 28)

    def test_asset_matching_ignores_extension_and_chinese_punctuation(self) -> None:
        index = {
            "assets": [
                {"filename": "沈青梧-三视图.png", "path": "C:/assets/沈青梧-三视图.png"},
                {"filename": "万宗大会环形广场-投影高台与城北远景-第28章-场景图.png", "path": "C:/assets/scene.png"},
            ]
        }
        look = {"title": "沈青梧", "kind": "CHAR", "reference_files": []}
        scene = {"title": "万宗大会环形广场、投影高台与城北远景", "kind": "LOC", "reference_files": []}
        self.assertEqual(_best_existing(look, index, {}), "C:/assets/沈青梧-三视图.png")
        self.assertEqual(_best_existing(scene, index, {}), "C:/assets/scene.png")

    def test_binding_candidates_are_limited_to_applicable_shot(self) -> None:
        assets = [
            {"asset_id": "PROP-001-P01", "applicable_shots": ["SG-015"]},
            {"asset_id": "CHAR-005-P01", "applicable_shots": ["SG-002"]},
            {"asset_id": "LOC-001-P01", "applicable_shots": []},
        ]
        eligible = _eligible_assets_for_shot(assets, "SG-015")
        self.assertEqual([item["asset_id"] for item in eligible], ["PROP-001-P01", "LOC-001-P01"])

    def test_binding_prefers_explicit_identity_over_generic_reference_sheet_words(self) -> None:
        assets = [
            {"asset_id": "CHAR-003", "title": "青鸾 青鸾-三视图", "purpose": "existing accepted reusable asset"},
            {"asset_id": "CHAR-004-P01", "title": "守衣银蛟", "purpose": "东方无翼蛟龙三视图"},
        ]
        result = _match_binding("青鸾三视图，只锁定翠绿青蓝羽、银白喙与赤金羽纹。", assets, {})
        self.assertIsNotNone(result)
        self.assertEqual(result["asset_id"], "CHAR-003")

    def _fixture(self, root: Path) -> tuple[Path, Path, Path]:
        project = root / "小说"
        image_dir = project / "图片"
        chapter = project / "第二十八章"
        asset_dir = chapter / "资产"
        image_dir.mkdir(parents=True)
        asset_dir.mkdir(parents=True)
        identity = image_dir / "甲-三视图.png"
        identity.write_bytes(PNG_1X1)
        (asset_dir / "04-gpt-image-2-prompts.md").write_text(
            """# prompts
## CHAR-001-P01 | 甲
- Model: gpt-image-2
- Quality: high
- Size: 1536x1024
- 用途：锁定甲。
- 适用分镜：SG-001、SG-002。
- 输入参考：上传`甲-三视图.png`。
### 可直接复制提示词
```text
character prompt
```
## LOC-002-P01 | 山门
- Model: gpt-image-2
- Quality: high
- Size: 1536x1024
- 用途：山门空间。
- 适用分镜：SG-001、SG-002。
### 可直接复制提示词
```text
location prompt
```
""",
            encoding="utf-8",
        )
        (asset_dir / "03-assets.md").write_text(
            """# 资产\n\n|ID|资产/境界状态|来源与文件|连续性锁|适用|\n|---|---|---|---|---|\n""",
            encoding="utf-8",
        )
        (asset_dir / "07-seedance-2-fast-prompts.md").write_text(
            """# shots
## SG-001 | duration=6.0s | Seedance 2.0 Fast 直投
```text
【豆包图片素材绑定】
- @图片1：锁定角色甲的同一张脸。
- @图片2：锁定山门空间。
【首帧与上镜承接】
章节开场。
```
## SG-002 | duration=8.0s | Seedance 2.0 Fast 直投
```text
【豆包图片素材绑定】
- @图片1：上传上一段视频最后一帧。
- @图片2：锁定角色甲的同一张脸。
【首帧与上镜承接】
尾帧直续。
```
""",
            encoding="utf-8",
        )
        config = root / "config.json"
        config.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_root": str(project),
                    "image_dir": "图片",
                    "asset_dir_name": "资产",
                    "shot_dir_name": "镜头",
                    "workflow_dir": ".workflow",
                    "download_dir": ".workflow/downloads",
                    "account_generation_limit": 3,
                    "reserved_last_account": "fei-1",
                    "reserved_tail_accounts": ["yindu-1", "yindu-2", "fei-1"],
                    "doubao": {"model": "Seedance 2.0 Fast", "ratio": "16:9", "max_images_per_shot": 9},
                    "chatgpt": {"model": "gpt-image-2"},
                    "aliases": {},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        index = root / "index.json"
        index.write_text(json.dumps({"assets": [{"name": identity.name, "path": str(identity)}]}, ensure_ascii=False), encoding="utf-8")
        return config, chapter, index

    def test_manifest_and_tail_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as value:
            config, chapter, index = self._fixture(Path(value))
            manifest = build_manifest(config, chapter, index)
            self.assertEqual(manifest["chapter"]["number"], 28)
            self.assertEqual(len(manifest["shots"]), 2)
            self.assertEqual(manifest["assets"][0]["status"], "generated")
            self.assertTrue(manifest["shots"][0]["tail_frame_required"])
            self.assertEqual(manifest["shots"][1]["bindings"][0]["source"], "previous_tail_frame")
            self.assertTrue(manifest["shots"][1]["bindings"][0]["path"].endswith("28-1-尾帧.png"))
            self.assertEqual(manifest["settings"]["reserved_tail_accounts"], ["yindu-1", "yindu-2", "fei-1"])

    def test_resumable_state(self) -> None:
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            config, chapter, index = self._fixture(root)
            manifest = build_manifest(config, chapter, index)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            db = root / "state.sqlite"
            initialize(db, manifest_path)
            set_shot(db, "SG-001", "downloaded", "account-a", str(root / "28-1.mp4"), None, 28)
            record_account(db, "account-a", 1, False, False)
            report = summary(db)
            self.assertIn({"status": "downloaded", "count": 1}, report["shots"])
            accounts = {item["account"]: item for item in report["accounts"]}
            self.assertEqual(accounts["account-a"]["used"], 1)
            for account in ("yindu-1", "yindu-2", "fei-1"):
                self.assertEqual(accounts[account]["reserved"], 1)

    def test_video_gate_rejects_pending_and_missing_assets(self) -> None:
        with tempfile.TemporaryDirectory() as value:
            config, chapter, index = self._fixture(Path(value))
            manifest = build_manifest(config, chapter, index)
            report = validate_shot_assets(manifest, "SG-001")
            self.assertFalse(report["ok"])
            self.assertTrue(any("pending_generation" in error for error in report["errors"]))
            self.assertTrue(any("does not exist" in error for error in report["errors"]))

    def test_video_gate_accepts_resolved_files(self) -> None:
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            config, chapter, index = self._fixture(root)
            manifest = build_manifest(config, chapter, index)
            location = root / "location.png"
            location.write_bytes(PNG_1X1)
            location_asset = next(item for item in manifest["assets"] if item["asset_id"] == "LOC-002-P01")
            location_asset["status"] = "generated"
            location_asset["output_path"] = str(location)
            manifest["shots"][0]["bindings"][1]["path"] = str(location)
            report = validate_shot_assets(manifest, "SG-001")
            self.assertTrue(report["ok"], report["errors"])

    def test_download_promotion_is_non_destructive(self) -> None:
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            source = root / "download.mp4"
            source.write_bytes(b"video")
            before = snapshot(root)
            self.assertIn(str(source.resolve()), before["files"])
            destination = root / "28-1.mp4"
            destination.write_bytes(b"old")
            promoted = promote(source, destination)
            self.assertEqual(promoted.name, "28-1-v2.mp4")
            self.assertEqual(destination.read_bytes(), b"old")

    def test_image_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            source = root / "browser-download.webp"
            source.write_bytes(PNG_1X1)
            destination = root / "accepted.png"
            result = normalize_png(source, destination)
            self.assertTrue(result["ok"])
            self.assertEqual(destination.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_video_inspection_and_tail_frame(self) -> None:
        try:
            import cv2
            import numpy as np
        except ImportError:
            self.skipTest("OpenCV is not installed")
        with tempfile.TemporaryDirectory() as value:
            root = Path(value)
            video = root / "shot.mp4"
            writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"mp4v"), 5.0, (32, 24))
            if not writer.isOpened():
                self.skipTest("OpenCV mp4v encoder is unavailable")
            try:
                writer.write(np.full((24, 32, 3), (0, 0, 255), dtype=np.uint8))
                writer.write(np.full((24, 32, 3), (0, 255, 0), dtype=np.uint8))
            finally:
                writer.release()
            report = inspect_video(video)
            self.assertTrue(report["readable"])
            tail = root / "shot-tail.png"
            extract_tail(video, tail)
            self.assertTrue(tail.is_file())

    def test_scripts_compile(self) -> None:
        scripts = [str(path) for path in SCRIPTS.glob("*.py")]
        result = subprocess.run([sys.executable, "-m", "py_compile", *scripts], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unified_cinematic_knowledge_base_is_packaged_and_routed(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        catalog = (SKILL_ROOT / "references" / "cinematic-production-knowledge-catalog.md").read_text(encoding="utf-8")
        base = SKILL_ROOT / "references" / "cinematic-seedance-production-knowledge.md"
        self.assertTrue(base.is_file())
        base_text = base.read_text(encoding="utf-8")
        self.assertGreater(len(base_text.splitlines()), 7000)
        self.assertGreater(base.stat().st_size, 600000)
        self.assertIn("cinematic-seedance-production-knowledge.md", skill)
        self.assertIn("cinematic-seedance-production-knowledge.md", catalog)
        self.assertIn("Never read `references/archive/` during production", skill)
        self.assertFalse((SKILL_ROOT / "references" / "v74-effective-knowledge-base.md").exists())
        self.assertFalse((SKILL_ROOT / "references" / "cinematic-v74-seedance-adaptation.md").exists())
        self.assertIn("16:9", base_text.split("## 保留内容", 1)[0])
        self.assertIn("fei-1", skill)
        self.assertIn("yindu-2", skill)


if __name__ == "__main__":
    unittest.main()
