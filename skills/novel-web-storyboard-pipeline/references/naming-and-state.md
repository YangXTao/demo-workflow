# Naming and state

## Images

Accepted images live in the configured global image directory.

- Reusable identity: `<角色名>-三视图.png`
- Chapter look/state: `<角色名>-第<章号>章-<造型或状态>-三视图.png`
- Group: `第<章号>章群体-<群体名称>.png`
- Prop: `第<章号>章道具-<道具名称>-<状态>.png`
- Scene: `第<章号>章场景-<场景名称>.png`

Omit an empty state suffix. Normalize accepted downloads to PNG. Never overwrite; append `-v2`, `-v3`, and so on.

## Videos

- Shot: `<章号>-<顺序>.mp4`
- Tail frame: `<章号>-<顺序>-尾帧.png`

Examples: `28-1.mp4`, `28-1-尾帧.png`.

## Workflow files

Under `<project>/.workflow/`:

- `config.json`: machine/project configuration.
- `asset-index.json`: regenerable asset inventory.
- `state.sqlite`: resumable state and audit events.
- `downloads/`: browser staging directory.
- `rejected/<chapter>/`: rejected generated images.
- `runs/chapter-<number>/manifest.json`: resolved run manifest.

The chapter asset directory may contain `image-manifest.json` as a user-readable map of reused and generated assets. It is not part of the seven-file chapter package contract.
