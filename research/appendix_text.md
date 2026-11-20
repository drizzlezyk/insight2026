
===== SLIDE 1 =====
  [20.0] openClaw 社区基于Bot高效透明治理issue
  [14.0] 接入后 · 全社区 issue 累计关闭率提高
  [12.0] 37.05%
  [12.0] 82.27%
  [12.0] +45.22 pp
  [6.0] 100%
  [6.4] 接入前 03/01–03/07 · n=2,526（936 关闭）｜接入后 05/15–05/21 · n=1,348（1,109 关闭）· 仓库 2026-04-28 接入。
  [9.5] 原始 issue
  [12.0] 11,468  100.0%
  [9.5] Agent 筛选后打评级标签
  [12.0] 9,497  82.8% of 原始
  [9.5] 未被 bot 自动关闭
  [12.0] 7,855  68.5% of 原始
  [9.5] 获得源码级可复现标签
  [12.0] 5,221   45.5% of 原始
  [9.5] completed 且带合并 PR
  [12.0] 2,769   24.1% of 原始
  [14.0] 1. 对贡献者：每条 Issue 都有回应、有理由、有下一步
  [14.0] - 证据不足 -> 补证据；分流附上原因是什么
  [14.0] 2. 对维护者：把精力从机械清理转移到真正需要人类判断的决策
  [14.0] 3.  对整个社区：处置透明、可追溯，建立可信的维护记录
  [14.0] - 每条处理都持久化存储record（可追溯）
  [12.0] - 针对标签做出的分流，机器人评论给出理由、详细建议
  [12.0] - 关闭动作都给出理由
  [14.0] issue 生命周期  ·  从提交到关闭
  [9.5] 人机协作  ·  小时–天级（外部）
  [10.0] bot按规则打标签
  [9.0] intake 规则 · 秒级
  [10.0] bot基于Agent分析
  [9.0] 复现 + 维度标签 · 分钟级（~3min）
  [10.0] bot review 意见/标签
  [9.0] 附可执行 fixPrompt（~9min）
  [10.0] maintainer 筛选后修复
  [9.0] 判断修 / 挂起 / 路由
  [10.0] 提交 / 关联 PR
  [9.0] 人或机器人开 PR
  [10.0] PR合并关闭 issue
  [9.0] 校验通过 · completed
  [14.0] issue随自动化链路逐层收窄 需要维护者介入的减半
  [10.0] 给出原因后关闭（~9min）
  [9.0] completed 占已关闭 issue 的比例（%）
  [12.0] 路由  下一步谁来接手
  [12.0] 评级  报告可验证度 / 证据强度
  [12.0] 优先级   可优先看哪条
  [12.0] 影响  数据丢失、安全、崩溃、消息、认证、UX 等类型，用来预判需要哪类人介入
  [9.0] 62 pt
  [9.0] 43 pt
  [9.0] 42 pt
  [9.0] 25 pt
  [9.0] 23 pt
  [9.0] 36.4%
  [9.0] 98.5%
  [9.0] 45.7%
  [9.0] 88.4%
  [9.0] 46.6%
  [9.0] 88.4%
  [9.0] 54.5%
  [9.0] 79.6%
  [9.0] 56.8%
  [9.0] 79.4%
  [12.0] 可复现  可不可信、现在还能不能复现
  [9.0] 2026-09-11 → 11-11
  [12.0] 五维深度分诊标签体系

