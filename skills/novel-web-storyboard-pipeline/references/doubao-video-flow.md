# Doubao website video flow

## Pre-submit gate

For the current shot, verify:

- The selected model visibly reads `Seedance 2.0 Fast`.
- Ratio visibly reads `16:9`.
- Duration visibly reads `10s` for this director-generated workflow.
- The visible account label exactly matches the current `video_account` cursor.
- Every required image exists and the count does not exceed the configured safe maximum.
- Upload order exactly matches `@图片1` through `@图片N`.
- Each binding's visual identity matches its description and referenced prompt role, not merely its filename or existence check. A character binding for 咪咪, for example, must resolve to the accepted 咪咪 asset rather than another existing creature asset.
- The prompt pasted is the complete code block for the same `SG`.
- No earlier job for the same shot is still pending.

Run `scripts/validate_shot_assets.py --manifest <manifest> --shot <SG-ID>` immediately before upload, then manually cross-check every binding's description, asset identity, and path against the prompt. Do not submit if any binding path is absent, any binding is unresolved, its role and asset identity disagree, or its manifest asset still has `pending_generation` status. A predicted output filename is not an existing asset.

Use the visible `+` material button and the browser file-chooser flow first. Start `waitForEvent("filechooser")`, then click that visible button, check `chooser.isMultiple()`, and call `chooser.setFiles()` once with all binding paths in their manifest order. This avoids duplicate thumbnails and is the verified multi-image path.

Do not click the hidden `input[type=file]` directly and do not use `locator.setInputFiles`; either action can fail to open a chooser. Do not replace this with a virtual-clipboard image paste: a Chrome control reconnect can give that paste a separate empty clipboard or close the native pipe. If the visible-button chooser itself times out or the connection closes, treat the upload as unknown, reconnect, inspect the unchanged composer for thumbnails, then create one clean Doubao video page and retry the same visible-button chooser once. Never paste or submit again before that inspection. Do not open an uncontrolled native picker or request manual file selection.

After `setFiles`, visually verify that the attachment strip has exactly the manifest's number of thumbnails and that its left-to-right order matches `@图片1` through `@图片N`. If that verification fails, remove only the unexpected attachment or restart the unsubmitted composer; never submit an ambiguous strip.

## Dialogue fit and anti-intersection gate

For every shot, submit the accepted `07` SG body unchanged. Before accepting `07`, reject any insufficient or internally contradictory SG in the same web director conversation. After acceptance, time axis, action chain, staging, stated effects, environment response, ending, and negative constraints are QC criteria only; never add, remove, or rewrite prompt text locally.

Before accepting `07`, verify that each complete spoken line and its voice direction fit the 10-second SG. Once `07` is accepted, do not add or alter a voice, rate, line, or timing instruction during video submission.

Before accepting `07`, verify that every two-or-more-character SG already defines readable staging and avoids intersection risks. Once accepted, use those details only for QC; do not add or alter staging during video submission.

After upload or submission, inspect any visible confirmation dialog. When `doubao.auto_confirm_generation_dialogs` is enabled and the dialog only confirms using the uploaded materials or continuing the already-authorized video generation, click its confirm button automatically. Do not auto-confirm login, CAPTCHA, payment, purchase, permission-sharing, quota-upgrade, or materially changed generation settings.

After an ordinary material-safety confirmation, record a shot as submitted and increment its account-use counter only when the page visibly returns the official confirmation beginning `视频生成已提交` and stating `本次使用 Seedance 2.0 Fast 生成，预计等待 5 分钟` plus the daily-quota-consumption notice. A conversational acknowledgement such as “已完整接收” or “正在生成视频” is not a job. If the confirmation closes but only that ordinary chat reply appears and, after one bounded wait, there is still no official confirmation or new resource, classify the attempt as `video_submit_unknown_no_job` and preserve the evidence without counting quota.

For the reserved tail accounts `yindu-1`, `yindu-2`, and `fei-1`, the user authorizes a bounded recovery policy for that exact no-job state: re-submit the same fully verified shot in the current conversation up to **10 total submissions**. For every retry after the first, use Doubao's edit action on the original submission and send it again; retain its already-verified attachments and do not upload the same images again. When the interface offers `重新生成` after a chat-only response, select it first and then edit and resend the original prompt; this preserves the working generation path and its verified attachments. If none creates the official acknowledgement, use a clean new conversation **in the same user-designated, proven Doubao tab/window** and repeat. Create at most **10 conversations** for that account/shot. Between every attempt inspect the visible job state and resource panel; never send again while a job may exist. After the 10-by-10 budget is exhausted, mark the shot failed for that account and stop that account's chain. This policy does not authorize retries for login, CAPTCHA, payment, quota upgrade, model removal, or changed page rules.

