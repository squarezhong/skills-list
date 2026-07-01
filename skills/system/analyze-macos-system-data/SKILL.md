---
name: analyze-macos-system-data
description: Analyze macOS Storage System Data composition by running safe read-only disk usage checks, mapping large folders to likely categories, explaining Finder/System Settings discrepancies, and identifying cautious cleanup candidates. Use when a user asks why macOS System Data is large, what is inside System Data, how to inspect local snapshots, caches, app containers, Homebrew, Xcode, TeX Live, virtual machines, backups, or other hidden storage, or asks for a safe storage breakdown on a Mac.
---

# Analyze macOS System Data

## Workflow

1. Treat System Data as a broad Finder/System Settings bucket, not a single folder. It commonly includes `~/Library`, `/Library`, `/private/var`, local snapshots, app containers, caches, developer tools, package managers, VM images, iOS backups, and hidden home-directory data.
2. Start with read-only inspection. Do not delete, thin snapshots, uninstall runtimes, or run cleanup commands unless the user explicitly asks.
3. Prefer bundled `scripts/scan_system_data.sh` for a first pass. Its default quick mode summarizes common high-value System Data locations without requiring sudo:

```bash
<skill-dir>/scripts/scan_system_data.sh
```

Use `<skill-dir>/scripts/scan_system_data.sh --deep` only when the user accepts a slower pass over top-level `~/Library`.

4. If a reported folder is large, drill into that folder with `du -sh <folder>/* 2>/dev/null | sort -hr | head -30`, quoting or escaping spaces. Use `tmutil listlocalsnapshots /` for local Time Machine snapshots and `df -h / /System/Volumes/Data` to explain volume-level totals.
5. Summarize findings by human meaning, not just path names: browser profile/cache, OneDrive sync state, Homebrew cache/packages, TeX Live, Xcode/iOS simulators, chat app containers, mail/messages, VM swap/sleepimage, or local snapshots.
6. Separate safe cleanup candidates from risky data stores. Caches are usually lower risk; app support, containers, OneDrive, Photos, Mail, Messages, Steam, and backups can contain user data.

## Report Format

Lead with the largest confirmed contributors and approximate sizes. Then explain what counts toward System Data and why the macOS UI may not match `du` exactly.

Use this shape:

- Confirmed large items: path, size, likely owner/app, why it appears as System Data.
- Notable hidden/system items: snapshots, `/private/var`, package managers, developer runtimes.
- Safe next steps: read-only follow-up checks first; cleanup commands only if requested.
- Cautions: name any folder that should not be manually deleted.

## Safety Rules

- Do not use `sudo` unless the user asks for deeper system-wide accounting and accepts the risk.
- Do not use `rm`, `git clean`, `tmutil deletelocalsnapshots`, app uninstallers, or package-manager cleanup commands without explicit user approval.
- Never recommend deleting `~/Library/Containers`, `~/Library/Group Containers`, or `~/Library/Application Support` wholesale.
- For cloud-sync folders such as OneDrive/iCloud/Dropbox, recommend app-native controls like "Free Up Space" rather than manual deletion.
- For developer/package-manager storage, prefer native cleanup commands after confirmation, such as `brew cleanup --prune=all`, `xcrun simctl delete unavailable`, or package-specific cache purge commands.

## References

Read `references/macos-system-data-sources.md` when you need path-to-category mapping, cleanup caution levels, or examples of follow-up commands.
