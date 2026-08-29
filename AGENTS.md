# hive-lore — Agent Operating Contract

`hive-lore` supplies **title-slide lore**: the subtitle candidates that sit
under the publisher chapter titles on the episode title slides of *Season of
the Blueberries*, the 12-chapter KubeStellar contributor series cut in
`castrojo/destiny-vids`.

It exists because `castrojo/destiny-vids` said *"Never invent on-screen copy"*
and the owner then authorised exactly one narrow exception. That exception
needs a contract of its own, or it becomes a hole in the one it came from.

## The corrected scope

Owner, correcting the previous contract: **custom/generated lore belongs only
on episode title slides. Contributor nameplates are factual GitHub data and
get no generated title.**

The contributor-epithet contract this file previously carried — generating a
`title` row for a real person's nameplate — is **obsolete and revoked**. It
was written before that ruling and it overreached:

| | |
|---|---|
| Episode title slide | Headline: the publisher chapter title, **verbatim and untouchable**. Subtitle: may be generated, from this repository's committed pool. |
| Contributor nameplate | **Factual GitHub data only.** Name, stats, dates. No generated title, no epithet, no lore string. Ever. |

The scar that already lived here still stands as the reason: a credit row is
a claim about a human being (`github.com/nimbatus` is a stranger;
`nimbinatus` is Laura Santamaria). A generated epithet next to a real login
reads as biography the moment it is on screen. The only generated prose left
in the programme is a subtitle under a chapter headline, where it plainly
describes the episode, not a person.

## Rule zero: the headline is the publisher's

Each of the 12 chapters keeps its **publisher chapter title** as the slide
headline, unchanged: *The Enclave, On Mars, Savathun, The Relic, To Be
Chosen, Remembering, Council, Worm, Defeated, The Witness, With Mara, Raid*.

Nothing here rewrites, reorders, shortens, or "improves" those headlines.
Their provenance is recorded in `vocab/season-one.yaml` under
`headline_source`: the publisher chapter metadata of
<https://www.youtube.com/watch?v=jlzQnXcUxqI>, captured with
`yt-dlp --dump-single-json --skip-download` and reshaped by
[`tools/capture_chapters.py`](tools/capture_chapters.py) into
`sources/jlzQnXcUxqI.chapters.json` — the artifact is the authority the
headlines are validated against. The raw yt-dlp dump nests each chapter
under `start_time`/`end_time` inside a video info dict of unrelated fields;
it is never the artifact's shape by itself, only that tool's input.
`captured_with` on both records names the actual pipeline, not the raw
command alone. This repository only offers **three subtitle candidates per
chapter**, and downstream picks one and freezes it.

## Generation is a proposal, and it is deterministic

For each chapter, `vocab/season-one.yaml` carries **three reviewed,
copyeditable subtitle candidates**. The owner may edit a candidate's words;
they may not edit the set below three without deleting the chapter's slide.

- Selection is a **pure function of chapter number** — `tools/titles.py
  <chapter>` prints the same JSON today, next week, and in 2027. No network
  call, no model call, no clock, no randomness.
- **The chosen subtitle is frozen downstream.** Once `destiny-vids` records
  a pick for a chapter, changing it there is a new editorial decision, never
  a side effect of a rebuild. A change to a candidate here does not reach an
  already-delivered episode.
- A re-render must never reshuffle copy. Stale copy is the one failure
  `destiny-vids` refuses outright.

## The lore must be real lore

Subtitles draw on **canon Destiny material**, recorded in
[`lore/witch-queen.md`](lore/witch-queen.md) with citations, and on the
**actual architecture** of `kubestellar/hive`, recorded in
[`mapping/kubestellar-hive.md`](mapping/kubestellar-hive.md) from the
repository's own README.

- Canon and extrapolation are labelled differently. Every candidate carries a
  `nature` field: `canon_inspired` (grammar or imagery assembled from cited
  canon terms) or `extrapolation` (the project metaphor). A pattern inferred
  from examples is marked as inferred. **A candidate never carries `canon`** —
  candidates are stylized project copy, and a `canon` label would assert the
  words are quoted scripture. Canon claims live in `lore/` entries only.
- A subtitle is assembled from documented lore terms, **not** lifted from a
  named character's epithet. Nobody's episode is titled by stealing Oryx's
  or Savathûn's personal titles.
- The mapping to the software is evidenced from the `kubestellar/hive`
  repository, not imagined. If the architecture has no component that fits,
  the metaphor does not get invented to fill the hole.

