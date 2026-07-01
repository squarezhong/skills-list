# macOS System Data Sources

Use this reference to map large paths to likely meaning and cleanup risk.

## Common Path Map

| Path | Likely contents | Cleanup posture |
| --- | --- | --- |
| `~/Library/Application Support` | App databases, browser profiles, IDE state, Steam data, chat app data | Risky; inspect per app |
| `~/Library/Caches` | User app caches, build/download caches | Usually safer; prefer app/package cleanup |
| `~/Library/Group Containers` | Shared app group data, Microsoft/OneDrive/Office, Telegram, Apple groups | Risky; use app settings |
| `~/Library/Containers` | Sandboxed app data for App Store and Apple apps | Risky; inspect per app |
| `~/Library/Developer` | Xcode DerivedData, archives, simulators, device support | Often cleanable with Xcode-aware commands |
| `~/Library/Mobile Documents` | iCloud Drive local materialization | Use iCloud/Finder controls |
| `~/Library/Mail`, `~/Library/Messages` | Local mail/messages stores and attachments | User data; clean in app |
| `~/Library/Application Support/MobileSync/Backup` | iPhone/iPad backups | Delete from Finder/Device settings only |
| `/Library/Developer` | Command line tools, shared simulators/device support | Inspect before removing |
| `/Library/Updates` | macOS update staging | Usually managed by macOS |
| `/private/var/folders` | Per-user temp/cache and app-translocation state | Usually self-managed; reboot can help |
| `/private/var/vm` | swap, sleepimage, memory pressure files | Do not manually delete while booted |
| `/private/var/db` | System databases, receipts, Spotlight, dyld caches | Do not manually delete |
| `/opt/homebrew` | Homebrew packages, Cellar, downloads | Use `brew cleanup` after confirmation |
| `/usr/local/texlive` | TeX Live distribution | Remove only if the user no longer needs TeX |
| `~/.cache`, `~/.npm`, `~/.cargo`, `~/.gradle`, `~/.m2` | Developer/tool caches | Usually cleanable with tool-native commands |
| VM app folders or images | Docker, UTM, Parallels, VMware disk images | Use app-native pruning/compaction |

## Follow-Up Commands

Use read-only commands first:

```bash
du -sh ~/Library/* 2>/dev/null | sort -hr | head -30
du -sh ~/Library/Application\ Support/* 2>/dev/null | sort -hr | head -30
du -sh ~/Library/Caches/* 2>/dev/null | sort -hr | head -30
du -sh ~/Library/Group\ Containers/* 2>/dev/null | sort -hr | head -30
du -sh ~/.??* 2>/dev/null | sort -hr | head -30
du -sh /Library/* /private/var/* /opt/* /usr/local/* 2>/dev/null | sort -hr | head -40
tmutil listlocalsnapshots /
df -h / /System/Volumes/Data
```

## Cleanup Guidance

Offer cleanup only after the user asks for it. Prefer:

- Homebrew: `brew cleanup --prune=all`
- pip: `pip cache purge`
- npm: `npm cache verify` then `npm cache clean --force` only if necessary
- Xcode simulators: `xcrun simctl delete unavailable`
- Xcode DerivedData: delete through Xcode settings or a targeted DerivedData removal after confirmation
- Time Machine snapshots: let macOS manage them, or thin/delete only after explaining that snapshots can be useful for recovery
- OneDrive/iCloud/Dropbox: app-native "Free Up Space" or selective sync controls

Avoid:

- Deleting entire app containers or group containers
- Deleting `/private/var/db` or `/private/var/vm`
- Treating APFS purgeable space as immediately reclaimable user files
- Equating Finder/System Settings categories with exact folder ownership
