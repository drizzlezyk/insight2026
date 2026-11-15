# ClawSweeper issue scoring/rating — primary-source account

**Scope:** How the "clawsweeper" bot assigns a *rating/score* to a GitHub **issue** in the
OpenClaw project (formerly Clawdbot / Moltbot).

**Key correction up front:** ClawSweeper does **not** score issues on a numeric scale, and it
does **not** use labels like `impact:low/medium/high`, `priority:p0/p1`, `community:rated`, or
`score:*`. An issue's *quality* is expressed by a deterministic mapping of two review fields
(`reproductionStatus` × `reproductionConfidence`) onto seven **`issue-rating: <emoji> <animal>`**
labels. Severity and routing are separate, orthogonal axes: `P0`–`P3` (priority), `impact:<category>`
(9 product-surface categories), and `clawsweeper:*` advisory labels.

All file line numbers below are against `openclaw/clawsweeper` @ commit
`a053c717e23fab69e83f6f2a0020da0c51bc6931` (`main`, dated 2026-11-14T11:53:57Z).

---

## 1. Sources (primary)

| # | Source | URL |
|---|--------|-----|
| S1 | Bot source repo (the scoring logic lives here) | https://github.com/openclaw/clawsweeper |
| S2 | Target repo (labels + issues live here) | https://github.com/openclaw/openclaw |
| S3 | Rating mapping function (exact code) | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/src/clawsweeper-label-selection.ts#L149-L181 |
| S4 | Advisory label selection (same file) | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/src/clawsweeper-label-selection.ts#L182-L289 |
| S5 | Output schema (field rubric) | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/schema/clawsweeper-decision.schema.json |
| S6 | Decision types (`ReproductionStatus`, `Confidence`) | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/src/clawsweeper-types.ts#L85-L90 , L182 |
| S7 | Base review prompt | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/prompts/review-item.md |
| S8 | Issue-specific prompt fragment | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/prompts/review-item-issue.md |
| S9 | Intake contract (the pre-classification call) | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/src/intake-triage-contract.ts |
| S10 | Intake doc | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/docs/intake-triage.md |
| S11 | Advisory-label doc (source→label table) | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/docs/work-lane.md |
| S12 | Label publication (apply path) | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/src/clawsweeper-apply-report-labels.ts#L224-L261 |
| S13 | Label sync operations | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/src/clawsweeper-label-operations.ts#L237-L315 |
| S14 | Failed-review retry | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/src/clawsweeper-failed-review-retry.ts |
| S15 | PR rating (contrast: `rating:` not `issue-rating:`) | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/src/clawsweeper-rating.ts |
| S16 | Live label list (GitHub API) | https://api.github.com/repos/openclaw/openclaw/labels |
| S17 | Limits / retries | https://github.com/openclaw/clawsweeper/blob/a053c717e23fab69e83f6f2a0020da0c51bc6931/docs/limits.md |

---

## 2. The scoring labels (exact)

Fetched from the GitHub API (S16) on 2026-11-14. There are exactly **seven** `issue-rating:`
labels in `openclaw/openclaw`. Name, color, and description are verbatim:

| Label (exact name) | Color | Description (verbatim) |
|---|---|---|
| `issue-rating: 🦀 challenger crab` | `#1F883D` | Exceptional issue quality: high-confidence current-main reproduction and actionable evidence. |
| `issue-rating: 🦞 diamond lobster` | `#0969DA` | Very strong issue quality with high-confidence source-level or clear reproduction. |
| `issue-rating: 🐚 platinum hermit` | `#0F766E` | Good issue quality with a plausible reproduction path needing some confirmation. |
| `issue-rating: 🦐 gold shrimp` | `#B7791F` | Decent issue quality, but reproduction details are still incomplete. |
| `issue-rating: 🦪 silver shellfish` | `#7A828E` | Thin issue quality; more reproduction proof or environment detail is needed. |
| `issue-rating: 🧂 unranked krab` | `#8C2F39` | Issue quality is currently too unclear to act on safely. |
| `issue-rating: 🌊 off-meta tidepool` | `#6E7781` | Issue quality rating does not apply to this item. |

