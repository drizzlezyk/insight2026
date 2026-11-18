# ClawSweeper「已在 main 实现」自动关闭流程调研

> 调研对象：公开仓库 `openclaw/clawsweeper`（默认分支 `main`）。
> 源码、提示词、文档、workflow 的引用均固定在提交 **`d6179da56748b0a0e791c700b0c7c10e7b6c7a4c`**。
> 真实样本：`openclaw/openclaw#197766`、`openclaw/openclaw#199533`（均于 2026-11-12 / 2026-11-15 由 `clawsweeper[bot]` 关闭）。
> 标注 **UNVERIFIED** 的条目表示公开源码/公开时间线不能直接证明，仅有间接证据。

## 一句话

ClawSweeper 把「已经在 main 修复/实现」编码为关闭原因 token **`implemented_on_main`**（展示文本 `already implemented on main`）：review lane 只产出高置信度 `close` 提案，并把一条可原地编辑的持久 review 评论发到 issue 上；apply lane 在重新读取 live 状态、标签、作者关系、会话锁、快照新鲜度和 `fixedSha` + `fixedRelease`（或 `fixedAt`）证据后，用 `PATCH {state:"closed", state_reason:"completed"}` 关闭 issue。真实样本从 issue 打开到关闭约 **8 分钟**，review 评论发布到关闭之间约 **22–26 秒**。

---

## 1. 关闭原因分类法（精确字符串）

### 1.1 规范原因 token 与展示文本

`src/clawsweeper-close-reasons.ts:25-63` 是 token → 人类可读文本的唯一映射。与「已在 main 实现」相关的两条是：

| token | 展示文本 | 引用 |
|---|---|---|
| `implemented_on_main` | `already implemented on main` | `src/clawsweeper-close-reasons.ts:27-28` |
| `mostly_implemented_on_main` | `mostly implemented on main` | `src/clawsweeper-close-reasons.ts:29-30` |

`src/clawsweeper-close-reasons.ts:31-62` 还定义了其余 token 的展示文本（见下表）。

### 1.2 全部 17 个可关闭原因 + `none`

决策 schema 的枚举顺序即 `schema/clawsweeper-decision.schema.json:69-90`；`ALLOWED_REASONS` 在 `src/clawsweeper-policy.ts:545-563`，`ALL_REASONS` 额外包含 `"none"`（`src/clawsweeper-policy.ts:584`）。

| # | token | 展示文本 | 允许的 item kind |
|---|---|---|---|
| 1 | `implemented_on_main` | already implemented on main | issue + PR |
| 2 | `mostly_implemented_on_main` | mostly implemented on main | 仅 PR |
| 3 | `cannot_reproduce` | cannot reproduce on current main | issue + PR |
| 4 | `clawhub` | belongs on ClawHub | issue + PR |
| 5 | `duplicate_or_superseded` | duplicate or superseded | issue + PR |
| 6 | `low_signal_unmergeable_pr` | low-signal unmergeable PR | 仅 PR |
| 7 | `oversized_pull_request` | pull request exceeds the review size limit | 仅 PR |
| 8 | `stalled_unproven_pr` | stalled PR without requested real-behavior proof | 仅 PR |
| 9 | `abandoned_pr` | abandoned inactive PR | 仅 PR |
| 10 | `unconfirmed_product_direction` | feature-like PR without confirmed product direction | 仅 PR |
| 11 | `unsponsored_feature_request` | feature request without maintainer sponsorship | 仅 issue |
| 12 | `author_pr_budget_exceeded` | lowest-signal PR over the author's open-PR budget | 仅 PR |
| 13 | `stale_version_bug` | bug report against a stale version | 仅 issue |
| 14 | `obsolete_fix_pr` | fix made obsolete by later main-branch changes | 仅 PR |
| 15 | `not_actionable_in_repo` | not actionable in this repository | issue + PR |
| 16 | `incoherent` | too unclear to act on | issue + PR |
| 17 | `stale_insufficient_info` | stale with insufficient information | 仅 issue |
| — | `none` | kept open | 仅用于 keep-open |

kind 限制的代码在 `src/clawsweeper-close-reasons.ts:5-23`；`implemented_on_main` 走 `default` 分支，因此 issue 与 PR 都允许（同文件 `:20-21`）。

### 1.3 机器标签与隐藏标记

- **GitHub issue 的机器可读关闭原因**：`state_reason`。实现类原因写 `completed`，其余写 `not_planned`：`src/clawsweeper-report-actions.ts:33`、`:36-51`。
- **没有专门标签**：仓库的受保护/自动化标签集合不含任何 `implemented_on_main` 标签（`src/clawsweeper-policy.ts:527-532`、`src/repair/exact-review-guard-labels.ts:5-35`）。关闭原因不通过 label 表达。
- **报告 front matter**：`close_reason: <token>`，见 `src/clawsweeper-report-document.ts:664`。
- **持久 review 评论的标记**（顺序固定）：
  - 版本标记：`<!-- clawsweeper-review-version item=<n> reviewed_at=<ISO> sha=<head|na> source_revision=<hash> lease_owner=<id> lease_comment_id=<id> v=1 -->`（`src/clawsweeper-review-comment-automation.ts:21-47`）。
  - 身份标记：`<!-- clawsweeper-review item=<n> -->`（`src/clawsweeper-review-comment-identity.ts:19-21`，由 `src/clawsweeper-review-comment-state.ts:85-89` 追加）。
  - PR 专用收据：`<!-- clawsweeper-close-applied item=<n> -->`（`src/clawsweeper-review-comment-identity.ts:23-25`），issue 关闭不使用（`README.md:337-339`）。
- **issue 的 verdict/action 标记只用于 `unsponsored_feature_request`**：`src/clawsweeper-review-comment-automation.ts:56-75`。因此 `implemented_on_main` 的 issue 评论里没有 `clawsweeper-verdict:close`。

---

## 2. 检测：模型/工具收到什么，判定标准是什么

### 2.1 输入

review 是单 item、只读的 Codex 运行：

- 只读工具与 REST-only GitHub 读取：`prompts/review-item.md:7-8`（`rg`、`sed`、`nl`、`find`、`git log/show/diff/blame`、`gh api`；禁止写操作）。
- GitHub 上下文包含完整 item（body、comments、timeline）以及 related items 索引（mentions、linked closing PRs、local report matches、gitcrawl siblings、search matches）：`prompts/review-item.md:19`。
- 要求读完整根 `AGENTS.md`、docs、tests、历史与调用点，并在 `evidence` 中记录 `repo/file/line/sha`：`prompts/review-item.md:11`、`:17`；schema 的 evidence 必填字段为 `repo,label,detail,file,line,command,sha`（`schema/clawsweeper-decision.schema.json:127-138`）。
- issue 的 review 目标：current `main` 或 merged PR 能证明修复即关闭：`prompts/review-item-issue.md:3`。
- 宿主在模型运行前做 PR 历史与 provenance 预取：`src/clawsweeper-review-item.ts:112-138`（`pullRequestHistoryCoverage`、`pullRequestProvenanceEvidence`）。
- 模型运行后，宿主再附加/校验修复 PR：`src/clawsweeper-review-item.ts:209-210`（`attachFixedPullRequest`、`verifyRegressionProvenance`）。

