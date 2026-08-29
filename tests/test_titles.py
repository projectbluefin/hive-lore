"""Tests for the title-slide subtitle supplier.

Covers the four things the contract promises: determinism (same chapter, same
bytes, forever), complete coverage of the 12 publisher chapters in order, the
bans on person-facing claims and lifted character epithets, and mandatory
provenance with resolvable lore/mapping references.

Offline: no network, no footage, no model.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
VOCAB = ROOT / "vocab" / "season-one.yaml"
LORE = ROOT / "lore" / "witch-queen.md"
MAPPING = ROOT / "mapping" / "kubestellar-hive.md"
TITLES = ROOT / "tools" / "titles.py"

# The 12 publisher chapter titles, verbatim and in order. These are the slide
# headlines and nothing in this repository may rewrite them (AGENTS.md).
PUBLISHER_CHAPTERS = [
    "The Enclave",
    "On Mars",
    "Savathun",
    "The Relic",
    "To Be Chosen",
    "Remembering",
    "Council",
    "Worm",
    "Defeated",
    "The Witness",
    "With Mara",
    "Raid",
]

NATURES = {"canon", "canon_inspired", "extrapolation"}

# Known person-shaped strings that must never appear in a subtitle. The
# yaml's banned_terms list is the policy floor; these are regression pins
# for the specific failure the contract exists to prevent — a subtitle that
# reads as being about a person.
PERSON_FACING_PINS = [
    "castrojo",
    "nimbinatus",
    "nimbatus",
    "Danathar",
    "Angie",
    "Shellea",
    "CortNick",
    "pull request author",
    "merged by",
    "employer",
]


def load_vocab() -> dict:
    with open(VOCAB, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def doc_ids(path: Path) -> set[str]:
    """The stable entry IDs of a reference doc: its `##` heading slugs."""
    return {
        match.group(1).strip()
        for match in re.finditer(r"^##\s+(.+)$", path.read_text(encoding="utf-8"), re.M)
    }


def run_cli(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, str(TITLES), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def all_candidates(vocab: dict):
    for chapter in vocab["chapters"]:
        for candidate in chapter["candidates"]:
            yield chapter, candidate


def test_exactly_twelve_chapters_in_publisher_order():
    vocab = load_vocab()
    headlines = [c["headline"] for c in vocab["chapters"]]
    assert headlines == PUBLISHER_CHAPTERS
    assert [c["number"] for c in vocab["chapters"]] == list(range(1, 13))


def test_each_chapter_has_exactly_three_candidates():
    vocab = load_vocab()
    assert vocab["policy"]["candidates_per_chapter"] == 3
    for chapter in vocab["chapters"]:
        assert len(chapter["candidates"]) == 3, chapter["headline"]
        assert [c["id"] for c in chapter["candidates"]] == [1, 2, 3]


def test_cli_is_deterministic_for_every_chapter():
    for number in range(1, 13):
        assert run_cli(str(number)) == run_cli(str(number))
    assert run_cli("--all") == run_cli("--all")


def test_cli_payload_matches_committed_vocab():
    vocab = load_vocab()
    payload = json.loads(run_cli("4"))
    chapter = vocab["chapters"][3]
    assert payload["chapter"] == 4
    assert payload["headline"] == chapter["headline"] == "The Relic"
    assert payload["candidates"] == chapter["candidates"]
    assert payload["authorised_by"] == vocab["authorised_by"]


def test_cli_rejects_unknown_chapter():
    result = subprocess.run(
        [sys.executable, str(TITLES), "13"], capture_output=True, text=True
    )
    assert result.returncode == 2
    assert "no chapter numbered 13" in result.stderr


def test_every_candidate_carries_full_provenance():
    vocab = load_vocab()
    for chapter, candidate in all_candidates(vocab):
        where = f"chapter {chapter['number']} candidate {candidate['id']}"
        assert candidate["text"].strip(), where
        assert candidate["copy_source"] == "generated_lore", where
        assert candidate["nature"] in NATURES, where
        assert isinstance(candidate["lore_refs"], list), where
        assert isinstance(candidate["mapping_refs"], list), where
        assert candidate["lore_refs"] or candidate["mapping_refs"], where
    assert vocab["authorised_by"].strip()


def test_every_ref_resolves_to_a_cited_entry():
    lore_ids = doc_ids(LORE)
    mapping_ids = doc_ids(MAPPING)
    assert lore_ids, "lore doc has no entries"
    assert mapping_ids, "mapping doc has no entries"
    for chapter, candidate in all_candidates(load_vocab()):
        for ref in candidate["lore_refs"]:
            assert ref in lore_ids, f"{ref} has no entry in {LORE.name}"
        for ref in candidate["mapping_refs"]:
            assert ref in mapping_ids, f"{ref} has no entry in {MAPPING.name}"


def test_no_banned_term_appears_in_any_subtitle():
    vocab = load_vocab()
    banned = vocab["banned_terms"]
    assert banned, "the banned list must exist and be non-empty"
    for chapter, candidate in all_candidates(vocab):
        text = candidate["text"]
        for term in banned:
            if term == "@":
                assert term not in text, f"@{chapter['number']}: {text!r}"
            else:
                assert term.lower() not in text.lower(), (
                    f"banned term {term!r} in {text!r}"
                )


def test_no_person_facing_claim_appears_in_any_subtitle():
    for chapter, candidate in all_candidates(load_vocab()):
        text = candidate["text"].lower()
        for pin in PERSON_FACING_PINS:
            assert pin.lower() not in text, (
                f"person-facing string {pin!r} in {candidate['text']!r}"
            )


def test_scope_is_title_slide_only():
    policy = load_vocab()["policy"]
    assert policy["generated_scope"] == "title_slide_subtitle_only"
    assert policy["headlines"] == "publisher_verbatim"
    assert policy["frozen_downstream"] is True


def test_owner_authored_ship_lore_is_verbatim():
    """Owner, 2026-08-29: Witch Queen archive 01:53 lower third, exactly two
    lines. Verbatim or omitted — never paraphrased, never canon."""
    entries = {e["id"]: e for e in load_vocab()["project_lore"]}
    ship = entries["savathuns-ship"]
    assert ship["lines"] == ["Palace of AI Expectations", "Tomb of Platform Teams"]
    assert ship["source"] == "Witch Queen archive, 01:53, bottom-right lower third"
    assert ship["nature"] == "owner_authored"
    assert ship["copy_source"] == "owner_authored_lore"
    assert ship["person_facing"] == "never"


def test_project_lore_is_never_canon_and_never_person_facing():
    vocab = load_vocab()
    for entry in vocab["project_lore"]:
        assert entry["nature"] == "owner_authored", entry["id"]
        assert entry["person_facing"] == "never", entry["id"]
        # Kept off the heroes and out of the canon reference: project-lore
        # text must not appear in any subtitle candidate or the lore doc.
        for line in entry["lines"]:
            for chapter, candidate in all_candidates(vocab):
                assert line.lower() not in candidate["text"].lower()
            assert line.lower() not in LORE.read_text(encoding="utf-8").lower()
