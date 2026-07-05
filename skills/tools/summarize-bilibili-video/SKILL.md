---
name: summarize-bilibili-video
description: Fetch and summarize Bilibili video subtitles. Use when Codex needs to quickly summarize a Bilibili video URL or BV/av id by retrieving available subtitle tracks, preferring zh-CN subtitles, then ai-zh auto captions, then the first subtitle track, and refusing with a fixed no-subtitle message when no subtitles are available.
---

# Summarize Bilibili Video

## Workflow

Use `scripts/bilibili_subtitle.py` to fetch subtitles for a Bilibili video before asking an LLM to summarize it.

1. Accept either a full Bilibili video URL or a `BV...`/`av...` id. Preserve the `p` page number when the user includes one.
2. Run the Python helper:

```bash
python3 scripts/bilibili_subtitle.py "<bilibili-url-or-id>"
```

3. If the helper prints `该视频无字幕，本skill无法总结`, return that exact sentence to the user and stop.
4. If the helper reports that subtitle access requires login or the cookie is invalid, relay the helper's `SESSDATA` acquisition and configuration instructions. Do not claim the video has no subtitles in this case, and do not ask the user to paste `SESSDATA` into chat.
5. Confirm that the helper output includes `Raw subtitle file: <path>`. Preserve that local raw subtitle file and mention its path when useful.
6. Otherwise, summarize the returned transcript according to the summary requirements below.

## Subtitle Selection

The helper must select subtitle tracks in this order:

1. `zh-CN`
2. `ai-zh`
3. The first subtitle track returned by Bilibili

Do not use the video description as a fallback. If no subtitle tracks are returned and Bilibili does not indicate login is required for subtitle access, the skill must fail with:

```text
该视频无字幕，本skill无法总结
```

## Raw Subtitle Preservation

The helper saves the unmodified Bilibili subtitle JSON response locally by default:

```bash
python3 scripts/bilibili_subtitle.py "<bilibili-url-or-id>"
```

The default output directory is `./bilibili_subtitles`. Use `--raw-dir <path>` only when the user wants a different local location.

Do not delete or overwrite the saved raw subtitle file during the task. Treat it as the audit source for the summary.

## Summary Requirements

Summarize for completeness before brevity:

- Preserve all core viewpoints, claims, evidence, caveats, and conclusions from the transcript.
- Keep the argument logic intact: show how the speaker moves from premise to reasoning to conclusion.
- Do not collapse opposing views, uncertainty, or conditional reasoning into a single absolute conclusion.
- If the transcript mentions stock, ETF, index, or listed-company names, annotate the first occurrence with the stock code or ticker, for example `英伟达（NVDA）`, `伯克希尔哈撒韦（BRK.A/BRK.B）`, or `贵州茅台（600519.SH）`.
- If a ticker is uncertain, say it is uncertain instead of inventing one. Verify with reliable sources when the ticker materially affects the summary.
- Keep later mentions natural after the first ticker annotation.

## Environment

Bilibili auto-generated AI subtitles often require authenticated subtitle access even when the webpage shows subtitles to a logged-in browser. Use any of these inputs:

- Set `BILIBILI_SESSION_TOKEN` to one or more comma-separated `SESSDATA` values.
- Set `BILIBILI_COOKIE_FILE` to a local cookie file path.
- Pass `--cookie-file <path>` to the helper.
- Put a local `.bilibili-cookie`, `.bilibili_cookie`, `.env.local`, or `.env` file in the current working directory.

Cookie files may contain any one of these formats. Raw and environment-style values may contain multiple comma-separated `SESSDATA` values.

```text
raw-SESSDATA-value
SESSDATA=raw-SESSDATA-value
BILIBILI_SESSION_TOKEN=raw-SESSDATA-value
Cookie: SESSDATA=raw-SESSDATA-value; other_cookie=...
```

Netscape `cookies.txt` rows are also supported when the cookie name is `SESSDATA`.

Prefer a local `.bilibili-cookie` file for repeated use so the token does not appear in shell history. Do not print or include the token in the final response.

When the user has not correctly provided a cookie, tell them this flow:

1. Log in to `https://www.bilibili.com` in a browser.
2. Open any Bilibili page, then open developer tools.
3. In Chrome/Edge, go to `Application -> Cookies -> https://www.bilibili.com`; in Firefox, go to `Storage -> Cookies -> https://www.bilibili.com`.
4. Find the `SESSDATA` cookie and copy only its `Value`.
5. Use one of these setup methods without posting the value in chat:

```bash
# Recommended: current working directory file
printf 'SESSDATA=your-value-here\n' > .bilibili-cookie

# Shell environment for future commands in the same shell
export BILIBILI_SESSION_TOKEN='your-value-here'

# One command only
BILIBILI_SESSION_TOKEN='your-value-here' python3 scripts/bilibili_subtitle.py '<bilibili-url>'

# Explicit cookie file
python3 scripts/bilibili_subtitle.py --cookie-file /path/to/cookie-file '<bilibili-url>'
```

The Python helper uses only the standard library.
