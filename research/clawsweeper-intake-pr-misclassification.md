# ClawSweeper 为什么把 PR 判成 issue

**分析对象**：openclaw/openclaw#197593（`fix(worktrees): avoid E2BIG during isolated Git hydration`，作者 `steipete`，2026-11-12）
**代码基线**：`openclaw/clawsweeper` @ `e7fd669`（2026-11-12）
**结论**：模型没有判错，**intake 规则本身是 issue 形态的，而 PR 也走同一条规则**。

---

## 0. 一句话

`intake` 问的三个问题里，有两个（`reproduction`、`environment`）只有 issue 才回答得了；PR 提交的是补丁而不是复现步骤，于是任何不含“复现步骤”一节的 bug 修复 PR 都会被系统性地判成“缺复现、缺环境”。

---

## 1. 现象

#197593 的 intake 标签在 06:51:37 出现，5 分钟后被同一条流水线撤销：

| 时间 (UTC) | 事件 | 执行者 |
|---|---|---|
| 06:51:37 | 打 `clawsweeper:intake:bug` / `needs-environment` / `needs-repro` | `clawsweeper[bot]` |
| 06:56:25 | **撤销全部三个**，改打 `P2` / `rating: 🦐 gold shrimp` / `status: 👀 ready for maintainer look` | `clawsweeper[bot]` |

撤销是设计行为，不是补偿：`docs/intake-triage.md:27-30` 写明 intake 标签是**预备性**的，“must be removed by the normal completed-review publication”。

但这条清除**不是保证的**：#197427 上它被迟到的 intake 写回覆盖，带着三个 issue 形态标签合并了（§5.1）。

问题在于这 5 分钟里，一个已经带齐 99 个测试、基准表和 CI 链接的 PR，对外显示的是“缺复现、缺环境”。

---

## 2. 数据流

```
PR opened
  └─ runIntakeWorkflow(kind = "pull_request")        src/intake-triage-workflow.ts:118
       ├─ readIntakeSnapshot()  → {title, body, labels, headSha}   :63-113
       ├─ intakeRequest(snapshot) → JSON {repository, number, kind, title, body}  contract.ts:86-112
       ├─ model answers 3 choice questions           contract.ts:11-58
       └─ intakeLabels(result) → clawsweeper:intake:*                contract.ts:143-153
```

关键点：`kind` **进了**模型输入（`contract.ts:96-102`），但三个问题的措辞和标签的生成规则都**没有**用到它。

---

## 3. 根因

### 3.1 三个问题是 issue 词汇

`src/intake-triage-contract.ts:11-58`：

| 问题 | 原文 | PR 语境下 |
|---|---|---|
| `category` | “Classify the author's request” | bug 修复 PR → `bug` ✓ |
| `reproduction` | “Does the submission itself include concrete actions or an executable example **to trigger the claimed failure**? … A failure is claimed but no concrete trigger is supplied.” | PR 里是补丁，不是触发步骤 → `missing` |
| `environment` | “Does the submission identify a **product version** and relevant platform/runtime?” | PR 正文按惯例不写 → `missing` |

对 issue 这是对的：报 bug 就该带复现和环境。
对 PR 这是错位的：**PR 的“证据”是测试和基准，不是触发步骤。**

### 3.2 标签生成不看 kind

`src/intake-triage-contract.ts:143-153`：

```ts
export function intakeLabels(result: IntakeResult): string[] {
  const answers = result.outcome === "classified" ? parseIntakeAnswers(result.answers) : null;
  if (!answers) return [];
  const labels: string[] = [];
  if (answers.category !== "unclear") labels.push(`clawsweeper:intake:${answers.category}`);
  if (answers.category === "bug") {                      // ← 没有 kind 判断
    if (answers.reproduction === "missing") labels.push("clawsweeper:intake:needs-repro");
    if (answers.environment === "missing") labels.push("clawsweeper:intake:needs-environment");
  }
  return labels;
}
```

调用点 `src/intake-triage-workflow.ts:226` 的 `options.kind` 就在手边，但没传进去。