These seven are the **only** "rating" labels for issues. The PR path uses a *different*
family, `rating: <emoji> <animal>` (S/A/B/C/D/F/NA tiers → `rating: …` labels, produced by
`src/clawsweeper-rating.ts`, S15). Do not conflate the two: issue-rating = "how verifiable is
this report"; PR rating = "how merge-ready is this patch" (also stated in the prior local
research `openclaw-clawsweeper-issue-labels.html`).

### Related (non-rating) scoring axes, exact, for context

These are *not* the issue rating but are commonly confused with it:

- **Priority** `P0`–`P3` (verbatim descriptions from S16):
  - `P0` `#B60205` — "Emergency: data loss, security bypass, crash loop, or unusable core runtime."
  - `P1` `#D93F0B` — "High-priority user-facing bug, regression, or broken workflow."
  - `P2` `#FBCA04` — "Normal backlog priority with limited blast radius."
  - `P3` `#8C959F` — "Low-priority cleanup, docs, polish, ergonomics, or speculative work."
- **Impact** `impact:<category>` (9 categories, at most 3 per issue per schema S5):
  `impact:data-loss` `#B60205`, `impact:security` `#B60205`, `impact:crash-loop` `#D93F0B`,
  `impact:message-loss` `#D93F0B`, `impact:session-state` `#F9D65C`, `impact:auth-provider` `#F9D65C`,
  `impact:ux-release-blocker` `#B60205`, `impact:ux-friction` `#FBCA04`, `impact:other` `#C5DEF5`.
- **Maturity** `maturity:stable` `#1F883D` — "Broken existing behavior primarily owned by an M4/M5 scorecard surface."

---

## 3. The rubric / criteria (how a rating level is chosen)

The rating is **not** chosen by the model and is **not** a numeric score. It is a pure,
deterministic function of two fields the review model fills in. The exact code (S3,
`src/clawsweeper-label-selection.ts`, function `issueRatingLabelForState`):

```ts
export function issueRatingLabelForState(state: IssueAdvisoryLabelState): string {
  if (state.type !== "issue") return "";
  if (state.reproductionStatus === "not_applicable") {
    return "issue-rating: 🌊 off-meta tidepool";
  }
  if (state.reproductionStatus === "reproduced" && state.reproductionConfidence === "high") {
    return "issue-rating: 🦀 challenger crab";
  }
  if ((state.reproductionStatus === "source_reproducible" ||
       state.reproductionStatus === "reproduced") &&
      state.reproductionConfidence === "high") {
    return "issue-rating: 🦞 diamond lobster";
  }
  if ((state.reproductionStatus === "source_reproducible" ||
       state.reproductionStatus === "reproduced") &&
      state.reproductionConfidence === "medium") {
    return "issue-rating: 🐚 platinum hermit";
  }
  if (state.reproductionStatus === "unclear" && state.reproductionConfidence === "medium") {
    return "issue-rating: 🦐 gold shrimp";
  }
  if (state.reproductionStatus === "not_reproduced" ||
      (state.reproductionStatus === "unclear" && state.reproductionConfidence === "low")) {
    return "issue-rating: 🦪 silver shellfish";
  }
  return "issue-rating: 🧂 unranked krab";
}
```

The two inputs and their allowed values come from the decision schema (S5) and types (S6):

- `reproductionStatus` ∈ `reproduced | source_reproducible | not_reproduced | unclear | not_applicable`.
  Schema description (verbatim): **"reproduced: high-confidence current-main reproduction;
  source_reproducible: source shows the path without a failing run."** (The schema documents only
  these two values; the other three have no description string in the schema.)
