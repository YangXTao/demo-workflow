# Changelog

## Unreleased

- Keep complete spoken dialogue in short Seedance shots by specifying controlled accelerated delivery (normally 1.10–1.35x) when ordinary pacing would overrun; return genuinely overlong lines for storyboard splitting instead of accepting a cutoff.
- Add a multi-character staging gate: explicit depth and screen lanes, staggered actions, stable camera axis, and prohibitions against body, robe, weapon, mount, and landing-plane intersections.

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
