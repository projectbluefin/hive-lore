# hive-lore — Agent Operating Contract

`hive-lore` holds the **epithet policy**: the rules for putting a fictional
title row on a card that credits a real person, and the lore that title is
drawn from.

It exists because `castrojo/destiny-vids` said *"Never invent on-screen copy"*
and the owner then authorised exactly one narrow exception. That exception
needs a contract of its own, or it becomes a hole in the one it came from.

## What this repository is for

Project Bluefin's videos credit real contributors on Destiny-style nameplates.
A nameplate carries a `name` row and a `title` row:

```
    MAINTAINER // GUARDIAN        <- label
    Danathar                      <- name   : a real person
    Blade of the Unbroken Tithe   <- title  : fiction
```

The `name` row is a claim about a human being. The `title` row is a costume.
This repository is the wardrobe, and the rules for who may wear what.

## Rule zero: the name is never generated

**A person's name row is their verified GitHub login, or copy the owner wrote.
It is never generated, never expanded, never "corrected".**

This is not softened by anything below. `destiny-vids` records the scar:
`github.com/nimbatus` is an unrelated empty account while Laura Santamaria is
`nimbinatus`, so resolving her by the character string would have put a
stranger's face on her credit. A login is verifiable; a display name is not;
an inferred real name is neither.

| | |
|---|---|
| Login verified, profile declares a real name | Either may be used. The owner picks. |
| Login verified, profile declares only the handle | **Use the handle.** It is honest. |
| Login verified, profile `name` is null | **Use the handle.** |
| No verified login | The person is not credited yet. Record it; do not guess. |

A handle is not a gap to be filled. `Danathar`'s profile says `Danathar`, and
`Danathar` is what the card says.

## The exception this repository exists to govern

Owner, authorising it: *"you may generate lore appropriate things, this
project needs AI generated titles to rotate weekly."*

So: **`title` may be generated. Nothing else may be.**

That is defensible because the title row is already fiction everywhere it
appears — Bob Killen is "Reconciler of the Plane", nobody believes he holds
that office — and because an epithet makes no factual claim about the person
wearing it. The moment a generated string would read as biography, affiliation,
employer, role, pronoun, or achievement, it has stopped being an epithet and
this exception no longer covers it.

### The closed field set still holds

The deck's fields are `label`, `class`, `name`, `title`, `trustee`. This
repository adds **no field**. It only supplies strings for `title`.

An epithet that needs a new row is not an epithet. Do not add an `AS
<CHARACTER>` line, a role line, or a house line to carry it.

## Generation must be deterministic

**A re-render must never reshuffle who was called what.** A card that reads
"Blade of the Unbroken Tithe" on Monday and something else on Tuesday makes
every earlier render stale, and stale copy is the one failure `destiny-vids`
refuses outright.

So generation is a **pure function of `(login, ISO week)`** over a committed
pool:

```
    epithet(login, iso_week) -> deterministic pick from vocab/
```

- The pool is committed here. It is data, not model output at render time.
- The seed is the ISO week, which is what "rotate weekly" means: the same
  person gets the same epithet all week, and a different one next week.
- No network call, no model call, at render time. A video built from week
  2026-W35 is reproducible in 2027 by asking for week 2026-W35.
- `tools/` regenerates; nothing downstream hand-edits an assigned epithet.

`destiny-vids`' `tools/ensemble.py` already seeds its rotation on the month
for exactly this reason. This is the same posture with a finer period.

### Rotation is not permission to churn a delivered film

A delivered video's epithets are **frozen at the week it was built**, recorded
in its manifest. Rotation applies to the *next* build, never retroactively.
Nothing in this repository is a reason to re-render a shipped act.

## The lore must be real lore

An epithet is generated from **canon Destiny Hive material**, recorded in
`lore/` with citations, and mapped onto the **actual architecture** of
`kubestellar/hive`, recorded in `mapping/`.

- Canon and extrapolation are labelled differently. A pattern inferred from
  three examples is marked as inferred.
- An epithet is assembled from documented Hive naming *grammar*, not lifted
  wholesale from a named character. Nobody gets to be Oryx.
- The mapping to the software is evidenced from the repository, not imagined.
  If `hive` has no component that fits, the metaphor does not get invented to
  fill the hole.

## Nobody is made a monster

The Hive are, in fiction, cruel. The people being credited are colleagues.

**An epithet must read as honorific.** Grand, ritual, a little baroque — never
an insult, never a slur, never a joke at the wearer's expense, and never
implying villainy a real person would object to.

- Cannon-fodder castes (`Thrall` and below) are **banned** as epithet material.
  Being credited as the lowest disposable rank is an insult even in jest.
- Terms coding cowardice, servility, filth, decay of the person, or bodily
  horror are banned.
- Anything that reads as a comment on the person's appearance, nationality,
  gender, or beliefs is banned outright.
- `vocab/banned.yaml` is the list, and it is a floor rather than a ceiling:
  a term that clears the list and still reads badly is still wrong.

**When in doubt, it does not ship.** An unassigned epithet degrades to no
title row at all, which is a complete, correct card.

## Degrade, never block

Inherited from `destiny-vids`, and unchanged:

- No epithet for somebody? **The card renders without a title row.** That is a
  finished card, not a broken one.
- Lore missing for a component? Record it; ship the rest.
- Nothing here may hold a release. A missing costume is never a reason to
  withhold a film.

## Provenance is mandatory

Every assigned epithet records where it came from:

| Field | Meaning |
|---|---|
| `copy_source: generated_lore` | Produced by this repository's generator. |
| `lore_refs` | The `lore/` entries the parts came from. |
| `seed` | The `(login, iso_week)` pair that produced it. |
| `authorised_by` | The owner instruction permitting generation at all. |

A generated title with no provenance is indistinguishable from an invented
one, which is the thing the parent contract bans. **`copy_source` is not
optional.**

## Boundaries

- **Never credit anyone this repository cannot resolve to a verified login.**
- **Never generate a `name`, a `class`, or a `label`.** Only `title`.
- **Never present extrapolation as canon.**
- **Never re-render a delivered film to apply a rotation.**
- **Never add a nameplate field.**
- This repository holds text and data. **No footage, no avatars, no renders.**

## Relationship to the other repositories

| Repository | Authority |
|---|---|
| `castrojo/destiny-vids` | The film, the plates, the casting, delivery. **Outranks this repo on everything except epithet text.** |
| `projectbluefin/hive-lore` | Epithet policy, lore reference, the architecture mapping, the generator. |
| `kubestellar/hive` | The software being mapped. Read-only evidence; never edited from here. |

This repository is a **supplier**. It hands `destiny-vids` strings for one
field. It does not decide who is cast, where a plate sits, when a film ships,
or what a person's name is.

## Layout

```
    AGENTS.md          this contract
    lore/              Destiny Hive reference, cited
    mapping/           kubestellar/hive architecture -> lore metaphor
    vocab/             the epithet pools and the banned list
    tools/             the deterministic generator
    tests/             the generator, the bans, and determinism
```

## Verification

```bash
python3 -m pytest -q          # determinism, banned terms, provenance
```

A generator change that moves an existing `(login, week)` assignment must fail
the suite. That is the point of the suite.