- `reproductionConfidence` ∈ `high | medium | low` (no description in schema; `Confidence` type, S6 L182).
- Companion field `reproductionAssessment` (schema description): "Public answer to: Do we have a
  high-confidence way to reproduce the issue? With the evidence."

### Full decision table (all 15 combinations, as actually evaluated by the code)

| reproductionStatus \ confidence | high | medium | low |
|---|---|---|---|
| `reproduced` | 🦀 challenger crab | 🐚 platinum hermit | 🧂 unranked krab (fallthrough) |
| `source_reproducible` | 🦞 diamond lobster | 🐚 platinum hermit | 🧂 unranked krab (fallthrough) |
| `not_reproduced` | 🦪 silver shellfish | 🦪 silver shellfish | 🦪 silver shellfish |
| `unclear` | 🧂 unranked krab (fallthrough) | 🦐 gold shrimp | 🦪 silver shellfish |
| `not_applicable` | 🌊 off-meta tidepool (any confidence) | | |

Subtlety verified in the code: the "diamond lobster" branch includes `reproduced` in its
condition, but because the "challenger crab" branch returns first on `reproduced && high`,
that `reproduced` clause is dead code — effectively **challenger crab = reproduced + high** and
**diamond lobster = source_reproducible + high**. The catch-all `🧂 unranked krab` covers the
remaining unmatched pairs (`reproduced/low`, `source_reproducible/low`, `unclear/high`).

### The same two fields drive the `clawsweeper:*` evidence labels (S4 L182–L207, S11 table)

- `reproduced` + `high` → `clawsweeper:current-main-repro`
- `source_reproducible` + `high` → `clawsweeper:source-repro`
- `not_reproduced` + `high` → `clawsweeper:not-repro-on-main`
- `source_reproducible` + confidence below high → `clawsweeper:needs-live-repro`
- `unclear` + confidence below high → `clawsweeper:needs-info`

So the evidence label and the animal rating are two renderings of the same verdict.

---

## 4. End-to-end scoring flow (step by step)

### Stage 0 — submission lands
An issue (or PR) is opened in `openclaw/openclaw`. ClawSweeper is a GitHub App/bot
(`clawsweeper[bot]`) whose logic lives in a **separate repo**, `openclaw/clawsweeper` (S1).
The workflow entry points are `.github/workflows/sweep.yml`, `review-plan.yml`,
`exact-review-batch-publish.yml` in that repo (named as source-of-truth in S10 L5; file names
confirmed from the repo tree; individual YAML contents not read — see "unverified").

### Stage 1 — intake (cheap pre-classification; **no rating produced here**)
`src/intake-triage-workflow.ts` + `src/intake-triage-contract.ts` (S9). A small model
(`gpt-6-luna`, S9 L5) answers three bounded questions: `category`, `reproduction`
(trigger steps present/missing), `environment` (version/platform present/missing)
(S9 L11–L58). Limits: input ≤ 12,000 bytes, 20 s deadline, 32 KB response cap, **no
application retry** (S9 L6–L8; S10 L20–L24). Output is only the preliminary
`clawsweeper:intake:*` label family; per S10 L27–L30 intake labels "never set priority, impact,
reproduction proof, good-first-issue eligibility, maturity, merge risk, or readiness" and are
removed by the later completed-review publication. Intake runs "after the review-in-progress
reservation … before target-source checkout and review hydration"; a failed intake phase does
not block the full review (S10 L64–L71).

### Stage 2 — full review (the LLM that *produces* the rating inputs)
The full review is a separate, heavier, scheduled step (review planning / hot intake; the
`.github/workflows/sweep.yml` + `review-plan.yml` paths). It runs **Codex** (OpenAI Codex CLI,
model reported as `"internal"`, S `src/codex-env.ts` L12), read-only, and returns one JSON
decision conforming to `schema/clawsweeper-decision.schema.json` (S5). Among its ~90 fields the
rating-relevant ones are `itemCategory`, `reproductionStatus`, `reproductionConfidence`,
`reproductionAssessment`, `triagePriority`, `impactLabels`, `workCandidate`, `workConfidence`
(see S5; decision record type in S6 L594–L604). The review also decides close vs. keep-open and
posts the public comment.

