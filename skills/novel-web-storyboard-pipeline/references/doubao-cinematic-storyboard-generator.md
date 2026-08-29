# Doubao cinematic-storyboard prompt-generator flow

## When this mode applies

Use this mode when the user asks for storyboard/video-generation prompts for one or two named chapters, or asks to produce a chapter end-to-end from its novel text. It is a planning pass before image and Seedance production. Keep the existing direct-package route available when the user supplies an already accepted seven-file package or expressly asks to skip this planning pass.

## 1. Classify the chapter before opening Doubao

Read the supplied chapter text and label the chapter `文戏`, `打戏`, or `混合叙事`. A mixed chapter has both performance/information beats and material conflict, spell, combat, pursuit, rescue, formation, or spectacle beats. Record the label and a one-line rationale in `10-资产复用台账.md` in the chapter asset directory. This label routes the director prompt; it must not flatten a mixed chapter into uniformly high-intensity action.

## 2. Make the existing-asset ledger

Refresh the project asset index and visually inspect only conservative candidates. Record every accepted existing on-screen asset that is relevant to the requested chapter in `10-资产复用台账.md`:

| 类别 | 角色/道具/场景 | 精确文件名 | 当前可见状态 | 用途/拟用分镜 |
|---|---|---|---|---|

Include characters, props, and locations. Do not create a replacement merely because an existing image is not the first search result. A master image is reusable only when its visible state matches; clothing, injury, projection, activation, damage, or realm-state changes require a separate state image.

For the director request, upload only the accepted **character and prop** reference images that the chapter needs. Keep their upload order and write an `@imageN = 名称` mapping. Do not upload scene images merely to pad the reference set; describe locations in the request unless a scene reference is genuinely necessary to disambiguate a recurring location.

## 3. Obtain the canonical director prompt from Doubao

In the already signed-in Doubao **desktop app**, create a **new conversation**. Choose `工作任务` → `本地电脑` → `技能/cinematic-storyboard-prompt-generator`, then select **豆包 2.1 Turbo 高** before submitting the director request. This model choice applies only to the prompt-generation task. Do not use the Doubao website for this stage: the website is reserved for later `Seedance 2.0 Fast` video production. The Chrome two-tab cap applies only to browser image/video work, not to this desktop-app director task.

Upload the ledger-selected character/prop images once in the declared order. Then submit one request containing:

1. the `@imageN = 名称` mapping;
2. chapter number and title;
3. the complete novel text, verbatim;
4. the classification (`文戏`/`打戏`/`混合叙事`), `修仙版`, `旁白模式B`, and audio routing: `打戏段无BGM；文戏段可加BGM`.

Use this request skeleton, replacing only bracketed values:

```text
@image1 = [角色或道具名称]
@image2 = [角色或道具名称]

第[章节号]章 [标题]
[完整小说原文]

生成第[章节号]章分镜，[文戏/打戏/混合叙事]型，修仙版，旁白模式B，打戏段无BGM，文戏段可加BGM。
```

The returned document is acceptable only when every shot has the cinematic file-style structure exemplified by the user-approved reference:

- a numbered `S01`-style heading with a 10-second start/end time range and shot title;
- `【上一镜尾帧衔接】`, including opening/no-tail or a precise predecessor end state;
- `①画质基准`, `②角色・场景・核心设定`, `③时间轴`, and `④负面提示词`;
- an ordered image mapping for every supplied reference and a real 10-second causal timeline;
- concrete staging, character voice and lip-sync requirements where dialogue occurs, sound/BGM routing, continuity/end state, and applicable V8 spectacle detail without contradicting plot facts;
- no missing shot indices, vague placeholders, bare adjective lists, or a generic summary in place of time-coded production instructions.

For a prose shot, accept restrained V8 camera language without requiring battle density. For a combat or mixed conflict beat, require the established V8/Seedance long-prompt gate, readable cause/contact/consequence, and the relevant voice baselines. The reference defines the **document structure and specificity**, not mandatory fixed color values, cameras, effect counts, or spectacle for every shot.

If the response is structurally incomplete, instruct the same skill conversation to regenerate it in the required structure. Do not upload the references again. Do not begin image or video production until a complete canonical prompt is saved and reviewed.

## 4. Save and derive the package

Save the accepted unabridged returned prompt to `<chapter>/资产/07-seedance-2-fast-prompts.md`. Preserve its `S01`-style sections and do not shorten production-critical detail. Also derive and save:

- `02-screenplay.md`: a chapter production screenplay derived from the accepted prompt and checked against the source novel. It must retain plot facts, dialogue, roles, realms/states, progression, and end states; it may not invent a different story.
- `03-assets.md` and `04-gpt-image-2-prompts.md`: update with every required missing character state, prop, and location identified by the accepted prompt.

Preserve the required seven-package-file contract. Add `10-资产复用台账.md` as an auditable supplement rather than replacing any required file.

## 5. Generate only missing images, then Seedance videos

Generate missing visual assets only through the signed-in ChatGPT website. Every human-character task must use the project’s accepted four-view turnaround format: front, left, rear, and right views in one clean readable reference sheet, with identity, costume/state, anatomy, and silhouette consistent across all four views; no watermark or unrelated text. Follow the existing fresh-chat, identity-isolation, visual-review, and naming rules.

Rebuild the manifest from the accepted canonical prompt after assets resolve. The manifest adapter accepts canonical `S01｜00:00—00:10` headings and maps them to `SG-001`, `SG-002`, and so on. Use 10 seconds, `Seedance 2.0 Fast`, and `16:9` for this director-generated mode unless the user explicitly authorizes another duration.

For every SG, upload only its ordered manifest bindings. Prepend the submitted video prompt with the binding legend:

```text
@image1 = [角色/道具/场景名称]
@image2 = [角色/道具/场景名称]
```

For a direct continuation, the first line must instead state `@image1 = S[前一镜编号]尾帧`, followed by the remaining image legend. Then keep the canonical prompt body intact. Select `生成视频` → `Seedance 2.0 Fast` → `16:9` → `10s`, submit only after the binding thumbnails match the legend, wait for the official acknowledgement, download the top watermark-free `视频1`, validate, extract the tail when the next SG requires it, and proceed sequentially.

## 6. Completion review

Perform the existing whole-chapter review. Rework severe body/prop/weapon intersections, identity failures, unreadable contact or consequence, broken tail continuity, incomplete dialogue, or a shot that materially contradicts its canonical prompt. Preserve originals and log the repair.
