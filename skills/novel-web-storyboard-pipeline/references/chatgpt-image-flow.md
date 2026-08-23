# ChatGPT website image flow

## Required invariants

- Use the signed-in ChatGPT website only.
- Submit the exact `可直接复制提示词` block from `04-gpt-image-2-prompts.md`.
- Use the package's declared model, quality, size, and reference files.
- Start a new ChatGPT conversation for every human character, character look, or human group image task.
- Never generate two unrelated character identities in the same conversation.

## Reference handling

- Existing identity with a new look: upload the accepted identity master in a fresh conversation; use it only to lock face, age, skin tone, hair, and other stated identity invariants.
- Existing asset that already satisfies the visible state: reuse it and skip generation.
- New identity: use a fresh conversation without another character's image.
- Props and empty scenes do not require per-asset conversation isolation, but their prompts and downloads must remain unambiguous.

## Visual acceptance gate

Inspect the generated image before download or promotion:

- Character sheet: one identity across all views, correct number of views, consistent clothing and body proportions, no text, labels, watermark, extra person, duplicate body, malformed hands, or unrelated face.
- New identity: compare the large head view with unrelated accepted character masters. Reject a face that is materially the same or confusingly similar.
- Existing identity/new look: require the same face as the uploaded master; reject identity drift.
- Group: require visibly different faces, heights, silhouettes, and clothing; reject cloned crowds or twins unless requested.
- Prop: correct 1:1 composition, no hands or people.
- Scene: correct 16:9 composition and strictly empty when the prompt requires it.

Save rejected attempts under the configured rejected directory. Accepted files use [naming-and-state.md](naming-and-state.md). If the browser supplied JPEG or WebP, run `scripts/image_tools.py` so the `.png` destination contains actual PNG data instead of a renamed file. Refresh the asset index immediately after promotion.
