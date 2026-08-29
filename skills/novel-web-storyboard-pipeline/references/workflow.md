# Workflow state machine

## Scope

One run accepts one or two explicit chapter directories. It never scans every chapter and decides to process them automatically.

## State order

Direct-package route:

`package_pending` -> `package_valid` -> `assets_resolving` -> `images_generating` -> `images_ready` -> `video_ready` -> `video_submitted` -> `video_downloaded` -> `video_valid` -> `complete`

Doubao director route (when the user asks for chapter storyboard prompts or end-to-end generation from source text):

`director_prompt_pending` -> `narrative_classified` -> `reuse_ledger_ready` -> `director_prompt_submitted` -> `director_prompt_valid` -> `screenplay_derived` -> `package_valid` -> `assets_resolving` -> `images_generating` -> `images_ready` -> `video_ready` -> `video_submitted` -> `video_downloaded` -> `video_valid` -> `complete`

The canonical director response is stored in `07-seedance-2-fast-prompts.md`; `10-资产复用台账.md` records the chapter classification and accepted existing character, prop, and location assets. Do not permit asset or video submission while the canonical director prompt is absent, structurally incomplete, or not yet saved.

## SQLite state keys

State rows are internally keyed as `<chapter>:<asset-or-shot-id>`. Whenever an ID is recorded after the initial manifest import, pass `--chapter <number>` to `state_cli.py set-asset` or `set-shot`. This is mandatory for ordinary short IDs because names such as `LOOK-002-P01` recur across chapters; never let a cross-chapter ambiguity block a completed asset or update the wrong row.

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

When a recovery launch creates the only normal `about:blank` user tab, leave that tab unclaimed as the browser keepalive. Create a separate agent tab for the work and mark it for handoff while production is unfinished. Do not let automatic agent-tab cleanup become the last remaining tab and terminate the signed-in Chrome process.

### Browser control unresponsive despite visible tabs

This is a separate condition from a stale tab, failed upload, logout, or disabled extension: `browser.user.openTabs()` / `tabs.list()` returns current Chrome tabs, but `tabs.get()`, `claimTab()`, a title/read, click, or screenshot request times out or resets the control channel.

Handle it once and only once per dependency chain:

1. Preserve every existing Chrome tab and record `browser_control_unresponsive` with the last successful tab list; do not infer that the web generation failed.
2. Wait two seconds, create a fresh browser binding, name the session, and make one lightweight tab-list call.
3. Make every probe atomic: one call to acquire a tab, then a separate call for a title or URL read, then a separate page snapshot only after the title/URL is returned. Never combine claim, navigation, page-load waiting, title, snapshot, screenshot, or click in one request; a slow but healthy page load must not be recorded as a dead channel.
4. If claiming a listed user tab alone fails, do not claim it again. Keep it open and create exactly one agent tab with `tabs.new()` in the same configured `Default` / `用户1` Chrome window. Probe that new tab with a separate title-or-URL read before any navigation. This is the preferred fallback because it retains all signed-in profile state while bypassing a stale user-tab claim bridge.
5. If that new-tab probe fails, open at most one new Chrome `Default` / `用户1` window without closing any existing tab, wait two seconds, then repeat the atomic title-or-URL probe on the new tab. Do not upload, paste, submit, download, or alter account state before this probe succeeds.
6. If the atomic safe probe fails, stop all browser calls for this dependency in the current run. Continue purely local, non-browser preparation if any remains; otherwise preserve the manifest/state and return `retryable` for the next explicit continuation.

Never repeatedly claim the same tab, repeatedly open windows, recommend uninstalling/reinstalling the browser extension, ask the user to sign in, or re-run image/video submission merely because this state occurred. The next continuation starts with one clean bounded recovery rather than replaying the old failed handle.

If Chrome, the selected `Default` / `用户1` profile, the enabled extension, and the native-host manifest all pass their read-only diagnostics but page-level operations still time out after one fresh-window recovery, classify the failure as `browser_page_control_unresponsive`. It is not an authentication, image, upload, model, or generation failure. Record the timestamp and last successful page title, retain all tabs and local run state, and end browser work for that dependency without proposing extension uninstall/reinstall or repeating any uncertain web action. A later explicit continuation may make one new bounded recovery attempt.

