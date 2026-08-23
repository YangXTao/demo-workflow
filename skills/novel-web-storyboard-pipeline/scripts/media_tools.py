from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _cv2() -> Any:
    try:
        import cv2

        return cv2
    except ImportError:
        return None


def inspect_video(path: Path) -> dict[str, Any]:
    cv2 = _cv2()
    if cv2 is not None:
        capture = cv2.VideoCapture(str(path))
        try:
            frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = float(capture.get(cv2.CAP_PROP_FPS))
            readable, _ = capture.read()
            return {
                "path": str(path),
                "readable": bool(readable),
                "size_bytes": path.stat().st_size,
                "frames": frames,
                "fps": fps,
                "duration_seconds": frames / fps if frames > 0 and fps > 0 else None,
                "width": int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "backend": "opencv",
            }
        finally:
            capture.release()
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("Neither OpenCV nor ffprobe is available")
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "stream=width,height,nb_frames,r_frame_rate:format=duration,size", "-of", "json", str(path)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    payload = json.loads(result.stdout)
    stream = (payload.get("streams") or [{}])[0]
    fmt = payload.get("format") or {}
    return {
        "path": str(path),
        "readable": True,
        "size_bytes": int(fmt.get("size", path.stat().st_size)),
        "frames": int(stream["nb_frames"]) if str(stream.get("nb_frames", "")).isdigit() else None,
        "fps": stream.get("r_frame_rate"),
        "duration_seconds": float(fmt["duration"]) if fmt.get("duration") else None,
        "width": stream.get("width"),
        "height": stream.get("height"),
        "backend": "ffprobe",
    }


def extract_tail(input_path: Path, output_path: Path, force: bool = False) -> dict[str, Any]:
    if output_path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2 = _cv2()
    if cv2 is not None:
        capture = cv2.VideoCapture(str(input_path))
        last = None
        try:
            frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            if frame_count > 0:
                capture.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
                ok, frame = capture.read()
                if ok:
                    last = frame
            if last is None:
                capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                while True:
                    ok, frame = capture.read()
                    if not ok:
                        break
                    last = frame
        finally:
            capture.release()
        if last is None:
            raise ValueError(f"No readable frame in {input_path}")
        ok, encoded = cv2.imencode(".png", last)
        if not ok:
            raise RuntimeError("OpenCV could not encode the tail frame")
        encoded.tofile(str(output_path))
        return {"ok": True, "input": str(input_path), "output": str(output_path), "backend": "opencv"}
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("Neither OpenCV nor ffmpeg is available")
    subprocess.run(
        [ffmpeg, "-y" if force else "-n", "-sseof", "-0.1", "-i", str(input_path), "-frames:v", "1", str(output_path)],
        check=True,
        capture_output=True,
    )
    return {"ok": True, "input": str(input_path), "output": str(output_path), "backend": "ffmpeg"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect downloaded videos and extract Unicode-safe PNG tail frames.")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("input", type=Path)
    tail = sub.add_parser("extract-tail")
    tail.add_argument("input", type=Path)
    tail.add_argument("output", type=Path)
    tail.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not args.input.exists():
        parser.error(f"Input does not exist: {args.input}")
    result = inspect_video(args.input.resolve()) if args.command == "inspect" else extract_tail(args.input.resolve(), args.output.resolve(), args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
