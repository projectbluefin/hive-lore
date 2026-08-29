#!/usr/bin/env python3
"""tools/titles.py — deterministic title-slide subtitle supplier.

Usage:
    python3 tools/titles.py <chapter>     # one chapter's candidates as JSON
    python3 tools/titles.py --all         # all 12 chapters as JSON
    python3 tools/titles.py --list        # chapter numbers and headlines
    python3 tools/titles.py --project-lore  # owner-authored project lore records

Selection is a pure function of chapter number: no clock, no randomness, no
network. The same input prints the same bytes forever. `destiny-vids` picks
one candidate per chapter and freezes it; nothing here knows or cares which.

Stdlib plus PyYAML (already a project dependency) only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
VOCAB = ROOT / "vocab" / "season-one.yaml"


def load_season(path: Path = VOCAB) -> dict:
    """Load the committed season vocab. Pure lookup data, no computation."""
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def chapter_payload(season: dict, number: int) -> dict:
    """One chapter's headline and candidates, or raise for an unknown number."""
    for chapter in season["chapters"]:
        if chapter["number"] == number:
            return {
                "season": season["season"],
                "chapter": chapter["number"],
                "headline": chapter["headline"],
                "candidates": chapter["candidates"],
                "authorised_by": season["authorised_by"],
            }
    raise KeyError(f"no chapter numbered {number}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print deterministic title-slide subtitle candidates as JSON."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("chapter", nargs="?", type=int, help="chapter number (1-12)")
    group.add_argument("--all", action="store_true", help="all chapters")
    group.add_argument("--list", action="store_true", help="chapter numbers and headlines only")
    group.add_argument(
        "--project-lore",
        action="store_true",
        help="owner-authored project lore records (verbatim, with source and placement)",
    )
    args = parser.parse_args(argv)

    season = load_season()

    if args.project_lore:
        payload = {
            "season": season["season"],
            "project_lore": season["project_lore"],
        }
    elif args.list:
        payload = {
            "season": season["season"],
            "chapters": [
                {"chapter": c["number"], "headline": c["headline"]}
                for c in season["chapters"]
            ],
        }
    elif args.all:
        payload = {
            "season": season["season"],
            "chapters": [
                {
                    "chapter": c["number"],
                    "headline": c["headline"],
                    "candidates": c["candidates"],
                }
                for c in season["chapters"]
            ],
            "authorised_by": season["authorised_by"],
        }
    else:
        try:
            payload = chapter_payload(season, args.chapter)
        except KeyError as exc:
            print(f"titles: {exc.args[0]}", file=sys.stderr)
            return 2

    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
