# ClawSweeper PR 的 P0–P3 优先级标签：prompt 依据与代码落点

**一句话结论：PR 没有专属的 `triagePriority` 评分表。** 唯一直接规定 item 优先级的是 issue 与 PR 共享的 `prompts/review-item.md:51`；`prompts/review-item-pr.md` 里出现的 P0–P3 全部是 `reviewFindings[].priority`（finding 等级），不是 GitHub 上的 P0/P1/P2/P3 标签。schema 只给五档一句话定义，代码只做 `triagePriority` → 同名标签的确定性映射；没有任何代码把 finding 等级、`workPriority` 或可修复性换算成 P 标签。

> 核验说明：本文引用的本地副本与 `https://raw.githubusercontent.com/openclaw/clawsweeper/main/` 对应文件逐字节一致（SHA-256 相同），行号按上游 `main` 计。核验快照：`openclaw/clawsweeper@c0b05e40f8fec5fa6087f9d1283b921e4bf61f0c`（2026-11-16）。

> 可视化版本：[pr-priority-labels-prompt-basis.html](pr-priority-labels-prompt-basis.html)；配套 issue 报告：[issue-priority-labels-prompt-basis.html](issue-priority-labels-prompt-basis.html)。

---

## 0. 先分清三个 “P0–P3”

| 概念 | 字段 | 取值 | 作用域 | 是否变成 GitHub 标签 | 主要依据 |
|---|---|---|---|---|---|
| item 优先级 | `triagePriority` | `P0` / `P1` / `P2` / `P3` / `none` | 整个 issue 或 PR，顶层必填 | **是**，一一映射为同名 `P0`–`P3`；`none` 表示不挂优先级标签 | `schema/clawsweeper-decision.schema.json:19,363-366`；`src/clawsweeper-policy.ts:242-274`；`src/clawsweeper-label-selection.ts:72-83` |
| finding 等级 | `reviewFindings[].priority` | 整数 `0` / `1` / `2` / `3` | 单条 review finding；issue 恒为 `[]` | **否** | `schema/clawsweeper-decision.schema.json:747-776`；`prompts/review-item-pr.md:34-36` |
| 工作优先级 | `workPriority` | `high` / `medium` / `low` | maintainer 工作分诊（工作车道） | **否** | `schema/clawsweeper-decision.schema.json:56,1040-1043`；`src/clawsweeper-decision-parser.ts:1002` |

三者的关系，按现有 prompt/schema/代码可以确定的只有三点：

1. P 标签**只**来自 `triagePriority`，不来自 finding 等级，也不来自 `workPriority`：`src/clawsweeper-label-selection.ts:72-83` 的 `priorityLabelForTriage` 只读 `TriagePriority`；`src/clawsweeper-label-operations.ts:117-141` 的 `syncPriorityLabel` 只接收 `triagePriority`。
2. finding 等级只决定“是否必做”和“是否阻止 merge”：`P0-P2` 是 required work，`P3` 是 advice 且 never blocks merge（`prompts/review-item-pr.md:36`）；`overallCorrectness: "patch is incorrect"` 只在列出的 P0–P2 finding 阻止 merge 时成立（`schema/clawsweeper-decision.schema.json:949-953`）。
3. prompt 明确要求 item 优先级与 finding 优先级**分开判断**（`prompts/review-item.md:51`），但没有规定两者必须一致，代码也不做一致性校验（`src/clawsweeper-decision-parser.ts:1031-1033` 只校验 label justifications，不比较 finding 等级）。

`workPriority` 在 prompt 里**没有以字段名出现**；共享 prompt 只要求 `workCandidate: "none"` 时带 “low confidence/priority”（`prompts/review-item.md:53`），并未说明这里的 “priority” 就是 `workPriority`。因此 prompt 对 `workPriority` 的判定标准**未规定**，schema 也只给了枚举、没有描述（`schema/clawsweeper-decision.schema.json:1040-1043`）。

---

## 1. 标签从哪来：prompt → schema → 代码

### 1.1 文件分工：共享 core + 按 item kind 注入

- `prompts/review-item.md` 是**共享 core**：它在第 29 行留出 `{{item_kind_review}}` 槽位（`prompts/review-item.md:29`），由代码按 `item.kind` 填入 issue 或 PR 段落（`src/clawsweeper-review-core.ts:225-232,287-299`）。
- `prompts/review-item-pr.md` 是 **PR-only** 段落，首行即 `## Pull request review`（`prompts/review-item-pr.md:1`）。
- `prompts/review-item-issue.md` 是 issue-only 段落（`prompts/review-item-issue.md:1`），且明确 “Pull-request-only fields take their issue values”（`prompts/review-item-issue.md:11`）。

