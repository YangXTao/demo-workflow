# Doubao website video flow

## Pre-submit gate

For the current shot, verify:

- The selected model visibly reads `Seedance 2.0 Fast`.
- Ratio visibly reads `16:9`.
- Duration matches the manifest.
- Every required image exists and the count does not exceed the configured safe maximum.
- Upload order exactly matches `@图片1` through `@图片N`.
- The prompt pasted is the complete code block for the same `SG`.
- No earlier job for the same shot is still pending.

## Submission and wait

Submit one shot at a time. Record account label, submission time, shot ID, and visible job state. Poll visible state without repeatedly clicking generate. A timeout is not proof of failure.

## Download

When the shot completes, open the watermark-free resource panel. Doubao always renumbers the newest generated result as `视频1`, so click the download button on the top `视频1` row only; never infer the target from a cumulative resource number such as `视频2` or `视频3`. Snapshot the download directory before clicking. Click once, wait for a new completed file, validate its duration and readability, then move it to `<chapter>/镜头/<chapter-number>-<shot-number>.mp4`.

## Tail frames

When the next shot is `尾帧直续`, run `scripts/media_tools.py extract-tail`. Save `<chapter-number>-<current-shot-number>-尾帧.png` in the same shot directory and bind it as the next shot's `@图片1`.

## Account rotation

Read the account label from the visible account menu. Maintain local usage, but prefer the page's actual limit signal. After the current account is exhausted, select another available account. Exclude `fei-1` until all other accounts are unavailable or exhausted. Never store passwords or authentication tokens.