Keep slow browser operations separate so each result can be observed. Use the visible Doubao `+` button and one file-chooser batch in manifest order first; after upload, verify the full visible attachment strip before entering the prompt. Do not use hidden file inputs or uncontrolled native file selection. If the verified chooser flow cannot emit a chooser event after Chrome's **Allow access to file URLs** setting has been checked, use the user-authorized recovery path: copy one manifest binding, paste it into the unchanged Doubao composer, then verify the thumbnail count increased by exactly one before copying the next binding. Preserve `@图片1` to `@图片N` order and never repeat an uncertain paste. A timeout or closed control pipe means the result is unknown, not failed: reconnect and inspect first. Retry only when the expected strip is proven absent.

For a fully loaded ChatGPT or Doubao page, use a browser-operation budget of at least 60 seconds for DOM snapshots, locator reads, clicks, typing, and uploads; do not pass a 10-second outer control timeout to a page operation. Treat generation completion as a separate long wait/polling phase, not as a reason to shorten the page-control budget. A failure that lands exactly at a self-selected timeout must first be classified as `control_budget_exhausted` and retried once with the appropriate longer budget before being called a browser failure.

When system file-copy paste is unavailable, a controlled tab may expose its own attachment clipboard. Write the original accepted image bytes to that browser clipboard as an `image/png` attachment, focus the already-visible composer, issue exactly one DOM-based `Ctrl+V`, then inspect the attachment strip before doing anything else. Treat a transport-pipe close during that paste as an unknown outcome, not a failed upload: retain the source file, reconnect once, and inspect whether the attachment arrived. Never paste the same asset a second time until absence is proven, never fall back to creating a `副本` merely for transfer, and do not repeat the failing native file-chooser probe in the same dependency chain.

Upload the original accepted assets. Do not create `副本`, compressed, or transfer images merely to work around browser upload behavior. Create a transfer copy only after a verified file-chooser size/type rejection, retain the original unchanged, record the mapping, and delete the temporary transfer copy after the shot is successfully downloaded.

## Retries

- Image rejection: start another fresh ChatGPT conversation for character assets. Stop after `image_retry_limit`.
- Video page failure: inspect visible state, then retry only if no job is active and duplication is ruled out. Stop after `video_retry_limit`.
- Account limit: switch to another non-reserved account; use the reserved account last.
- Login/CAPTCHA/model removal: stop cleanly and preserve state.

## Completion

Write `<chapter>/镜头/完成报告.md` and `完成报告.json`. Include expected and actual shot counts, total measured duration, tail frames, reused/generated images, account usage, retries, and unresolved failures.

Completion is a hard acceptance gate, not merely a file-count check. Review every shot in sequence at normal speed and sample key frames for: finished dialogue; identity and costume continuity; readable anatomy; no body, robe, limb, weapon, mount, prop, or ground-plane intersection; no unintended disappearance, duplication, jump, or spatial contradiction; and a clean beginning and ending state for every direct continuation.

For each battle setup, attack, impact, aftermath, and spectacle reveal, verify readable cause and effect plus high-energy presentation: substantial layered VFX, directional light, volumetric depth, contact/pressure effects, environmental deformation, debris, scale contrast, and a camera response proportionate to the action. Reject calm, flat, sparse, cheap-looking, or glow-only action even when the action technically occurs.

Log each rejection with shot ID, time range, evidence, defect class, and repair decision. Preserve the canonical original. When the defect is isolated and both surrounding states are usable, generate only a short bridge/replacement clip for that interval, named `<chapter>-<shot>-局部重制-v<version>-<start>-<end>.mp4`; its prompt must lock the incoming and outgoing state, edit in/out points, and only the missing action. Mark it as an editorial insert in the report. When the issue affects continuity, dialogue timing across the shot, multiple frames, or the shot's core dramatic beat, regenerate the entire shot as `<chapter>-<shot>-重制-v<version>.mp4`. Never overwrite or delete prior variants.

If a returned video duration differs from the manifest by more than one frame, classify it as a model-output mismatch. Preserve the returned file under a diagnostic name and regenerate the shot; do not silently trim or stretch it into the canonical `<chapter>-<shot>.mp4` output. Include every mismatch and any manual exception in the completion report.
