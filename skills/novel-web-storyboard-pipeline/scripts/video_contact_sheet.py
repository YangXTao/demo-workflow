"""Create a compact visual contact sheet from one or more local videos."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def frame_at(cap: cv2.VideoCapture, index: int) -> np.ndarray:
    cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError(f"cannot read frame {index}")
    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("videos", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--frames", type=int, default=6)
    args = parser.parse_args()

    rows: list[np.ndarray] = []
    for video in args.videos:
        cap = cv2.VideoCapture(str(video))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total < 1:
            raise RuntimeError(f"cannot open {video}")
        indices = np.linspace(0, total - 1, args.frames, dtype=int)
        frames = [frame_at(cap, int(index)) for index in indices]
        cap.release()
        height = min(frame.shape[0] for frame in frames)
        resized = [cv2.resize(frame, (round(frame.shape[1] * height / frame.shape[0]), height)) for frame in frames]
        label = np.full((44, sum(frame.shape[1] for frame in resized), 3), 245, dtype=np.uint8)
        cv2.putText(label, video.stem, (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 2, cv2.LINE_AA)
        rows.append(np.vstack((label, np.hstack(resized))))

    width = max(row.shape[1] for row in rows)
    padded = [cv2.copyMakeBorder(row, 0, 0, 0, width - row.shape[1], cv2.BORDER_CONSTANT, value=(245, 245, 245)) for row in rows]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(".png", np.vstack(padded))
    if not ok:
        raise RuntimeError("cannot encode contact sheet")
    args.output.write_bytes(encoded.tobytes())


if __name__ == "__main__":
    main()
