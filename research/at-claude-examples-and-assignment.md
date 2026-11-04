# anthropics/claude-code：@claude 用户请求样例 与 issue 打标后的分配机制调研

调研时间：2026-11-04
数据来源：GitHub REST API（`api.github.com`，无认证，60 req/h）、仓库原文（`contents` API + `Accept: application/vnd.github.raw`）。
`raw.githubusercontent.com` 在本网络环境无法直连（连接超时），全部原文改经 `api.github.com/repos/anthropics/claude-code/contents/<path>` 获取，内容与 raw 一致。

---

## 1. 问题 1：用户在 issue 里 @claude 一般请求什么

### 1.1 触发机制（背景）

`.github/workflows/claude.yml`（50 行）是 @claude 的入口。触发条件（第 3–19 行）：

- `issue_comment.created` 且评论正文包含 `@claude`（`contains(github.event.comment.body, '@claude')`，第 16 行）
- `pull_request_review_comment` / `pull_request_review` 正文包含 `@claude`
- `issues` 事件（`opened`、`assigned`）且 issue 标题或正文包含 `@claude`（第 9、19 行）

触发后运行 `anthropics/claude-code-action@v1`，`--permission-mode auto`（第 48 行）——即 @claude 触发的是一个**通用 Claude Code agent**，可以对 issue 做分析、回复、甚至提交修改，而不是只走 triage 打标流程。

> 搜索口径说明：GitHub Search API 里直接搜 `"@claude"` 会把 `@` 符号丢掉、退化成搜 "claude"，返回 96394 条假阳性（仓库 issue 总数约 10.7 万）。**正确姿势是 `mentions:claude`**（@claude 是真实 GitHub 用户，login=`claude`, id=81847），全仓库命中 **447 个 issue**。下面的例子来自这 447 个中的抽样。

### 1.2 真实例子（抽样）

| issue | URL | 请求类型 | @claude 原文摘录（评论，作者/时间） |
|---|---|---|---|
| #105607 | https://github.com/anthropics/claude-code/issues/105607 | 请求修复（催处理） | `Please fix this, having a lot of issue lately due to this. @claude` — @Indranil-Mondal, 2026-11-02 |
| #102056 | https://github.com/anthropics/claude-code/issues/102056 | 请求实现功能 | `@claude could we do that?`（针对「插件面板隐藏关闭按钮」的功能建议）— @iagopadilha, 2026-10-15 |
| #97842 | https://github.com/anthropics/claude-code/issues/97842 | 给诊断 + 修复方案（让 Claude 修 bug） | `@claude @ozplayground The likely problem is that Claude interpreted "squash the commits" as "reset the branch"... The fix is to build the squash commit only from the existing committed tree...` — @nastylex, 2026-09-28 |
| #97814 | https://github.com/anthropics/claude-code/issues/97814 | 扩展功能设计建议 | `@claude @florentkaltenbach-dev I'd expand this feature around trusted personal infrastructure rather than giving Claude direct access to passwords...` — @nastylex, 2026-09-28 |
| #96043 | https://github.com/anthropics/claude-code/issues/96043 | 询问进展 / 催更 | `any update @claude` — @seangastinov, 2026-10-23 |
| #94481 | https://github.com/anthropics/claude-code/issues/94481 | 请求帮助 / 支持 | `#anthropic @claude, can someone provide some assistance here? This has burned through 2 weekly resets.` — @Smithy060, 2026-09-18 |
| #93287 | https://github.com/anthropics/claude-code/issues/93287 | 催促 / 升级（escalation） | `HI @claude & @bcherny I AM STILL WAITING FOR THIS ISSUE TO BE ADDRESSED!!! PLEASE PAY ATTENTION!!` — @RahulSDeshpande, 2026-09-15 |
| #92345 | https://github.com/anthropics/claude-code/issues/92345 | 根因分析（帮 Claude 定位） | `@byalvaroft @claude @chrislloyd The installation failure is caused by priconfig.xml being unintentionally included in the shipped MSIX package...` — @nastylex, 2026-09-28 |
| #94532 | https://github.com/anthropics/claude-code/issues/94532 | 反驳 triage 标签 / 申诉 | `@claude I don't think this is an invalid report. Here is an MD that claude provided for me on analysis:...` — @pruinsure, 2026-09-17 |
| #65833 | https://github.com/anthropics/claude-code/issues/65833 | 用法 / 回退问题 | `@claude is there way to rollback/disable? There are plenty of keyboards without PgUp/PgDn...` — @Nordsoft91, 2026-06-08 |
| #53437 | https://github.com/anthropics/claude-code/issues/53437 | 请求修复 | `please fix @claude` — @bleuf1sh, 2026-05-10 |
| #89694 | https://github.com/anthropics/claude-code/issues/89694 | 测试 @claude 功能 | `@claude Please analyze this test issue and provide feedback on the GitHub integration.` — @Putpy0, 2026-08-26 |
| #78621 | https://github.com/anthropics/claude-code/issues/78621 | 抱怨 / 情绪宣泄 | `@claude wtf is wrong with your developers?` — @AlqattanDev, 2026-07-17 |
| #12925 | https://github.com/anthropics/claude-code/issues/12925 | 功能请求（正文里举例 @Claude） | 正文：`Cursor recently launched a Linear integration where assigning an issue to @Cursor automatically spins up a cloud agent... Register Claude Code as an assignable agent in Linear workspaces; When assigned or mentioned (@Claude), automatically spin up a cloud session...` |