===== SLIDE 2 =====
  [-] Bot治理下openClaw 社区PR效率提升
  [12.0] ready for maintainer look是外部 PR 进入维护者视野的通行证。真正的速度差来自 PR 大小、风险和作者是否已经在维护者信任圈内。
  [12.0] 没有 proof 的外部 PR 大多停在低合并率区间；
  [12.0] proof 齐全后，维护者才愿意花时间在那一次合并动作。
  [10.0] 内部作者自合(98.6% 自合): Bot帮助维护者判断自己的pr质量 （中位时间：28min）
  [6.9] obviyus 提交
  [6.4] 11-13 19:39
  [6.9] Barnacle 打标
  [6.4] 19:39
  [6.9] bot: proof + ready
  [6.4] 19:55
  [6.9] obviyus 自合
  [6.4] 20:10
  [7.0] 维护者动作：自己合入 · 30 min  （样例：github.com/openclaw/openclaw/pull/198427）
  [14.0] PR典型合入路径（典型）
  [10.0] 机器人直接修：Bot自己提交pr并review，维护者只需要review后和合入（中位时间：42min）
  [6.9] ClawSweeper 开 PR
  [6.4] 10-05 16:21
  [6.9] Barnacle 打标
  [6.4] 16:21
  [6.9] 自审 + ready
  [6.4] 16:28
  [6.4] 16:30
  [6.9] shakkernerd 合并
  [6.4] 17:05
  [7.0] 维护者动作：1 次合并 · 44 min   （样例：github.com/openclaw/openclaw/pull/165662）
  [12.0] 2个月合入了33586条PR（高吞吐），作者角色：
  [12.0] 官方维护者：30位
  [12.0] 维护者（名单未提及）：9位
  [12.0] 外部贡献者：613位
  [10.0] 79.4%(26667)
  [10.0] 0.6%(203)
  [10.0] 9.6% (3211)
  [10.0] 10.4% (3493)
  [9.0] 2026-09-11 → 11-11
  [12.0] 1. 对贡献者：把模糊的等待，变成一份可执行、可预期的改进清单
  [12.0] 评论会给出Rank-up moves: 和 Proof guidance:
  [14.0] 2. 维护者：把PR 从“扁平化堆叠”变为经过预审、附有证据摘要的决策流
  [12.0] - 作者过滤：超过20个open pr的作者有标签block
  [12.0] - Barnacle：结构不明确的pr过滤掉（关闭/标签）
  [14.0] 3. 对整个社区：让 PR 的处置建立在可审计的证据之上，而非印象或积压压力
  [12.0] - 机器人评论原地更新：有一条可追溯、可复核的证据链，而不是一个黑箱裁决
  [10.0] 外部贡献者提交:Bot帮助维护者判断外部的pr质量，补证循环后放行  （中位时间：34.9 h）
  [6.9] huwei-xydt 提交
  [6.4] 11-13 12:41
  [6.9] bot: needs proof
  [6.4] 13:36
  [6.9] obviyus 补 proof
  [6.4] 15:04
  [6.9] bot 放行 ready
  [6.4] 15:13
  [6.9] obviyus 合并
  [6.4] 15:51
  [7.0] 维护者动作：补 proof + 合并 · 3h10m   （样例：github.com/openclaw/openclaw/pull/198263）
  [12.0] 全社区 PR · 接入前后 30天累计合并率提升
  [7.6] +29pp
  [5.5] 03/01–03/28
  [5.5] 05/01–05/28
  [6.0] 关闭未合并
  [6.0] 仍 open
  [6.0] 合并率 = 已合并 ÷ 带该标签的全部 PR（0–100%）
  [7.2] 评级  7 档
  [4.9] unranked krab → platinum hermit
  [6.0] 20.6%
  [6.0] 85.4%
  [8.2] 65 pt
  [7.2] 状态  8 态
  [4.9] waiting on maintainer → ready for maintainer look
  [6.0] 24.9%
  [6.0] 85.5%
  [8.2] 61 pt
  [7.2] 证明  6 标签
  [4.9] supplied → override
  [6.0] 33.3%
  [6.0] 93.0%
  [8.2] 60 pt
  [7.2] 合并风险  8 类
  [4.9] message-delivery → automation
  [6.0] 38.0%
  [6.0] 67.3%
  [8.2] 29 pt
  [7.2] 优先级  4 档
  [4.9] P1 → P3
  [6.0] 60.7%
  [6.0] 77.9%
  [8.2] 17 pt
  [14.0] 外部作者PR（10%）分析
  [14.0] 82.3% 是机器人有ready for maintainer look结论后合入

