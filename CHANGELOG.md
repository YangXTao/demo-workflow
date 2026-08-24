# Changelog

## Unreleased

- Recover from stale browser-control tabs without confusing them with website logout.
- Treat timed-out uploads as unknown outcomes and require visible attachment count/order verification before retrying.
- Add a hard per-shot asset validator so missing files and `pending_generation` assets cannot reach Doubao.
- Normalize indexed filenames without extensions and handle Chinese list punctuation so conservative reuse candidates are not missed.
- Handle Doubao's duplicate clipboard thumbnails and optionally auto-confirm material/generation dialogs without accepting payment, permission, login, or quota changes.
- Disallow multi-image clipboard batching after confirming that Doubao can drop the control connection before reporting the paste result.

## v0.1.0 - 2026-08-24

- Add the portable `novel-web-storyboard-pipeline` Codex skill.
- Coordinate `novel-chapter-3d-pipeline`, ChatGPT web image generation, and Doubao Seedance 2.0 Fast web video generation for one or two chapters.
- Add regenerable asset indexing, deterministic chapter manifests, resumable SQLite state, download detection, image normalization, video inspection, and tail-frame extraction.
- Enforce fresh ChatGPT conversations for human assets, exact Doubao image order and duration, three-use account tracking, and `fei-1` last-use reservation.