### 1.3 一类特殊「假 @claude」：GitHub integration 自动上报的坏 issue

抽样中发现 `mentions:claude` 命中的 issue 里混着一类**不是用户主动 @claude** 的：标题为 `[GitHub integration]`，正文每个字段都只是占位符 `@claude`（集成故障导致字段没填上）。例如：

- #105444、#103694：正文形如 `### Screenshot\n\n@claude\n\n### What were you trying to do?\n\n@claude\n\n### What happened instead?\n\n@claude`，带 `Report code: GH-XXXXXX`、`Filed from: GitHub settings for Claude Code on claude.ai`。这类会被 triage 打上 `bug, platform:web, needs-info, github-integration`。

统计 @claude 使用量时要排除这类噪声。

### 1.4 请求类型分布归纳（基于上述抽样，非全量 447 条）

1. **请求修复 / 催处理 / 升级** —— 最常见（#105607、#53437、#93287、#78621、#94481）。用户把 @claude 当「召唤 AI 来解决问题」的入口，很多只是 tag 求关注。
2. **给诊断 / 根因 / 修复方案，让 Claude 动手** —— #97842、#92345。进阶用户直接给 Claude 技术分析再让它修。
3. **请求实现 / 扩展功能** —— #102056、#97814。
4. **询问进展 / 状态** —— #96043。
5. **用法 / 回退 / 工作绕过问题** —— #65833。
6. **反驳 AI 打标结果（申诉）** —— #94532（用户认为被误标 `invalid`，@claude 请它重看）。
7. **测试 @claude 功能本身** —— #89694。
8. **（正文引用）功能请求里举例 @Claude/@Cursor** —— #12925。

一句话概括：@claude 在 issue 里主要被当作「召唤 AI 处理这个 issue 的万能入口」，最多的是「请修复 / 求关注 / 催更」，其次才是给上下文让它实际干活（诊断、修 bug、实现功能），偶尔用来申诉 AI 的误打标。

---

## 2. 问题 2：AI 打标之后，issue 如何分配给人？结论：**只打标、不分配（无自动 assignee）**

### 2.1 明确结论

**`anthropics/claude-code` 仓库本身是「AI 只打标、不分配」。** 打标（triage / dedupe / @claude）之后**没有任何自动 assignee 机制**；指派完全靠人工。仓库内唯一涉及 assignee 的逻辑是「自动关闭脚本会跳过已被人工指派的 issue」，而不是「自动指派」。

### 2.2 证据（文件 / 行号，全部为 `main` 分支原文）

