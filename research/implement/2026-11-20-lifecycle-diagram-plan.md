# Lifecycle Diagram Reframe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the bottom lifecycle band on slide 1 of `research/community-issue-pr-io-issue.pptx` so it claims “bot 用 ≈10 分钟产出可决策包” instead of only describing roles and durations.

**Architecture:** Surgical python-pptx edit. Remove only the lifecycle shapes and two overlapping draft annotations on slide 1; redraw a two-panel band (bot 10-minute outputs / human irreversible actions), keep the six-node rail, and replace the old fork note with two exits plus one takeaway line. Back up first; verify text, media, and slides 2–19 are unchanged.

**Tech Stack:** Python 3, python-pptx 1.0.2, Pillow (font metrics + rough render).

**Spec:** `research/implement/2026-11-20-lifecycle-diagram-design.md`

## Global Constraints

- Canvas 13.333 × 7.5 in; 1 in = 914400 EMU.
- Font: 微软雅黑 for every run (`font.name` and `a:ea`).
- Palette: ink `16191E`, teal `0F766E`, amber `B45309`, gray `9AA1AC`, border `C9D0D6`.
- Only slide 1 may change. Slides 2–19 text and all `ppt/media/*` bytes must hash identical.
- No new statistics beyond existing `~3min`, `~9min`, `99.2%`.
- `≈10 分钟` assumes `~3min` / `~9min` are elapsed-time points after creation; the panel note states this.

## Review Focus

- **Text overflow** — 7.5–9 pt Chinese labels in fixed boxes; a box that looks fine in the design sketch can overflow when rendered with real 微软雅黑 metrics.
- **Panel/rail collision** — the two panels live at y=5.86–6.38 and the rail at 6.52; a stray shape from the old diagram (auto-close branch, work-lane box) will overlap them if not removed.
- **Bottom-edge clipping** — the fork line at y=7.00 and takeaway at y=7.22 must fit above 7.5 in.
- **Slide 2–19 drift** — python-pptx re-serialization can reorder XML; compare text and media hashes, not zip bytes.
- **Z-order** — panel backgrounds must be added before panel text; otherwise text hides behind the fill.

---

### Task 1: Baseline + verifier

**Files:**
- Create: `research/verify_lifecycle.py`
- Read: `research/community-issue-pr-io-issue.pptx`

**Interfaces:**
- Produces: `verify_lifecycle.py <path>` exits 0 on success; prints `OK` plus counts.

- [ ] **Step 1: Capture baseline**

```bash
cp research/community-issue-pr-io-issue.pptx research/community-issue-pr-io-issue.backup-20261120-lifecycle.pptx
```

- [ ] **Step 2: Write `research/verify_lifecycle.py`**

Checks, in order:
1. 19 slides.
2. Slide 1 contains all strings from the design doc’s 文案 section, and none of `谁在做、多久、在哪分叉`, `work lane`, `clawsweeper触发只在创建和人工@`.
3. Slides 2–19 concatenated text equals the baseline saved at `research/implement/lifecycle-baseline.json`.
4. `ppt/media/*` sha256 map equals baseline.
5. Every shape’s left/top/width/height is inside 0..12192000 × 0..6858000 EMU (allow 1 EMU rounding).
6. For every text box on slide 1, measured 微软雅黑 width ≤ box width + 2 px and height ≤ box height + 2 px.
7. No two text boxes on slide 1 overlap by more than 6 px².

Baseline JSON is written by the same script with `--write-baseline`.

- [ ] **Step 3: Run against the original and confirm it fails**

```bash
python research/verify_lifecycle.py research/community-issue-pr-io-issue.pptx --write-baseline
python research/verify_lifecycle.py research/community-issue-pr-io-issue.pptx
```
Expected: second command fails on missing new strings.

### Task 2: Patch script

**Files:**
- Create: `research/patch_lifecycle.py`
- Modify: slide 1 of `research/community-issue-pr-io-issue.lifecycle.pptx`

**Interfaces:**
- Consumes: `research/community-issue-pr-io-issue.pptx`.
- Produces: `research/community-issue-pr-io-issue.lifecycle.pptx`.

- [ ] **Step 1: Remove exactly these shape IDs from slide 1**

`{11, 12, 15, 21, 24, 26, 28, 30, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 75, 76, 77, 131, 132}`

Assert every ID was found before saving.

- [ ] **Step 2: Draw the new band in z-order**