===== SLIDE 3 =====
  [10.0] 机器人怎么做到的How：
  [10.0] 举例：自动关闭原因-已在main修复
  [16.0] openclaw社区issue治理洞察
  [10.0] 给出评论后关闭(30%)
  [10.0] 对基础设施的启示：
  [8.2] 接入前后 · 全社区 issue 累计闭合率（30–36 天观察窗）
  [16.0] 37.05%
  [16.0] 82.27%
  [8.6] +45.22 pp
  [6.0] 100%
  [6.4] 接入前 03/01–03/07 · n=2,526（936 关闭）｜接入后 05/15–05/21 · n=1,348（1,109 关闭）· 仓库 2026-04-28 接入。
  [6.2] completed 占已关闭 issue 的比例（%）
  [7.6] 路由  7 标签
  [5.6] needs-product-decision → queueable-fix
  [7.6] 可复现  5 标签
  [5.6] needs-info → source-repro
  [7.6] 评级  6 档
  [5.6] gold → diamond
  [7.6] 优先级  4 标签
  [5.6] P3 → P1
  [7.6] 影响  9 标签
  [5.6] ux-release-blocker → data-loss
  [8.6] 62 pt
  [8.6] 43 pt
  [8.6] 42 pt
  [8.6] 25 pt
  [8.6] 23 pt
  [6.4] 36.4%
  [6.4] 98.5%
  [6.4] 45.7%
  [6.4] 88.4%
  [6.4] 46.6%
  [6.4] 88.4%
  [6.4] 54.5%
  [6.4] 79.6%
  [6.4] 56.8%
  [6.4] 79.4%
  [7.6] 分流先于评分
  [7.4] 5 个 work-lane 决定去向；P 与 rating 不改变 issue 去哪。
  [7.6] schema 卡死关闭
  [7.4] required 证据 + 硬校验：file+sha、fixedSha、fixedAt/release，缺一即拒。
  [7.6] 关闭原因先过滤
  [7.4] 按 kind / guard 预筛后再给模型：
  [7.6] 模型只提议
  [7.4] 只读评审 + 确定性 Apply，写前由代码重检，边界不交给模型。
  [10.0] 对社区维护者（运营、maintainer）的启示：
  [7.6] 先读 work-lane
  [7.4] 再看 P 和 rating；前者决定去向，后者只描述问题。
  [7.6] queueable-fix 是承诺
  [7.4] 98.5% completed，可直接进可修队列，不用再筛。
  [7.6] 别把 P 当 SLA
  [7.4] P0 中位关闭 8.8 天，P3 0.2 天 —— 越严重，闭环越慢。
  [7.6] 分流判断用 rating
  [7.4] 值不值得派人看 rating，派给谁看可复现证据。
  [8.6] Codex
  [8.0] ① 输入
  [9.5] pr/issue 本身的内容
  [8.0] ② prompt  ·  组装
  [7.4] 共享规则
  [7.4] 品类作业单
  [7.4] 关闭原因（预过滤）
  [7.4] 仓库附则
  [7.4] 上下文索引
  [8.0] ③ 输出  ·  decision: close / keep-open
  [6.4] review_record（内部）
  [8.4] closeReason
  [7.3] enum: 16 选 1
  [8.4] confidence
  [7.3] 高 / 中 / 低
  [8.4] evidence
  [7.3] file + sha
  [8.0] schema 校验
  [7.0] 56 个 required 字段
  [7.0] closeComment（公开）
  [7.0] labels（P2 / impact）
  [7.0] report / ledger
  [6.5] 校验  schema · decision=close · confidence=high · evidence file+sha · fixedSha · fixedRelease|fixedAt ·（PR）verified fixing PR
  [7.8] ④ ClawSweeper Apply · 实时重检（把“review 时的提案”和“现在的 GitHub 状态”再对一遍） + 写回
  [7.2] 成功 → closed (completed)
  [7.0] 失败 → kept_open / skipped_*
  [10.0] 打多维度标签/评论