1. **`.claude/commands/triage-issue.md`（75 行）—— 提示词层面明确禁止打标以外的一切**
   - 第 2 行：`allowed-tools: Bash(./scripts/gh.sh:*),Bash(./scripts/edit-issue-labels.sh:*)` —— 只允许这两个只读/打标脚本。
   - 第 8 行：`IMPORTANT: Don't post any comments or messages to the issue. Your only actions are adding or removing labels.` —— 明文「你的唯一动作是加/删标签」。
   - 全文**没有** `assign` / `assignee` / 指派 字样；任务步骤（第 27–65 行）只涉及 label list / issue view / search / `--add-label` / `--remove-label`。

2. **`scripts/edit-issue-labels.sh`（85 行）—— 唯一被授权的写操作只有标签**
   - 第 23–38 行：参数解析只接受 `--add-label` 和 `--remove-label`，遇到其他参数直接报错退出。
   - 第 67、77 行：最终只构造 `gh issue edit <n> --add-label X --remove-label Y`。**没有 `--add-assignee`**。

3. **`scripts/gh.sh`（97 行）—— `gh` 白名单里根本没有 assignee 能力**
   - 第 23–24 行：`ALLOWED_FLAGS=(--comments --state --limit --label)`。
   - 第 30 行：只允许 4 个子命令 `issue view` / `issue list` / `search issues` / `label list`。没有 `issue edit`，没有 assignee 相关命令。

4. **`.github/workflows/claude-issue-triage.yml`（57 行）—— triage workflow 无 assign 步骤**
   - 第 40 行：`prompt: "/triage-issue REPO: ... ISSUE_NUMBER: ... EVENT: ..."`（调用上面的命令）。
   - 第 55 行：`--disallowedTools "WebFetch,WebSearch,Write,Edit,MultiEdit,NotebookEdit"` —— 连写文件/编辑都禁了，更不可能指派。
   - permissions 只有 `contents: read` + `issues: write`（第 21–22 行，issues:write 用于改标签）。

5. **`.github/workflows/claude.yml`（50 行）—— @claude 通用 agent 也不分配**
   - 第 9 行 `issues: types: [opened, assigned]` —— 这里的 `assigned` 是「监听人工指派事件」作为触发，**不是自动指派**（即：有人指派后可以再 @claude）。
   - 第 48 行：`--permission-mode auto`，但没有 assignee 相关的 prompt 或步骤。

6. **`scripts/sweep.ts`（169 行）—— 全仓库唯一读取 assignee 的地方**
   - 第 63 行：`if (issue.assignees?.length > 0) continue;` —— sweep（自动 stale/关闭）会**跳过已被指派的 issue**。这恰恰证明：指派存在，但是**人做的**；自动化只会「读到 assignee 就保护它」，从不会「写入 assignee」。

7. **其余 14 个 workflow 与 9 个 scripts 全部 grep 过 `assign|assignee|owner|responsible`**：命中的只有 `GITHUB_REPOSITORY_OWNER` 环境变量、`context.repo.owner` API 调用、URL 里的 `owner/repo` 字符串——均与指派无关。无 CODEOWNERS 文件（git tree 全量扫描无 `CODEOWNERS` 路径）。

8. **issue 模板（`.github/ISSUE_TEMPLATE/*.yml` 共 6 个）grep `assign|project|board|triage`**：均无 assignee 字段，`config.yml` 只是 `blank_issues_enabled: false` + 外链（Discord / 文档）。

### 2.3 标签体系如何间接辅助人工认领

虽然不自动分配，但打标产出了一套**可路由的标签体系**，让维护者能按标签筛选/认领（`/repos/anthropics/claude-code/labels` 共 90 个标签，实测抓取）：