### 1.2 `triagePriority` 的唯一 prompt 指令在共享文件

对三个 prompt 做全文检索可以确认：

- `prompts/review-item-pr.md` **没有任何** `triagePriority` 字样；其中的 P0–P3 仅出现在 finding 规则里（`prompts/review-item-pr.md:36,38,39,47-49,99`）。
- `prompts/review-item-issue.md` 也没有 `triagePriority` 字样。
- 唯一以字段名提出要求的是共享行：**`prompts/review-item.md:51`**。

因此，**PR 专属的 `triagePriority` 评分 rubric 不存在**。PR 侧只有 finding 的 P0–P3 例子；item 标签的判据对所有 item 共用第 51 行。

### 1.3 schema 是等级定义的唯一出处

schema 把 `triagePriority` 定义为顶层必填枚举（`schema/clawsweeper-decision.schema.json:19,363-366`）：

> `P0: Emergency: data loss, security bypass, crash loop, or unusable core runtime. P1: Urgent regression or broken agent/channel workflow affecting real users now. P2: Normal priority bug or improvement with limited blast radius. P3: Low-risk cleanup, docs, polish, ergonomics, or speculative feature. none: no priority label.`

注意它**没有**标注 “Issue-only”（对比 `impactLabels` 的 “Issue-only, at most 3” 与 `maturityLabels` 的 “Issue-only”，见 `schema/clawsweeper-decision.schema.json:385,412`），所以 `triagePriority` 对 PR 同样适用。

### 1.4 代码只做确定性映射

1. `src/clawsweeper-policy.ts:242-274` 定义 `PRIORITY_LABELS`，每项含 `priority`（0–3）、`triagePriority`（`P0`–`P3`）、`name`（GitHub 标签名，同样是 `P0`–`P3`）、颜色与描述。描述与 schema 第 366 行逐字一致。
2. `src/clawsweeper-label-selection.ts:72-83`：`priorityLabelForTriage("none")` 查不到条目返回 `null`；`nextPriorityLabels` 先移除全部既有 P 标签，再按映射追加一个；`none` 什么都不加。
3. `src/clawsweeper-label-operations.ts:117-141`：`syncPriorityLabel` 计算要删/要加的 P 标签并执行；`src/clawsweeper-label-selection.ts:126-136` 负责创建标签。
4. `src/clawsweeper-apply-report-labels.ts:173-181`：在共享的 report-label 同步路径里，**无论 issue 还是 PR**都调用 `syncPriorityLabel({ triagePriority: decision.triagePriority })`。
5. PR 专用的 `src/clawsweeper-apply-pull-request-labels.ts:82-117` 只同步 proof、rating、showcase、status 等 PR 附加标签，**不处理** P/impact/maturity；P 标签由上面的共享路径完成。

测试也固定了行为：`nextPriorityLabels(["bug"], "P2") === ["bug","P2"]`；`["bug","P3"]` + `P1` → `["bug","P1"]`；`["P0","bug"]` + `none` → `["bug"]`（`test/pr-label-policy.test.ts:668-672`）。

---

## 2. Prompt 原文与判定顺序

共享行 `prompts/review-item.md:51` 的完整顺序是：**UX override → 通用四维 → CI 例外 → 标签选择与理由**。

### 2.1 UX override（先于通用规则）

原文条件（`prompts/review-item.md:51`）：

| 情形 | 结果 | 原文要点 |
|---|---|---|
| 非技术背景的首次/社区用户，在 website/download/install/update/setup/onboarding/auth/provider setup/first useful run/in-product recovery 被卡住，且**产品内无路可走**（恢复需要 terminal commands、config/file edits、log inspection、internal knowledge、maintainer/support help） | `P0` + `impact:ux-release-blocker` | 并要求 `bestSolution`/`workReason` 推荐 Doctor/Fix button、setup wizard、inline recovery 或 visible command launcher |
| 可恢复的 docs/support/guessing 路径 | `P1`/`P2` + `impact:ux-friction` | “Recoverable docs/support/guessing paths” |
| 纯 cosmetic 或完全可在产品内恢复的 confusion | `P2`/`P3` | “cosmetic or fully recoverable in-product confusion” |
| advanced/power-user 的 terminal/config workflow | **不升级** | “advanced or power-user terminal/config workflows are not promoted” |