===== SLIDE 4 =====
  [20.0] openClaw社区pr
  [8.2] PR 标签的五个维度
  [8.6] 对基础设施的启示
  [8.6] 对社区维护者的启示
  [5.9] D 层 = 主评审的五个评分轴；A 路径 / B 体积是描述层，C 预备分流会被主评审清空，E 人控护栏是叫停层
  [6.0] 合并率 = 已合并 ÷ 带该标签的全部 PR（0–100%）
  [7.2] 评级  7 档
  [4.9] unranked krab → platinum hermit
  [6.0] 20.6%
  [6.0] 85.4%
  [8.2] 65 pt
  [7.2] 状态  8 态
  [4.9] waiting on maintainer → ready for maintainer look
  [6.0] 24.9%
  [6.0] 85.5%
  [8.2] 61 pt
  [7.2] 证明  6 标签
  [4.9] supplied → override
  [6.0] 33.3%
  [6.0] 93.0%
  [8.2] 60 pt
  [7.2] 合并风险  8 类
  [4.9] message-delivery → automation
  [6.0] 38.0%
  [6.0] 67.3%
  [8.2] 29 pt
  [7.2] 优先级  4 档
  [4.9] P1 → P3
  [6.0] 60.7%
  [6.0] 77.9%
  [8.2] 17 pt
  [9.0] 给出评论后合并（0.8%）
  [9.0] 打多维度标签/评论
  [9.0] 给出评论后关闭（3%）
  [8.2] Codex
  [8.0] 机器人怎么做到的：只读 Codex → typed decision → 确定性 Apply
  [6.5] 橙 = 与 issue 不同
  [7.0] ① 输入
  [7.9] PR 正文 + diff / files
  [7.9] checks（仅未通过）
  [7.9] 评论时间线
  [7.9] current main 源码
  [7.0] ② Prompt
  [7.3] 共享规则 60 行
  [5.9] 与 issue 共用
  [7.3] PR 作业单 100 行
  [5.9] issue 11 行
  [7.3] 关闭原因（含 PR 专属）
  [5.9] issue 16 选 1
  [7.3] 作者身份分支
  [5.9] 社区硬闸门 / 维护者跳过
  [7.0] ③ 输出
  [7.0] typed decision · 五轴路由　← issue 是 close / keep-open + closeReason
  [7.7] P0–P3
  [7.7] rating ×7
  [7.7] proof
  [7.7] merge-risk ×8
  [7.7] status（可为 null）
  [6.6] 产物　marker 评论（93.2%）· 五层标签 · review_record（内部）
  [6.5] 校验　proof · status 可为 null · 缺证据 → needs proof（不关闭，只拦合并）
  [7.0] ④ Apply
  [6.9] 重检 + 确定性写回：标签 + 一条 marker 评论
  [6.9] 合并只在 automerge 授权内，模型不执行
  [6.4] 成功 → 标签 + 评论
  [6.4] 合并：人 99.2% · bot 0.8%
  [9.2] 全社区 PR · 接入前后 30天累计合并率
  [7.6] 10.97%
  [7.6] 39.61%
  [7.6] +28.64pp
  [8.2] ×3.6
  [5.5] 03/01–03/28
  [5.5] 05/01–05/28
  [6.0] 关闭未合并
  [6.0] 仍 open
  [10.0] openClaw社区维护者需要看什么
  [9.0] 1. 确定性规则标签和Agent智能标签+评论分层设计
  [9.0] 2. Agent侧只有typed decision + schema，最终打标签是确定性 Apply
  [9.0] 3. 设计多个维度的标签正交（优先级、评分、合入风险等级、proof）
  [9.0] 4. 给人流后门
  [9.0] 5. 对作者的过滤：对于pr open过多的作者进行屏蔽
  [9.0] 1.先根据pr标签过滤，status 判「need-proof」的 PR 只有 33% 会合并，别先花时间读代码。
  [10.0] 1. 内部人员的pr（88.9%）：
  [10.0] 参考机器人给的review意见+标签，自行合入
  [10.0] 2. 外部人员的pr（11.1%）：
  [9.0] 外部 PR：先分队列，再排序，最后才读 diff
  [5.8] 先按 status 分队列 → 只在 ready 队列内按 rating / merge-risk 排序 → 排完再读 diff；其余队列先退回 / 等待 / 决策。

===== SLIDE 5 =====
  [12.0] clawsweeper  dashboard
  [12.0] dashboard的主要用户是谁？ 1.服务运维人员；2. 社区维护者
  [12.0] 通过dashboard的主要的用法，是否通过dashboard找到what to do next？
  [12.0] 2. 面向社区维护者：
  [12.0] Assesment页面：（晾晒）
  [12.0] 为解决的issue的列表：
  [12.0] 排序：先按审查者分配的优先级（P0–P3），再按审查时间从旧到新。
  [12.0] 目的：通过优先展示P0，并让同优先级中更陈旧的条目靠前，页面确保了最危险、且被搁置最久的问题，能持续获得可见性。
  [12.0] mgoin pinboard（工作台，效率提升）
  [12.0] 将待处理的 PR、Issue 按“待审查”、“进行中”、“待合并”等状态分类，帮助维护者快速识别哪些需要自己介入，哪些可以交由其他贡献者处理。
  [12.0] 展示每个变更所处的阶段。对于复杂的性能优化或功能 PR，维护者需要判断其是否满足了合并条件（如 CI 通过、性能基准达标）
  [12.0] 看板所聚合的完整讨论上下文。
  [12.0] 作为知识沉淀与交接依据