### Stage 3 — deterministic label selection (code, not the model)
In `src/clawsweeper-label-selection.ts`: priority from `triagePriority` (L75–L83), impact labels
(L84–L94, capped at 3), maturity (L95–L105), merge-risk (PR-only, L106–L116), and — for issues —
the advisory set `wantedIssueAdvisoryLabels` (L182–L247), which includes exactly one
`issue-rating:` label from `issueRatingLabelForState` (L189–L190) plus the `clawsweeper:*`
evidence/work-lane labels and `good first issue` / `no-stale`.

### Stage 4 — publication / label sync
`src/clawsweeper-apply-report-labels.ts` (S12) builds `IssueAdvisoryLabelState` from the report
markdown + decision (L228–L231) and calls `syncIssueAdvisoryLabels` (L243–L249). The actual
mutation lives in `src/clawsweeper-label-operations.ts` `syncIssueAdvisoryLabels`
(S13 L237–L315), which adds/removes only labels in the owned group: `clawsweeper:*`,
`issue-rating:*`, plus `good first issue` / `no-stale` / `stale` transitions. Per `docs/work-lane.md`
(S11 L19–L31): advisory labels are applied **only** for open issues with complete, current,
kept-open reviews; **failed or stale reports are skipped**; close proposals are not label-mutated;
and a `queueable-fix` result additionally adds `no-stale` (L49–L55). Reruns add matching labels,
remove stale owned labels, and preserve unrelated labels (L57–L61).

### Stage 5 — routing / response (what the rating *does* and does not do)
The rating label itself is informational; routing is carried by the work-lane labels
(S11 L33–L47; S4 L205–L245):

- `clawsweeper:queueable-fix` — `work_candidate: queue_fix_pr` + `work_status: candidate` + `work_confidence: high` (eligible for a bounded automated fix PR; also gets `no-stale`).
- `clawsweeper:needs-maintainer-review` — `work_candidate/status: manual_review` (defer to a human).
- `clawsweeper:needs-product-decision` — `requires_product_decision: true`.
- `clawsweeper:needs-security-review` — `item_category: security` or `securityReview.status: needs_attention`.
- `clawsweeper:linked-pr-open` / `clawsweeper:no-new-fix-pr` — an open PR already owns the fix.

The public review comment (report) accompanies the labels; the review can also close the issue
under a close-reason rubric (S7 L31–L46).

---

## 5. LLM prompt / config

### Full-review prompt assembly
- Base prompt: `prompts/review-item.md` (S7). It contains placeholders `{{item_kind_review}}`
  (L29) and `{{close_reasons}}` (L42), filled by `prompts/review-item-issue.md` (S8) or
  `prompts/review-item-pr.md` for PRs, and `prompts/review-close-reasons.md`.
- Issue fragment `prompts/review-item-issue.md` (S8) is 12 lines. Rating-relevant passages
  (verbatim):
  - L3: "…identify a bounded, high-confidence existing-behavior bug suitable for a focused repair
    PR when no open PR owns the fix; otherwise name the concrete safety, evidence, or
    product-decision blocker…"
  - L8 (defines `autoImplementationCandidate: "strict_bug"`): "`itemCategory` exactly `bug`,
    `reproductionConfidence` and `workConfidence` both `high`, all three `requires*` flags `false`,
    and `reproductionStatus` `reproduced`, or `source_reproducible` with
    `implementationComplexity: small` when current source establishes the defect and its narrow
    repair."
- Base prompt on confidence (S7 L17): "high confidence means you read enough current code, tests,
  docs, history, comments, and related reports to understand the real product boundary."