If Doubao reports `生成内容中疑似包含侵权 / 违规内容` and explicitly says the generation quota was not deducted, retain the failed request and mark it as a policy no-result. Do not rewrite the accepted SG locally. Continue only with an exact resubmission when the page explicitly permits it; otherwise record the blocked shot and continue independent work.

## Submission and wait

Submit one shot at a time. Record account label, submission time, shot ID, and visible job state. Poll visible state without repeatedly clicking generate. A timeout is not proof of failure.

After the official submission acknowledgement, if 7–8 minutes pass with no visible video and no explicit failure, reload the **same current Doubao tab once**. Wait for that conversation to restore, then inspect the existing submission, the visible job state, and the watermark-free resource panel. Treat the reload only as a delayed-result visibility refresh: do not click `重新生成`, edit the message, upload materials, resubmit, switch accounts, or increment the account-use counter. If the result appears after reload, download that existing result normally. If it remains absent, continue bounded inspection of the same job and only then apply `doubao.pending_stale_minutes`; the 7–8 minute refresh does not shorten the stale threshold and is not evidence of failure.

If a job remains visibly submitted for longer than `doubao.pending_stale_minutes` with no downloadable result and no failure message, preserve the old job and classify it as server-stale. Resubmit the shot once on a different non-reserved account, after repeating the full upload gate. Accept the first valid result that arrives and ignore any later duplicate. Never delete the old conversation and never resubmit more than once solely because it is slow.

## Download

When the shot completes, open the watermark-free resource panel. Doubao always renumbers the newest generated result as `视频1`, so click the download button on the top `视频1` row only; never infer the target from a cumulative resource number such as `视频2` or `视频3`. Snapshot the download directory before clicking. Click once, wait for a new completed file, validate its duration and readability, then move it to `<chapter>/镜头/<chapter-number>-<shot-number>.mp4`.

## Tail frames

When the next shot is `尾帧直续`, run `scripts/media_tools.py extract-tail`. Save `<chapter-number>-<current-shot-number>-尾帧.png` in the same shot directory and bind it as the next shot's `@图片1`.

## Battle visual QC and rework

After every chapter is downloaded, visually sample the battle setup, primary attack, impact/aftermath, and any spectacle reveal against the accepted SG. Pass only when the returned video visibly fulfills its stated action cause and effect, effect hierarchy, light, environment response, and consequences. Do not add a separate legacy or V8 acceptance gate.

For a failed battle shot, preserve the original `<chapter>-<shot>.mp4`. Re-submit the exact accepted canonical SG body with its required binding legend to obtain a new stochastic result; do not locally revise the body. Save each result as `<chapter>-<shot>-重制-v1.mp4` (increment the version for later attempts) and use that variant's tail frame for any directly continuous rework. Keep both variants; do not overwrite or delete the original.

## Whole-chapter acceptance audit and exact-prompt rework

After all canonical videos are available, review every shot in narrative order and record pass/fail. Reject a shot for unfinished dialogue, serious visual cheating, identity/costume discontinuity, anatomy failure, intersection or clipping, unwanted duplicate/disappearing subjects, broken spatial logic, or a direct-continuation state mismatch. For battle shots also reject insufficient energy layering, weak light/shadow contrast, missing physical impact, calm pacing, or an unconvincing spectacle scale.

When a returned video fails QC, preserve it and regenerate the complete SG with the exact same accepted prompt body and required image legend. Do not create a locally rewritten interval prompt or altered full-shot prompt. Save retries as `<chapter>-<shot>-重制-v<version>.mp4` and retain every version.

## Account rotation

Record the step-3 account as `director_account` and initialize `video_account = director_account`. Director-prompt generation consumes no Seedance use. Use the same account for consecutive SG submissions until it has three official `视频生成已提交` acknowledgements in the current quota cycle or the page visibly reports exhaustion. If it already used some quota before this run, use only its actual remaining quota.

Switch accounts only after the current job is resolved and downloaded or explicitly failed; never switch while submission state is pending or unknown. On every new account, visibly reselect `生成视频` → `Seedance 2.0 Fast` → `16:9` → `10s`, then continue with the next SG and the unchanged accepted prompt. The new video account does not need `Cinematic Storyboard Prompt Generator`.

After the initial director account, exhaust remaining ordinary accounts before `yindu-1` → `yindu-2` → `fei-1`; `fei-1` remains last among accounts not yet used. If the user explicitly selected a reserved account as the director account for this run, that explicit selection makes it the initial video account; this is the only exception to the normal tail order. Never store passwords or authentication tokens.