### 3.3 没有 PR 用例的测试覆盖

`test/intake-triage.test.ts` 里 12 处 fixture **全部是 `kind: "issue"`**（第 17、40、80、119、172、211、244 行）。`pull_request` 这条路径从上线起就没有测试断言过。

### 3.4 为什么 #197593 特别刺眼

正文长达 8,731 字符，含“Evidence”一节、A/A/B 三组基准表、CI job 链接、99 个测试结果。但：

- 没有“Steps to reproduce”这种可被判定为 trigger 的段落；
- 版本/平台信息散落在“APFS/native Git/file transport”“macOS ARG_MAX”等句中，不是“版本 + 环境”的结构化陈述。

规则按字面读，`missing` 是正确答案；按意图读，这是一次明确的误判。

---

## 4. 不是模型判错

三条证据：

1. **规则不问 kind**。同样的输入换成 issue，答案完全正确；说明分类器执行了给定规则。
2. **撤销由另一套逻辑完成**。5 分钟后全量评审读完 diff，给出 `status: 👀 ready for maintainer look`——两套判断并存本身就是设计（`docs/intake-triage.md:64-71`），但这也说明 intake 阶段没有 diff。
3. **包里有 kind 却没用**。`IntakePacket.kind` 存在于 `contract.ts:65`，只在选 API 端点和校验 head sha 时使用（`workflow.ts:71,92`），从不进入标签决策。

所以这是**规则设计缺陷**，不是模型能力问题。换更强的模型不会改变结果。

---

## 5. 影响面与严重度

**受影响**：所有 `category=bug` 且正文没有结构化复现步骤的 PR——即绝大多数 bug 修复 PR。维护者自建的 PR 同样中招（#197593 就是）。

**持续时长**：标签存活到全量评审发布为止。本例 5 分钟；队列拥塞时会更久（`docs/limits.md` 的 hot-intake 限流意味着等待可达小时级）。**并且不保证被清除——见 §5.1。**

**实际危害**：
- 对外可见的假信号。读者会以为 PR 缺证据，而它其实附了完整基准。
- 与全量评审的 `triage: needs-real-behavior-proof`（真正管“证据”的标签）语义重叠且取向相反：一个有证据的 PR 会被 intake 说缺复现，又被全量评审说无需证据（维护者 PR 豁免）。
- 不影响合并。标签不参与任何门禁（`docs/intake-triage.md:27-30`：标签“never set priority, impact, reproduction proof, … readiness”）。

**但要如实说**：维护者可以在文档意义上一句话驳回——“标签是 preliminary 且会被清除，这是已知设计”。把它当 bug 还是当 trade-off，取决于他们是否愿意为 PR 付一次额外的规则分支。

---

## 5.1 第二个样本：#197427 —— 清理被后到的写回覆盖

openclaw/openclaw#197427（作者 `vincentkoc`，`MEMBER`，2026-11-12 00:35 开、02:41 合并）跑了 **4 轮** intake，前 3 轮都被清掉，第 4 轮**活到了合并之后**：

| 轮次 | 打标签 | 清理 | 存活 |
|---|---|---|---|
| 1 | 00:50:05 | 00:54:31（全量评审发布） | 4m26s |
| 2 | 01:28:12 | 01:33:18（re-review 发布） | 5m06s |
| 3 | 02:24:10 | 02:29:19（re-review 发布） | 5m09s |
| 4 | **02:30:45** | **无** | **至今** |

第 4 轮距离第 3 轮的清理只有 **1 分 26 秒**，距合并 10 分 24 秒。这个 PR 现在的标签是：

```
agents  size: M  proof: sufficient  P2
rating: 🐚 platinum hermit
status: 👀 ready for maintainer look
clawsweeper:intake:bug
clawsweeper:intake:needs-environment
clawsweeper:intake:needs-repro      ← 已合并，且评审说 proof: sufficient
```

