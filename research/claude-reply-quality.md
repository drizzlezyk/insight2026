# @claude 之后，Claude 到底有没有正常回答？

研究时间：2026-11-04。仓库：`anthropics/claude-code`。

## 1. 方法与样本

**样本**：20 个含 `@claude` 提及的 issue（`mentions:claude` 搜索命中 447 个中的 20 个）。

- 5 个已知典型：#105607（求修复）、#102056（求实现功能）、#97842（给方案让 AI 修 bug）、#96043（催更）、#94532（申诉误标）。
- 10 个补充（覆盖测试帖、情绪帖、bug、feature、关于 bot 本身的 meta 请求、0 评论帖）：#89694、#76596、#95756、#93287、#97854、#66433、#89128、#64632、#88094、#99474。
- 5 个大线程交叉验证（高评论量，最可能藏有实质回复）：#62503、#71542、#63060、#74649、#84352。

**数据**：无认证 GitHub API（`api.github.com`，core 限额 60/h，中途等待一次重置，共约 50 次请求）。每个 issue 取 `issues/<n>`（正文）+ `issues/<n>/comments?per_page=100`（全部评论）；对已知 5 例另取 `issues/<n>/timeline`（标签/关闭事件）；另取 `.github/workflows/` 下 `claude.yml`、`claude-issue-triage.yml`、`claude-dedupe-issues.yml` 及 `claude.yml` 的 workflow 运行列表。

**如何识别"哪条是 Claude 的回复"**：

- 机器人判定：评论作者 `user.type === "Bot"`（样本中唯一出现的是 `github-actions[bot]`）。注意用户名含 "bot" 的普通用户（如 `therobotprogrammer`、`action-gate`）是 `type: User` 的人类，不算机器人。
- 但 `github-actions[bot]` 背后有**多套不同的工作流**，必须区分：
  1. **@claude 工作流**（`claude.yml`，触发条件为评论/正文/标题含 `@claude`）——配置里 `permissions: issues: read`（**只有读权限，没有 write**），且不向 action 传 `github_token`/`prompt`。**它没有能力回帖**。
  2. **triage 工作流**（`claude-issue-triage.yml`，每个新 issue + 每条人类评论都触发）——负责打标签、关闭"与 Claude Code 无关"的帖、标 invalid。产物："Closing for now — this doesn't appear to be about Claude Code"、加 `invalid` 标签等。
  3. **dedupe 工作流**（`claude-dedupe-issues.yml`，新 issue 触发）——带 "🤖 Generated with Claude Code" 签名的查重评论（"Found N possible duplicate issues…"）。
  4. **规则型生命周期 bot**——"automatically locked…"、"Closing for now — inactive for too long…"。
- 结论性签名：只有 dedupe/duplicate 关闭评论带 `🤖 Generated with [Claude Code]` 签名；@claude 工作流本身**从未**产出可见回帖。

## 2. 逐例评估

档位定义：✅ 正常回答（切题给出用户要的东西）；⚠️ 部分/泛泛（回了但没真正解决，或模板化动作）；❌ 答错/误判（答非所问、把对的标错）；✖️ 没回/失败（@claude 后无任何 AI 回复，或回复是报错/权限拒绝）。