===== SLIDE 6 =====
  [8.5] OPENCLAW × CLAWSWEEPER  ·  标签体系拆解
  [25.0] PR 标签分 5 层
  [8.5] 基线 2026-11-12
  [8.5] clawsweeper @ e7fd669  ·  openclaw/openclaw
  [9.5] 一句话：A/B 描述改动，C 是占位，D 是结论，E 是人叫停；D 层五个维度彼此正交，只有 Before merge → status 存在因果。
  [7.0] 证据：clawsweeper-policy.ts:96–380  ·  clawsweeper-label-policy.ts:83–114  ·  clawsweeper-apply-report-labels.ts:171–205  ·  clawsweeper-label-presentation.ts:104–126  ·  scripts/github/labeler-labels.mjs:16–41  ·  .github/
  [7.6] merge-risk · 8 类（仅 PR，统一前缀 merge-risk: 🚨）
  [6.8] compatibility · message-delivery · session-state · auth-provider · security-boundary · availability · automation · other
  [6.2] 中位合并 = 创建→合并，2026-09-01～11-12 合并样本（每档≤100，S 仅 2 例）；NA 不适用。
  [7.8] P0–P3 · 优先级（impact，不是处理顺序）
  [6.6] P0  数据丢失、安全绕过、崩溃循环、核心运行时不可用
  [6.6] P1  正在影响真实用户的 agent / channel 工作流
  [6.6] P2  影响面有限的 bug 或改进
  [6.6] P3  清理、文档、打磨、易用性、推测性功能
  [7.8] status · 8 态（由 Before merge 派生）
  [6.5] 👀 ready for maintainer look  — 无阻断项 （codedx怎么得到这个结论的）
  [6.5] ⏳ waiting on author  — 等作者改 （codedx怎么得到这个结论的）
  [6.5] ⏳ waiting on maintainer  — 只差维护者
  [6.5] 📣 needs proof  — 缺真实证据
  [6.5] 🛠️ actively grinding  — 作者已动
  [6.5] 🔁 re-review loop  — 显式复审
  [6.5] needs maintainer proof decision  — 维护者定
  [6.5] null  — 暂停/失败，不打
  [7.8] proof · 3 态
  [6.5] sufficient 解锁闸门 · override 人工豁免 · 📸/🎥 媒体子标签（可并存）
  [-] 社区用codex review，结合5个维度的标签设计（设计理念），帮助maitainer 提效

===== SLIDE 7 =====
  [8.2] 02  /  ISSUE GOVERNANCE
  [16.5] clawsweeper Issue 治理流程
  [7.3] INTAKE → REVIEW → DECISION → APPLY · INTAKE 只是预备分流；完整评审才产出 Decision；Apply 重取实时状态后分流。
  [6.6] INTAKE 初筛
  [6.6] AI 只读
  [6.6] 确定性 Apply
  [6.6] 人类控制
  [7.4] ① 触发
  [5.8] INTAKE
  [7.4] ② 评审
  [5.8] REVIEW
  [7.4] ③ 判定
  [5.8] DECISION
  [7.4] ④ 写回
  [5.8] APPLY
  [7.4] ⑤ 反馈
  [5.8] HUMAN
  [8.2] 触发与调度
  [6.2] • 新开 / 编辑 / 评论
  [6.2] • 维护者：review / re-review / explain / stop
  [6.2] • 调度：热 5 min；<30 天每日；陈旧每周
  [6.2] • 只读 token；审查期无写权限
  [7.5] INTAKE 初筛 · clawsweeper:intake:*
  [6.0] AI 轻量分类（gpt-6-luna）；只读标题+正文 ≤12 KB；20 秒超时。
  [5.4] feature
  [5.4] docs
  [5.4] support
  [5.4] needs-repro
  [5.4] needs-environment
  [8.2] Intake 规则与用途
  [6.1] • 只回答：类别 / 复现是否给出 / 版本环境
  [6.1] • needs-*：仅 bug 类别；不写 P / impact / rating
  [6.1] • 用途：给维护者早期分诊，不是评审证据
  [6.1] • 生命周期：完整评审发布即清空
  [8.2] 上下文与证据
  [6.1] • 读取：正文 / 讨论 / 关联 issue & PR
  [6.1] • 源码：当前 main；只读 GitHub token
  [6.1] • 证据：复现步骤 / 源码路径 / 环境
  [6.1] • 缺口：未读到 ≠ 不存在，必须明示
  [8.2] Codex 完整评审
  [6.1] • sandbox + 受控 prompt；proposal-only
  [6.1] • 审查期无写权限；不建 PR / 不关闭
  [6.1] • 输出：逐条证据 + 置信度 high/med/low
  [6.1] • 原则：模型给判断，代码管边界
  [6.1] • Decision JSON：结构化判定
  [6.1] • 报告：Markdown + frontmatter
  [6.1] • 决策包：yml；可复现 / 可审计
  [6.1] • 落盘：records/<repo>/items
  [8.2] 结构化判定字段
  [6.0] category：bug / feature / docs / support
  [6.0] repro：status + confidence
  [6.0] product：new feature / config / decision
  [6.0] complexity：small / medium / large
  [6.0] work lane：none / manual / queue_fix_pr
  [6.0] close：reason + comment + evidence
  [7.2] 需要关闭？
  [5.9] 9 类 issue reason
  [7.7] 9 类 issue reason（关闭提案）
  [5.8] implemented_on_main
  [5.8] cannot_reproduce
  [5.8] clawhub
  [5.8] duplicate_or_superseded
  [5.8] unsponsored_feature_request
  [5.8] stale_version_bug
  [5.8] not_actionable_in_repo
  [5.8] incoherent
  [5.8] stale_insufficient_info
  [5.5] 另有 8 类 reason 仅适用 PR；none = 保持开放。
  [8.2] 关闭路径 · APPLY
  [6.1] 写报告 + 决策包（records/<repo>/items）
  [6.1] 重取实时状态：labels / author / pair / drift
  [6.1] 四道门：结构 · 证据 · 权限 · 实时
  [6.1] 评论 → 关闭；记录 action / applied_at / sha
  [6.1] 例外：unsponsored → idea-archive；失败 → 保持开放
  [8.2] 保持开放路径
  [6.1] 保持开放；保护 maintainer / linked PR / pair
  [6.1] 投影 advisory labels：证据 / 可修 / 决策 / 查重
  [6.1] queueable-fix → no-stale；其他状态不保护
  [6.1] 不派发任何修复 / 合并 / 关闭动作
  [6.1] 审计：报告 + action ledger；可一条评论复活
  [5.4] 失败 →
  [6.6] 维护者命令
  [5.7] review / re-review / explain / stop
  [6.6] 一条评论复活
  [5.7] 重新评估；可 reopen；人类保留否决权
  [6.6] protected labels
  [5.7] human-review / manual-only / bulk-filed / no-stale
  [6.6] action ledger
  [5.7] 可审计；good first issue 人工移除 = opt-out
  [6.6] 依据：clawsweeper-apply-close-execution.ts · clawsweeper-close-decision.ts · clawsweeper-apply-close-policies.ts · clawsweeper-label-selection.ts · baseline e7fd669

