# Changelog

## v0.3.5 - 2026-08-26

- Make manifest rebuilds recognize an exact generated output filename before fuzzy asset reuse, so verified new character, look, and prop files remain video-eligible after regeneration.

## v0.3.4 - 2026-08-26

- Fix cross-chapter SQLite state resolution: `state_cli.py` now accepts `--chapter` for asset and shot updates, so repeated short IDs resolve deterministically to the active chapter.

## v0.3.3 - 2026-08-26

- Resolve contradictory upload-recovery instructions: the verified single-image copy-and-paste path now supersedes the file chooser only after that chooser is proven unavailable.
- Add bounded browser-page recovery: preserve user1 tabs, use one fresh window at most, and record the page-control state instead of suggesting extension reinstallation or risking duplicate generation.
- Add ChatGPT attachment-clipboard recovery without creating image copies, plus Chapter 31 manifest support for explicit output names, new visible character looks, and packaged reusable assets.
- Require cultivation-state continuity, timed dialogue delivery at up to 1.50x when needed, multi-character anti-intersection staging, and full long-prompt combat gates.
- Fix false browser failures caused by a self-imposed 10-second page-control budget; page operations now use at least 60 seconds and recovery Chrome windows retain one normal keepalive tab.

## v0.3.1 - 2026-08-25

- Add a bundled Node/Playwright local-video fallback for inspection and tail-frame extraction when OpenCV or FFmpeg are unavailable.
- Add a safe, ordered Windows copy-and-paste material-upload recovery path after the verified Chrome file-chooser flow fails.

## v0.3.0 - 2026-08-25

- Learn a structured long-prompt method from four user-supplied reference documents and six AI-donghua reference videos: continuous micro-beat timelines, complete action causality, three collision intensities, five-layer VFX, scale ladders, motivated camera changes, exposure protection, and aftermath-driven endings.
- Add hard pre-submit and final QC gates for combat and spectacle prompts; prompt completeness now takes priority over brevity, while overloaded or contradictory beats must be split instead of piled into one shot.

## v0.2.3 - 2026-08-25

- Add a hard whole-chapter acceptance audit for dialogue completion, visual cheating, continuity, anatomy, intersection/clipping, and battle spectacle/impact; preserve all rejected originals and log evidence.
- Support narrow editorial replacement clips for isolated defects, with locked edit-in/edit-out states and deterministic `局部重制` names, while retaining whole-shot rework for continuity or core-beat failures.

## v0.2.2 - 2026-08-25

- Keep complete spoken dialogue in short Seedance shots by specifying controlled accelerated delivery (normally 1.10–1.50x, selected for dialogue density, emotion, and intelligibility) when ordinary pacing would overrun; return genuinely overlong lines for storyboard splitting instead of accepting a cutoff.

## v0.2.1 - 2026-08-25

- Add a multi-character staging gate: explicit depth and screen lanes, staggered actions, stable camera axis, and prohibitions against body, robe, weapon, mount, and landing-plane intersections.

## v0.2.0 - 2026-08-25

- Recover from stale browser-control tabs without confusing them with website logout.
- Treat timed-out uploads as unknown outcomes and require visible attachment count/order verification before retrying.
- Add a hard per-shot asset validator so missing files and `pending_generation` assets cannot reach Doubao.
- Normalize indexed filenames without extensions and handle Chinese list punctuation so conservative reuse candidates are not missed.
- Handle Doubao's duplicate clipboard thumbnails and optionally auto-confirm material/generation dialogs without accepting payment, permission, login, or quota changes.
- Disallow multi-image clipboard batching after confirming that Doubao can drop the control connection before reporting the paste result.
- Raise the per-image upload timeout to 60 seconds and restart from a clean composer when an unsubmitted stale page cannot be reclaimed promptly.
- Restrict storyboard binding candidates to assets explicitly applicable to the current shot, preventing cross-shot image misbinding.
- Recover once from a server-stale Doubao job by preserving it and resubmitting on a different non-reserved account after a configurable timeout.

## v0.1.0 - 2026-08-24

- Add the portable `novel-web-storyboard-pipeline` Codex skill.
- Coordinate `novel-chapter-3d-pipeline`, ChatGPT web image generation, and Doubao Seedance 2.0 Fast web video generation for one or two chapters.
- Add regenerable asset indexing, deterministic chapter manifests, resumable SQLite state, download detection, image normalization, video inspection, and tail-frame extraction.
- Enforce fresh ChatGPT conversations for human assets, exact Doubao image order and duration, three-use account tracking, and `fei-1` last-use reservation.