**守卫为什么没拦住**：`intake-triage-workflow.ts:228-232` 的 `assertCurrent()` 校验的是“自我读取快照以来条目未发生变化”，快照里包含 labels。它能挡住“我读的时候没有、现在有了”的变化，但挡不住**“我读的时候已经被清理干净了，所以我的快照是干净的”**——当 intake 的读取发生在清理之后，写入时快照当然没变，守卫放行，于是把评审刚删掉的标签又贴回来。

真正的缺口是：**守卫没有“这个 head 的评审已经完成过”这一事实**。`EXACT_REVIEW_SOURCE_HEAD_SHA` 和 lease/generation 都在 env 里，但没有一个“已发布评审的 head 摘要”用于拒绝迟到的 intake 写入。

候选修法（都不在本次提交范围内）：
- intake 发布前比对“最近一次已完成评审的 head”，相同则拒绝写入；
- 或者在评审发布的标签批次里，把 intake 标签的删除放到批次的最后并对并发写入加短租约；
- 或者最简单：item 进入 merged/closed 时无条件清除 `clawsweeper:intake:*`。

这一条比 §3 的“规则错位”更硬：它是**状态机竞态**，有确定的时间戳证据，不依赖对 rubric 意图的解读。


**另一个悬崖**：`INTAKE_MAX_INPUT_BYTES = 12_000`（`contract.ts:6`）。#197593 的包是 8,936 字节；正文再长 34% 就会触发 `Intake packet exceeds byte budget` 并整段放弃分类。越是写得详细的 PR，越容易既不分类、也不打标签——与“详细更好”的直觉相反。

---

## 6. 三种修复选项

### A. 标签门控（最小改动）

```ts
export function intakeLabels(result: IntakeResult, kind: "issue" | "pull_request" = "issue"): string[]
...
if (answers.category === "bug" && kind === "issue") { ... }
```

调用点补 `options.kind`。PR 仍保留 `clawsweeper:intake:bug`，不再产出 issue 形态的两个缺证标签。
**代价**：一个条件分支 + 若干测试；行为面对 PR 收窄。
**风险**：如果维护者确实想在 PR 上看到“作者没给复现”，这就把信号删了——不过全量评审的 `triage: needs-real-behavior-proof` 已经覆盖该语义。

### B. 问题措辞按 kind 分支

`reproduction` 对 PR 改问：“提交本身是否包含证明改动被执行过的证据（测试、基准、日志）？”
**代价**：要同时改两个 adapter（`intake-triage-api.ts`、`intake-triage-decisions.ts`）的 questions 构造与 schema，改动面大；`needs-repro` 这个标签名对 PR 也不再贴切。

### C. PR 走独立 rubric

最干净，也最贵：新增一套 PR 问题和标签族，等于重做 intake 的一半。

**若要提，A 是唯一符合“小而可审”的选项。**

---

## 7. 若要提交，需要跨过的门槛

`CONTRIBUTING.md` 明确要求：涉及 automation / workflow 的改动**先开 issue 或问维护者**。因此直接提 PR 不合规。

即使提 PR，还要满足：

- Node ≥ 24（`package.json` engines），本机是 22.22.0，跑不了 `pnpm run build`；
- `changelog.d/<slug>.md` 片段（面向用户可见的改动）；
- real-behavior proof contract + 最终整分支 Codex review（`AGENTS.md`，CONTRIBUTING 引用）；
- `pnpm run check`（typecheck / lint / guard / import-cycle / dead-export）。

也就是说，一份未被本地验证的补丁大概率会被以“缺行为证明”关掉——这正是它自己对社区 PR 做的事。

---

## 8. 局限

- 无法证明维护者认为这是缺陷。文档层面它自洽（preliminary 标签 + 全量评审清除）。
- 样本 n=2（#197593 与 #197427）+ 代码阅读，没有统计全仓有多少 PR 收到过这三联标签、多少条在合并后仍然残留。
- 撤销原因可能不止“全量评审发布”，也可能是模型重跑；timeline 只能看到先后，看不到内部触发。
- 代码基线是 2026-11-12 的 `e7fd669`，intake 规则可能已在其后变更。