同一行的选择规则还有：

- 同一证据同时支持两者时，优先 `impact:ux-release-blocker` 而非 `impact:ux-friction`；
- 优先具体标签而非 `impact:other`；
- “claim no more certainty than the evidence”；
- “justify each selected label once”。

### 2.2 通用四维（否则）

> “Otherwise choose `triagePriority` from user impact, severity, confidence, and urgency for the whole item, separately from finding priorities and repairability.”

即：在没有命中 UX override 时，按**整个 item** 的 user impact、severity、confidence、urgency 四维选一个 `triagePriority`，并与 finding 优先级、可修复性**分开**。这四维是 prompt 给出的全部正向判据。

### 2.3 CI 例外（对“升 P”的唯一显式限制）

> “failing, pending, or flaky CI raises it only for user-facing automation failures or diff-caused urgent regressions.”（`prompts/review-item.md:51`）

PR prompt 补充了 CI 归因方式：每个失败 required check 必须归因于 diff（blocking finding）、有证据的外部原因，或从未运行的检查；作者只修 diff 导致的失败，重跑 job 和无关 CI 修复不是作者的工作（`prompts/review-item-pr.md:52`）。另外 “red, pending, flaky, or absent CI alone is not” `merge-risk: 🚨 automation`（`prompts/review-item-pr.md:96`）。

### 2.4 理由

每个被选中的 review label（含 P 标签）必须且只能有一条 justification（`prompts/review-item.md:51` 的 “justify each selected label once”；schema 与 parser 的强制见第 6 节）。

---

## 3. 等级依据表

| 等级 | schema 定义（`schema/clawsweeper-decision.schema.json:366`） | `review-item-pr.md` 中的具体 finding 例子 | 硬边界 |
|---|---|---|---|
| `P0` | Emergency: data loss, security bypass, crash loop, or unusable core runtime | **没有给出任何具体 PR 例子**。PR prompt 只写 “P0-P2 rank impact”（`prompts/review-item-pr.md:36`），schema 对 finding `0` 只写 “0=P0 critical”（`schema/clawsweeper-decision.schema.json:772-776`） | 属于 required work（`prompts/review-item-pr.md:36`）；列出的 P0 finding 可使 `overallCorrectness: "patch is incorrect"`（`schema/clawsweeper-decision.schema.json:949-953`） |
| `P1` | Urgent regression or broken agent/channel workflow affecting real users now | 重新实现配置/docs/CLI flags/env vars/现有 API/plugins/skills/setup 已有的能力 → P1（`prompts/review-item-pr.md:38`）；upgrade 会 break setups、覆盖 config/preferences、静默替换行为、产生竞争性 source of truth → P1（`:48`）；plugin API 的机械修复（保留 API、去掉并行调用、加 deprecation、补兼容测试）→ P1（`:49`） | required work；可 `queue_fix_pr`（plugin API 机械修复，`:49`） |
| `P2` | Normal priority bug or improvement with limited blast radius | 新增 `AGENTS.md`/skill/prompt 规则但未引用 incident → P2（`prompts/review-item-pr.md:39`）；smallest complete fix 中不必要的 production machinery → P2（`:47`）；为 speculative/极不可能 race 或 security edge case 增加 machinery（且无 maintainer 接受的具体 failure mode）→ P2（`:47`）；upgrade 行为本身保持但缺 migration/docs/upgrade proof → P2（`:48`） | required work |
| `P3` | Low-risk cleanup, docs, polish, ergonomics, or speculative feature | 非 production 的 test scaffolding/多余结构 → P3（`prompts/review-item-pr.md:47`）；只有一个 caller、提前抽出的 helper → P3（`:47`）；low-risk discoverability 或 docs gap → P3（`:48`） | **advice，never blocks merge or changes the verdict**（`prompts/review-item-pr.md:36`）；但窄小的机械 blocker 仍可为 `queue_fix_pr`，“even when process-only or P3”（`:99`） |
| `none` | no priority label | 无 | 代码移除所有 P 标签且不添加（`src/clawsweeper-label-selection.ts:75-83`；`test/pr-label-policy.test.ts:671`）；prompt **未规定**何时该用 `none` 而不是 `P3` 或某个具体等级 |

