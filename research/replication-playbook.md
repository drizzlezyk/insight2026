# 复刻 Claude Code 社区自动化：可执行 Playbook

> 来源：对 `anthropics/claude-code` 主分支（`main`，抓取日 2026-11-04）的**一手原文逐行深挖**。
> 所有行号以抓取到的原始文件为准。抓取方式：GitHub raw 原文 + GitHub API 目录列表，全部 17 个目标文件均成功（**无 404**），另补抓了 4 个未列出的关联 workflow。
>
> 定位：这不是概览，而是「拿到文件、看懂约束、照抄/改造」的工程手册。

---

## 0. 系统总览（数据流）

```
issue opened / comment created ──► claude-issue-triage.yml ──► Claude Code 执行 /triage-issue
                                      │  只允许 gh.sh(读) + edit-issue-labels.sh(写标签)，从不评论
issue opened / workflow_dispatch ──► claude-dedupe-issues.yml ──► /dedupe
                                      │  5 个并行搜索 agent → 过滤 agent → comment-on-duplicates.sh(≤3 候选)
labeled 事件 ──► issue-lifecycle-comment.yml ──► lifecycle-comment.ts 贴 nudge 评论
cron 0 10,22 * * * ──► sweep.yml ──► sweep.ts 打 stale / 关到期标签
cron 0 9 * * * ──► auto-close-duplicates.yml ──► auto-close-duplicates.ts 3 天后关重复
PR / push main ──► workflow-hardening.yml ──► check_workflow_hardening.py 门禁
```

核心设计原则：**AI 只做「读 + 打标签 / 评论候选」，不直接持笔**。所有写操作都收敛到受白名单约束的 bash/TS 脚本里，脚本再对参数做二次校验。AI 的权限收口分五层（见 §5）。

---

## 1. 复用资产清单（哪些文件可直接抄）

| 文件 | 角色 | 可复刻性 |
|---|---|---|
| `scripts/gh.sh` (97 行) | `gh` CLI 白名单包装器 | **直接抄**（纯 bash+gh，无需改动，仓库从 env 读） |
| `scripts/edit-issue-labels.sh` (85 行) | 增删标签（自动与仓库真实标签求交集） | **直接抄**（bash+jq+gh，标签集自适应） |
| `scripts/comment-on-duplicates.sh` (96 行) | 贴去重候选评论 | 直接抄，**改 L11 硬编码 `REPO="anthropics/claude-code"`** |
| `scripts/issue-lifecycle.ts` (39 行) | 生命周期唯一真源（阈值+nudge 文案） | **直接抄**（改标签名/文案即可） |
| `scripts/sweep.ts` (169 行) | 打 stale、关闭到期标签 | 直接抄，**改 L7 `NEW_ISSUE` URL** |
| `scripts/lifecycle-comment.ts` (54 行) | 标签事件贴 nudge 评论 | **直接抄** |
| `scripts/auto-close-duplicates.ts` (278 行) | 3 天后关重复 issue | 直接抄，**改 L108-109 owner/repo 默认值** |
| `scripts/backfill-duplicate-comments.ts` (213 行) | 一次性回填：给历史 issue 补触发去重 workflow | 直接抄，**改 L89-93 owner/repo/MAX_ISSUE_NUMBER**；默认 DRY_RUN=true |
| `.github/workflows/sweep.yml` | 调度 sweep.ts | **直接抄** |
| `.github/workflows/issue-lifecycle-comment.yml` | labeled 事件 → lifecycle-comment.ts | **直接抄** |
| `.github/workflows/auto-close-duplicates.yml` | cron 调度 auto-close-duplicates.ts | **直接抄** |
| `.github/workflows/workflow-hardening.yml` | CI 门禁 | **直接抄** |
| `.github/scripts/check_workflow_hardening.py` (340 行) | 硬化规则引擎 | **直接抄**（如你的 runner/action 名不同，改 L14/L18 常量） |
| `triage-issue.md` / `dedupe.md` 的**逻辑与措辞** | AI 提示词本体 | 照抄逻辑，改「产品信号词 + 标签枚举」（见 §2/§3） |
| `.github/egress-firewall.yaml` | 网络白名单 | 概念可抄；**依赖 egress-firewall runner**（见 §7） |
| `.claude/commands/*.md` 的 `allowed-tools` 机制 | 提示词级工具白名单 | **Claude Code 专属**（见 §7） |
| `.github/workflows/claude-issue-triage.yml` / `claude-dedupe-issues.yml` / `claude.yml` | LLM 调度 | 结构可抄，**需替换 LLM runner**（见 §7） |

