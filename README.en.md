# Skills List

[简体中文](./README.md)

A personal Skills collection with a few curious skills, just for fun.

## Quickstart

Preview the skills available in this repository:

```bash
npx skills add squarezhong/skills-list --list
```

Install all skills from this repository:

```bash
npx skills add squarezhong/skills-list --all
```

Install one specific skill:

```bash
npx skills add squarezhong/skills-list --skill adjust-retail-sales-by-index
```

## Repository Layout

```text
skills/
  finance/
    adjust-retail-sales-by-index/
  system/
    analyze-macos-system-data/
  tools/
    summarize-bilibili-video/
```

## Skills

### Finance

#### `adjust-retail-sales-by-index`

*Generate retail sales data adjusted to the scope of a specific consumer index.*

Example usage:

```text
Use adjust-retail-sales-by-index: based on the SSE Consumer 50 constituents I provide, adjust and summarize official NBS 2019-2026 Jan-Jun total retail sales of consumer goods data.
```

### System

#### `analyze-macos-system-data`

*Analyze macOS Storage System Data usage in a read-only way, identifying the sources of large folders, risk levels, and cautious cleanup candidates.*

Example usage:

```text
Use analyze-macos-system-data to explain why macOS System Data is taking so much space, listing the largest confirmed contributors and safe next steps.
```

### Tools

#### `summarize-bilibili-video`

*Fetch Bilibili video subtitles and summarize the video from the transcript.*

Example usage:

```text
Use summarize-bilibili-video to summarize this video: https://www.bilibili.com/video/BV1EfTe6jEVe
```

## Adding a New Skill

When adding a skill, follow the current layout:

```text
skills/<category>/<skill-name>/*
```

## License

MIT