### 2.2 治理提示词/rubric（`implemented_on_main` 的核心）

`prompts/review-close-reasons.md:10` 是完整 rubric，关键要求可拆为：

1. current `main` 足够好地修复请求，即使实现方式/文件拆分/命名与提议不同；main-only 也算。
2. 必须在 source（必要时 tests/docs）中验证行为，并从 merged `closingPullRequests` 或 `referencingMergedPullRequests` 条目追踪到 commit、timestamp、first release（`git tag --contains <sha>`、changelog、`gh api repos/<owner>/<repo>/releases`）或 current-main-only 状态。
3. 证据必须包含带 `file` 和 `sha` 的 source 条目、一个 `git blame/log/show` provenance 条目，以及该 release 检查；没有 `fixedSha` 和 `fixedRelease` 或 `fixedAt` 就 keep open，禁止编造 release。
4. main-only 的关闭评论必须说明修复在 current `main` 并给出 `fixedAt`。
5. PR 不能只靠 source 相似、功能重叠或 main 上某个 commit；必须引用 GitHub 正式链接、已合并、同仓库的 fixing PR，并明确对应请求行为。链接不完整、歧义、跨仓库或推断时，keep PR open，且不得关闭任何 linked issue。
6. `mostly_implemented_on_main` 仅适用于 60 天以上 PR，且必须满足同一 provenance 标准（`prompts/review-close-reasons.md:11`）。

`prompts/review-close-reasons.md:1` 还定义：maintainer engagement = assignee / requested reviewer / maintainer comment or review；automation labels = `clawsweeper:human-review`、`clawsweeper:manual-only`、`clawsweeper:autofix`、`clawsweeper:automerge`。

产品/范围类原因（`unconfirmed_product_direction`、`unsponsored_feature_request`、`clawhub`、`not_actionable_in_repo`）只是建议，apply 永不执行：`prompts/review-close-reasons.md:3-8`。

### 2.3 keep-open 与误报护栏（提示词层）

`prompts/review-item.md:31-38`：

- 第一条规则优先：maintainer 作者（`OWNER`/`MEMBER`/`COLLABORATOR`）必须显式人工判断；受保护 label（`security`、`beta-blocker`、`release-blocker`、`maintainer`）阻止关闭；被 open PR 用 `Fixes`/`Closes`/`Resolves` 引用的 issue 必须等 PR 合并；同作者 open issue/PR 配对未解决时 stay open。
- close 必须 `confidence: high`、至少一条 evidence、并带该原因要求的 `closeComment`（`prompts/review-item.md:38`）。
- 规范项搜索：`relatedItems`、全状态 issue/PR 搜索、本地 reports，按同义词/旧名/linked PR 追踪；一个 canonical item 拥有剩余工作才可用 `duplicate_or_superseded`（`prompts/review-item.md:44-46`）。

### 2.4 宿主侧的硬校验（不信任模型自述）

`src/clawsweeper-close-decision.ts`：

- `hasUsableCloseComment`：空评论或占位符 `_No close comment posted._` 不可用（`:33-36`）。
- issue/PR 都要求至少一条 evidence 同时有 `file` 和 `sha`（`:38-42`、`:413-422`）。
- 要求 `fixedSha`（`:436-442`），`fixedAt` 必须是 ISO 时间（`:443-453`），并且 `fixedRelease` 或 `fixedAt` 至少有一个（`:454-464`）。
- 对 PR：必须有 high-confidence、同仓库、非自身的 `fixedPullRequest`，`mergedAt` 存在，`source` 属于 GitHub 验证来源，URL 与 `repo#number` 一致（`:49-71`、`:423-434`）。
- GitHub 验证来源白名单：`"GitHub closing PR reference"`、`"GitHub linked-issue current closing PR"`、`"GitHub reviewed implementation landing"`、`"GitHub commit PR lookup"`（`src/clawsweeper-policy.ts:534-539`）。
- PR 的 fixing PR 是否仍可从默认分支到达：`compare/<merge_commit_sha>...<branch>` 返回 `ahead`/`identical`（`src/clawsweeper-fixed-pull-request.ts:629-643`）。

### 2.5 git 操作在哪里发生

- 模型 sandbox 内的只读 git：`prompts/review-item.md:7`。
- 宿主的 PR 历史预取（为 blame 补齐旧 blob）：`src/clawsweeper-review-item.ts:110-119`。
- 宿主通过 GitHub API 做 commit→PR 查找：`src/clawsweeper-fixed-pull-request.ts:406-459`（`fixedSha` → `recentPullsForFixedSha` 或 `repos/<repo>/commits/<sha>/pulls`）。
- issue 的 commit→PR 兜底：`src/clawsweeper-fixed-pull-request.ts:700-715`（`GitHub commit PR lookup`）。

---

## 3. 流水线各阶段

### 3.1 事件摄入

- `ClawSweeper Dispatch` 监听 `issues`（opened/reopened/edited/labeled/unlabeled）、`issue_comment`（created/edited）、`pull_request_target`（opened/reopened/synchronize/ready_for_review/edited/labeled/unlabeled）：`.github/workflows/clawsweeper-dispatch.yml:3-9`。
- 评论命令预过滤正则包含 `@clawsweeper` / `/clawsweeper` / `/review` / `/re-review` / `/stop` 等：`.github/workflows/clawsweeper-dispatch.yml:39-49`。
- 非评论事件直接 POST 到 `https://clawsweeper.openclaw.ai/github/target-dispatch`，携带 `TARGET_REPO`、`ITEM_NUMBER`、`ITEM_KIND`、`SOURCE_EVENT`：`.github/workflows/clawsweeper-dispatch.yml:51-60`。

### 3.2 队列与 claim/lease

- 队列是 Cloudflare Worker + Durable Object：`ExactReviewQueue` 类在 `dashboard/exact-review-queue.ts:995`。
- claim 端点：`POST /claim`，要求 `lease_id`/`run_id`，支持 `item_key` + `lease_revision` 的 tuple claim：`dashboard/exact-review-queue.ts:2937-2957`。
- 心跳端点：`POST /heartbeat`：`dashboard/exact-review-queue.ts:3124`。
- 默认 lease 时长：dispatch 6 分钟、publication dispatch 15 分钟、execution 130 分钟、heartbeat grace 20 分钟、retry 30 秒：`dashboard/exact-review-read-model.ts:26-30`。
- 队列把 item 状态持久化为 `pending`/`dispatching`/`leased`/`parked`，并记录 `leaseId`、`leaseRevision`、`leaseExpiresAt`、`claimedRunId`、`claimGeneration`：`dashboard/exact-review-queue.ts:385-406`。

### 3.3 只读 review