未在任务清单但同样存在且被用到：`auto-close-duplicates.yml`、`issue-lifecycle-comment.yml`、`claude.yml`（@claude 提及响应）、`backfill-duplicate-comments.yml`、`issue-opened-dispatch.yml`、`lock-closed-issues.yml`、`log-issue-events.yml`、`non-write-users-check.yml`、`remove-autoclose-label.yml`、`mod-tests.yml`。

---

## 2. 分诊提示词解剖（`.claude/commands/triage-issue.md`，75 行）

### 2.1 工具白名单（L2）
```
allowed-tools: Bash(./scripts/gh.sh:*),Bash(./scripts/edit-issue-labels.sh:*)
```
只暴露两个脚本。L15-23 再进一步限定 `gh.sh` 可用子命令：`label list`、`issue view [--comments]`、`issue list --state open --limit 20`、`search issues "query" [--limit 10]`。`edit-issue-labels.sh` 只接受 `--add-label/--remove-label`。

### 2.2 明确禁令
- **L8**（最强约束）：`IMPORTANT: Don't post any comments or messages to the issue. Your only actions are adding or removing labels.`
- L69 再次强调 `DO NOT post any comments`。
- L27：只能使用 `label list` 返回的标签，**永不发明新标签**。
- L71：生命周期标签只给 bug，不给 question/enhancement。
- L72：拿不准就不打（"false positives are worse than missing labels"）。

### 2.3 分类标签枚举（L73）
新 issue **必须打且只打一个**：`bug` / `enhancement` / `question` / `invalid` / `duplicate`。技术领域/平台标签来自 `label list`（不硬编码在提示词里）。

### 2.4 判「是否关于 Claude Code」的信号词（L33-36）
命中**任一**信号即判定为 Claude Code issue：
`Claude Code Version` 字段、`claude --version` 输出、`claude` CLI 命令、终端会话、VS Code/JetBrains 扩展、`CLAUDE.md` 文件、`.claude/` 目录、MCP servers、Cowork、Remote Control、web UI `claude.ai/code`。

仅当**零命中**时，再判断是否别的 Anthropic 产品（claude.ai chat、Claude Desktop/Mobile 应用、原始 Anthropic API/SDK、与 CLI 无关的账号计费）是「投诉主体」（不是顺带提及）→ 打 `invalid` 并停止；模糊则继续、不打 invalid。
**L36**：body 文本是权威，表单下拉（如 Platform）常被选错，body 与下拉矛盾时信 body。

### 2.5 needs-repro / needs-info 规则（L43-51）
- `needs-repro`（**仅 bug**，7 天）：无清晰复现步骤。已给错误信息/日志/文件路径/做了什么就不打；叙述性描述也算；模型行为类 issue（"Claude 该做 Y 却做 X"）给示例与模式即可，不要求传统复现步骤。
- `needs-info`（**仅 bug**，7 天）：缺社区侧信息（错误、版本、环境、后续问题答案）。已给版本+环境+错误就不打；"需要工程调查"≠ needs-info。
- L50：打上这些标签后，超时无响应自动关闭，目标是避免 issue 悬置。

### 2.6 生命周期标签判据（评论事件，L56-65）
- 新的人类评论 → 移除 `stale`/`autoclose`（L59-60）。
- `needs-repro`/`needs-info` 的信息已补 → 移除对应标签（L61-62）。
- `+1`/`me too`/`same here`/emoji **不算**补充信息（L64）。
- 评论事件**不改**类别标签（bug/enhancement 等，L65）。

### 2.7 脚本层的二次白名单（AI 越权也写不进）
`gh.sh`：L23-24 只允许 flag `--comments --state --limit --label`；L29-36 只允许 4 个子命令；**L76-82 禁止 `repo:`/`org:`/`user:` 限定符**（防跨仓库逃逸）；L84-89 `issue view` 只接受单个数字；L14 固定 `GH_HOST=github.com`；L16-21 强制 `GH_REPO` 为 `owner/repo`。

`edit-issue-labels.sh`：L13 从 `GITHUB_EVENT_PATH` 读 issue 号（**绑定触发事件，防串号**，fallback 到 workflow_dispatch inputs）；**L45-64 与仓库真实标签求交集**——AI 编造的标签会被静默丢弃；L67-77 调 `gh issue edit ISSUE --add-label/--remove-label`。

---

## 3. 去重多 agent 解剖（`.claude/commands/dedupe.md`，27 行 + 两个脚本）

