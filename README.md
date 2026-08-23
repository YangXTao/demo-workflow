# Novel Web Storyboard Pipeline

This repository contains the portable Codex skill `novel-web-storyboard-pipeline`.

It coordinates `novel-chapter-3d-pipeline`, the signed-in ChatGPT website, and the signed-in Doubao website to process one or two Chinese novel chapters with reusable image assets, resumable Seedance 2.0 Fast shot generation, tail-frame continuity, account rotation, and local verification.

Install the folder `skills/novel-web-storyboard-pipeline` into your Codex skills directory. The separate `novel-chapter-3d-pipeline` skill and browser control remain required. Browser credentials are never included.

On Windows PowerShell:

```powershell
$target = Join-Path $env:USERPROFILE '.codex\skills\novel-web-storyboard-pipeline'
Copy-Item -Recurse -LiteralPath '.\skills\novel-web-storyboard-pipeline' -Destination $target
```

Copy `assets/config.example.json` to `<project>/.workflow/config.json` and adjust only machine-specific paths or account policy. The default staging directory is `<project>/.workflow/downloads`, which for the included example resolves to `D:\jimeng\我的嫁妆，谁也别想拿去飞升\.workflow\downloads`.

Example preflight:

```powershell
python .\skills\novel-web-storyboard-pipeline\scripts\preflight.py --config 'D:\jimeng\我的嫁妆，谁也别想拿去飞升\.workflow\config.json' 'D:\jimeng\我的嫁妆，谁也别想拿去飞升\第二十八章'
```

Run the included preflight before consuming image or video quota.