| # | URL | 用户请求（@claude 时） | Claude 是否回复 | 档位 | 证据摘录 |
|---|---|---|---|---|---|
| 105607 | …/issues/105607 | "Please fix this… @claude"（2026-11-02） | 无任何回复 | ✖️ 没回 | 8 条评论全为人类；timeline 只有 bot 自动打 `bug`/`platform:vscode` 等标签 |
| 102056 | …/issues/102056 | "@claude could we do that?"（求实现功能） | 无 | ✖️ 没回 | 仅 bot 自动打 `enhancement`/`area:plugins` 标签 |
| 97842 | …/issues/97842 | "@claude @ozplayground 问题在 squash 被当 reset…"（给方案） | 无 | ✖️ 没回 | 2 分钟后**人类** ozplayground 手动关闭，Claude 未答 |
| 96043 | …/issues/96043 | "any update @claude"（催更） | 无 | ✖️ 没回 | 6 条评论全为人类 |
| 94532 | …/issues/94532 | "Why is this marked invalid?"（申诉误标） | 有 bot 动作但无解释 | ❌ 误判 | timeline：用户 14:58 标 `bug` → bot 14:59 加 `invalid` 并**移除 `bug`**；用户追问"为什么标 invalid"后 bot 无任何说明，issue 至今挂着 `invalid` 标签 |
| 89694 | …/issues/89694 | "Test @claude mention… Please analyze this" | 无实质回复 | ✖️ 没回 | 发帖人自称"verified to trigger correctly"并自行关闭，但评论里没有任何 AI 回帖（仅 10 月 17 日规则型 auto-lock） |
| 76596 | …/issues/76596 | HackerOne 安全研究，测试 @claude 触发 | bot 回帖=误关 | ❌ 误判 | bot："Closing for now — this doesn't appear to be about Claude Code"——把测试触发器的帖判为"与 Claude Code 无关"并关闭 |
| 95756 | …/issues/95756 | "Is it ok to use 'clauding' as a verb?" | bot 回帖=误关 | ❌ 误判 | bot："…doesn't appear to be about Claude Code"——问题本身正与 Claude 相关 |
| 93287 | …/issues/93287 | "HI @claude & @bcherny I AM STILL WAITING"（误删 Applications 目录） | 无 | ✖️ 没回 | 4 条评论全为人类 |
| 97854 | …/issues/97854 | "@claude do something haha"（classifier 故障，31 评论） | 无 | ✖️ 没回 | 31 条全为人类互助，无 bot 参与 |
| 66433 | …/issues/66433 | 求 bot 能接受 collaborator 邀请（meta） | 无（仅 stale-close） | ✖️ 没回 | bot："Closing for now — inactive for too long"（7 月 16 日，与请求无关） |
| 89128 | …/issues/89128 | "look at this shit @claude"（输出质量下降） | 无 | ✖️ 没回 | 仅 2 个月后 stale-close |
| 64632 | …/issues/64632 | 正文含 "@claude"（实为终端截图里 "tag @claude" 提示文案，**误触发**） | bot 回帖=查重 | ⚠️ 部分 | bot："Found 3 possible duplicate issues… will be automatically closed as a duplicate in 3 days"（带 🤖 签名），后关闭为 #64533 的重复；是查重模板，不是对"回复慢"问题的诊断 |
| 88094 | …/issues/88094 | "…not taking this seriously @claude @bcherny"（Remote Control 默认开启） | 无 | ✖️ 没回 | 10 条评论全为人类；`therobotprogrammer` 是用户名含 "bot" 的人类 |
| 99474 | …/issues/99474 | 报告 "iOS 发的 @Claude 评论永远到不了 Claude"（0 回复） | 无 | ✖️ 没回 | 本身就是"@claude 不通"的 bug 报告，0 条 bot 回复，互为印证 |
| 62503 | …/issues/62503 | 申诉表跳转死循环（42 评论） | 无（仅 stale-close） | ✖️ 没回 | 唯一 bot 评论是 9 月的 "inactive for too long" |
| 71542 | …/issues/71542 | "this shit is still not fixed @claude"（71 评论） | 无 | ✖️ 没回 | 0 条真实 bot 回复 |
| 63060 | …/issues/63060 | "@claude grateful for help"（88 评论） | 无 | ✖️ 没回 | 0 条真实 bot 回复 |
| 74649 | …/issues/74649 | "Why hasn't Anthropic fixed…? @claude"（87 评论） | 无（仅 stale-close） | ✖️ 没回 | 唯一 bot 评论是 9 月的 "inactive for too long" |
| 84352 | …/issues/84352 | "fuck you @claude" / "they didnt respond yet @claude"（201 评论） | 无 | ✖️ 没回 | 201 条评论中 0 条真实 bot 回复 |

**统计（n=20）**：✅ 正常回答 0；⚠️ 部分/泛泛 1（#64632，且为误触发的查重模板）；❌ 误判 3（#94532 invalid 标签、#95756、#76596 误关）；✖️ 没回/失败 16。

