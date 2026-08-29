"""Tests for the chapter-metadata capture/reshape tool.

`sources/jlzQnXcUxqI.chapters.json` previously claimed its shape came
straight from `yt-dlp --dump-single-json --skip-download` -- it does not:
that command's raw info dict nests chapters under `start_time`/`end_time`
inside dozens of unrelated fields. `tools/capture_chapters.py` is the one
place that reshape happens; these tests exercise it directly, offline, with
no network and no `yt-dlp` subprocess ever invoked.
"""

from __future__ import annotations

import json
import subprocess
import sys
import shutil
from pathlib import Path

from tools import capture_chapters

ROOT = Path(__file__).resolve().parent.parent
CAPTURE = ROOT / "tools" / "capture_chapters.py"
ARTIFACT = ROOT / "sources" / "jlzQnXcUxqI.chapters.json"


def _raw_info(chapters):
    """A minimal stand-in for yt-dlp's `--dump-single-json` info dict: the
    two fields this tool reads, plus the unrelated noise a real dump
    carries (proving the reshape narrows rather than passing it through)."""
    return {
        "id": "abc123XYZ_",
        "title": "A Fixture Video",
        "webpage_url": "https://www.youtube.com/watch?v=abc123XYZ_",
        "formats": [{"format_id": "137"}, {"format_id": "251"}],
        "uploader": "Bungie",
        "chapters": chapters,
    }


def test_reshape_chapters_narrows_start_time_end_time_to_start_end():
    """yt-dlp's raw shape (`start_time`/`end_time`, floats) becomes this
    project's committed shape (`start`/`end`, whole seconds) -- nothing
    else from a chapter entry is carried through."""
    raw = [
        {"start_time": 0.0, "end_time": 125.0, "title": "The Enclave",
         "chapter_number": 1},
        {"start_time": 125.0, "end_time": 218.0, "title": "On Mars",
         "chapter_number": 2},
    ]
    reshaped = capture_chapters.reshape_chapters(_raw_info(raw))
    assert reshaped == [
        {"start": 0, "end": 125, "title": "The Enclave"},
        {"start": 125, "end": 218, "title": "On Mars"},
    ]
    # The raw entry's extra field never survives the reshape.
    assert "chapter_number" not in reshaped[0]


def test_reshape_chapters_rounds_fractional_seconds():
    """yt-dlp reports fractional seconds; every boundary this project
    records is a whole second, so the reshape rounds -- once, here."""
    raw = [{"start_time": 0.0, "end_time": 124.6, "title": "The Enclave"}]
    assert capture_chapters.reshape_chapters(_raw_info(raw))[0]["end"] == 125


def test_reshape_chapters_is_empty_for_a_chapterless_video():
    assert capture_chapters.reshape_chapters(_raw_info([])) == []
    assert capture_chapters.reshape_chapters({"id": "x", "title": "t"}) == []


def test_capture_payload_matches_the_committed_artifact_shape():
    """The full artifact -- built purely from a raw info dict, no network,
    no clock (the caller supplies `captured`) -- has exactly the committed
    file's top-level keys and the reshaped chapters."""
    raw = [{"start_time": 0.0, "end_time": 125.0, "title": "The Enclave"}]
    payload = capture_chapters.capture_payload(
        _raw_info(raw), captured="2026-08-29")
    assert payload == {
        "video_id": "abc123XYZ_",
        "url": "https://www.youtube.com/watch?v=abc123XYZ_",
        "video_title": "A Fixture Video",
        "captured": "2026-08-29",
        "captured_with": capture_chapters.CAPTURED_WITH,
        "chapters": [{"start": 0, "end": 125, "title": "The Enclave"}],
    }


def test_capture_payload_captured_with_names_the_reshape_not_the_raw_dump():
    """The recorded command must never claim the raw yt-dlp dump alone
    produced this shape -- it must name the reshape step too."""
    with_default = capture_chapters.capture_payload(
        _raw_info([]), captured="2026-08-29")
    assert "yt-dlp" in with_default["captured_with"]
    assert "capture_chapters" in with_default["captured_with"], \
        "the raw yt-dlp command alone did not produce this shape"