- 入口：`createReviewCommandWorkflow`（`src/clawsweeper-review-command-workflow.ts:146`）→ `runPreparedReviewItem`（`src/clawsweeper-review-item.ts:38`）。
- prompt 组装：`buildReviewPrompt` 在 `src/clawsweeper-review-core.ts:289-301` 渲染 core、item-kind 模板，并用 `applicableCloseReasons` 填充 `{{close_reasons}}`。
- `applicableCloseReasons` 只过滤「宿主事实层面不可能」的原因；**maintainer 作者或受保护 item 会得到空列表**：`src/review-prompt-sections.ts:120`、`:137`。
- review 是 proposal-only，从不关闭：`README.md:290`、`docs/scheduler.md:1136-1137`。

### 3.4 报告/评论发布

- review 结果写成 `records/<repo-slug>/items/<number>.md`，包含 decision、evidence、建议评论、运行元数据、GitHub snapshot hash：`README.md:310-314`。
- 高置信度允许的 close 决策变成 `proposed_close`：`README.md:315`。
- 单条 marker-backed review 评论由 `upsertReviewComment` 发布；存在可 PATCH 的旧评论就 PATCH，否则 POST：`src/clawsweeper-review-comment-publication.ts:245-321`（PATCH 分支 `:304-312`，POST 分支 `:313-321`）。
- close 决策的评论正文就是 close comment，再拼 markers 与 version marker：`src/clawsweeper-report-comment-presentation.ts:610-624`。

### 3.5 close 提案 → apply 通道

- 定时 apply job：`apply-existing`（`name: Apply close proposals`），cron `3,18,33,48 * * * *`：`.github/workflows/sweep.yml:3594-3597`、`:104-108`。
- apply 的实际命令是 `pnpm run apply-decisions -- ...`：`.github/workflows/sweep.yml:3953`、`:4013`。
- apply 只从 report 里的 typed `review_record` 读取 decision，不从散文中推断：`README.md:329-333`；实现 `src/clawsweeper-apply-close-decision.ts:34-45`（强制 `decision:"close"`、`confidence:"high"`、使用 `publishedCloseComment`）。
- 每次 apply 默认最多 40 个新关闭、每对 close 后延迟 2 秒：`README.md:345-353`、`docs/scheduler.md:1165-1169`；workflow 默认值 `apply_close_delay_ms=2000`、`apply_checkpoint_size=40`：`.github/workflows/sweep.yml:97-103`。

### 3.6 安全门重检 → close mutation

- 入口：`executeApplyClose`（`src/clawsweeper-apply-close-execution.ts:192`）。
- 最终 mutation 只通过 `closeItem`：PR 用 `gh pr close`；issue 用 `PATCH repos/<repo>/issues/<n>`，payload 为 `{state:"closed", state_reason:"completed"}`（实现类原因）或 `not_planned`（其他）：`src/clawsweeper-report-actions.ts:26-53`。
- 关闭后更新报告 `action_taken: closed`、`applied_at`、`apply_checked_at`，并归档到 `closed/`：`src/clawsweeper-apply-close-execution.ts:1033-1044`；`README.md:340-343`。

### 3.7 持久化状态

- report：`records/<repo-slug>/items/<number>.md`；关闭后 `records/<repo-slug>/closed/<number>.md`（`README.md:310-314`、`:340-343`）。
- typed review record 是 front matter 里的一行 JSON：`review_record: {"version":1,"decision":{...}}`（`src/review-record.ts:23-26`）；读不出就要求 fresh review（`src/clawsweeper-apply-close-decision.ts:23-30`）。
- action ledger / mutation idempotency：`ghObservedMutationCommand` 把每次 mutation 包成带 `identity` 与 `idempotencyIdentity` 的 receipt（`src/clawsweeper-github-execution.ts:177-204`）；关闭的 identity 为 `item_close:<n>:<kind>:<reason>`（`src/clawsweeper-report-actions.ts:29`、`:42`）。
- apply 的 checkpoint 与 status 写入状态仓库：`README.md:343`、`docs/scheduler.md:1145-1152`。

---

## 4. apply/安全门：关闭前到底重验什么

### 4.1 决策合法性（`validateCloseDecision`）

顺序见 `src/clawsweeper-close-decision.ts:241-465`：

1. 必须是 close（`:248-254`）。
2. security review 不能是 `needs_attention` 或有 concern（`:255-264`）。
3. `applyBlockingProtectedLabels(item.labels, reason)` 必须为空（`:265-271`）。
4. `canClose`：close + high confidence + allowed reason（`:73-79`、`:272-278`）。
5. repository profile 必须允许该 reason（`:279-285`）。OpenClaw 的 issue/PR profile 都包含 `implemented_on_main`（`src/repository-profiles.ts:75-93`、`:183-189`）。
6. 原因专属证据门：file+sha、`fixedSha`、`fixedAt`、`fixedRelease`/`fixedAt`、PR 的 verified fixing PR（`:413-464`）。

### 4.2 `implemented_on_main` 对受保护标签的唯一例外

- `applyBlockingProtectedLabels` 对 `implemented_on_main`（以及 `oversized_pull_request`）**只移除 `maintainer` 一个标签**，其余受保护标签（`security`、`beta-blocker`、`release-blocker`、`area: security`、`impact:security`、`security-review-required`、`security-sensitive-changed`、`merge-risk: 🚨 security-boundary`、`clawsweeper:needs-security-review`）仍然阻止关闭：`src/clawsweeper-item-policy.ts:117-131`；集合定义在 `src/repair/exact-review-guard-labels.ts:18-35`。
- 文档明确：只有 `implemented_on_main` 对「maintainer 作者 / `maintainer` label」有例外，不豁免 security、manual hold、lock、outstanding human decision、freshness 或任何实现证据：`docs/implemented-on-main-close-policy.md:12-18`。
- README 同样说明：当唯一受保护状态是 maintainer 所有权、且原因是 verified `implemented_on_main` 时可以关闭：`README.md:399-406`。

### 4.3 apply 执行期重检（`executeApplyClose`）

按执行顺序：