## 3. 归纳

**成功率：样本内 @claude 得到"正常回答"的比例为 0/20。** 16/20 完全没有任何 AI 回复；3 例虽有 bot 动作但是**误判**（且来自 triage 工作流，不是对 @claude 的应答）；1 例是误触发后的查重模板。

**为什么（根因，来自工作流配置）**：`claude.yml` 的 @claude job 配置为 `permissions: issues: read`（无 `issues: write`）、不传 `github_token`、不传 `prompt`，且把 @claude 的 `acceptEdits` 模式用 `--permission-mode auto` 覆盖掉。也就是说——@claude 触发时 Claude Code 确实被拉起（在 egress-firewall runner 上跑 `claude-sonnet-5-5`），但**没有任何回帖通道**。用户可见的 bot 行为几乎全部来自另两个工作流：`claude-issue-triage.yml`（每条人类评论都触发，负责打标签/误关/invalid）和 `claude-dedupe-issues.yml`（新 issue 查重），以及规则型 lock/stale-close bot。

**最常见失败模式（按频率）**：

1. **没回（16/20）**：@claude 后彻底沉默——无论求修复、求功能、催更、申诉、情绪帖。用户在 @claude 时常常还 @ 了真人维护者（`@bcherny` 等），实际兜底的是人类而非 AI。
2. **误判（3/20）**：Claude Code（triage）把真 bug 标 `invalid` 并摘掉 `bug` 标签（#94532，用户当场申诉、多人 +1，无人回应）；把"clauding 能否当动词"和"测试 @claude 触发"都判成"与 Claude Code 无关"而关闭。
3. **模板化动作代替回答（1/20）**：误触发时只给查重模板并自动关闭为 duplicate，不给诊断。
4. **权限/机制性失败**：@claude job 本身因只读权限无法回帖——这是系统性失败而非个案。

**对"AI 当社区成员"的含义**：

- 现状是 **@claude 这个"AI 社区成员"入口实际处于静默/半失效状态**：它会触发（工作流有运行记录），但既不回答问题，也常被隔壁 triage 工作流抢跑成误标签/误关。
- 用户侧体验最糟的组合是 **沉默 + 误伤**：不回答也就罢了，还会把真问题标 invalid 或误关，让用户感觉"被 AI 打错标签又无处申诉"（#94532 是完整样本）。
- 没有任何一例能证明"Claude 给出切题修复/诊断/实现"。若要评估"AI 当社区成员"的正面价值，本样本里看不到正面证据；能看到的是**自动化 triage 的误判风险**和**触发机制与回复机制脱节**。

## 4. 局限

- **样本量与选择偏差**：20/447，非随机——偏重已知 5 例、近期 issue 和大评论量线程。可能存在（未抽到的）@claude 得到实质回复的案例，但 20 例里 0 例且含 201 评论大线程，信号很强。
- **速率限制**：无认证 API 60 req/h，中途等待一次窗口重置；未做全量扫描，也未能核对 dedupe 是否正确（未读 #64533）。
- **"哪条是 AI 发的"无法 100% 确证**：同一 `github-actions[bot]` 身份背后有至少 4 套工作流。本文据评论措辞/签名（`🤖 Generated with Claude Code`）与工作流配置推断归属；不排除个别评论归因有误（例如某条 triage 评论被我当成 dedupe）。
- **未能确认 @claude job 的运行结局**：workflow run 列表分页在沙箱中超时（近期 100 条 run 全部为 `skipped`，符合"非 @claude 流量不触发"的预期）；无法区分 @claude job 是"静默成功但无写通道"还是"运行报错"。两者用户可见结果相同（无回帖），根因推断（`issues: read` 无写权限）来自配置而非运行日志。
- **评论/编辑的删改不可见**：comments API 看不到已删除评论与 issue 正文编辑历史；timeline 抽样中未发现被删的 bot 评论，但不能排除。
- 只覆盖 **issue**，未覆盖 PR 评论/PR review 上的 @claude（同样由 claude.yml 触发，但可能行为不同）。