### Field rubric (the schema, S5)
- `triagePriority` description (verbatim): "P0: Emergency: data loss, security bypass, crash loop,
  or unusable core runtime. P1: Urgent regression or broken agent/channel workflow affecting real
  users now. P2: Normal priority bug or improvement with limited blast radius. P3: Low-risk
  cleanup, docs, polish, ergonomics, or speculative feature. none: no priority label."
- `impactLabels` description lists the same 9 categories with per-category definitions and
  "Issue-only, at most 3".
- `reproductionStatus` / `reproductionConfidence` / `reproductionAssessment` as quoted in §3.
- `prRating` (PR-only): tiers `S/A/B/C/D/F/NA`, "Tiers per the rating rubric; NA for non-PR items."
  (This is the PR rating rubric, not the issue rating.)

### Models / config
- Intake model: `gpt-6-luna` (S9 L5), overridable via `CLAWSWEEPER_DECISION_MODEL`; backend
  `decisions` or `responses` (S10 L24, L54–L62).
- Full review: Codex CLI, model reported as `"internal"` (`PUBLIC_CODEX_MODEL = "internal"`,
  `src/codex-env.ts` L12); internal model overridden by `CLAWSWEEPER_INTERNAL_MODEL` /
  `CLAWSWEEPER_OPENCLAW_MODEL` env vars; optional private inference through ClawRouter
  (`docs/private-inference.md`, `CLAWSWEEPER_CODEX_AUTH_MODE=clawrouter`). The concrete upstream
  model is deliberately opaque/redacted ("internal") — the actual underlying model id is not
  visible in the public source (unverified).
- Failed-review retry prompt (`src/clawsweeper-failed-review-retry.ts` L119–L131, verbatim core):
  "This is a bounded exact-item retry for a prior Codex timeout or infrastructure failure. …
  Produce a normal fresh review from the live item and checkout context. Do not infer any verdict
  from the failed review artifact; use it only as retry context."

---

## 6. Thresholds, timeouts, retries, fallbacks

- **Intake:** input ≤ 12 KB (oversized → abstain, never silently truncate), 20 s timeout,
  32 KB response cap, **no application retry** and **no automatic cross-backend retry**
  (S9 L4–L8, L105–L106; S10 L20–L24, L62, L85). Missing credentials / timeout / refusal /
  malformed output → **no labels at all** (S10 L17).
- **Full review failure:** `src/clawsweeper-failed-review-retry.ts` — bounded retry, defaults
  `max_attempts = 2`, cooldown 45 min, batch `limit = 5` (S14 L554–L556). On exhaustion the
  report is marked "next step: needs human review; retry attempts for this exact revision are
  exhausted" (S14 L151–L154).
- **Publication:** GitHub/transient failures retry "at most 12 attempts or 24 hours"; permanent
  failures get two confirmation retries before dead-lettering; an artifact unavailable three
  times queues one fresh review (S17 L506–L510).
