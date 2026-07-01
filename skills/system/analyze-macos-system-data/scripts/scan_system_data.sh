#!/usr/bin/env bash
set -u

limit=30
deep=0

usage() {
  echo "Usage: $0 [--deep] [top-count]" >&2
  echo "  --deep     also scan top-level ~/Library, which can be slow" >&2
}

while (($#)); do
  case "$1" in
    --deep)
      deep=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    [0-9]*)
      limit="$1"
      ;;
    *)
      usage
      exit 2
      ;;
  esac
  shift
done

if ! [[ "$limit" =~ ^[0-9]+$ ]]; then
  usage
  exit 2
fi

section() {
  printf '\n## %s\n' "$1"
}

top_du() {
  local target="$1"
  local label="$2"

  section "$label"
  if [[ -e "$target" ]]; then
    du -sh "$target"/* 2>/dev/null | sort -hr | head -n "$limit"
  else
    printf 'not found: %s\n' "$target"
  fi
}

echo "# macOS System Data read-only scan"
echo "Generated: $(date)"
echo "Top entries per section: $limit"
if (( deep )); then
  echo "Mode: deep"
else
  echo "Mode: quick"
fi

section "Volumes"
df -h / /System/Volumes/Data 2>/dev/null

if (( deep )); then
  top_du "$HOME/Library" "User Library"
fi
top_du "$HOME/Library/Application Support" "Application Support"
top_du "$HOME/Library/Caches" "User Caches"
top_du "$HOME/Library/Group Containers" "Group Containers"
top_du "$HOME/Library/Containers" "Containers"
top_du "$HOME/Library/Developer" "User Developer"
top_du "$HOME/.cache" "Hidden User Cache"

section "Hidden Home Entries"
du -sh "$HOME"/.??* 2>/dev/null | sort -hr | head -n "$limit"

top_du "/Library" "System Library"
top_du "/private/var" "Private Var"
top_du "/opt" "Opt"
top_du "/usr/local" "Usr Local"

section "Local Time Machine Snapshots"
tmutil listlocalsnapshots / 2>/dev/null || true

section "Notes"
echo "This script is read-only. It does not use sudo and may miss protected system locations."
echo "macOS Storage categories can include purgeable space and APFS snapshot accounting that do not map 1:1 to folder sizes."