- **`area:*` 共 40 个**（核心路由标签）：`area:core`、`area:cli`、`area:desktop`、`area:vscode`、`area:web`、`area:mcp`、`area:agents`、`area:cowork`、`area:security`、`area:api`、`area:auth`、`area:bash`、`area:hooks`、`area:skills`、`area:plugins`、`area:ide`、`area:lsp`、`area:networking`、`area:installation`、`area:packaging`、`area:permissions`、`area:providers`、`area:sandbox`、`area:statusline`、`area:tui`、`area:ui`、`area:docs`、`area:cost`、`area:model`、`area:integrations`、`area:browser-extension`、`area:chrome`、`area:claude-code-web`、`area:routines`、`area:self-hosted-environments`、`area:agent-sdk`、`area:agent-view`、`area:a11y`、`area:tools` 等 → 对应不同模块维护者认领。
- **`platform:*` 共 10 个**：android / ios / linux / macos / windows / wsl / web / vscode / intellij / aws-bedrock。
- **`api:*` 3 个**（anthropic / bedrock / vertex）、**`perf:*` 3 个**（cpu / memory / reliability）。
- **优先级**：`high-priority` / `med-priority` / `low-priority` → 决定认领顺序。
- **生命周期**：`needs-repro`、`needs-info`、`has repro`、`reproduced`、`stale`、`autoclose` → 决定是否值得认领/等社区补信息。
- 特殊标签：`oncall`（暗示存在值班认领流程，但仍是人工打标，仓库内无自动 assignee 逻辑）、`claude-code-assisted`（标记 Claude 协助处理过的 issue）、`github-integration`、`external`、`data-loss`、`regression`。

即：**AI 负责「归类 + 路由信号」（bug/enhancement + area:* + platform:* + 优先级），人工负责「按标签认领与指派」**。两段之间没有自动化连接，也没有 CODEOWNERS 式的「标签→负责人」映射。

---

## 3. 公开可借鉴的「打标后自动分配」方案清单

（以下为业界通行模式；Claude Code 仓库本身**没有**采用任何一条。按「机制 / 适用场景 / 可复刻成本」给出。）

| 方案 | 机制 | 适用场景 | 可复刻成本 |
|---|---|---|---|
| **1. `gh issue edit --add-assignee` + `actions/github-script` 自定义 workflow** | 监听 `labeled` 事件，用一张「标签→负责人/团队」映射表，脚本调 GitHub API 写入 assignee；或直接在 CI 里跑 `gh issue edit <n> --add-assignee @user` | 标签体系已稳定（如 area:*）、负责人明确的中小团队 | 低。几十行 YAML + 一张 JSON 映射表即可；无需外部服务 |
| **2. Probot `auto-assign`（GitHub App）** | 在 `.github/auto_assign.yml` 声明规则：按 `addAssignees: author` 或按 label 指定 reviewers/assignees；新 issue/PR 自动指派 | 想要开箱即用、不想自己写 workflow 的团队 | 低。装一个 App + 一份配置文件 |
| **3. `kentaro-m/auto-assign-action` 或 `pozil/auto-assign-issue`** | GitHub Action 版本，同样按标签/作者/随机轮转自动指派，支持 `noReply` 等 | 已有 Actions、想内联进 CI 的团队 | 低。直接引用 action + 配置 |
| **4. CODEOWNERS + 自动 request review** | `.github/CODEOWNERS` 按路径/glob 把文件归到团队；GitHub 对触碰这些文件的 PR **自动请求对应团队 review** | 按「代码路径」而非「issue 标签」路由；适合把 issue 转成 PR 后自动拉人 review | 低。纯仓库内一个文件；但注意 CODEOWNERS 只作用于 PR review，**不会自动指派 issue**，issue 侧仍需另配 |
| **5. GitHub Projects v2 + `project` workflow / 自动 assign** | 打标后自动把 issue 加进对应 Project，用 Projects 的「Item assigned to / Status」等自动化规则做认领流转；或用 `actions/add-to-project` | 团队已经用 Projects 做看板/迭代管理 | 中。需要建 Project + 配 workflow，规则可视化但碎片化 |
| **6. `actions/labeler`（按文件路径自动打 area 标签）+ 方案 1/3 的映射** | labeler 根据改动文件路径自动贴 area 标签，再走「标签→assignee」映射完成指派 | 把「路由」和「指派」解耦、标签不由 AI 而由代码路径决定 | 中。两个 action 串起来 |
| **7. PagerDuty / OpsGenie 值班轮转 + API 挂钩** | issue 进来时按值班表（on-call schedule）查询当班人，自动 assign 给当班人 | 需要「谁值班谁认领」的 SLO/响应时限场景（Claude Code 的 `oncall` 标签暗示这类思路） | 高。需要外部值班系统 + API 集成 |
| **8. 轮转（round-robin）指派 bot** | 维护一个成员列表，新 issue 按计数器轮流 assign；带「跳过已 busy 的人 / 主动认领 / 超时升级」扩展 | 维护者众多、无明确模块划分、只想均衡负载 | 低。几十行脚本，但轮转效果对「懂行的人」匹配度差 |