补充：finding 的 P3 是 “a real low-impact defect”，不是“随便的建议”（`prompts/review-item-pr.md:36`）；P0–P2 “rank impact”，P3 只是不阻塞 merge。

---

## 4. 与 finding priority 的关系

### 4.1 finding：P0–P2 必做，P3 建议

> “A finding is required work at P0-P2 and advice at P3, which never blocks merge or changes the verdict.”（`prompts/review-item-pr.md:36`）

同一行还要求 finding 必须有 actual introduced trigger、causal link、failing input and wrong result；P0–P2 是 impact 排序，P3 是真实的低影响缺陷。`overallCorrectness` 的 `patch is incorrect` 只在 “a listed P0-P2 finding blocks merge” 时成立（`schema/clawsweeper-decision.schema.json:949-953`）。

### 4.2 item 标签：独立选择，不自动继承

- prompt 的措辞是 “separately from finding priorities and repairability”（`prompts/review-item.md:51`）。
- schema 把 `triagePriority` 与 `reviewFindings` 放在两个独立字段：前者在顶层 properties（`schema/clawsweeper-decision.schema.json:363-366`），后者在数组项内部（`:747-799`）。
- 代码只把 `triagePriority` 映射成标签（`src/clawsweeper-label-selection.ts:72-83`），从不读取 `reviewFindings`；parser 也不校验两者语义一致（`src/clawsweeper-decision-parser.ts:1031-1033`）。

**实践含义：** 一个 PR 可以含 P0/P1 finding，但 item 仍被标为 `P2`/`P3`，只要该 PR 整体对用户的影响/紧迫性不高；反过来，一个紧急用户问题对应的 PR 即使只有 P2 级实现瑕疵，也可以获得较高 item 优先级。prompt 没有规定“取 finding 最大值”或“不得低于最高 finding”之类的规则。**注意**：prompt 也没有明确 `triagePriority` 衡量的是“PR 要解决的问题的价值”还是“PR 自身缺陷的严重性”；schema 的描述偏 issue 语境（“bug or improvement”），但字段同时用于 PR。这是一个未解决的语义边界。

### 4.3 `workPriority` 与标签无关

`workPriority` 是工作车道字段（`schema/clawsweeper-decision.schema.json:56,1040-1043`），parser 仅做 `high/medium/low` 枚举校验（`src/clawsweeper-decision-parser.ts:1002`）。它不出现在任何标签映射或 apply 路径中，因此**不会**变成 GitHub 标签。prompt 没有给出它的判据（仅在 `prompts/review-item.md:53` 出现 “low confidence/priority” 的措辞）。

---

## 5. 不能仅凭这些因素升 P

下表把“明确针对优先级标签的规则”与“相邻但并非针对优先级的规则”分开。只有 CI 一行是 prompt 对 `triagePriority` 的显式限制；其余多为 finding、work lane 或 rating 规则，prompt 没有逐条写明“不得用于 P”，但它们也不在共享行给出的四个正向维度里。

