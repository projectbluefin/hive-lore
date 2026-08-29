# kubestellar/hive — architecture mapping

Verified facts about `kubestellar/hive` used as the project half of the
title-slide metaphor. Every entry has a stable ID (the `##` heading slug) that
`vocab/season-one.yaml` references through `mapping_refs`.
`tests/test_titles.py` fails if a `mapping_refs` value has no entry here.

Primary source: the `kubestellar/hive` README on the `v4` branch —
<https://github.com/kubestellar/hive>. All entries below are evidenced from
that README unless marked *(extrapolation)*.

## orchestrator

Hive is **a single Go binary** for AI agent orchestration on open source
projects. It **enumerates GitHub issues and PRs, classifies them by
complexity, and dispatches work to AI agents** (Claude, Copilot, Gemini,
Goose) on **adaptive cadences governed by queue depth**.

Source: README overview paragraph.

## deterministic-pipeline

Hive separates decisions into two layers. A **deterministic pipeline of shell
scripts handles filtering, classification, merge-gating, and enforcement
before any LLM sees the work**. Agents only handle judgment calls — reading
code, reasoning about fixes, writing PRs.

Source: README overview paragraph.

## agent-roster

The dispatched agents are a named roster of model backends: **Claude, Copilot,
Gemini, and Goose**. Several voices, one queue of work.

Source: README overview paragraph. *(The council metaphor in the vocab treats
the roster as a court; that shape is extrapolation, the roster is fact.)*

## cadence

Agents are dispatched on **adaptive cadences governed by queue depth**: the
more work waiting, the faster the hive cycles.

Source: README overview paragraph.

## gateway

The deployment is **two services: Hive plus its authenticating gateway**, and
the gateway publishes a **single port (3001)** for the dashboard. Internal
ports stay inside the container network. The stack is confirmed end to end
with `curl -sf http://127.0.0.1:3001/api/health`.

Source: README quick-start sections (Compose and Podman).

## enforcement-gate

The security posture is an **enforced egress gate**: the shipped unit requests
`CAP_NET_ADMIN` so the forced-proxy gate is on by default, and without the
capability (or a deliberate advisory-mode opt-in) **Hive refuses to start with
exit 77 rather than run an unenforced capability model**.

Source: README "Security posture" section.

## persistence

The Podman path wires the stack to **boot through systemd units** so it
survives reboots, and a lifecycle probe distinguishes "healthy now" from
"healthy after a reboot". The Kubernetes path keeps state on a
PersistentVolumeClaim.

Source: README Podman and Kubernetes sections.

## hub

**The Hive Hub** (<https://hive.kubestellar.io>) provides hosted hives with
OAuth-protected dashboards, a public registry, and **cross-hive leaderboards**
— an alliance of hives with no cluster required.

Source: README Hub section.

## classification

Issues and PRs are **classified by complexity** so that agents are dispatched
to work sized for them. Judgment is delegated to agents; classification and
gating are not.

Source: README overview paragraph. *(The phrasing "judgment is delegated,
enforcement is not" in the vocab is extrapolation from the two-layer split.)*