- **No-rating fallbacks:**
  - If the review is failed/stale/incomplete, the advisory sync is **skipped** — no `issue-rating:`
    label is written (S11 L24–L25; S15 L32–L40 shows the analogous PR-rating path returning no
    label when `reviewFailed`).
  - Unmatched (reproductionStatus, confidence) pairs → `🧂 unranked krab` ("too unclear to act on
    safely").
  - Non-issues / items the rubric doesn't apply to → `🌊 off-meta tidepool` ("rating does not
    apply").
- **Human hand-off when uncertain:** the review routes to humans via `work_candidate: manual_review`
  → `clawsweeper:needs-maintainer-review`, `requires_product_decision` →
  `clawsweeper:needs-product-decision`, security → `clawsweeper:needs-security-review`
  (S11 L45–L47); there is also a `clawsweeper:human-review` label ("Needs maintainer review before
  ClawSweeper can continue", S16). Keep-open guards force maintainer judgment for
  maintainer-authored and protected-label items (S7 L35).

---

## 7. Concrete examples (real issues, labels verified 2026-11-14 via GitHub API)

Search totals for the exact labels (GitHub search `total_count`, S16-adjacent; not a full census):

| Rating label | live issue count (search) |
|---|---|
| 🦀 challenger crab | 112 |
| 🦞 diamond lobster | 13,177 |
| 🐚 platinum hermit | 2,473 |
| 🦐 gold shrimp | 819 |
| 🦪 silver shellfish | 4,338 |
| 🌊 off-meta tidepool | 3,459 |
| 🧂 unranked krab | (not captured — API rate-limited) |

Example issues with exact label sets:

1. **🦀 challenger crab** — https://github.com/openclaw/openclaw/issues/187770
   `[open]` "Docs Bug: macOS app requirement conflicts…"
   labels: `bug, docs, no-stale, P2, clawsweeper:fix-shape-clear, clawsweeper:queueable-fix,
   clawsweeper:current-main-repro, issue-rating: 🦀 challenger crab, impact:ux-friction`
   (rating ↔ `current-main-repro` = reproduced+high, as coded).

2. **🦞 diamond lobster** — https://github.com/openclaw/openclaw/issues/158375
   `[closed]` "followup queue drain loops for 5+ hours…"
   labels: `clawsweeper:source-repro, issue-rating: 🦞 diamond lobster`
   (rating ↔ `source-repro` = source_reproducible+high).

3. **🐚 platinum hermit** — https://github.com/openclaw/openclaw/issues/196417
   `[open]` "A2A adapter lacks durableFinal.reconcileUnknownSend…"
   labels: `P2, clawsweeper:no-new-fix-pr, clawsweeper:needs-maintainer-review,
   clawsweeper:needs-live-repro, impact:session-state, issue-rating: 🐚 platinum hermit`
   (rating ↔ `needs-live-repro` = source_reproducible + confidence<high).

4. **🦐 gold shrimp** — https://github.com/openclaw/openclaw/issues/186995
   `[closed]` "Update failure: gateway-stop-unverified"
   labels: `stale, P2, clawsweeper:needs-info, issue-rating: 🦐 gold shrimp, impact:ux-friction`
   (rating ↔ `needs-info` = unclear + medium).

5. **🦪 silver shellfish** — https://github.com/openclaw/openclaw/issues/186723
   `[closed]` "Control UI side-panel PDF preview renders blank…"
   labels: `stale, P2, clawsweeper:not-repro-on-main, issue-rating: 🦪 silver shellfish,
   impact:ux-friction`
   (rating ↔ `not-repro-on-main` = not_reproduced).

6. **🌊 off-meta tidepool** — https://github.com/openclaw/openclaw/issues/187010
   `[open]` "[Feature]: Session-scoped agent cursor…"
   labels: `stale, P3, clawsweeper:no-new-fix-pr, clawsweeper:needs-maintainer-review,
   clawsweeper:needs-product-decision, issue-rating: 🌊 off-meta tidepool, impact:ux-friction`
   (feature requests → `not_applicable`).

---

## 8. Unverified / caveats

1. The exact GitHub-event → workflow trigger wiring (e.g. which event starts `sweep.yml` /
   `review-plan.yml`) was **not** read from the workflow YAML; the file names are confirmed but
   their `on:` triggers are unverified.
2. The concrete upstream LLM model behind the "internal" Codex reviewer is deliberately
   redacted in public source — the actual model id is **unverified**.
3. The schema's `reproductionStatus` description documents only `reproduced` and
   `source_reproducible`; the operational meaning of `not_reproduced`, `unclear`, and
   `not_applicable` is inferred from the label names, `docs/work-lane.md`, and the rating
   function, not from an explicit rubric string.
4. `🧂 unranked krab` live count was not captured (GitHub search API rate-limited on the final
   query).
5. The seven-label mapping and the counts were captured against `main` @ `a053c71`
   (2026-11-14); both the code and the label set may have changed since.