| 因素 | 相关原文 | 它实际约束什么 | 对 P 标签的结论 |
|---|---|---|---|
| process / style / naming / taste / PR-body paperwork | “Process, style, naming, and taste are not merge work: keep them out of findings, `risks`, and a required `nextStep`… PR-body paperwork … is process even when `AGENTS.md` or a PR-body check asks for it”（`prompts/review-item-pr.md:37`） | finding、`risks`、required `nextStep` | prompt **未直接**写“不得升 P”；但它不属于 `prompts/review-item.md:51` 的四维，不能作为 user impact/severity/urgency 的证据。可把窄小 process-only 修复放进 `queue_fix_pr`（`:99`），那是工作车道，不是优先级 |
| CI 失败/挂起/flaky 本身 | “failing, pending, or flaky CI raises it only for user-facing automation failures or diff-caused urgent regressions”（`prompts/review-item.md:51`） | **直接约束 `triagePriority`** | 只有“用户可见的自动化失败”或“diff 导致的紧急回归”才能升 P；单纯红/挂起/flaky 不行 |
| `maintainer` 标签 | keep-open guard 包含 `maintainer` 等 protected label，阻止关闭和 cleanup，但 “not by itself a clean review verdict”（`prompts/review-item.md:35`）；`maintainer` label 不是 `manual_review` 的理由（`prompts/review-item-pr.md:99`） | close policy、work lane | 不是 P 的依据；prompt 未赋予它提升 item 优先级的效力 |
| `size:*` 大标签 / broad surface | “The `maintainer` label, a large `size:*` label, broad surface, or ordinary review expectations are no reason for `manual_review`”（`prompts/review-item-pr.md:99`） | PR work lane 的 `manual_review` 判定 | 这是 work-lane 规则，**不是** P 标签规则；规模本身不在四维中 |
| ordinary review expectations | 同上（`prompts/review-item-pr.md:99`） | work lane | 同上；不能仅凭“通常要 review”升 P |
| workflow state（draft、protected labels、pending maintainer action） | “Workflow state (draft, protected labels, a pending maintainer action) never lowers a tier”（`prompts/review-item-pr.md:100`） | `prRating.overallTier` | 这是 rating 规则；prompt 未说它会升/降 P。draft/conflict/stale head 可作为 `manual_review` 的理由（`:99`），仍是 work lane |
| finding 等级本身 | “separately from finding priorities and repairability”（`prompts/review-item.md:51`）；finding P0–P2 必做、P3 建议（`prompts/review-item-pr.md:36`） | finding 的 required/advice | 高等级 finding 不等于高 item P；必须回到“整个 item”的四维重新判断 |
| title / label 相似性 | 用 “intent, similarity, quality, relevance, or a score decided by regex, keyword lists, or string matching” 作决定是 finding（`prompts/review-item-pr.md:39`）；“title similarity … are no evidence”（`schema/clawsweeper-decision.schema.json:971-973`）；“a similar title proves nothing”（`prompts/review-item-pr.md:57`） | finding、regression assessment、late-finding | prompt **未直接**把它写成 P 规则；但它不是 user impact/severity 的证据，不能作为升 P 的依据 |
| 证据不足 / 工具不可用 | “unavailable evidence is neither a pass nor a contributor defect”（`prompts/review-item-pr.md:36`）；“claim no more certainty than the evidence”（`prompts/review-item.md:51`） | finding 与置信度 | 不能因“CI 看不到/工具失败”升 P；confidence 维度要求不夸大确定性 |
| maintainer-authored / owner decision | maintainer-authored 的方向视为 owner decision（`prompts/review-item-pr.md:21`） | product review 的决策归属 | 与 P 标签无关；prompt 未说 owner 身份提高优先级 |
| protected label（`security`、`release-blocker` 等） | 阻止关闭与 cleanup，但不单独构成 clean verdict（`prompts/review-item.md:35`） | close policy | 与 P 标签无关；需要独立证据判断影响 |

**不要混淆：** 上表中 `size:*`、broad surface、`maintainer` label、ordinary review expectations、workflow state 的原文都明确指向 `manual_review` 或 `prRating`，不是 `triagePriority`。把它们直接说成“P 标签禁令”会超出 prompt 原文；准确说法是：它们不属于共享行给出的四个正向维度，且 prompt 没有授权用它们提升 P。

---

## 6. 代码强制层

### 6.1 `labelJustifications`：一标签一理由，且精确匹配

- schema 规定每个对象含 `label` + `reason`，`label` 枚举覆盖 `P0`–`P3`、全部 impact、`maturity:stable`、全部 merge-risk；描述为 “One per selected `triagePriority`, impact, maturity, and merge-risk label”（`schema/clawsweeper-decision.schema.json:460-500`）。
- parser 的 `requireLabelJustifications` 要求数组、拒绝重复 label（`src/clawsweeper-decision-parser.ts:305-315`）。
- `selectedReviewLabels` 把 `triagePriority`（`none` 除外）、`impactLabels`、`mergeRiskLabels`、`maturityLabels` 展开为应有集合（`src/clawsweeper-decision-parser.ts:317-329`）。
- `validateLabelJustifications` 分别检查 **missing selected labels** 与 **unselected labels**，任一不匹配直接抛错（`src/clawsweeper-decision-parser.ts:331-355`）；该函数在模型输出路径中被调用（`:1031-1033`）。
- `triagePriority` 本身经 `requireEnum(..., TRIAGE_PRIORITIES, ...)` 校验，只接受 `P0`/`P1`/`P2`/`P3`/`none`（`src/clawsweeper-decision-parser.ts:912-916`；`src/clawsweeper-policy.ts:602`）。

**范围细节：** 精确匹配只覆盖上述四类 review label。PR 的 `rating:`、`status:`、`proof:` 等标签的 justification 由 presentation 层另行生成（`src/clawsweeper-label-presentation.ts:272-333`），不要求模型在 `labelJustifications` 里逐条列出；因此“one per selected label”应理解为“one per selected **review** label”。