| 检查 | 位置 | 失败动作 |
|---|---|---|
| 需要 maintainer product decision 的原因 | `src/clawsweeper-apply-close-execution.ts:346-353` | `kept_open` |
| close 数量上限 | `:354-357` | `stop` |
| apply kind 过滤 | `:358-360` | `kept_open` |
| reason 是否在本次 apply 启用集合 | `:361-363` | `kept_open` |
| PR 的 `fixed_pr_url/number/confidence/source/merged_at` 是否仍满足 GitHub 验证来源 | `:86-118`、`:387-393` | `kept_open` |
| PR 必须显式、同仓库、恰好 1 个 linked issue | `:370-405` | `kept_open` |
| PR 的 linked issue 仍 open、当前 fixing PR 的 `closingIssuesReferences` 仍包含它 | `src/clawsweeper-fixed-pull-request.ts:181-219`、`:485-528` | `kept_open` |
| 报告重新校验（review record、证据、profile） | `src/clawsweeper-apply-close-execution.ts:415-428` | `skipped_*` 或 `kept_open` |
| 年龄门（`implemented_on_main` 无最小年龄；`mostly_implemented_on_main` 有 60 天） | `src/clawsweeper-item-policy.ts:180-196`、`src/review-prompt-sections.ts:87-96` | `kept_open` |
| 终局 live 检查：security hidden payload、live close-reason policy、same-author pair、最后读锁 | `src/clawsweeper-apply-close-execution.ts:475-528` | `kept_open` / `skipped_protected_label` / `skipped_same_author_pair` / `skipped_locked_conversation` |
| mutation lease | `:530-531` | skip lease |
| issue 的 `implemented_on_main` 必须有当前 durable review comment | `:544-549` | `kept_open` |
| 配对关闭容量 | `:550-555` | `kept_open` |
| pre-note 终局重检 | `:673-680` | 同上 |
| PR close receipt（issue 不发） | `:681-707` | `skipped_comment_auth` / `skipped_locked_conversation` |
| 最终 freshness（评论发布后的自 mutation receipt、item 源活动） | `:708-733` | `skipped_changed_since_review` / `kept_open` |
| PR 的 provenance 再读一次 | `:734-745` | `kept_open` |
| post-note 终局重检、最终 mutation lease | `:755-761` | 同上 |
| 最后 `closeItem` | `:1033` | mutation |

live policy 使用 `evaluateApplyCloseReasonPolicy`；`implemented_on_main` 不命中任何专属分支，两个 phase 都走 `default: allowed()`：`src/clawsweeper-apply-close-policies.ts:83-137`、`:140+`。

### 4.4 具体 skip 原因

`ActionTaken` 全集见 `src/clawsweeper-types.ts:183-205`。与 `implemented_on_main` 最相关的：

- `skipped_protected_label`：security 等受保护 label（maintainer 已被例外移除）。
- `skipped_invalid_decision`：缺证据/`fixedSha`/release-or-fixedAt、非 high confidence、reason 不在 profile、PR 的 fixing PR 未验证。
- `skipped_changed_since_review`：item 在 review 后变化、durable comment 不新鲜、review record 读不出。
- `skipped_maintainer_authored`：仅当 reason 不是 verified `implemented_on_main` 时；`:1875-1881` 的条件包含 `!isVerifiedFixedCloseReason(closeReason)`。
- `skipped_locked_conversation`：最后读到 `locked === true`（`src/clawsweeper-apply-close-execution.ts:512-517`）。
- `skipped_already_closed`：状态已不是 open（`src/clawsweeper-apply-decision-workflow.ts:1499-1506`）。
- `skipped_same_author_pair`、`skipped_open_closing_pr`：配对保护（`src/clawsweeper-policy.ts:615-618`）。
- `skipped_comment_auth`、`skipped_runtime_budget`：写入认证/运行预算。

apply 层把这些 skip 分为三类选择器：live-recheck guard（`skipped_protected_label`、`skipped_close_exempt_label`、`skipped_locked_conversation`）、legacy fixed close skip（`skipped_maintainer_authored`、`skipped_invalid_decision`，**仅当 reason 为 `implemented_on_main` 时才算可重选**）、以及其他可选动作（`proposed_close`、`retry_pr_close_coverage_proof`、`kept_open`、`skipped_low_signal_live_guard`、`skipped_open_closing_pr`、`skipped_same_author_pair`）：`src/apply-close-actions.ts:1-38`。这说明 `implemented_on_main` 在历史遗留的 maintainer/invalid 跳过上有一条专门的重试通道。

### 4.5 `@clawsweeper stop` 与 `clawsweeper:human-review`

- `stop` 的动作是：加 `clawsweeper:human-review`，移除 `clawsweeper:automerge`、`clawsweeper:autofix`、`clawsweeper:merge-ready`，然后回复：`src/repair/comment-router.ts:639-656`；README 说明见 `README.md:212-216`。
- `human-review` **不在** `CLOSE_PROTECTED_LABEL_NAMES` / `APPLY_PROTECTED_LABELS` 中（`src/repair/exact-review-guard-labels.ts:18-53`、`src/clawsweeper-policy.ts:527-532`），也不是 `implemented_on_main` 的 close guard。
- 它在 `PR_AUTO_CLOSE_EXEMPT_LABEL_NAMES` 中，但 `prAutoCloseExemptDecisionReason` 只对 PR 且仅对 `unconfirmed_product_direction`、`stalled_unproven_pr`、`abandoned_pr`、`author_pr_budget_exceeded`、`obsolete_fix_pr` 生效：`src/clawsweeper-apply-guard-activity.ts:192-215`；`implemented_on_main` 不在其中。
- **结论（负面发现）**：按当前公开代码，`@clawsweeper stop` 单独**不会**阻止 issue 的 `implemented_on_main` 自动关闭。
- 间接影响：`human-review` 被计入 issue 的 `close_guard_labels` 并参与 `source_content_revision` 哈希（`docs/target-dispatcher.md:150-193`），所以加标签可能使进行中的 review 快照变旧，触发 fresh review；fresh review 之后它不再阻碍。**该间接路径在真实 issue 上的效果 UNVERIFIED。**

### 4.6 幂等与竞态

- 每个 mutation 有稳定 `identity`（关闭为 `item_close:<n>:<kind>:<reason>`），receipt runner 用 `idempotencyIdentity` 去重：`src/clawsweeper-github-execution.ts:177-204`、`src/clawsweeper-report-actions.ts:29`、`:42`。
- 已关闭 item 在 apply 里直接 `skipped_already_closed`，不会重复 PATCH：`src/clawsweeper-apply-decision-workflow.ts:1499-1506`。
- 关闭前最后读 `locked`，且 policy 读取绕过 generation cache：`src/clawsweeper-apply-close-execution.ts:512-517`；`docs/implemented-on-main-close-policy.md:40-51`。
- 文档明确这不是远端两 item 事务：GitHub 可在最后一次读之后改变，后续 mutation 可独立失败：`docs/implemented-on-main-close-policy.md:53-56`。

---

## 5. 精确产物

### 5.1 标签

以真实案例 #197766 的 timeline 为准（GitHub timeline API）：

- 打开后约 3 分钟：`clawsweeper[bot]` 加 `clawsweeper:intake:bug`、`clawsweeper:intake:needs-repro`（2026-11-12T14:07:04Z）。
- review/apply 前：移除上述 intake 标签，加 `P2`、`impact:auth-provider`（2026-11-12T14:11:32–33Z）。
- 关闭时：没有加任何「已关闭 / implemented」标签；关闭后标签就是 `P2`、`impact:auth-provider`。

代码侧：intake 标签是初步标签，完整 review 后由 guarded label batch 移除（`docs/intake-triage.md:27-28`、`:83-84`）；优先级/impact 标签由 apply 的 `syncPriorityLabel` / `syncImpactLabels` 同步（`src/clawsweeper-apply-report-labels.ts:64-80`）。**`implemented_on_main` 没有专属标签。**

### 5.2 持久 review 评论（issue 关闭的唯一评论）

结构（`src/clawsweeper-report-comment-helpers.ts:573-660`）：

