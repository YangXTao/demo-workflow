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

Run `scripts/validate_shot_assets.py --manifest <manifest> --shot <SG-ID>` immediately before upload. Do not submit if any binding path is absent, any binding is unresolved, or its manifest asset still has `pending_generation` status. A predicted output filename is not an existing asset.

Upload one image at a time. Never batch multiple binary clipboard items into one paste; Doubao can close the browser-control channel before returning an outcome. After each upload, count the visible attachments and verify their order. If the browser action times out or the control connection closes, treat the outcome as unknown: reconnect and inspect the attachments before any retry. Never paste the same image again until the previous attempt is proven absent.

Doubao may render two identical thumbnails from one clipboard paste. When the just-uploaded asset appears twice, remove only the later duplicate and verify that one copy remains in the intended order before uploading the next image.

After upload or submission, inspect any visible confirmation dialog. When `doubao.auto_confirm_generation_dialogs` is enabled and the dialog only confirms using the uploaded materials or continuing the already-authorized video generation, click its confirm button automatically. Do not auto-confirm login, CAPTCHA, payment, purchase, permission-sharing, quota-upgrade, or materially changed generation settings.

## Submission and wait

Submit one shot at a time. Record account label, submission time, shot ID, and visible job state. Poll visible state without repeatedly clicking generate. A timeout is not proof of failure.

## Download

When the shot completes, open the watermark-free resource panel. Doubao always renumbers the newest generated result as `视频1`, so click the download button on the top `视频1` row only; never infer the target from a cumulative resource number such as `视频2` or `视频3`. Snapshot the download directory before clicking. Click once, wait for a new completed file, validate its duration and readability, then move it to `<chapter>/镜头/<chapter-number>-<shot-number>.mp4`.

## Tail frames

When the next shot is `尾帧直续`, run `scripts/media_tools.py extract-tail`. Save `<chapter-number>-<current-shot-number>-尾帧.png` in the same shot directory and bind it as the next shot's `@图片1`.

## Account rotation

Read the account label from the visible account menu. Maintain local usage, but prefer the page's actual limit signal. After the current account is exhausted, select another available account. Exclude `fei-1` until all other accounts are unavailable or exhausted. Never store passwords or authentication tokens.