===== SLIDE 8 =====
  [8.2] 02  /  ISSUE GOVERNANCE  ·  SIMPLE FLOW
  [22.0] ClawSweeper Issue 治理流程（简版）
  [9.2] AI 只产提议；Apply 做确定性校验；关闭与保持开放两条路径。
  [10.0] INTAKE 初筛
  [10.0] Codex 完整评审
  [10.0] 结构化判定
  [9.6] 需要关闭？
  [9.6] Apply 四道门
  [9.2] idea-archive
  [9.6] 保持开放
  [9.6] Advisory 标签
  [9.2] no-stale
  [7.0] 失败 →
  [8.0] 维护者命令   ·   一条评论复活   ·   action ledger
  [6.4] maintainer-trust-efficiency · p5 简版 · openclaw/clawsweeper @ e7fd669

===== SLIDE 9 =====
  [8.2] CLAWSWEEPER  ·  FULL REVIEW PROMPT
  [23.0] Codex 完整评审：Prompt 是怎么拼出来的
  [9.2] buildReviewPrompt() 在运行时把共享规则、item-kind 段落、关闭策略、仓库策略和上下文拼成一个 prompt——没有单一“完整 prompt 文件”。
  [10.5] Prompt 来源
  [10.5] 运行时组装
  [5.8] CORE
  [7.6] prompts/review-item.md
  [6.4] 共享规则：ground rules / review 方法 / close policy 框架
  [5.8] KIND
  [7.6] prompts/review-item-issue.md / review-item-pr.md
  [6.4] item-kind 段落；填入 {{item_kind_review}}
  [5.8] CLOSE
  [7.6] prompts/review-close-reasons.md
  [6.4] 关闭原因指导：issue 9 类 / PR-only 补充
  [5.8] POLICY
  [7.6] src/repository-profiles.ts
  [6.4] Repository Policy：promptNote + kindPromptNotes
  [5.8] CONTEXT
  [7.6] src/clawsweeper-prompt-context.ts
  [6.4] + review-prompt-sections.ts：context JSON / notes / provenance / media
  [9.4] buildReviewPrompt()
  [6.2] clawsweeper-review-core.ts:283
  [7.2] core
  [6.4] review-item.md
  [7.2] kind
  [6.4] {{item_kind_review}} → issue / PR
  [7.2] close
  [6.4] review-close-reasons.md
  [7.2] policy
  [6.4] ## Repository Policy
  [7.2] context
  [6.4] context JSON + runtime sections
  [7.6] → 最终 Prompt
  [5.6] prompt
  [9.2] Prompt（Markdown）
  [7.0] 按 1–5 顺序拼接；运行时生成
  [7.0] core + kind + close + Repository Policy
  [7.0] + context JSON / runtime sections
  [9.2] Codex 完整评审
  [7.0] runCodex() → runAgentProcess()
  [7.0] sandbox · 只读 GitHub token · proposal-only
  [8.8] Decision JSON
  [6.4] schema/clawsweeper-decision.schema.json · strict
  [8.4] 改 prompt 的入口：core / kind template / repository policy  ·  改组装逻辑：buildReviewPrompt()  ·  改输出：decision schema
  [6.6] openclaw/clawsweeper @ e7fd669 · 路径相对仓库根目录 · 详细代码：src/clawsweeper-review-core.ts