1. `closeIntro(reason)`：`implemented_on_main` 固定句 "Thanks for the context here. I did a careful shell check against current `main`, and this is already implemented."（`:394-395`）。
2. 空行 + `summary`（一句 verdict/rationale）。
3. 若 `fixedPullRequest.confidence === "high"`，追加 "I found the merged PR that appears to have closed this: [#N: title](url)."（`:597-604`）。
4. 可选 regression / root-cause cluster / duplicate canonical path。
5. `<details><summary>Review details</summary>` 折叠块：`Best possible solution`、两个 review questions、`Security review`、`AGENTS.md`、`What I checked`（最多 6 条 evidence）、`Likely related people`、`Codex review notes`（`:636-658`）。
6. `closeOutro(reason)`：`implemented_on_main` 固定句 "So I’m closing this as already implemented rather than keeping a duplicate issue open."（`:437-438`）。
7. 末尾 markers：`<!-- clawsweeper-review-version ... -->`、`<!-- clawsweeper-review item=N -->`。

### 5.3 原地编辑

issue 的持久 review 评论是单条、marker-backed、可 PATCH 的评论；apply 会在 stale 时更新它（`README.md:316-318`、`:335`；`src/clawsweeper-review-comment-publication.ts:304-312`）。真实案例 #197766 的评论 `created_at == updated_at`（2026-11-12T14:11:39Z），说明本次关闭没有二次编辑。

### 5.4 关闭评论

- issue：**没有单独的关闭评论**；持久 review 评论就是 ClawSweeper 的唯一评论（`README.md:337-339`；`src/clawsweeper-apply-close-execution.ts:681-691` 只对 PR 发 close-applied receipt）。
- PR：发一条幂等、marker-backed 的 close-applied receipt，文本包含 "ClawSweeper recorded implementation evidence for this proposed close."、`Close reason: already implemented on main.`、`Implementation evidence: ...`（`src/clawsweeper-review-comment-publication.ts:416-447`）。

---

## 6. 真实 `openclaw/openclaw` 案例

### 6.1 主案例：#197766（人类作者，NONE association）

- 标题：`[Bug]: image/music generation completion always falls back off claude-cli ("CLI runtimes cannot enforce restart-safe tool restrictions")`
- URL：https://github.com/openclaw/openclaw/issues/197766
- 作者：`jzmudzinski`，`author_association: NONE`
- 最终状态：`closed`，`state_reason: completed`，`closed_by: clawsweeper[bot]`
- 最终标签：`P2`、`impact:auth-provider`

完整 UTC 时间线（GitHub issue + timeline API）：

| 时间 | 事件 |
|---|---|
| 2026-11-12T14:04:09Z | issue opened by `jzmudzinski` |
| 2026-11-12T14:07:04Z | `clawsweeper[bot]` 加 `clawsweeper:intake:bug`、`clawsweeper:intake:needs-repro` |
| 2026-11-12T14:11:32Z | 移除 `clawsweeper:intake:bug` |
| 2026-11-12T14:11:33Z | 移除 `clawsweeper:intake:needs-repro`；加 `P2`、`impact:auth-provider` |
| 2026-11-12T14:11:39Z | `clawsweeper[bot]` 发布 review 评论（id 6825937985） |
| 2026-11-12T14:12:05Z | `clawsweeper[bot]` 关闭 issue（`state_reason: completed`） |

从打开到关闭：**7 分 56 秒**。从 review 评论到关闭：**26 秒**。

review/关闭评论（verbatim，trim 掉中段代码链接细节）：

```text
Thanks for the context here. I did a careful shell check against current `main`, and this is already implemented.

Current main removes the restricted media-completion dispatch that triggers CLI rejection and provider fallback; the repair is available in v2026.11.5-beta.1, while stable v2026.11.3 retains the old path.

So I’m closing this as already implemented rather than keeping a duplicate issue open.

<details>
<summary>Review details</summary>

Best possible solution:

Use a release containing the host-delivery repair, verified in v2026.11.5-beta.1.

...
- **Merged fixing PR and provenance:** https://github.com/openclaw/openclaw/pull/174696 merged as 749464ce0a56c75d8b2ef9b4fa2caf745a8bc549; its patch removes forceRestartSafeTools from media dispatch. obviyus's landing explanation credits https://github.com/openclaw/openclaw/issues/169118 and describes host-owned delivery followed by ordinary completion. ([`src/gateway/server-restart-sentinel-agent-delivery.ts`](https://github.com/openclaw/openclaw/blob/749464ce0a56c75d8b2ef9b4fa2caf745a8bc549/src/gateway/server-restart-sentinel-agent-delivery.ts), [749464ce0a56](https://github.com/openclaw/openclaw/commit/749464ce0a56c75d8b2ef9b4fa2caf745a8bc549))

Codex review notes: model internal, reasoning medium; reviewed against [1888857db11c](...); fix evidence: release [v2026.11.5-beta.1](...), commit [749464ce0a56](...).

</details>

<!-- clawsweeper-review-version item=197766 reviewed_at=2026-11-12T14:10:59.534Z sha=na source_revision=2e2b6b539111ed01ccb2e25001a6e088d8390ae9fc4b9ff683213fcc544fea37 lease_owner=github-run-43233665723-1 lease_comment_id=6825815292 v=1 -->

<!-- clawsweeper-review item=197766 -->
```

修复 provenance 核验：

- PR #174696：`merged: true`、`merged_at: 2026-10-17T03:09:00Z`、`merge_commit_sha: 749464ce0a56c75d8b2ef9b4fa2caf745a8bc549`、base `main`、head repo `openclaw/openclaw`。
- 该 PR body 只写 `Related: #169118`，**没有** `Fixes #197766`；GraphQL `closingIssuesReferences(first:10, excludeUserLinked:true)` 返回空。
- 因此这个 issue 的关闭不是依赖「PR 正式关闭 issue」关系，而是依赖 current `main` 源码等价 + merged commit + release 证据。这与代码一致：verified fixing PR 的硬门只对 PR kind 生效（`src/clawsweeper-close-decision.ts:423-434`），issue 只要求 evidence(file+sha) + `fixedSha` + release/fixedAt（`:413-422`、`:436-464`）。

### 6.2 次案例：#199533（bot 生成的 update report）

- 标题：`Update failure: gateway-stop-unverified (2026.11.3)`
- URL：https://github.com/openclaw/openclaw/issues/199533
- 作者：`changyogpt-code`；最终 `closed`、`state_reason: completed`、`closed_by: clawsweeper[bot]`；标签 `P2`、`impact:ux-friction`。
- 时间线：opened 2026-11-15T09:02:31Z → intake 标签 09:04:56Z → `P2`/`impact:ux-friction` 09:10:10Z → review 评论 09:10:16Z → closed 09:10:38Z。总时长 **8 分 07 秒**；评论到关闭 **22 秒**。
- 评论首段同样是固定句 "Thanks for the context here. I did a careful shell check against current `main`, and this is already implemented."，并给出 fixing PR #187020（merge commit `171702ee2b0f06feb87accbe0f3c473ec53acc58`）、release `v2026.11.5-beta.1`、`fixedAt` 语义的 "current main ... stable 2026.11.3 still contains the older behavior"。

