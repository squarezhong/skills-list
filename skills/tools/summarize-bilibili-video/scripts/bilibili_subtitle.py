#!/usr/bin/env python3
"""Fetch Bilibili subtitles for Codex summarization."""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


NO_SUBTITLE_MESSAGE = "该视频无字幕，本skill无法总结"
DEFAULT_MAX_BYTES = 16000
DEFAULT_COOKIE_FILES = (".bilibili-cookie", ".bilibili_cookie", ".env.local", ".env")
DEFAULT_RAW_DIR = "bilibili_subtitles"


def login_required_message(has_cookie: bool = False) -> str:
    status = "已提供的 SESSDATA 无效或已过期" if has_cookie else "未检测到有效的 Bilibili SESSDATA"
    return f"""该视频字幕需要登录访问，{status}。

获取 SESSDATA:
1. 在浏览器登录 https://www.bilibili.com
2. 打开任意 Bilibili 页面后打开开发者工具
3. Chrome/Edge: Application -> Cookies -> https://www.bilibili.com
   Firefox: Storage -> Cookies -> https://www.bilibili.com
4. 找到名为 SESSDATA 的 cookie，复制它的 Value

可用设置方式:
- 推荐: 在当前目录创建 .bilibili-cookie，内容写成 SESSDATA=你的值，然后重新运行本脚本
- 环境变量: export BILIBILI_SESSION_TOKEN='你的值'
- 一次性命令: BILIBILI_SESSION_TOKEN='你的值' python3 bilibili_subtitle.py '<视频链接>'
- 指定文件: python3 bilibili_subtitle.py --cookie-file /path/to/cookie-file '<视频链接>'

不要把 SESSDATA 发到聊天或公开日志里。"""


class SubtitleLoginRequired(RuntimeError):
    pass


def parse_video(value: str, explicit_page: int | None = None) -> tuple[str, int | None]:
    value = value.strip()
    page = explicit_page

    if re.fullmatch(r"BV[0-9A-Za-z]+", value) or re.fullmatch(r"av\d+", value, re.I):
        return value, page

    parsed = urllib.parse.urlparse(value if "://" in value else f"https://{value}")
    query = urllib.parse.parse_qs(parsed.query)
    if page is None and query.get("p"):
        try:
            page = int(query["p"][0])
        except ValueError:
            page = None

    match = re.search(r"/video/([^/?#]+)", parsed.path)
    if match:
        return match.group(1), page

    raise ValueError("Expected a Bilibili URL, BV id, or av id")