**具体例子（测试固定）：** `triage_priority: "P1"` 对应 `{"label":"P1","reason":"The PR changes an active channel workflow affecting real users."}`；同一组测试还给出 `impact:message-loss` 与 `merge-risk: 🚨 compatibility` 的各自理由，并断言渲染结果为 “Label justifications:” 下的 `- \`P1\`: …`（`test/pr-review-labels.test.ts:822-838,900-903`）。这说明 justification 是**逐标签**写的，且 P1 的理由直接引用 P1 定义中的“active … workflow affecting real users”，而不是复述 finding。

### 6.2 `none` 与确定性映射

- `selectedReviewLabels` 在 `triagePriority === "none"` 时不加入任何 P 标签（`src/clawsweeper-decision-parser.ts:323-328`）。
- `nextPriorityLabels` 先过滤全部 `PRIORITY_LABEL_NAMES`，再按 `priorityLabelForTriage` 追加；`none` 返回 `null`，所以结果是“没有 P 标签”（`src/clawsweeper-label-selection.ts:72-83`）。
- 映射表是硬编码的 0→P0、1→P1、2→P2、3→P3（`src/clawsweeper-policy.ts:242-274`）；没有模糊匹配、没有从 finding 推导。
- 测试确认 `none` 会移除旧 P 标签（`test/pr-label-policy.test.ts:671`）。

### 6.3 PR 侧 impact/maturity 被抑制，但 `triagePriority` 仍生效

- `desiredClawSweeperLabelsFromPublicReport` 先无条件应用 `nextPriorityLabels(labels, decision.triagePriority)`（`src/clawsweeper-label-presentation.ts:108`），随后对 PR 传入空数组：
  - `nextImpactLabels(labels, isPullRequest ? [] : decision.impactLabels)`；
  - `nextMaturityLabels(labels, isPullRequest ? [] : decision.maturityLabels)`（`src/clawsweeper-label-presentation.ts:106-110`）。
- 实际 apply 路径同样如此：`syncPriorityLabel` 无条件执行（`src/clawsweeper-apply-report-labels.ts:173-181`），而 `syncImpactLabels` / `syncMaturityLabels` 在 `item.kind === "pull_request"` 时收到 `[]`（`:182-199`）。
- schema 也把 impact 标为 “Issue-only, at most 3”、maturity 标为 “Issue-only”（`schema/clawsweeper-decision.schema.json:385,412`）。
- 因此：**PR 会得到 P0–P3 `triagePriority` 标签，但不会得到 `impact:*` 或 `maturity:*` 标签。** 共享 prompt 的 UX override 里 “P0 + `impact:ux-release-blocker`” 这套组合在 PR 上只能落地 P 部分，impact 部分被代码丢弃。这是 prompt 与代码之间最明显的错位。

### 6.4 等级描述只在 schema

测试明确断言 P0–P3 的描述文本只存在于 schema，prompt 不得复述（`test/pr-label-policy.test.ts:646-666`）。这解释了为什么 prompt 本身非常紧凑：具体等级定义要去 schema 查，而不是去 PR prompt 找。

---

## 7. 边界与容易误读的地方

1. **PR 没有专属 `triagePriority` rubric。** 唯一指令是共享的 `prompts/review-item.md:51`；PR-only prompt 里的 P0–P3 全是 finding 等级。不要把它当成 PR 标签清单。
2. **P0 finding 例子缺失。** `review-item-pr.md` 给出了 P1/P2/P3 finding 的具体场景，但没有任何 P0 finding 的具体 PR 例子；P0 只能依赖 schema 的 “Emergency: data loss, security bypass, crash loop, or unusable core runtime” 与 finding `0=P0 critical`。
3. **`none` 没有细化标准。** schema 只说 “no priority label”；prompt 没有说明何时该用 `none` 而非 `P3`。可确定的只有代码行为：移除全部 P 标签。
4. **UX override 与 PR 不兼容。** 它要求同时挂 `impact:ux-release-blocker` / `impact:ux-friction`，但 schema 标注 impact 为 issue-only，代码在 PR 上把 impact 置空（见 6.3）。因此对 PR 而言，这一段究竟应整体跳过、还是只取其中的 P0/P1/P2/P3 部分，**prompt 未规定**；代码只能执行后者的 P 部分。
5. **共享行可能是唯一指令。** `prompts/review-item.md:51` 同时承担 UX override、通用四维、CI 例外和理由要求；没有第二处解释或优先级决策树。若该行被修改，PR 与 issue 的 P 标签行为会一起改变。
6. **`triagePriority` 的语义对象未定义。** 对 PR，它是“这个改动有多重要/多紧急”，还是“这个 PR 引入的问题有多严重”？schema 描述偏 issue（“bug or improvement”），prompt 只说 “for the whole item”，代码直接透传，没有澄清。
7. **`workPriority` 语义未规定。** prompt 未以字段名提及，schema 无描述；不要把它当作 P 标签的隐藏来源。
8. **精确匹配不等于语义正确。** parser 只保证“选中的 label 与 justification 集合完全一致”，不保证理由质量，也不保证 `triagePriority` 与 finding 等级/PR 评级自洽。