### 6.3 关闭原因 token 的直接可见性

公开评论只显示自然语言 "already implemented"，不显示 token `implemented_on_main`。判断这两个案例属于该原因的公开证据是：

1. 评论模板与 `closeIntro`/`closeOutro` 的 `implemented_on_main` 分支逐字一致（`src/clawsweeper-report-comment-helpers.ts:394-395`、`:437-438`）。
2. `state_reason: completed` 仅在 `isImplementationCloseReason(reason)` 时写入（`src/clawsweeper-report-actions.ts:33`），即 `implemented_on_main` 或 `mostly_implemented_on_main`；后者只允许 PR（`src/clawsweeper-close-reasons.ts:7-15`），这两个都是 issue，所以只能是 `implemented_on_main`。
3. 报告中的 `review_record` 不公开。**因此「报告内确实存的是 `implemented_on_main`」仍属推断，标记 UNVERIFIED。**

---

## 7. 时序特征

### 7.1 review 节奏

`docs/scheduler.md:1021-1028`：

- 上次真实 review 后有 target-side activity：每小时
- 最近 7 天创建且无新活动：每天
- hot window 之外的 PR：每天
- 最近 30 天创建的 issue：每天
- 更老的 inactive issue：每周
- review policy hash 变化：立即 due

### 7.2 workflow cron

`openclaw/openclaw`（`docs/scheduler.md:620-625`，workflow 实际值）：

| lane | cron | 引用 |
|---|---|---|
| hot intake | `*/5 * * * *` | `.github/workflows/review-plan.yml:69` |
| normal backfill | `9/20 * * * *`（9、29、49 分） | `.github/workflows/review-plan.yml:74` |
| apply | `3,18,33,48 * * * *` | `.github/workflows/sweep.yml:104-108` |
| comment sync | `6,21,36,51 * * * *` | `.github/workflows/sweep.yml:110` |

### 7.3 观察到的延迟

- 两个已核验案例：打开 → 关闭 **7m56s** 与 **8m07s**；review 评论 → 关闭 **26s** 与 **22s**。
- 对 `search/issues` 查询 `repo:openclaw/openclaw is:issue is:closed "closing this as already implemented"` 的最近 100 个命中，按 `created_at` → `closed_at` 计算，中位数 **7.7 分钟**（样本含少数长尾，最大约 5.4 天）。
- 抽样核验该 100 个命中里最早的 25 个：25/25 均为 `state: closed`、`state_reason: completed`、`closed_by: clawsweeper[bot]`。
- 关闭发生在 review 评论之后 22–26 秒，而 apply cron 是每 15 分钟一次（`:03/:18/:33/:48`）。14:12:05 不在这些分钟上，说明这次关闭来自 exact publisher 的「review 完立刻 apply 同一 item」路径（`README.md:278-281`：队列租约一个执行器 review 一个 item、sync 持久评论、并对同一 item 只应用安全 close 提案），而不是等待下一次 cron。**该归因是时间+文档推断，UNVERIFIED。**

### 7.4 apply 节流

- 每次 apply 最多 40 个新关闭；每 40 个 checkpoint 提交并续跑；饱和且 0 关闭则停止：`docs/scheduler.md:1165-1169`。
- 每个 close/comment 对之间默认 2 秒延迟：`README.md:348-349`、`.github/workflows/sweep.yml:96-99`。

---

## 未验证 / 需要谨慎的结论

1. **UNVERIFIED**：两个真实案例报告内的 `review_record.closeReason` 字面值。公开证据是评论模板 + `state_reason: completed` + kind 限制的联合推断。
2. **UNVERIFIED**：`@clawsweeper stop` 的间接影响（通过 `source_content_revision` 触发 fresh review）在真实 issue 上的效果。代码只证明该标签参与 issue 的 close-guard label 哈希；不证明它会阻止 `implemented_on_main`。
3. **UNVERIFIED（代码层张力）**：`README.md:399-406` / `docs/implemented-on-main-close-policy.md:12-18` 说 maintainer 作者可在 `implemented_on_main` 下关闭，但 review prompt 对 maintainer 作者/受保护 item 返回空 close-reason 列表（`src/review-prompt-sections.ts:120`、`:137`），因此 review 侧不会提出该原因；apply 侧的例外仍存在（`src/clawsweeper-apply-decision-workflow.ts:1875-1881`、`src/clawsweeper-item-policy.ts:128-130`）。实际生产行为未观察。
4. **UNVERIFIED**：exact publisher 与定时 apply 的具体归属（见 7.3）。
5. `docs/scheduler.md` 头部的 "Last verified" 是更早的 `647503ec...`（`docs/scheduler.md:9`），而本笔记所有引用都取 `d6179da...` 的文件内容；两者在该文件上可能存在后续编辑差异。

---

## 证据索引

所有 `openclaw/clawsweeper` 链接都指向固定 SHA `d6179da56748b0a0e791c700b0c7c10e7b6c7a4c`。