def unquote_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def unique_values(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = unquote_value(value).strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def extract_sessdata_values(text: str) -> list[str]:
    values: list[str] = []

    for match in re.finditer(r"(?:^|\s|;|Cookie:\s*)SESSDATA=([^;\s]+)", text, re.I):
        values.append(match.group(1))

    env_pattern = r"(?m)^\s*(?:export\s+)?(?:BILIBILI_SESSION_TOKEN|SESSDATA)\s*=\s*(.+?)\s*$"
    for match in re.finditer(env_pattern, text):
        raw_value = unquote_value(match.group(1).split(" #", 1)[0])
        values.extend(part.strip() for part in raw_value.split(","))

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 7 and parts[5] == "SESSDATA":
            values.append(parts[6])

    if not values:
        first_data_line = next((line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")), "")
        if first_data_line and not re.search(r"\s", first_data_line) and "=" not in first_data_line:
            values.extend(part.strip() for part in first_data_line.split(","))

    return unique_values(values)


def read_cookie_file(path_value: str | None) -> list[str]:
    if not path_value:
        return []
    path = Path(path_value).expanduser()
    try:
        return extract_sessdata_values(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []


def load_sessdata_values(cookie_file: str | None = None) -> list[str]:
    values: list[str] = []
    values.extend(part.strip() for part in os.getenv("BILIBILI_SESSION_TOKEN", "").split(","))
    values.extend(read_cookie_file(cookie_file))
    values.extend(read_cookie_file(os.getenv("BILIBILI_COOKIE_FILE")))

    for filename in DEFAULT_COOKIE_FILES:
        values.extend(read_cookie_file(filename))

    return unique_values(values)


def headers(cookie_file: str | None = None) -> dict[str, str]:
    sessdata_values = load_sessdata_values(cookie_file)
    selected_sessdata = random.choice(sessdata_values) if sessdata_values else ""
    result = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.bilibili.com/",
    }
    if selected_sessdata:
        result["Cookie"] = f"SESSDATA={selected_sessdata}"
    return result


def has_session_token(request_headers: dict[str, str]) -> bool:
    return "SESSDATA=" in request_headers.get("Cookie", "")


def fetch_json(url: str, request_headers: dict[str, str]) -> Any:
    request = urllib.request.Request(url, headers=request_headers, method="GET")
    with urllib.request.urlopen(request, timeout=20) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return json.loads(response.read().decode(charset))


def fetch_json_with_raw_text(url: str, request_headers: dict[str, str]) -> tuple[Any, str]:
    request = urllib.request.Request(url, headers=request_headers, method="GET")
    with urllib.request.urlopen(request, timeout=20) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        raw_text = response.read().decode(charset)
        return json.loads(raw_text), raw_text


def get_video_info(video_id: str, request_headers: dict[str, str]) -> dict[str, Any]:
    if video_id.lower().startswith("av"):
        params = urllib.parse.urlencode({"aid": video_id[2:]})
    else:
        params = urllib.parse.urlencode({"bvid": video_id})
    data = fetch_json(f"https://api.bilibili.com/x/web-interface/view?{params}", request_headers)
    if data.get("code") != 0 or not isinstance(data.get("data"), dict):
        raise RuntimeError(data.get("message") or "Bilibili video API returned no data")
    return data["data"]


def choose_page(video_info: dict[str, Any], page_number: int | None) -> tuple[str | int, str | int]:
    aid = video_info.get("aid")
    pages = video_info.get("pages") or []
    if not pages:
        cid = video_info.get("cid")
        if aid and cid:
            return aid, cid
        raise RuntimeError("Bilibili response did not include aid/cid")

    wanted = page_number or 1
    selected = next((p for p in pages if p.get("page") == wanted), pages[0])
    cid = selected.get("cid")
    if not aid or not cid:
        raise RuntimeError("Bilibili page response did not include aid/cid")
    return aid, cid


def extract_tracks_from_player_data(data: dict[str, Any], request_headers: dict[str, str]) -> list[dict[str, Any]]:
    if data.get("code") != 0 or not isinstance(data.get("data"), dict):
        raise RuntimeError(data.get("message") or "Bilibili player API returned no data")
    player_data = data["data"]
    subtitle = player_data.get("subtitle") or {}
    tracks = subtitle.get("subtitles") or subtitle.get("list") or []
    normalized_tracks = [track for track in tracks if isinstance(track, dict)]
    if not normalized_tracks and player_data.get("need_login_subtitle"):
        raise SubtitleLoginRequired(login_required_message(has_session_token(request_headers)))
    return normalized_tracks


def get_subtitle_tracks(aid: str | int, cid: str | int, request_headers: dict[str, str]) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"aid": aid, "cid": cid})
    last_tracks: list[dict[str, Any]] = []
    for endpoint in ("https://api.bilibili.com/x/player/v2", "https://api.bilibili.com/x/player/wbi/v2"):
        data = fetch_json(f"{endpoint}?{params}", request_headers)
        tracks = extract_tracks_from_player_data(data, request_headers)
        if tracks:
            return tracks
        last_tracks = tracks
    return last_tracks


def choose_track(tracks: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not tracks:
        return None
    for language in ("zh-CN", "ai-zh"):
        for track in tracks:
            if track.get("lan") == language:
                return track
    return tracks[0]


def normalize_subtitle_url(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith("//"):
        return "https:" + url
    return url


def safe_filename_part(value: str) -> str:
    value = value.strip() or "unknown"
    return re.sub(r"[^0-9A-Za-z._-]+", "_", value).strip("._") or "unknown"


def save_raw_subtitle(
    raw_text: str,
    video_id: str,
    page_number: int | None,
    language: str,
    raw_dir: str | None,
) -> str:
    output_dir = Path(raw_dir or DEFAULT_RAW_DIR).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = (
        f"{safe_filename_part(video_id)}"
        f"_p{page_number or 1}"
        f"_{safe_filename_part(language)}"
        "_raw_subtitle.json"
    )
    output_path = output_dir / filename
    output_path.write_text(raw_text, encoding="utf-8")
    return str(output_path.resolve())


def grouped_lines(body: list[dict[str, Any]], group_size: int = 7) -> list[str]:
    lines: list[str] = []
    for start_index in range(0, len(body), group_size):
        group = body[start_index : start_index + group_size]
        if not group:
            continue
        start_time = group[0].get("from", "")
        text = " ".join(str(item.get("content", "")).strip() for item in group).strip()
        if text:
            lines.append(f"{start_time} - {text}")
    return lines


def byte_len(text: str) -> int:
    return len(text.encode("utf-8"))


def fit_to_budget(lines: list[str], max_bytes: int) -> list[str]:
    if max_bytes <= 0:
        return lines
    joined = "\n".join(lines)
    if byte_len(joined) <= max_bytes:
        return lines

    for keep_count in range(len(lines), 0, -1):
        if keep_count == 1:
            candidate = [lines[0]]
        else:
            indexes = sorted({round(i * (len(lines) - 1) / (keep_count - 1)) for i in range(keep_count)})
            candidate = [lines[i] for i in indexes]
        if byte_len("\n".join(candidate)) <= max_bytes:
            return candidate

    return []


def fetch_transcript(
    video: str,
    page: int | None,
    max_bytes: int,
    cookie_file: str | None = None,
    raw_dir: str | None = DEFAULT_RAW_DIR,
) -> str:
    video_id, parsed_page = parse_video(video, page)
    request_headers = headers(cookie_file)
    video_info = get_video_info(video_id, request_headers)
    aid, cid = choose_page(video_info, parsed_page)
    tracks = get_subtitle_tracks(aid, cid, request_headers)
    track = choose_track(tracks)
    subtitle_url = normalize_subtitle_url(track.get("subtitle_url") if track else None)

    if not subtitle_url:
        return NO_SUBTITLE_MESSAGE

    subtitle_data, raw_subtitle_text = fetch_json_with_raw_text(subtitle_url, request_headers)
    body = subtitle_data.get("body") if isinstance(subtitle_data, dict) else None
    if not isinstance(body, list) or not body:
        return NO_SUBTITLE_MESSAGE

    language = str(track.get("lan") or "unknown")
    raw_subtitle_path = save_raw_subtitle(raw_subtitle_text, video_id, parsed_page, language, raw_dir)

    lines = fit_to_budget(grouped_lines(body), max_bytes)
    if not lines:
        return NO_SUBTITLE_MESSAGE

    title = str(video_info.get("title") or video_id).strip()
    page_note = f"\nPage: {parsed_page or 1}"
    omitted = "" if len(lines) == math.ceil(len(body) / 7) else "\nNote: transcript was sampled to fit the byte budget."
    return (
        f"Title: {title}"
        f"{page_note}\nSubtitle language: {language}"
        f"\nRaw subtitle file: {raw_subtitle_path}"
        f"{omitted}\nTranscript:\n"
        + "\n".join(lines)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Bilibili subtitles for summarization.")
    parser.add_argument("video", help="Bilibili URL, BV id, or av id")
    parser.add_argument("--page", type=int, help="Video page number for multi-part videos")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES, help="Maximum transcript bytes; use 0 for no limit")
    parser.add_argument(
        "--raw-dir",
        default=DEFAULT_RAW_DIR,
        help="Directory where the raw Bilibili subtitle JSON is saved. Defaults to ./bilibili_subtitles.",
    )
    parser.add_argument(
        "--cookie-file",
        help=(
            "Path to a file containing a raw SESSDATA value, SESSDATA=..., "
            "a Cookie header, a dotenv entry, or a Netscape cookies.txt row."
        ),
    )
    args = parser.parse_args()

    try:
        print(fetch_transcript(args.video, args.page, args.max_bytes, args.cookie_file, args.raw_dir))
        return 0
    except SubtitleLoginRequired as exc:
        print(str(exc))
        return 2
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