### 3.1 五步流程（L6-17）
1. **L10**：先派一个 agent 判断是否该去重：(a) issue 已关闭、(b) 无需去重（无具体解决方案的泛产品反馈 / 正面反馈）、(c) 已贴过去重评论 —— 任一成立则不继续。
2. **L11**：一个 agent 读 issue，返回摘要。
3. **L12**：**启动 5 个并行 agent** 搜重复，用「多样化关键词与搜索方式」，基于第 2 步的摘要。
4. **L13**：把结果喂给**过滤 agent** 剔除误报；无剩余则不继续。
5. **L14-17**：`./scripts/comment-on-duplicates.sh --potential-duplicates <dup1> <dup2> <dup3>`。

### 3.2 关于「5 个 agent 各自策略」的诚实结论
**原文没有硬编码 5 个 agent 各自的关键词或搜索策略**。L12 只有一句 "using diverse keywords and search approaches"——多样性是**委托指令**，具体策略由各 agent 自拟（现实做法是各取一个切面：错误信息原文、功能/命令名、版本号、平台、症状短语）。所有搜索都经 `gh.sh search issues`（限本仓库、禁 `repo:/org:/user:`）。
同理，**过滤 agent 的误报剔除标准也没有枚举**（L13 只有 "likely not actually duplicates"），也是委托判断。
> 复刻启示：不要试图复刻一份「官方关键词表」——不存在。要复刻的是「并行 N 路 + 独立过滤 agent + 硬性上限 3」这个**结构**。

### 3.3 上限与评论
- 最多评论 **3** 个候选：L6 "up to 3"；`comment-on-duplicates.sh` L46-49 硬校验 1..3。
- `comment-on-duplicates.sh`：L15 base issue 从 event payload 读；L26-38 只接受 `--potential-duplicates`；L59-70 校验 base 与每个 dup 真实存在；L72-90 评论体要点：
  - "Found N possible duplicate issues:" + 链接列表
  - **L87** "This issue will be automatically closed as a duplicate in **3 days**."
  - **L88** "If your issue is a duplicate, please close it and **👍 the existing issue** instead"
  - **L89** "To prevent auto-closure, **add a comment or 👎 this comment**"
  - 生成署名（🤖 Generated with Claude Code）
- L11 `REPO` 硬编码，复刻时必改。

### 3.4 自动关闭：时限与 👍/👎 干预（`scripts/auto-close-duplicates.ts`）
- **时限 3 天**：L112-113 `threeDaysAgo = now - 3d`；评论文案 L87 同步写 3 天。
- 候选筛选链（L149-249）：issue open 且创建>3 天 → 有 bot 的 "Found...possible duplicate" 评论 → 该评论>3 天 → **该评论之后无新评论** → **作者未对该评论 👎** → 从评论提取 dup 号。
- **两个干预门**：
  1. 重复评论之后有任何新评论 → 跳过（L203-215）。
  2. 作者对重复评论点了 👎（reaction `-1` 且 `user.id == issue.user.id`）→ 跳过（L228-241）。
- 关闭动作（L73-95）：`PATCH state=closed, state_reason=duplicate, labels=["duplicate"]`，再贴一条关闭评论。
- **注意**：👍 在去重流程里**不是门**——👍 是对「规范 issue」的用户引导（自己关掉重复 issue 并给原 issue 点赞）；👍≥10 是**生命周期** stale 的门（见 §4）。

### 3.5 调度与回填
- `claude-dedupe-issues.yml`：`issues[opened]` + `workflow_dispatch(issue_number)`；之后有 Statsig 埋点步骤（L50-99，失败不阻断）。
- `auto-close-duplicates.yml`：`cron "0 9 * * *"`（每日 9:00 UTC）。
- `backfill-duplicate-comments.ts`：一次性迁移，对 `#1..#4050`（L92 默认 `MAX_ISSUE_NUMBER=4050`）中缺去重评论的历史 issue 逐个 `workflow_dispatch` 触发去重 workflow；默认 DRY_RUN=true（L91）。

---

## 4. 生命周期唯一真源（`scripts/issue-lifecycle.ts`）

### 4.1 阈值表（L3-34，`lifecycle` 数组）

| label | days | reason | 到期行为 |
|---|---|---|---|
| `invalid` | **3** | 不像是 Claude Code 的问题 | 3 天无响应 → 关闭 |
| `needs-repro` | **7** | 仍缺复现步骤 | 7 天 → 关闭 |
| `needs-info` | **7** | 仍缺信息 | 7 天 → 关闭 |
| `stale` | **14** | 长期不活跃 | 14 天 → 关闭 |
| `autoclose` | **14** | 长期不活跃 | 14 天 → 关闭 |

