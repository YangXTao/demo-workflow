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

## Downloads

Before clicking download, run `scripts/download_watch.py snapshot`. After the click, use `scripts/download_watch.py wait` and accept only a newly created completed file. Ignore `.crdownload`, zero-byte files, and old files. Validate it, then use `scripts/download_watch.py promote` to move it to the expected chapter shot path. Never select a file merely because it is newest before the download action.

## Browser recovery and upload uncertainty

Website authentication and browser-control state are independent. If a controlled tab becomes stale or explicitly disconnects, keep the signed-in browser session, discard the stale tab binding, and obtain one fresh controlled tab. Do not repeatedly reuse a failed handle or ask the user to sign in when the fresh tab visibly remains authenticated.

Keep slow browser operations separate so each result can be observed. After every image upload, verify the actual visible attachment count and order before the next upload. A timeout or closed control pipe means the result is unknown, not failed: reconnect and inspect first. Retry only when the attachment is proven absent; if it is present twice, remove the duplicate before continuing.

When the website's binary paste path is unstable, a temporary high-quality transfer copy is allowed. Preserve the original dimensions, leave the accepted source asset unchanged, keep a source-to-transfer mapping, and use the transfer copy only for browser upload.

## Retries

- Image rejection: start another fresh ChatGPT conversation for character assets. Stop after `image_retry_limit`.
- Video page failure: inspect visible state, then retry only if no job is active and duplication is ruled out. Stop after `video_retry_limit`.
- Account limit: switch to another non-reserved account; use the reserved account last.
- Login/CAPTCHA/model removal: stop cleanly and preserve state.

## Completion

Write `<chapter>/镜头/完成报告.md` and `完成报告.json`. Include expected and actual shot counts, total measured duration, tail frames, reused/generated images, account usage, retries, and unresolved failures.
