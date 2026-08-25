# Workflow state machine

## Scope

One run accepts one or two explicit chapter directories. It never scans every chapter and decides to process them automatically.

## State order

`package_pending` -> `package_valid` -> `assets_resolving` -> `images_generating` -> `images_ready` -> `video_ready` -> `video_submitted` -> `video_downloaded` -> `video_valid` -> `complete`

Failures use `retryable`, `blocked`, or `failed`. Store the last visible evidence and error reason. A restart must verify the filesystem before trusting a stored success state.

## Chapter package

The configured asset directory must contain:

1. `01-adaptation.md`
2. `02-screenplay.md`
3. `03-assets.md`
4. `04-gpt-image-2-prompts.md`
5. `05-storyboard-video-prompts.md`
6. `06-qc.md`
7. `07-seedance-2-fast-prompts.md`

Call `novel-chapter-3d-pipeline` when any file is missing or the package validator fails. Do not rewrite a valid package without user direction.

## Asset resolution

Build an index from the configured global image directory. Resolution order:

1. Explicit filename in the prompt package.
2. Configured alias plus explicit filename.
3. Canonical asset name and matching kind.
4. Visual inspection of a conservative candidate.
5. Generate a new asset.

An existing identity master does not automatically satisfy a new clothing, injury, projection, activation, or damage state. When a prompt changes a visible state, generate a state-specific image using the master as reference.

## Shot dependencies

- `章节开场`: no previous tail frame.
- `尾帧直续`: previous accepted video is a hard dependency; its tail frame is `@图片1`.
- `匹配切`: no tail frame; rely on the prompt's matching direction, framing, light, or sound.
- `时空硬切`: no tail frame.

Process independent shots after a blocked branch only when their required assets and previous-state assumptions remain valid.

## Dialogue pacing and multi-character staging

Before production, compare every spoken line with the group duration. Do not shorten, cut off, or replace approved dialogue merely to fit a 10-second-or-shorter shot. When ordinary delivery will overrun, the Seedance prompt must specify the locked voice, the complete line, and controlled accelerated delivery, normally 1.10–1.50x chosen for dialogue density, emotion, and intelligibility. Keep consonants and emotional intent intelligible; the generated clip may be retimed in editorial. If even controlled acceleration cannot make the line intelligible, split the dramatic beat into additional storyboard groups before submission rather than accepting an unfinished line.

For a multi-character prompt, define stable screen placement before defining action: foreground/midground/background or left/center/right, each actor's movement lane, and the camera axis. Stagger entries, attacks, landings, and reactions in time and depth. Use inserts, cutaways, or shot/reverse-shot for handoffs, pets, weapons, and close-range exchanges. Prohibit body overlap, intersecting robes or weapons, shared landing positions, and actors passing through one another; do not rely on dense effects to hide a collision.

## Downloads

Before clicking download, run `scripts/download_watch.py snapshot`. After the click, use `scripts/download_watch.py wait` and accept only a newly created completed file. Ignore `.crdownload`, zero-byte files, and old files. Validate it, then use `scripts/download_watch.py promote` to move it to the expected chapter shot path. Never select a file merely because it is newest before the download action.

## Browser recovery and upload uncertainty

Website authentication and browser-control state are independent. If a controlled tab becomes stale or explicitly disconnects, keep the signed-in browser session, discard the stale tab binding, and obtain one fresh controlled tab. Do not repeatedly reuse a failed handle or ask the user to sign in when the fresh tab visibly remains authenticated.

At recovery and between shots, close only confirmed stale, blank, error, or duplicate agent-created tabs. Keep a normal user-created Chrome tab open at all times, and use `browser.user.openTabs()` plus `claimTab()` to resume that tab after a control reconnect; agent-created tabs are ephemeral and are not a durable checkpoint. Never close the browser's final tab merely to clean up; navigate or reuse it first so cleanup does not terminate the signed-in browser process.

If Chrome is not running or the extension instance is absent, launch the configured browser profile once, wait for it to initialize, then reconnect and claim a currently listed user tab. For this project the configured profile is Chrome `Default` / visible label `用户1`; do not silently switch profiles. A stale control binding does not imply an expired website login. If the reconnect itself fails twice, preserve the existing normal tab and record the failure rather than repeatedly opening and closing windows.

Keep slow browser operations separate so each result can be observed. Use the visible Doubao `+` button and one file-chooser batch in manifest order; after upload, verify the full visible attachment strip before entering the prompt. Do not use binary clipboard paste, hidden file inputs, or native manual file selection. A timeout or closed control pipe means the result is unknown, not failed: reconnect and inspect first. Retry only when the expected strip is proven absent.

Upload the original accepted assets. Do not create `副本`, compressed, or transfer images merely to work around browser upload behavior. Create a transfer copy only after a verified file-chooser size/type rejection, retain the original unchanged, record the mapping, and delete the temporary transfer copy after the shot is successfully downloaded.

## Retries

- Image rejection: start another fresh ChatGPT conversation for character assets. Stop after `image_retry_limit`.
- Video page failure: inspect visible state, then retry only if no job is active and duplication is ruled out. Stop after `video_retry_limit`.
- Account limit: switch to another non-reserved account; use the reserved account last.
- Login/CAPTCHA/model removal: stop cleanly and preserve state.

## Completion

Write `<chapter>/镜头/完成报告.md` and `完成报告.json`. Include expected and actual shot counts, total measured duration, tail frames, reused/generated images, account usage, retries, and unresolved failures.

If a returned video duration differs from the manifest by more than one frame, classify it as a model-output mismatch. Preserve the returned file under a diagnostic name and regenerate the shot; do not silently trim or stretch it into the canonical `<chapter>-<shot>.mp4` output. Include every mismatch and any manual exception in the completion report.