| # | 来源（URL） | file:line | 证明什么 |
|---|---|---|---|
| 1 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-close-reasons.ts | `src/clawsweeper-close-reasons.ts:25-30` | `implemented_on_main` 的规范展示文本是 `already implemented on main` |
| 2 | 同上 | `src/clawsweeper-close-reasons.ts:5-23` | `implemented_on_main` 对 issue 和 PR 都允许；8 个 reason 仅 PR、3 个仅 issue |
| 3 | 同上 | `src/clawsweeper-close-reasons.ts:31-62` | 其余 15 个 reason 的展示文本 |
| 4 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/schema/clawsweeper-decision.schema.json | `schema/clawsweeper-decision.schema.json:69-90` | decision 枚举与 17 个 close reason 的完整集合 |
| 5 | 同上 | `schema/clawsweeper-decision.schema.json:127-138` | evidence 条目必填 `repo,label,detail,file,line,command,sha` |
| 6 | 同上 | `schema/clawsweeper-decision.schema.json:959-970` | `fixedSha` 必填；`fixedRelease` 为 null 时 `fixedAt` 必填 |
| 7 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-policy.ts | `src/clawsweeper-policy.ts:545-563` | `ALLOWED_REASONS` 的 17 项列表 |
| 8 | 同上 | `src/clawsweeper-policy.ts:527-539` | 受保护标签集合；GitHub 验证 fixed-PR 来源白名单 |
| 9 | 同上 | `src/clawsweeper-policy.ts:615-640` | pair/closed-state/event-guarded skip 动作集合 |
| 10 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/prompts/review-close-reasons.md | `prompts/review-close-reasons.md:10` | `implemented_on_main` 的完整 rubric（源码+测试+docs、git tag/changelog/releases、fixedSha+fixedRelease/fixedAt、PR 的 GitHub 正式 fixing PR 要求） |
| 11 | 同上 | `prompts/review-close-reasons.md:1-8` | maintainer engagement / automation labels 定义；产品类原因 apply 永不执行 |
| 12 | 同上 | `prompts/review-close-reasons.md:11` | `mostly_implemented_on_main` 的 60 天与同一 provenance 标准 |
| 13 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/prompts/review-item.md | `prompts/review-item.md:7-8` | review 只读；git 与 `gh api` REST 读取；禁止写操作 |
| 14 | 同上 | `prompts/review-item.md:17-19` | 要求深读 source/tests/docs/history/comments；GitHub 上下文包含完整 item 与 related items |
| 15 | 同上 | `prompts/review-item.md:31-42` | keep-open 护栏（maintainer、保护标签、open Fixes PR、same-author pair）；close 必须 high confidence + evidence + closeComment |
| 16 | 同上 | `prompts/review-item.md:44-46` | canonical search 与 `implemented_on_main` / `duplicate_or_superseded` 的选择 |
| 17 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/prompts/review-item-issue.md | `prompts/review-item-issue.md:3` | issue review 的目标：current main 或 merged PR 证明修复即关闭 |
| 18 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/review-prompt-sections.ts | `src/review-prompt-sections.ts:87-96` | `implemented_on_main` 没有最小年龄门槛；`mostly_implemented_on_main` 有 |
| 19 | 同上 | `src/review-prompt-sections.ts:120`、`:137` | maintainer 作者或受保护 item 得到空 close-reason 列表 |
| 20 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-review-core.ts | `src/clawsweeper-review-core.ts:289-301` | prompt 用 `applicableCloseReasons` 渲染 `{{close_reasons}}` |
| 21 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-close-decision.ts | `src/clawsweeper-close-decision.ts:33-47` | close comment 可用性；file+sha evidence；`fixedAt` ISO 校验 |
| 22 | 同上 | `src/clawsweeper-close-decision.ts:49-79` | PR fixing PR 必须同仓库、非自身、merged、GitHub 验证来源、URL 匹配；`canClose` |
| 23 | 同上 | `src/clawsweeper-close-decision.ts:241-285` | 关闭决策的顺序：security、protected label、allowed reason、profile policy |
| 24 | 同上 | `src/clawsweeper-close-decision.ts:413-464` | 实现类原因专属硬门：file+sha、`fixedSha`、`fixedAt`、`fixedRelease`/`fixedAt`、PR verified fixing PR |
| 25 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-item-policy.ts | `src/clawsweeper-item-policy.ts:117-131` | `implemented_on_main` 只移除 `maintainer` 保护标签 |
| 26 | 同上 | `src/clawsweeper-item-policy.ts:180-196` | `mostly_implemented_on_main` 与 `stale_insufficient_info` 的年龄门；`implemented_on_main` 无 |
| 27 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/repair/exact-review-guard-labels.ts | `src/repair/exact-review-guard-labels.ts:18-53` | close-protected 标签全集；`human-review` 只在 PR auto-close-exempt 集合 |
| 28 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-apply-guard-activity.ts | `src/clawsweeper-apply-guard-activity.ts:188-215` | auto-close-exempt 只对特定 PR 原因生效，不含 `implemented_on_main` |
| 29 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-apply-close-execution.ts | `src/clawsweeper-apply-close-execution.ts:86-118` | apply 对 PR 的 fixed PR provenance 重检 |
| 30 | 同上 | `src/clawsweeper-apply-close-execution.ts:346-428` | reason/kind/limit/provenance/pair/报告重校验门 |
| 31 | 同上 | `src/clawsweeper-apply-close-execution.ts:475-555` | 终局 live 检查顺序：security、live policy、pair、最后读锁；issue 必须有 durable review comment |
| 32 | 同上 | `src/clawsweeper-apply-close-execution.ts:673-761` | pre-note/post-note 重检、PR receipt、freshness、最终 lease |
| 33 | 同上 | `src/clawsweeper-apply-close-execution.ts:996-1068` | 最终 `closeItem`、报告状态更新、归档、2 秒延迟 |
| 34 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-report-actions.ts | `src/clawsweeper-report-actions.ts:26-53` | issue close 用 PATCH `state_reason:"completed"`（实现类）或 `"not_planned"`；PR 用 `gh pr close` |
| 35 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-apply-close-policies.ts | `src/clawsweeper-apply-close-policies.ts:57-137` | `implemented_on_main` 走默认 allowed，无专属 live policy 阻断 |
| 36 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-apply-decision-workflow.ts | `src/clawsweeper-apply-decision-workflow.ts:1089-1101`、`:1873-1896` | profile policy 重检；maintainer 作者门对 `implemented_on_main` 例外 |
| 37 | 同上 | `src/clawsweeper-apply-decision-workflow.ts:1499-1506` | 已关闭 item 的 `skipped_already_closed` 幂等路径 |
| 38 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-fixed-pull-request.ts | `src/clawsweeper-fixed-pull-request.ts:19-127` | 显式 Close/Fix/Resolve 解析，忽略 fence/缩进/HTML 注释，最多 5 个 |
| 39 | 同上 | `src/clawsweeper-fixed-pull-request.ts:129-179` | 从 issue timeline 的最后一个 ClosedEvent 取 closer PR，且 issue 必须 CLOSED |
| 40 | 同上 | `src/clawsweeper-fixed-pull-request.ts:181-219`、`:327-353` | 当前 `closingIssuesReferences(..., excludeUserLinked:true)` 必须包含仍 open 的同仓库 issue |
| 41 | 同上 | `src/clawsweeper-fixed-pull-request.ts:406-459` | `fixedSha` → PR 查找（recent pulls 或 `commits/<sha>/pulls`） |
| 42 | 同上 | `src/clawsweeper-fixed-pull-request.ts:485-528` | apply 重新读取 PR body、断言恰好一个 linked issue、canonical closing reference、verified PR |
| 43 | 同上 | `src/clawsweeper-fixed-pull-request.ts:629-643` | merge commit 仍可从默认分支到达（compare ahead/identical） |
| 44 | 同上 | `src/clawsweeper-fixed-pull-request.ts:722-745` | issue 与 PR 的 fixed PR 附加策略 |
| 45 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-report-comment-helpers.ts | `src/clawsweeper-report-comment-helpers.ts:390-428` | `implemented_on_main` 的固定开场白 |
| 46 | 同上 | `src/clawsweeper-report-comment-helpers.ts:431-468` | `implemented_on_main` 的固定收尾句 |
| 47 | 同上 | `src/clawsweeper-report-comment-helpers.ts:573-660` | close 评论整体结构（intro、summary、fixed PR、details、evidence、outro） |
| 48 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-report-comment-presentation.ts | `src/clawsweeper-report-comment-presentation.ts:565-624` | close 决策的 review 评论正文 = close comment + markers + version |
| 49 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-review-comment-publication.ts | `src/clawsweeper-review-comment-publication.ts:245-321` | 持久 review 评论的 PATCH/POST 与 marker 处理 |
| 50 | 同上 | `src/clawsweeper-review-comment-publication.ts:401-447` | PR close-applied receipt 文本（issue 不发） |
| 51 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-review-comment-automation.ts | `src/clawsweeper-review-comment-automation.ts:21-47`、`:49-75` | version marker 格式；issue 仅 `unsponsored_feature_request` 发 verdict/action markers |
| 52 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-review-comment-identity.ts | `src/clawsweeper-review-comment-identity.ts:19-25` | `clawsweeper-review item=N` 与 `clawsweeper-close-applied item=N` 标记 |
| 53 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/repair/comment-router.ts | `src/repair/comment-router.ts:639-656` | `@clawsweeper stop` 加 `human-review` 并移除 repair-loop 标签 |
| 54 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/docs/target-dispatcher.md | `docs/target-dispatcher.md:150-193` | `human-review` 计入 issue 的 `close_guard_labels` / `source_content_revision` |
| 55 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-github-execution.ts | `src/clawsweeper-github-execution.ts:177-204` | mutation receipt 的 `identity` / `idempotencyIdentity` |
| 56 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/review-record.ts | `src/review-record.ts:23-26`、`:100-120` | typed review record 是 front matter 一行 JSON；读不出则要求 fresh review |
| 57 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-report-document.ts | `src/clawsweeper-report-document.ts:664` | 报告 front matter 写 `close_reason: <token>` |
| 58 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/README.md | `README.md:260-286` | 两条 lane；hot/hourly/daily/weekly cadence；apply 每 15 分钟 |
| 59 | 同上 | `README.md:288-322` | review 是 proposal-only；报告路径；持久评论；PR 评论结构 |
| 60 | 同上 | `README.md:324-353` | apply 只信 typed `review_record`；issue 关闭只留持久 review；40 closes、2 秒延迟 |
| 61 | 同上 | `README.md:375-378` | exact publisher 默认只启用三个 immediate-safe 原因，含 `implemented_on_main` |
| 62 | 同上 | `README.md:399-406` | maintainer 作者例外；OpenClaw 可在 release 前按 current main 关闭 |
| 63 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/docs/implemented-on-main-close-policy.md | `docs/implemented-on-main-close-policy.md:8-56` | 配对关闭政策、maintainer 例外、关系要求、mutation 边界、非事务性 |
| 64 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/docs/scheduler.md | `docs/scheduler.md:614-625` | 各仓库 cron（hot/normal/apply/audit） |
| 65 | 同上 | `docs/scheduler.md:1014-1028` | review cadence（hourly/daily/weekly） |
| 66 | 同上 | `docs/scheduler.md:1134-1186` | apply 每 15 分钟、live 重读、40 个/批、checkpoint |
| 67 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/.github/workflows/clawsweeper-dispatch.yml | `.github/workflows/clawsweeper-dispatch.yml:3-9` | 事件触发类型 |
| 68 | 同上 | `.github/workflows/clawsweeper-dispatch.yml:39-60` | 命令正则含 `stop`；target-dispatch URL 与载荷 |
| 69 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/.github/workflows/review-plan.yml | `.github/workflows/review-plan.yml:69-75` | hot intake `*/5`、normal backfill `9/20` |
| 70 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/.github/workflows/sweep.yml | `.github/workflows/sweep.yml:104-110` | apply cron `3,18,33,48`；comment sync `6,21,36,51` |
| 71 | 同上 | `.github/workflows/sweep.yml:202-204` | exact event review job |
| 72 | 同上 | `.github/workflows/sweep.yml:2020-2022` | exact review publish job |
| 73 | 同上 | `.github/workflows/sweep.yml:3594-3597` | apply-existing job 与 cron 条件 |
| 74 | 同上 | `.github/workflows/sweep.yml:3744-3761` | apply 输入：40、2 秒、reason 过滤 |
| 75 | 同上 | `.github/workflows/sweep.yml:3953`、`:4013` | `pnpm run apply-decisions` 实际调用 |
| 76 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/dashboard/exact-review-queue.ts | `dashboard/exact-review-queue.ts:995`、`:2937`、`:3124` | `ExactReviewQueue`、`/claim`、`/heartbeat` |
| 77 | 同上 | `dashboard/exact-review-queue.ts:385-406` | queue item 的 lease/claim 持久字段 |
| 78 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/dashboard/exact-review-read-model.ts | `dashboard/exact-review-read-model.ts:26-30` | dispatch 6m / publication 15m / execution 130m / grace 20m / retry 30s |
| 79 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-review-item.ts | `src/clawsweeper-review-item.ts:38`、`:112-138`、`:209-210` | review 入口；宿主预取历史/provenance；模型后附加 fixed PR |
| 80 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-review-command-workflow.ts | `src/clawsweeper-review-command-workflow.ts:146` | review command workflow 入口 |
| 81 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-apply-close-decision.ts | `src/clawsweeper-apply-close-decision.ts:23-45` | apply 从 review record 构造 close decision，强 conf high，缺记录则 fresh review |
| 82 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/repository-profiles.ts | `src/repository-profiles.ts:75-93`、`:183-189` | OpenClaw profile 允许 `implemented_on_main`；`isAutoCloseAllowed` |
| 83 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/clawsweeper-apply-report-labels.ts | `src/clawsweeper-apply-report-labels.ts:64-80` | review 标签（priority/impact/intake）由 apply 同步 |
| 84 | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/docs/intake-triage.md | `docs/intake-triage.md:27-28`、`:83-84` | intake 标签是初步标签，完整 review 后移除 |
| 84b | https://github.com/openclaw/clawsweeper/blob/d6179da56748b0a0e791c700b0c7c10e7b6c7a4c/src/apply-close-actions.ts | `src/apply-close-actions.ts:1-38` | apply 可选动作集合；`implemented_on_main` 的 legacy fixed close skip 重选通道 |
| 85 | https://github.com/openclaw/openclaw/issues/197766 | issue 197766 | 主案例；打开/关闭/时间线/评论 |
| 86 | https://github.com/openclaw/openclaw/issues/197766#issuecomment-6825937985 | comment 6825937985 | 逐字 review/关闭评论与 markers |
| 87 | https://github.com/openclaw/openclaw/pull/174696 | PR 174696 | 同仓库 merged fix PR，merge commit 749464ce0a56...；body 仅 `Related: #169118` |
| 88 | https://github.com/openclaw/openclaw/issues/199533 | issue 199533 | 次案例；8m07s 时间线 |
| 89 | https://github.com/openclaw/openclaw/issues/199533#issuecomment-6892141407 | comment 6892141407 | 次案例逐字评论与 markers |
| 90 | https://api.github.com/repos/openclaw/openclaw/issues/197766/timeline | Timeline API | 标签、评论、关闭的 UTC 时间戳 |
| 91 | https://api.github.com/repos/openclaw/openclaw/issues/199533/timeline | Timeline API | 标签、评论、关闭的 UTC 时间戳 |
| 92 | https://api.github.com/search/issues?q=repo%3Aopenclaw%2Fopenclaw+is%3Aissue+is%3Aclosed+%22closing+this+as+already+implemented%22 | Search API | 最近 100 个命中，median open→close 7.7 分钟；样本 25/25 closed by `clawsweeper[bot]` |
