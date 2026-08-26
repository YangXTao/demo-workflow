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

Use the visible `+` material button and the browser file-chooser flow first. Start `waitForEvent("filechooser")`, then click that visible button, check `chooser.isMultiple()`, and call `chooser.setFiles()` once with all binding paths in their manifest order. This avoids duplicate thumbnails and is the verified multi-image path.

Do not click the hidden `input[type=file]` directly and do not use `locator.setInputFiles`; either action can fail to open a chooser. Do not replace this with a virtual-clipboard image paste: a Chrome control reconnect can give that paste a separate empty clipboard or close the native pipe. If the visible-button chooser itself times out or the connection closes, treat the upload as unknown, reconnect, inspect the unchanged composer for thumbnails, then create one clean Doubao video page and retry the same visible-button chooser once. Never paste or submit again before that inspection. Do not open an uncontrolled native picker or request manual file selection.

After `setFiles`, visually verify that the attachment strip has exactly the manifest's number of thumbnails and that its left-to-right order matches `@图片1` through `@图片N`. If that verification fails, remove only the unexpected attachment or restart the unsubmitted composer; never submit an ambiguous strip.

## Dialogue fit and anti-intersection gate

For combat, spell, giant-form, disaster, army, or other spectacle shots, read `seedance-cinematic-prompt-craft.md` and apply its long-prompt gate before submission. Do not trim a structured prompt merely to make it visually short. Verify the continuous time axis, physical action chain, scale reference, VFX layers, light direction and exposure protection, environment response, exact ending, and shot-specific prohibitions. If the requested beats cannot fit the selected duration without conflicts, return the shot for splitting rather than submitting an overloaded prompt.

Before sending a spoken prompt, verify that each complete line can be delivered in the selected duration. When it cannot, retain the complete line and specify the character's locked voice plus a controlled accelerated rate of 1.10–1.50x selected for dialogue density, emotion, and intelligibility, with no trailing unfinished words. Do not reduce the duration to force a cutoff. If that rate remains insufficient, return the shot to storyboard splitting rather than submitting a line that will not finish.

Before sending any prompt with two or more characters, add explicit staging in the prompt: screen-left/center/right or foreground/midground/background positions, movement directions, separate vertical or depth lanes, and a stable camera axis. Stagger motions so only one close-range action occupies a contact zone at a time. Prefer an insert or reaction cut for a handoff, pet interaction, weapon clash, or landing. Explicitly forbid body, robe, limb, weapon, mount, and ground-plane intersection; do not use blur, smoke, white flashes, or dense particles to conceal a collision.

After upload or submission, inspect any visible confirmation dialog. When `doubao.auto_confirm_generation_dialogs` is enabled and the dialog only confirms using the uploaded materials or continuing the already-authorized video generation, click its confirm button automatically. Do not auto-confirm login, CAPTCHA, payment, purchase, permission-sharing, quota-upgrade, or materially changed generation settings.

After an ordinary material-safety confirmation, verify a **new visible Seedance job-state message or resource-panel transition** before recording the shot as submitted or incrementing the account-use counter. If the confirmation closes but the composer merely becomes an ordinary chat message and, after one bounded wait, there is still no job state and no new resource, classify the attempt as `video_submit_unknown_no_job` and preserve the evidence without counting quota.

For the reserved last-use accounts `fei-1` and `yindu-1`, the user authorizes a bounded recovery policy for that exact no-job state: re-submit the same fully verified shot in the current conversation up to **10 total submissions**; if none creates a visible job, use a clean new conversation and repeat. Create at most **10 conversations** for that account/shot. Between every attempt inspect the visible job state and resource panel; never send again while a job may exist. After the 10-by-10 budget is exhausted, mark the shot failed for that account and stop that account's chain. This policy does not authorize retries for login, CAPTCHA, payment, quota upgrade, model removal, or changed page rules.

## Submission and wait

Submit one shot at a time. Record account label, submission time, shot ID, and visible job state. Poll visible state without repeatedly clicking generate. A timeout is not proof of failure.

If a job remains visibly submitted for longer than `doubao.pending_stale_minutes` with no downloadable result and no failure message, preserve the old job and classify it as server-stale. Resubmit the shot once on a different non-reserved account, after repeating the full upload gate. Accept the first valid result that arrives and ignore any later duplicate. Never delete the old conversation and never resubmit more than once solely because it is slow.

## Download

When the shot completes, open the watermark-free resource panel. Doubao always renumbers the newest generated result as `视频1`, so click the download button on the top `视频1` row only; never infer the target from a cumulative resource number such as `视频2` or `视频3`. Snapshot the download directory before clicking. Click once, wait for a new completed file, validate its duration and readability, then move it to `<chapter>/镜头/<chapter-number>-<shot-number>.mp4`.

## Tail frames

When the next shot is `尾帧直续`, run `scripts/media_tools.py extract-tail`. Save `<chapter-number>-<current-shot-number>-尾帧.png` in the same shot directory and bind it as the next shot's `@图片1`.

## Battle visual QC and rework

After every chapter is downloaded, visually sample the battle setup, primary attack, impact/aftermath, and any spectacle reveal. Pass only when the shots show readable action cause and effect plus a cinematic hierarchy of energy: substantial volumetric light, environmental reaction, layered particles/debris, directional shock or pressure effects, and a scale contrast appropriate to the scene. A named ultimate move or heavenly spectacle must not degrade into isolated glow lines, sparse sparks, a white flash, an unlit close-up, or an explosion that ends before its environmental and character consequences are visible. Apply the full acceptance gates in `seedance-cinematic-prompt-craft.md`.

For a failed battle shot, preserve the original `<chapter>-<shot>.mp4`. Produce a revised prompt that specifies the missing scale, energy layers, light direction, environmental deformation, camera response, and prohibitions against cheap effects. Regenerate it as `<chapter>-<shot>-重制-v1.mp4` (increment the version for later attempts) and use that variant's tail frame for any directly continuous rework. Keep both variants; do not overwrite or delete the original.

## Whole-chapter acceptance audit and local repair

After all canonical videos are available, review every shot in narrative order and record pass/fail. Reject a shot for unfinished dialogue, serious visual cheating, identity/costume discontinuity, anatomy failure, intersection or clipping, unwanted duplicate/disappearing subjects, broken spatial logic, or a direct-continuation state mismatch. For battle shots also reject insufficient energy layering, weak light/shadow contrast, missing physical impact, calm pacing, or an unconvincing spectacle scale.

If the failure is confined to a short interval and the frames immediately before and after it are usable, submit a dedicated replacement interval rather than regenerating the whole shot. Use the two surrounding accepted states as first- and last-state references when supported by the current Doubao surface; otherwise state precise matching edit-in and edit-out conditions in the prompt. The interval prompt must identify the exact start/end seconds, camera axis, actor placement, and required repaired action. Save it as `<chapter>-<shot>-局部重制-v<version>-<start>-<end>.mp4`, preserve the original shot, and list it as an editorial insert rather than silently replacing the canonical file. Rebuild the full shot only when the defect spans the beat, breaks dialogue timing or continuity, or cannot cleanly rejoin both sides.

## Account rotation

Read the account label from the visible account menu. Maintain local usage, but prefer the page's actual limit signal. After the current account is exhausted, select another available account. Exclude `fei-1` and `yindu-1` until all other accounts are unavailable or exhausted, then use `fei-1` before `yindu-1`. Never store passwords or authentication tokens.