**给 Claude Code 这类仓库最务实的借鉴**：既然 AI 已经稳定产出 `area:*`（40 个）+ `platform:*`（10 个）+ 优先级标签，缺的只是把「标签 → 负责人/团队」的映射落到机器里。成本最低的补法是方案 1 或 3：在 `labeled` 事件上挂一个 action，维护一张 `{ "area:mcp": "@alice", "area:security": "@bob", "platform:windows": "@carol", ... }` 映射，打标后自动 `--add-assignee`（或至少 `@team` 提及 / 加进对应 Project），即可把「AI 打标」和「人工认领」之间的断点接上。

---

## 4. 局限与没抓到的证据

1. **速率限制**：无认证 GitHub API 只有 60 req/h（core），本次调研用到了 `remaining: 1/60`。因此：
   - `mentions:claude` 命中 447 个 issue，**只抽样检查了其中约 20 个的评论**，请求类型分布是抽样归纳，不是全量统计。
   - 没能对全部 447 个 issue 逐一拉评论做精确分类。
2. **搜索 API 的 `@` 陷阱**：`"@claude"` 关键词搜索会丢 `@`、退化为 "claude"，返回 96394 条假阳性（≈ 仓库全部含 "claude" 的 issue）。已改用 `mentions:claude`（447 条）修正；但 `in:body` / `in:comments` 两个限定符与 `mentions:` 组合时表现异常（两组返回同样的 447 条），**无法用它精确区分「正文 @claude」和「评论 @claude」**，这个区分是靠手动拉评论完成的。
3. **没抓到 Claude 的回复内容**：本次只归纳「用户请求 @claude 什么」，没有系统拉取 claude-code-action 在触发后发的回复/PR，因此「Claude 实际做了什么」不在结论内。
4. **代码搜索不可用**：GitHub code search API 无认证会 401，因此「仓库内是否有 assignee 机制」用的是 git tree 全量路径扫描 + 抓取全部 14 个 workflow、9 个 scripts、`.claude/commands`、issue 模板并 grep `assign/assignee/owner`。覆盖面已经很全，但若机制存在于**仓库之外的第三方 GitHub App / 组织级设置**（例如 anthropics 组织的 App、Projects 自动化），无法从仓库内看到——这一点无法排除。
5. **raw.githubusercontent.com 不通**：本环境直连超时，原文改经 `contents` API 获取（内容一致），但个别大文件有截断处理（如超过 220 行的文件只打印前段，靠 grep 补全）。
6. **`[GitHub integration]` 假 @claude 污染统计**：447 条里混有「集成故障导致字段全是 `@claude` 占位符」的自动上报 issue（见 1.3），真实「用户主动 @claude」的数量小于 447。

---

### 附：证据文件清单（`main` 分支）

- `.claude/commands/triage-issue.md`（75 行）——打标提示词，第 8 行明示「只打标」
- `scripts/edit-issue-labels.sh`（85 行）——仅 `--add-label/--remove-label` → `gh issue edit`
- `scripts/gh.sh`（97 行）——`gh` 白名单，无 assignee
- `.github/workflows/claude.yml`（50 行）——@claude 触发入口（`issues:[opened, assigned]` + `contains(body,'@claude')`）
- `.github/workflows/claude-issue-triage.yml`（57 行）——triage workflow（`/triage-issue`，禁 WebFetch/Write/Edit）
- `.github/workflows/claude-dedupe-issues.yml`（100 行）——去重 workflow（`/dedupe`）
- `scripts/sweep.ts`（169 行）——第 63 行 `if (issue.assignees?.length > 0) continue;`（唯一 assignee 逻辑：跳过已指派）
- 仓库标签列表：90 个标签（40 个 `area:*`、10 个 `platform:*`、优先级/生命周期/`oncall` 等）