===== SLIDE 10 =====
  [8.4] OPENCLAW × CLAWSWEEPER  /  QUALITY CONTROLS
  [23.5] clawsweeprt准确性控制：模型给判断，代码管边界
  [10.2] 以证据、结构校验、确定性规则和受控写回降低错误风险；这是多层护栏，不是准确率保证。
  [8.2] REVIEW / 01
  [8.0] EVIDENCE
  [13.0] 审查有证据边界
  [-] • 汇集 Issue 正文、讨论、关联项与当前源码。
  [-] • 要求明示证据及覆盖缺口；未读到不等于不存在。
  [-] • Codex 使用受限 sandbox 与只读 GitHub token。
  [7.2] review-core.ts
  [8.0] SCHEMA GATE
  [13.0] 输出先过机器校验
  [-] • Decision JSON 严格检查字段、枚举、分数范围与字段关系。
  [-] • 标签必须在白名单内；每个选中标签都要有理由。
  [-] • 缺字段、越界或矛盾即拒绝，不进入后续同步。
  [7.2] decision-parser.ts
  [8.0] POLICY
  [13.0] 标签由确定性规则映射
  [-] • 规则读取已校验 Decision 与 Issue 当前状态，不直接信任原始 JSON。
  [-] • queueable-fix 要求候选路径、candidate 状态、高置信度且非 bulk。
  [-] • 证据不足或涉及安全、产品决策时，转补证或人工处理标记。
  [7.2] label-selection.ts
  [8.0] CONTROLLED APPLY
  [13.0] 写回与模型隔离
  [-] • 模型只读；宿主 Apply 阶段另行检查状态、时效与保护条件。
  [-] • 只有合格报告才同步建议标签或执行允许的操作。
  [-] • 维护者仍负责需人工判断的边界案例。
  [7.2] apply-report-labels.ts
  [11.0] 准确性边界
  [9.1] 这些护栏能拦截格式错误、越权写入和部分规则违例，不能保证模型语义判断无误。公开 Assessments 页面也明示：记录不是独立准确率测量；未见公开 gold-set、precision / recall。
  [7.6] review-plan.yml  ·  review-core.ts  ·  decision-parser.ts  ·  label-selection.ts  ·  apply-report-labels.ts  ·  Assessments
  [7.0] 解读口径：护栏与流程控制 ≠ 统计学准确率；Dashboard snapshot checked 2026-11-09。
  [14.0] Contains AI-generated