---

## 8. 来源清单（URL + 行号）

上游 raw 基址：`https://raw.githubusercontent.com/openclaw/clawsweeper/main/`

| 来源 | 关键行号 | 用途 |
|---|---|---|
| `prompts/review-item.md` | `29`（`{{item_kind_review}}`）；`35`（protected label keep-open）；`51`（UX override + 四维 + CI + 理由）；`53`（work lane / “low confidence/priority”） | 共享 core，唯一 `triagePriority` 指令 |
| `prompts/review-item-pr.md` | `1`；`21`；`34-39`；`47-49`；`52`；`57`；`95-100` | PR-only 段落；finding P0–P3 与 merge/rating/work-lane 规则 |
| `prompts/review-item-issue.md` | `1`；`11` | issue-only 段落；PR-only 字段在 issue 上的取值 |
| `schema/clawsweeper-decision.schema.json` | `19,25,56`（required）；`363-366`（`triagePriority`）；`368-386`（impact，Issue-only）；`387-413`（merge-risk PR-only / maturity Issue-only）；`460-500`（`labelJustifications`）；`747-799`（`reviewFindings`，`priority` 0–3 在 772-776）；`949-953`（`overallCorrectness`）；`971-973`（title similarity no evidence）；`1040-1043`（`workPriority`） | 等级定义与字段约束 |
| `src/clawsweeper-review-core.ts` | `225-232`（读取 core/issue/PR prompt）；`287-299`（`{{item_kind_review}}` 注入） | 证明文件分工 |
| `src/clawsweeper-policy.ts` | `242-274`（`PRIORITY_LABELS`）；`602`（`TRIAGE_PRIORITIES`） | 确定性映射表 |
| `src/clawsweeper-label-selection.ts` | `42-52`（justification 补齐）；`71-83`（`priorityLabelForTriage` / `nextPriorityLabels`） | 标签选择 |
| `src/clawsweeper-label-operations.ts` | `117-141`（`syncPriorityLabel`） | 实际增删 P 标签 |
| `src/clawsweeper-apply-report-labels.ts` | `156-210`（共享 apply：`syncPriorityLabel` 173-181；PR 时 impact/maturity 置空 182-199） | 证明 PR 仍应用 P、但不应用 impact/maturity |
| `src/clawsweeper-apply-pull-request-labels.ts` | `82-117` | PR 专用 apply 仅同步 proof/rating/showcase/status |
| `src/clawsweeper-label-presentation.ts` | `100-110`（PR 时 impact/maturity 传 `[]`，priority 仍应用）；`156-163`（P 标签变化理由）；`272-333`（PR rating/status/proof justification 另行生成） | 展示层行为 |
| `src/clawsweeper-decision-parser.ts` | `305-355`（justification 去重与精确匹配）；`912-916`（`triagePriority` 枚举校验）；`1002`（`workPriority`）；`1031-1033`（校验调用点） | 强制层 |
| `test/pr-label-policy.test.ts` | `646-666`（P 描述只在 schema）；`668-672`（映射与 `none`） | 回归测试固定行为 |
| `test/pr-review-labels.test.ts` | `822-838`（P1/impact/merge-risk 的逐标签 justification 示例）；`900-903`（渲染断言） | 具体 justification 写法 |

补充：schema 的 GitHub 页面为 `https://github.com/openclaw/clawsweeper/blob/main/schema/clawsweeper-decision.schema.json`；本地副本名为 `decision.schema.json`，内容与上游 `schema/clawsweeper-decision.schema.json` 的 SHA-256 一致。