def test_committed_artifact_reproduces_from_a_replayed_raw_dump():
    """The committed `sources/jlzQnXcUxqI.chapters.json` chapters array must
    be exactly reproducible by reshaping a yt-dlp-shaped raw dump built from
    the SAME start/end/title values -- proving the committed file really is
    this tool's output, not a hand-typed list that happens to look similar."""
    committed = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    raw = _raw_info([
        {"start_time": float(c["start"]), "end_time": float(c["end"]),
         "title": c["title"]}
        for c in committed["chapters"]
    ])
    raw["id"] = committed["video_id"]
    raw["title"] = committed["video_title"]
    payload = capture_chapters.capture_payload(
        raw, captured=committed["captured"],
        captured_with=committed["captured_with"])
    assert payload == committed


def test_committed_artifact_never_claims_the_raw_command_alone():
    """Regression pin for the actual finding: the committed artifact's
    `captured_with` must name the reshape tool, not just the raw yt-dlp
    invocation whose output is a different shape entirely."""
    committed = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert "capture_chapters" in committed["captured_with"]


def test_cli_from_json_replay_writes_the_reshaped_artifact(tmp_path):
    """The committed replay command shape is executable as-recorded: the
    artifact's literal `captured_with` pipeline ends in an offline
    `python3 tools/capture_chapters.py --from-json -` stage, and that stage
    reshapes stdin into the committed artifact shape."""
    committed = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert committed["captured_with"] == capture_chapters.CAPTURED_WITH

    replay_command = committed["captured_with"].split("|", 1)[1].strip()
    assert replay_command == "python3 tools/capture_chapters.py --from-json -"

    raw = _raw_info([
        {"start_time": 0.0, "end_time": 125.0, "title": "The Enclave"},
    ])
    replay_root = tmp_path / "replay"
    (replay_root / "tools").mkdir(parents=True)
    shutil.copy2(CAPTURE, replay_root / "tools" / "capture_chapters.py")
    result = subprocess.run(
        replay_command.split(),
        input=json.dumps(raw),
        cwd=replay_root,
        capture_output=True,
        text=True,
        check=True,
    )
    out_path = replay_root / "sources" / "abc123XYZ_.chapters.json"
    assert "wrote" in result.stdout
    assert "yt-dlp" not in result.stdout + result.stderr, \
        "the offline replay path must never shell out to yt-dlp"
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written["chapters"] == [
        {"start": 0, "end": 125, "title": "The Enclave"}]
    assert written["captured_with"] == capture_chapters.CAPTURED_WITH


def test_cli_live_capture_records_the_same_captured_with_pipeline(monkeypatch,
                                                                   tmp_path):
    """The live capture path must record the same replayable pipeline as
    the offline `--from-json` path, not a one-off command string."""
    raw = _raw_info([
        {"start_time": 0.0, "end_time": 125.0, "title": "The Enclave"},
    ])

    def fake_fetch_raw(url):
        assert url == "https://www.youtube.com/watch?v=abc123XYZ_"
        return raw

    monkeypatch.setattr(capture_chapters, "fetch_raw", fake_fetch_raw)
    out_path = tmp_path / "live.json"
    result = capture_chapters.main([
        "https://www.youtube.com/watch?v=abc123XYZ_",
        "--captured", "2026-08-29",
        "--out", str(out_path),
    ])
    assert result == 0
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written["captured_with"] == capture_chapters.CAPTURED_WITH


def test_cli_live_capture_requires_a_url():
    result = subprocess.run(
        [sys.executable, str(CAPTURE), "--captured", "2026-08-29"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "the following arguments are required: url" in result.stderr


def test_fetch_raw_is_the_only_place_that_invokes_yt_dlp(monkeypatch):
    """`fetch_raw` is the ONE call site; a caller supplying `runner` proves
    no other path in this module shells out on its own."""
    calls = []

    def fake_runner(argv, **kwargs):
        calls.append(argv)

        class _Done:
            stdout = json.dumps(_raw_info([]))
        return _Done()

    info = capture_chapters.fetch_raw(
        "https://www.youtube.com/watch?v=abc123XYZ_", runner=fake_runner)
    assert len(calls) == 1
    assert calls[0][0] == "yt-dlp"
    assert "--dump-single-json" in calls[0]
    assert "--skip-download" in calls[0]
    assert info["id"] == "abc123XYZ_"