## Owner-authored project lore is a fourth class of copy

Beside `canon`, `canon_inspired`, and `extrapolation` there is
**`owner_authored`**: lore the owner wrote for this project. It is recorded in
`vocab/season-one.yaml` under `project_lore` with its source timecode and
exact wording.

| | |
|---|---|
| It is **project lore, never Destiny canon.** It may not be cited as canon and may not inform `canon*` candidates. |
| The wording is **verbatim**. Reproduce it exactly or omit it; never paraphrase, "fix", or extend it. |
| It is **kept off the heroes.** It never renders on a nameplate, dossier, or any person-facing surface. Placement belongs to the film renderer; this repository supplies provenance and data only. |

Current record: `savathuns-ship` — source 01:53 in the Witch Queen archive, a
bottom-right lower third naming Savathûn's ship from this project's point of
view, in exactly two lines: `Palace of AI Expectations` /
`Tomb of Platform Teams`.

## Subtitles are never about people

A subtitle describes the **episode's fiction or its architecture metaphor**.
It never describes a contributor, a GitHub account, a company, or a role.

- No login, display name, real name, or `@`-mention appears in a subtitle.
- No factual claim about any person: no roles, employers, achievements,
  pronouns, or affiliations — not even flattering ones.
- `banned_terms` in `vocab/season-one.yaml` is the floor, not the ceiling: a
  term that clears the list and still reads as a person-facing claim is still
  wrong. `tests/test_titles.py` enforces both.

**When in doubt, the candidate does not ship.** A chapter with no acceptable
subtitle degrades to the publisher headline alone, which is a complete,
correct title slide.

## Degrade, never block

Inherited from `destiny-vids`, and unchanged:

- No acceptable subtitle for a chapter? **The slide renders with the headline
  only.** That is a finished slide, not a broken one.
- Lore missing for a chapter's theme? Record it; ship the rest.
- Nothing here may hold a release. A missing subtitle is never a reason to
  withhold an episode.

## Provenance is mandatory

Every candidate in `vocab/season-one.yaml` records where it came from:

| Field | Meaning |
|---|---|
| `copy_source: generated_lore` | Produced under this repository's contract. |
| `lore_refs` | The `lore/` entry IDs the canon parts came from. May be empty. |
| `mapping_refs` | The `mapping/` entry IDs the architecture metaphor came from. May be empty. |
| `nature` | `canon_inspired` or `extrapolation` for candidates (`canon` is reserved for `lore/` claims); `owner_authored` for `project_lore`. |
| `authorised_by` | The owner instruction permitting generation at all. |

A generated subtitle with no provenance is indistinguishable from an invented
one, which is the thing the parent contract bans. **`copy_source` is not
optional.**

## Boundaries

- **Never put generated copy on a contributor nameplate.** That is the whole
  correction.
- **Never rewrite a publisher chapter title.**
- **Never name or reference a real person in a subtitle.**
- **Never present extrapolation as canon.**
- **Never unfreeze a subtitle downstream has already frozen.** A candidate
  edit here applies to unpicked chapters only.
- This repository holds text and data. **No footage, no avatars, no renders.**

## Relationship to the other repositories

| Repository | Authority |
|---|---|
| `castrojo/destiny-vids` | The season, the slides, the casting, the freeze, delivery. **Outranks this repo on everything except subtitle candidate text.** |
| `projectbluefin/hive-lore` | Subtitle policy, lore reference, the architecture mapping, the deterministic CLI. |
| `kubestellar/hive` | The software being mapped. Read-only evidence; never edited from here. |

This repository is a **supplier**. It hands `destiny-vids` three strings per
chapter. It does not decide which one ships, where a slide sits, when an
episode airs, or anything about a contributor.

## Layout

```
    AGENTS.md          this contract
    lore/              Destiny Witch Queen reference, cited
    mapping/           kubestellar/hive architecture -> lore metaphor
    vocab/             season-one subtitle candidates and the banned list
    tools/             the deterministic CLI, and the chapter capture/reshape tool
    tests/             determinism, coverage, banned-terms, provenance
```

## Verification

```bash
python3 -m pytest -q          # determinism, coverage, banned terms, provenance
```

The suite is offline: no network, no footage, no model. A change that alters
what `tools/titles.py <chapter>` prints for a frozen chapter must be caught
by review, and a change that breaks determinism, coverage, or the bans fails
the suite. That is the point of the suite.
