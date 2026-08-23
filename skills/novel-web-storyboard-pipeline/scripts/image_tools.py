from __future__ import annotations

import argparse
import json
from pathlib import Path


def normalize_png(source: Path, destination: Path, force: bool = False) -> dict[str, object]:
    if destination.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image

        with Image.open(source) as image:
            image.load()
            if image.mode not in {"RGB", "RGBA"}:
                image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            image.save(destination, format="PNG", optimize=True)
            width, height = image.size
        backend = "pillow"
    except ImportError:
        import cv2
        import numpy as np

        data = np.fromfile(str(source), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError(f"Unreadable image: {source}")
        ok, encoded = cv2.imencode(".png", image)
        if not ok:
            raise RuntimeError("OpenCV could not encode PNG")
        encoded.tofile(str(destination))
        height, width = image.shape[:2]
        backend = "opencv"
    return {"ok": True, "source": str(source), "output": str(destination), "width": width, "height": height, "backend": backend}


def main() -> int:
    parser = argparse.ArgumentParser(description="Decode a browser image download and save a real PNG without overwriting by default.")
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not args.source.is_file():
        parser.error(f"Source does not exist: {args.source}")
    print(json.dumps(normalize_png(args.source.resolve(), args.destination.resolve(), args.force), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