1. Teal panel rect: x=0.35, y=5.86, w=5.95, h=0.52, fill `F0F7F6`, no line.
2. Amber panel rect: x=6.45, y=5.86, w=6.20, h=0.52, fill `FBF4EC`, no line.
3. Title runs at x=0.50, y=5.55, w=8.7, h=0.26, 14 pt bold:
   `bot 用 ` ink + `≈10 分钟` teal + `，把原始 issue 变成「可决策包」` ink.
4. Date at x=10.75, y=5.58, w=1.95, h=0.16, 8.5 pt gray, right aligned: `2026-09-11 → 11-11`.
5. Accent bar: x=0.32, y=5.55, w=0.06, h=0.19, fill amber.
6. Bot header at x=0.48, y=5.89, w=2.2, h=0.16, 10.5 pt bold teal: `bot · ≈10 分钟`.
7. Bot note at x=2.52, y=5.91, w=3.7, h=0.14, 7.5 pt gray: `（~3min / ~9min 为创建后时点）`.
8. Three output columns at y=6.08 (title) and y=6.23 (sub), each w=1.85:
   - x=0.48: `① 分流` 8.5 pt bold ink / `类别 / 缺什么证据` 7.5 pt gray.
   - x=2.38: `② 复现 + 标签` / `源码级结论 / 五维标签`.
   - x=4.28: `③ review 意见` / `证据链 / fixPrompt / 关闭理由`.
9. Human header at x=6.58, y=5.89, w=2.0, h=0.16, 10.5 pt bold amber: `人接手 · 小时–天`.
10. Human note at x=8.55, y=5.91, w=2.4, h=0.14, 7.5 pt gray: `只做 3 个关键动作`.
11. Human line at x=6.58, y=6.12, w=5.9, h=0.16, 8 pt ink:
    `定夺（修 / 挂起 / 路由）· 开 PR · 合并 99.2% 由人`.
12. Rail rect: x=0.60, y=6.52, w=12.05, h=0.02, fill `C9D0D6`.
13. Six dots at y=6.45, 0.16 × 0.16, x = 1.13, 3.21, 5.30, 7.39, 9.46, 11.55; first three teal, last three amber.
14. Six label pairs at y=6.62 / 6.78, 10 pt:
    `规则分流`/`bot · 秒级`, `Agent 判定`/`bot · ~3min`, `review 意见`/`bot · ~9min`,
    `maintainer 定夺`/`人 · 小时–天`, `开 PR`/`人 / bot`, `校验合并`/`人 99.2% · bot 0.8%`.
    First line ink; second gray. Label boxes x = 0.28, 2.36, 4.44, 6.53, 8.61, 10.59; widths 1.88, 1.88, 1.88, 1.88, 1.88, 2.08.
15. Fork line at x=0.50, y=6.98, w=8.6, h=0.16, 8 pt teal:
    `分叉也在 10 分钟内：证据足 → 关闭 + 理由（可复活）｜证据不足 → 补证据`.
16. Takeaway at x=0.50, y=7.20, w=12.0, h=0.17, 9 pt: `启示：` teal bold + rest ink:
    `人拿到的是「可决策包」，不是原始 issue —— 省下的是判断前的整理时间。`

- [ ] **Step 3: Save `research/community-issue-pr-io-issue.lifecycle.pptx` and print removed/added counts.**

### Task 3: Verify and render

- [ ] **Step 1: Run verifier**

```bash
python research/verify_lifecycle.py research/community-issue-pr-io-issue.lifecycle.pptx
```
Expected: `OK slides=19 ...` and no overflow/overlap issues.

- [ ] **Step 2: Rough render**

Extend `research/render_page1.py` (or a copy) to accept an input path and write `research/implement/lifecycle_render.png`; draw rects, ovals, and text boxes.

- [ ] **Step 3: Inspect the bottom-band crop**

Crop y=520..720, downscale to ≤ 640 px wide, save JPEG. Confirm: two panels, three bot outputs, rail, fork line, takeaway; no overlapping old shapes.

### Task 4: Promote

- [ ] **Step 1: Replace the original only after Task 3 passes**

```bash
cp research/community-issue-pr-io-issue.lifecycle.pptx research/community-issue-pr-io-issue.pptx
```

- [ ] **Step 2: Re-run verifier against the original path.**

- [ ] **Step 3: Report** file changed, backup path, and the verification counts. Do not commit unless asked.
