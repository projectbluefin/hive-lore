#!/usr/bin/env python3
"""tools/capture_chapters.py — reproducible chapter-metadata capture/reshape.

`sources/<video_id>.chapters.json` is a committed artifact: the publisher's
own chapter list, reshaped into the narrow shape `tests/test_titles.py`
validates the season's headlines against. This is the ONE tool that produces
it, and it does the SAME reshape whether the input just came from a live
yt-dlp process or from a raw dump already saved to disk.

yt-dlp's raw `--dump-single-json --skip-download` output is NOT this file's
shape: it nests every chapter under `start_time` / `end_time` (floats, in
seconds) inside a video info dict carrying dozens of unrelated fields
(formats, thumbnails, uploader metadata, ...). `reshape_chapters()` is the
one place that narrowing happens, so a committed artifact's `captured_with`
can name the command that ACTUALLY produced it -- the raw yt-dlp dump piped
through this reshape, never the raw dump alone. (`sources/jlzQnXcUxqI.chapters.json`
previously claimed the raw yt-dlp command alone produced its shape; it did
not, and `captured_with` now names this tool.)

Usage:
    # Live capture (network; the ONLY place yt-dlp is invoked):
    python3 tools/capture_chapters.py <youtube-url>

    # Reproducible offline replay, from a yt-dlp dump already saved to disk.
    # This is how the artifact can be rebuilt -- and how it is tested --
    # with no network at all:
    python3 tools/capture_chapters.py --from-json raw.json

Stdlib only. yt-dlp is an external subprocess, never imported.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"

RAW_CAPTURE_COMMAND = ("yt-dlp", "--dump-single-json", "--skip-download")

# The command that actually produces a committed artifact: the raw yt-dlp
# dump is never the artifact itself, only this reshape's input.
CAPTURED_WITH = (
    "yt-dlp --dump-single-json --skip-download <url> | "
    "python3 tools/capture_chapters.py --from-json -"
)


def reshape_chapters(info: dict) -> list[dict]:
    """yt-dlp's raw `chapters` entries, reshaped to this project's narrow
    committed shape: whole-second `start` / `end` plus `title`, nothing else.

    yt-dlp reports `start_time` / `end_time` as floats; every chapter
    boundary this project records is a whole second, so they are ROUNDED
    here -- once, in the one place that does it -- rather than left as
    floats for some later, less careful reader to truncate."""
    return [
        {
            "start": round(chapter["start_time"]),
            "end": round(chapter["end_time"]),
            "title": chapter["title"],
        }
        for chapter in info.get("chapters") or []
    ]


def capture_payload(info: dict, *, captured: str,
                    captured_with: str = CAPTURED_WITH) -> dict:
    """The full committed artifact shape, built from a yt-dlp info dict
    (live or replayed from a saved dump) plus the date it was captured.

    Pure: no clock read here unless the caller omits ``captured`` at the
    CLI layer, so this function itself is exactly what a test calls."""
    return {
        "video_id": info["id"],
        "url": f"https://www.youtube.com/watch?v={info['id']}",
        "video_title": info.get("title", ""),
        "captured": captured,
        "captured_with": captured_with,
        "chapters": reshape_chapters(info),
    }


def fetch_raw(url: str, runner=subprocess.run) -> dict:
    """The ONE place yt-dlp is invoked: dump-single-json, parsed. Never
    called by a test -- ``--from-json`` is the offline, reproducible path."""
    result = runner([*RAW_CAPTURE_COMMAND, url],
                    capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Capture (or replay) a video's chapter metadata into "
                    "this project's committed sources/ shape.")
    parser.add_argument(
        "url", nargs="?",
        help="the source video's YouTube URL (required unless "
             "--from-json is used)")
    parser.add_argument(
        "--from-json", type=Path, metavar="PATH",
        help="reshape a yt-dlp dump already saved to disk ('-' for stdin) "
             "-- no network, fully reproducible")
    parser.add_argument(
        "--captured", default=None,
        help="ISO capture date to record (defaults to today)")
    parser.add_argument(
        "-o", "--out", type=Path,
        help="output path (defaults to sources/<video_id>.chapters.json)")
    args = parser.parse_args(argv)

    if args.from_json:
        raw = (sys.stdin.read() if str(args.from_json) == "-"
              else args.from_json.read_text(encoding="utf-8"))
        info = json.loads(raw)
        captured_with = CAPTURED_WITH
    else:
        if not args.url:
            parser.error("the following arguments are required: url")
        info = fetch_raw(args.url)
        captured_with = CAPTURED_WITH

    captured = args.captured or dt.date.today().isoformat()
    payload = capture_payload(info, captured=captured,
                              captured_with=captured_with)
    out = args.out or SOURCES / f"{payload['video_id']}.chapters.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