- **L38**：`STALE_UPVOTE_THRESHOLD = 10`（issue 自身 👍 数达到 10 即豁免）。
- 每条含 `nudge` 文案（贴给作者的提醒话术）。

### 4.2 sweep.ts 执行逻辑（cron 每日两次）
`markStale`（L45-90）：遍历 open issues（`sort=updated&direction=asc`）；跳过 PR/locked/**有 assignee**（L61-63）；`updated_at` 落在 14 天截止之后 → 提前返回（L65-66）；已 stale/autoclose → 跳过（L68-71）；**issue 👍 ≥ 10 → 跳过**（L73-74）；否则打 `stale`（L82）。

`closeExpired`（L92-154）：对 `lifecycle` 数组每个 label 按各自 days 算截止；拉带该 label 的 open issues（updated 升序）；跳过 PR/locked（L107-108）；**issue 👍 ≥ 10 → 跳过**（L110-111）；从 `events` 找该 label 的 labeled 时间，不足 days → 跳过（L117-122）；**安全网：label 之后有任何非 Bot 评论 → 跳过关闭**（L127-138）；否则贴 CLOSE_MESSAGE + `PATCH state=closed, state_reason=not_planned`（L144-145）。

### 4.3 豁免条件汇总
- 打 stale 前豁免：是 PR；locked；有 assignee（仅 stale 阶段有这条，closeExpired 阶段没有）；已 stale/autoclose；👍≥10；14 天内有过更新。
- 到期关闭前豁免：是 PR；locked；👍≥10；label 打上不满 N 天；label 之后有人评论。

### 4.4 配套
- `issue-lifecycle-comment.yml`：`issues[labeled]` 触发 `lifecycle-comment.ts`，贴 nudge（"This issue will be closed automatically if there's no activity within N days"，L25）。
- 人类评论 → 分诊 workflow 移除 `stale`/`autoclose`/`needs-*`（triage-issue.md L56-64）——这是人工干预的闭环。
- `sweep.yml`：`cron "0 10,22 * * *"`，`concurrency: daily-issue-sweep`，`runs-on: ubuntu-latest`（**不是** firewall runner，因为不调 Claude）。

---

## 5. 安全硬化清单

### 5.1 五层防护（纵深防御）
1. **提示词层**：`allowed-tools` 只暴露 2 个脚本。
2. **脚本层**：`gh.sh` 子命令/flag 白名单 + 禁跨仓库限定符；`edit-issue-labels.sh` 与真实标签求交集；`comment-on-duplicates.sh` 上限 3 + 存在性校验。
3. **workflow 层**：最小权限 `contents: read` + `issues: write` + `id-token: write`；`--permission-mode auto`；`--disallowedTools`。
4. **网络层**：egress-firewall runner + `.github/egress-firewall.yaml` allowlist。
5. **身份层**：OIDC（`id-token: write`）→ WIF 换**短期** Claude API token，仓库里无静态 API key。

### 5.2 workflow-hardening 强制检查（`check_workflow_hardening.py`，340 行）
判定「调 Claude 的 job」（L97-106）：job 内出现 marker `anthropic_federation_rule_id`（L17），或某 step `uses` 官方 action（L18：`anthropics/claude-code-action` / `anthropics/claude-code-base-action`），或本地 action 带 `claude_args` 输入。

每档检查（`check_job` L231-274）：
1. **runner**：必须 `runs-on: ubuntu-24.04-firewall`（常量 L14），否则报错（L243-253）。豁免表 `EXEMPT_FROM_FIREWALL_RUNNER`（L30，当前为空）。
2. **permission mode**（L109-189）：每个 claude-code-action step 必须 `--permission-mode auto`；**禁止** `--dangerously-skip-permissions`（L125-129）；禁止任何非 auto 的 mode（L142-152）；禁止 settings 里出现 `defaultMode`（L174-175，job 级 L260-265）；**模型必须 ≥ `claude-opus-4-6`**（`AUTO_MODE_MIN_VERSION=(4,6)` L22；`predates_auto_mode` L200-209；`haiku` 一律判旧 L203-204）。模型来源可来自 step `model` 输入、`ANTHROPIC_MODEL`、`--model`/`--fallback-model`、settings。
3. **豁免**：`EXEMPT_FROM_AUTO_MODE`（L31，当前为空）里的 job **不得设置任何 permission mode**（L134-139）。
4. **egress policy**（`check_policy` L277-309）：`.github/egress-firewall.yaml` 必须存在、`mode: enforce`、`allow` 非空、host 不含 `*`。

门禁只在「至少有一个调 Claude 的 job」时才检查 policy（L325-326）。`workflow-hardening.yml` 在 PR + push main 触发。

### 5.3 egress-firewall 白名单完整主机列表（`.github/egress-firewall.yaml` L5-27）

| host | 用途 |
|---|---|
| `api.anthropic.com` | Claude API（模型请求、WIF 换短期 token、取 Claude GitHub App token） |
| `api.github.com` | GitHub API（Claude Code action + gh 脚本） |
| `claude.ai` | Claude Code 安装脚本 |
| `downloads.claude.ai` | Claude Code 二进制 |
| `release-assets.githubusercontent.com` | Bun 下载（oven-sh/setup-bun） |
| `registry.npmjs.org` | action 的 npm 依赖 |
| `azure.archive.ubuntu.com` | apt（bubblewrap/socat，非写权限用户场景） |
| `archive.ubuntu.com` | apt |
| `security.ubuntu.com` | apt |
| `events.statsigapi.net` | Statsig 埋点（dedupe workflow） |

注意：`github.com` 本身不在列表（GitHub 防火墙默认放行一部分）；无通配符、每条注释用途（L1-3 规定「只加需要的、写全名不带 `*`、说明用途」）。

### 5.4 CLAUDE.md 的硬化段（根 `CLAUDE.md` L5-40）
三点保护（firewall runner / allowlist / auto permission mode，L10-24）+ `claude.yml` 回答 @claude 提及（L26-28）+ workflow-hardening 门禁与豁免表（L30-37）+ 「permissions 最小化、别打印 token」（L39-40）。

### 5.5 关键参数实抄
- 分诊/去重 workflow 的 `claude_args`（triage L53-56、dedupe L48）：
  `--permission-mode auto --disallowedTools "WebFetch,WebSearch,Write,Edit,MultiEdit,NotebookEdit" --model claude-sonnet-5-5`
- `CLAUDE_CODE_SCRIPT_CAPS`：triage 是 `{"edit-issue-labels.sh":2}`（L36），dedupe 是 `{"comment-on-duplicates.sh":1}`（L33）——claude-code-action 的脚本能力授予项。
- `allowed_non_write_users: "*"`（triage L39、dedupe L36）：允许**非写权限用户**触发时也运行（社区 issue 的常态；对应 egress 注释里「非写权限用户触发时 action 会装 bubblewrap/socat 沙箱」）。

---

## 6. 最小可复刻路线图（分阶段）

### Phase 0 — 标签规范 + issue 模板（无 AI，纯 GitHub）
- **改动文件**：`.github/ISSUE_TEMPLATE/*.yml`（bug/feature 表单，强制 `version`、`environment` 字段，让「信号词」从自由文本变结构化）；仓库标签集：`bug / enhancement / question / invalid / duplicate` + `needs-repro / needs-info / stale / autoclose`。
- **依赖**：无。
- **风险**：低。关键是标签语义统一，后续自动化全靠它。

### Phase 1 — 确定性生命周期（脚本/工作流，仍无 LLM）
- **改动文件**：抄 `issue-lifecycle.ts`、`sweep.ts`、`lifecycle-comment.ts` + `sweep.yml`、`issue-lifecycle-comment.yml`（改 `NEW_ISSUE` URL、标签名、nudge 文案）。
- **依赖**：Node/Bun 运行时、`GITHUB_TOKEN`、Phase 0 的标签集。
- **风险**：**误关真实 issue**。对策：先 `--dry-run` 跑一遍看输出；`STALE_UPVOTE_THRESHOLD` 先调低（如 3）；先把 `needs-*` 的自动关闭关掉、只开 stale。

### Phase 2 — AI 分诊（上 LLM）
- **改动文件**：抄 `gh.sh`、`edit-issue-labels.sh`；把 `triage-issue.md` 的「信号词段（L33-36）」改成**你的产品**信号词与「非本产品」清单；抄 `claude-issue-triage.yml` 并替换 LLM runner。
- **依赖**：Claude Code CLI/action **或** 任意 LLM + 自建 runner（等价物：显式工具定义 `list_labels / get_issue / set_labels`，无文件系统/网络工具）；API key 或 WIF。
- **风险**：AI 幻觉标签 → 标签枚举锁死 + `edit-issue-labels.sh` 交集过滤 + 「只打标签、不评论」三保险；超时/成本 → `timeout-minutes:10` + `concurrency` per-issue `cancel-in-progress`；对非写权限用户的 prompt 注入 → 最小权限 + 沙箱。

### Phase 3 — AI 去重（多 agent）
- **改动文件**：抄 `comment-on-duplicates.sh`（改 REPO）、`dedupe.md`（改产品语境）、`claude-dedupe-issues.yml`、`auto-close-duplicates.ts` + `auto-close-duplicates.yml`。
- **依赖**：支持并行/子 agent 的 LLM runner（否则自己并发调 `search issues` 再单独调一次 LLM 过滤）。
- **风险**：误报重复 → 过滤 agent + 上限 3 + 3 天缓冲 + 👎/评论否决；评论轰炸 → 每 issue 只一条评论（脚本幂等校验 + 已贴过则不贴）。

### Phase 4 — 安全硬化（CI 门禁）
- **改动文件**：抄 `check_workflow_hardening.py`、`workflow-hardening.yml`；有 egress runner 则抄 `egress-firewall.yaml`，否则**以 `disallowedTools` + 最小 `permissions` + 无静态 key 替代**网络白名单。
- **依赖**：PyYAML（或 yq）、（可选）egress-firewall runner。
- **风险**：检查误报阻塞 PR → 用 `EXEMPT_FROM_FIREWALL_RUNNER` / `EXEMPT_FROM_AUTO_MODE` 豁免表；过度收紧导致 workflow 网络失败 → 按报错逐个加 host。

---

## 7. 不可直接复刻的边界（Claude Code 专属 vs 通用）

### 7.1 明确依赖 Claude / Anthropic 专属能力的部分
| 组件 | 专属点 | 通用替代 |
|---|---|---|
| `.claude/commands/*.md` 的 `allowed-tools` 前置元数据 | Claude Code slash command 的提示词级权限白名单 | 任意 agent 框架里**显式定义工具集**，别给文件系统/网络工具 |
| `anthropics/claude-code-action@v1` + `claude` CLI | 调度 + 沙箱执行 + 子 agent（Task）能力 | Claude Agent SDK / LangGraph / 自建 agent loop；子 agent 换成并发工具调用 |
| `--permission-mode auto` / `--disallowedTools` | Claude Code 的安全审查回退机制 | 等价物：只暴露 N 个工具、无 Write/Edit/WebFetch，天然无需「审查回退」 |
| WIF 四变量 `anthropic_federation_rule_id / organization / service_account / workspace` | Anthropic 的 OIDC→短期 token 联邦 | 通用：`id-token: write` + 各家 OIDC 登录（azure/login、gcp 的 workload identity 等）或短期 PAT |
| `runs-on: ubuntu-24.04-firewall` egress runner | GitHub 托管的出站过滤 runner（非所有仓库可用） | 自托管 runner 配网络策略；或退化为 `disallowedTools` + 最小权限 |
| 模型 `claude-opus-4-6` 门槛 | Claude Code auto 模式的版本要求 | 你的 runner 若不用该机制，此门槛不存在 |

### 7.2 完全可移植（与 LLM 品牌无关）
- 全部 bash/TS 脚本（`gh.sh`、`edit-issue-labels.sh`、`comment-on-duplicates.sh`、`issue-lifecycle.ts`、`sweep.ts`、`lifecycle-comment.ts`、`auto-close-duplicates.ts`、`backfill-duplicate-comments.ts`）——只用 `gh` CLI / GitHub REST API，零 LLM 依赖。
- `check_workflow_hardening.py` 与 `workflow-hardening.yml`——检查的是**你自己的** workflow YAML。
- 两个提示词的**决策逻辑**（信号词判属、标签枚举、5 并行+过滤、3 天上限+干预门）——任何模型都能执行。

### 7.3 复刻结论
这套系统的精髓不在 Claude Code，而在：**（1）提示词把「权力」写死成禁令与枚举；（2）脚本把「写」收敛到带二次校验的白名单；（3）确定性 cron 脚本兜底生命周期，LLM 只做标注；（4）CI 强制校验每一条安全约束，防止回退。** 用「GitHub Actions + 任意 LLM/Claude Agent SDK + 这些 bash/TS 脚本」即可复刻 80% 的实效；剩下 20% 是 Anthropic 特有的 runner/action/WIF 便利设施，按 §7.1 的映射替换即可。