===== SLIDE 11 =====
  [8.4] OPENCLAW × CLAWSWEEPER  ·  CLOSE DECISION GATE
  [22.5] 实现类关闭：五道证据门，缺一不开
  [8.0] DECISION / 01
  [9.0] isImplementationCloseReason(...) 为真时依次校验；任一失败即 actionTaken=skipped_invalid_decision，item 保持 open。
  [6.6] GATE CHAIN · 顺序 AND · 02 仅 PR
  [6.6] RESULT · 全过才继续
  [6.4] if (!hasImplementationSourceEvidence(decision))
  [7.6] 源码证据
  [6.2] evidence[] 至少一条同时带 file + sha；行为要在 current main 源码中成立。
  [5.2] FAIL
  [5.8] requires evidence with file and sha
  [6.4] if (item.kind === "pull_request"
  [6.4] && verifiedImplementationPullRequestBlockReason(...))
  [7.6] PR 来源（仅 PR）
  [6.2] fixing PR 必须已合并、同仓库、来源可信、URL 与编号一致；不能是正在关闭的这条 PR。
  [5.2] FAIL
  [5.8] block reason 非空 → 拒绝
  [6.4] if (!decision.fixedSha?.trim())
  [7.6] 修复提交
  [6.2] fixedSha 必填：必须指向真正的修复提交，不能只凭「看起来修了」。
  [5.2] FAIL
  [5.8] requires fixedSha
  [6.4] if (decision.fixedAt
  [6.4] && !hasValidFixedAt(decision))
  [7.6] 时间格式
  [6.2] 只要填了 fixedAt，就必须是合法的 ISO 时间戳；格式错误直接拒绝。
  [5.2] FAIL
  [5.8] fixedAt must be an ISO timestamp
  [6.4] if (!decision.fixedRelease?.trim()
  [6.4] && !hasValidFixedAt(decision))
  [7.6] 版本或时间
  [6.2] fixedRelease 与合法 fixedAt 至少有一个；main-only 也必须由 fixedAt 或 release 佐证。
  [5.2] FAIL
  [5.8] requires fixedRelease or fixedAt
  [6.6] ✓ ALL PASS
  [9.4] 五门全过 → continue
  [6.6] 交给 Apply 执行；后面还有实时状态、标签保护、锁与幂等重检。
  [6.2] closeItem(item,
  [6.2] closeReason)
  [6.6] ✕ ANY FAIL
  [9.4] 任一失败 → return
  [5.8] { ok: false,
  [5.8] actionTaken:
  [5.8] "skipped_invalid_decision" }
  [6.6] item 仍 open；写入拒绝原因，等重审或下一轮。不是异常，是硬拒绝。
  [6.2] 守卫：全部检查都以 isImplementationCloseReason(...) 为前提；
  [6.2] duplicate / stale 等非实现类原因不进入这段。
  [8.0] 一句话  这五道门是 decision 层的硬门——证据缺一段，关闭就不会发生；PR 比 issue 多一道 fix-PR 来源门。
  [6.8] 源码：src/clawsweeper-close-decision.ts:413–464  ·  实现类原因 = implemented_on_main | mostly_implemented_on_main  ·  与 Apply 层四道门分属不同阶段（见治理流程页）

===== SLIDE 12 =====
  [8.4] OPENCLAW × CLAWSWEEPER  ·  ISSUE REPRODUCIBILITY FLOW
  [22.5] 2 个月 11,147 条 issue：从「可复现程度」到四类去向
  [9.0] 窗口 2026-09-13 ~ 11-13 · 每条 issue 先经 ClawSweeper 复现判定，再按最终状态收口；色带宽度 = issue 数。
  [8.0] OUTCOME / 01
  [6.6] STAGE 00 · ORIGINAL
  [7.6] 全部 issue
  [6.6] STAGE 01 · BOT REVIEW
  [7.6] 按 clawsweeper 复现证据标签
  [6.6] STAGE 02 · OUTCOME
  [7.6] 最终关闭去向 / 是否仍开放
  [9.0] 全部 issue
  [24.0] 11,147
  [6.8] 2026-09-13 ~ 11-13
  [6.8] 2 个月 · 100%
  [8.2] 已复现 17
  [6.3] current-main-repro · 0.2%
  [8.2] 源码级可复现 5,137
  [6.3] source-repro · 46.1%
  [8.2] 待活体复现 453
  [6.3] needs-live-repro · 4.1%
  [8.2] 信息不足 1,150
  [6.3] needs-info · 10.3%
  [8.2] 未复现 212
  [6.3] not-repro-on-main · 1.9%
  [8.2] 不适用 1,114
  [6.3] off-meta tidepool · 10.0%
  [8.2] 未评级 / 无结论 3,064
  [6.3] 无评级 / 无证据 · 27.5%
  [10.0] 已解决关闭 4,770
  [6.8] completed · 42.8%
  [10.0] 未解决关闭 1,552
  [6.8] not_planned + duplicate · 13.9%
  [10.0] 老化关闭 1,306
  [6.8] stale 标签 · 84.9% 为 not_planned · 11.7%
  [10.0] 仍开放 3,519
  [6.8] open · 31.6%
  [8.0] 一句话  真正复现的只有 17 条（0.2%），一半停在「源码级」。源码级解决率 57%，待活体 34%，信息不足 / 不适用仅 25–27%。
  [6.6] 「main 上不复现」是例外（39%），更像“已修好”信号。  ·  68.4% 已关闭，31.6% 仍开放。
  [6.6] 已解决关闭
  [6.6] 未解决关闭
  [6.6] 老化关闭
  [6.2] 数据：GitHub Search API · repo:openclaw/openclaw · is:issue · created:2026-09-13..2026-11-13 · 快照 2026-11-16
  [6.2] 口径：证据标签互斥；未评级 = 无 issue-rating 或未命中证据标签；未解决 = not_planned + duplicate；老化 = 带 stale 标签且已关闭；仍开放 = 当前 open。