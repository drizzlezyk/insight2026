# openclaw × ClawSweeper：PR 的每条去向

**统计范围**：`openclaw/openclaw`，2026-04-26（ClawSweeper 首次在仓库活动）～2026-11-12 创建的 PR
**分母**：**92,536 个 PR**
**数据源**：GitHub Search API（全量计数）、公开 GitHub 事件流（`github_events`，约 4% 覆盖，2,567 次合并事件 / 272 个合并账号）、32 个关闭样本 / 12 个合并样本的 timeline 校验、`openclaw.org/people` 官方名单

---

## 0. 一句话

**70% 的 PR 被合并、93% 被 ClawSweeper 评论过，但 70% 的合并只由 5 个账号完成。**

其中 `steipete` 一人占 **54.1%** 的合并量，而他不在这份项目的任何官方维护者名单上。所谓“社区共同维护”，在这份数据里是一个五个人的流水线。

---

## 1. 先把“维护者”定义清楚

原先把维护者等同于 top-5，这个口径经不起检验。三层事实：

**① 官方名单 48 人。** `CONTRIBUTING.md` 指向 `openclaw.org/people`：

| 层级 | 人数 | 构成 |
|---|---:|---|
| OpenClaw Foundation（全职） | 18 | 产品与工程 12、运营 6（主席/人事/财务/活动/合作/幕僚长） |
| Core Maintainers（外部） | 30 | NVIDIA 6、Microsoft 6、OpenAI 4、Tencent 3、Atlassian 2、Independent 7、Xiaomi / Hugging Face / Red Hat / Paradigm 各 1 |

工程岗合计约 **42 人**，运营 6 人基本不合并 PR。

**② 实际有合并动作的账号 272 个。** 2,567 次样本合并中，272 个不同账号执行过合并（人类 266、机器人 6）。按 4% 覆盖率外推，全量约 400–600 个账号有写权限。

**③ 合并量高度集中。** ≥100 次合并的只有 3 个账号，≥10 次的 20 个，≥3 次的 59 个，其余 213 个账号只有 1–2 次。

所以正确的切分不是“维护者 vs 非维护者”——**能合并的人必然有写权限，有写权限就是维护者**。原来的 C 组“无维护者参与却有 9,201 个合并”在逻辑上不成立：那 9,201 个合并全部由有写权限者（或机器人）执行。

### 1.1 合并者身份四分类

| 合并者身份 | 账号数 | 样本合并 | 占已合并 | 外推（64,786） |
|---|---:|---:|---:|---:|
| **核心 5 人**（steipete、vincentkoc、RomneyDa、obviyus、shakkernerd） | 5 | 1,800 | **70.1%** | **45,429** |
| **官方名单其他成员**（48 人名单中除上述 4 人，实测出现 27 人） | 27 | 185 | 7.2% | 4,669 |
| **名单外、但持有写权限的协作者** | 234 | 444 | 17.3% | 11,206 |
| **机器人**（roboclaw / mantis / clawsweeper 等） | 6 | 138 | 5.4% | 3,482 |
| 合计 | 272 | 2,567 | 100% | 64,786 |

两个必须点破的事实：

- **`steipete` 不在 Foundation，也不在 Core Maintainers**，却执行了 54.1% 的合并。
- **官方 48 人名单只解释 23.3% 的合并**；加上名单外的 234 个账号才补齐到 100%。名单里另有 7 人（Spectorian、Takhoffman、drobison00、mbelinky、momothemage、shanselman、sliverp）在样本中一次都没合并过。

---

## 2. 主表：每条 PR 的终态由谁执行

| 终态 | 执行者 | 数量 | 占 92,536 |
|---|---|---|---:|---:|
| 合并 | 核心 5 人 | 45,429 | **49.1%** |
| 合并 | 官方名单其他成员 | 4,669 | 5.0% |
| 合并 | 名单外有写权限者 | 11,206 | 12.1% |
| 合并 | 机器人 | 3,482 | 3.8% |
| 关闭 | 作者自己关闭 | 12,216 | 13.2% |
| 关闭 | 维护者关闭他人 PR | 6,872 | 7.4% |
| 关闭 | ClawSweeper 关闭 | 4,581 | 4.9% |
| 关闭 | 其他机器人关闭 | 764 | 0.8% |
| 未终结 | 仍 open | 3,319 | 3.6% |

> 合并类按 2,567 次样本事件的比例外推到 64,786；关闭类按 32 个样本的比例外推到 24,432；各分项独立取整，合计与 92,536 可能相差个位数。

**读法**：把“合并”四行加起来是 70.0%，其中 **49.1% 落在 5 个人身上**；把“关闭”四行加起来是 26.4%，其中作者自关占一半、ClawSweeper 占近五分之一。

### 2.1 最终状态（自上表的横向汇总）

| 状态 | 数量 | 占比 | 补充说明 |
|---|---:|---:|---|
| 已合并 | 64,786 | **70.0%** | 其中 45,429（70.1%）由核心 5 人执行 |
| 关闭未合并 | 24,432 | **26.4%** | 关闭者样本中 6/32 为维护者自关 |
| 仍 open | 3,319 | **3.6%** | — |

---

## 3. ClawSweeper 到底做了什么

**评论覆盖：86,217 / 92,536 = 93.2%**

| 状态 | ClawSweeper 评论过 | 覆盖率 |
|---|---:|---:|
| 已合并 | 61,026 | 94.2% |
| 关闭未合并 | 22,431 | 91.8% |
| 仍 open | 2,760 | 83.2% |

**status 标签漏斗**（当前快照，合计 92,536）：

> 口径：下面每一档都按 PR **当前的 `status:*` 标签**统计，不解析评论正文。标签由 `clawsweeper[bot]` 通过 timeline API 写入，可逐条审计（例：PR #71885，2026-05-20T14:40:55Z 打上 `status: 📣 needs proof`，见 §3 末的样例）。

| status | 数量 | 占比 | 合并 | 关闭 | open | 官方名单参与 |
|---|---:|---:|---:|---:|---:|---:|
| 👀 ready for maintainer look | 46,393 | **50.1%** | 39,697 | 5,479 | 1,216 | 81.7% |
| 📣 needs proof | 14,738 | **15.9%** | 4,101 | 9,665 | 972 | 46.2% |
| ⏳ waiting on author | 8,223 | 8.9% | 4,987 | 2,849 | 387 | 72.2% |
| ⏳ waiting on maintainer | 440 | 0.5% | — | — | — | — |
| automerge armed | 473 | 0.5% | — | — | — | — |
| actively grinding | 83 | 0.1% | — | — | — | — |
| re-review | 33 | 0.04% | — | — | — | — |
| 无 status 标签 | ~22,153 | 23.9% | — | — | — | — |

两条规律：

1. **`ready for maintainer look` 的合并率 85.6%，`needs proof` 只有 27.8%。** 机器人的状态判断和最终结果高度一致。
2. **`needs proof` 是关闭的主入口**：24,432 个关闭里有 9,665 个落在这一档（占 39.6%，占该档 14,738 个 PR 的 65.6%），且这里官方名单参与率最低（46.2%）。

**机器人自己的合并量**：样本中 `clawsweeper[bot]` 执行了 21 次合并（占 0.8%，外推约 530 个）。它确实会在护栏内合并，但量级只有其关闭量的十分之一。

### 3.1 一个具体样例：PR #71885

`fix(tasks): serialize structured task values for sqlite`，作者 `likewen-tech`（`CONTRIBUTOR`），2026-04-26 创建。完整时间线（均为 timeline API 原始事件）：

| 时间（UTC） | 事件 | 执行者 |
|---|---|---|
| 04-26 01:51 | 评论“Confidence Score: 5/5，Safe to merge” | `greptile-apps[bot]` |
| **05-20 14:40:55** | **打标签 `status: 📣 needs proof`** | **`clawsweeper[bot]`** |
| 05-20 14:41:27 | 打标签 `triage: needs-real-behavior-proof` | `openclaw-barnacle[bot]` |
| 06-14 05:01 | 标记 stale | `openclaw-barnacle[bot]` |
| 06-26 06:45:13 | 评论“ClawSweeper applied the proposed close” | `clawsweeper[bot]` |
| 06-26 06:45:14 | **关闭**（理由：duplicate or superseded） | `clawsweeper[bot]` |

同一时刻 ClawSweeper 的正文写得很直白：“the branch still lacks merge-ready proof”，并附上一条“PR egg”激励——**只有通过 real-behavior proof 检查，蛋才会孵**。也就是说标签和评论是同一套判断的两个产物，但统计用的是标签。

这个例子也说明 `needs proof` **不等于必然被关**：它最终是以“重复 / 已被取代”关掉的，`needs proof` 起的作用是把它挡在合并闸门外 37 天。

### 3.2 维护者自己的 PR：机器人怎么协作（#197593）

`fix(worktrees): avoid E2BIG during isolated Git hydration`，作者 **`steipete`**（即全仓最大合并者本人），2026-11-12 06:40:18 创建，**24 分 51 秒后合并**。全流程只有 3 条评论、0 条 inline comment、0 个正式 review。

| 时间 (UTC) | T+ | 事件 | 执行者 |
|---|---|---|---|
| 06:40:18 | 0 | 开 PR（2 commits，+103/−9，6 个文件） | `steipete` |
| 06:40:24 | 6s | 接单：“ClawSweeper picked this up” | `clawsweeper[bot]` |
| 06:40:32 | 14s | 路径标签 `docs` / `scripts` / `agents`，2 秒后 `size: S` | `openclaw-barnacle[bot]` |
| 06:40:37 | 19s | 独立 review 摘要：completed，no findings | `chatgpt-codex-connector[bot]` |
| 06:51:37 | 11m19s | intake 标签 `clawsweeper:intake:bug` / `needs-environment` / `needs-repro` | `clawsweeper[bot]` |
| 06:56:25 | 16m07s | **撤销上述 3 个 intake 标签**，改打 `P2`、`rating: 🦐 gold shrimp`、`status: 👀 ready for maintainer look` | `clawsweeper[bot]` |
| 06:56:43 | 16m25s | 完整评审：证明力 3/6，“Before merge: None”，但正文注明 CI gate 未解决 | `clawsweeper[bot]` |
| 07:05:09 | 24m51s | **合并**（此时 `openclaw/ci-gate` 状态为 failure，06:49:31 已判红） | `steipete` |

六个可以复用的观察：

1. **人是瓶颈之外的一切，机器人是瓶颈之内的一切。** 从开 PR 到“可以看了”只用了 16 分钟，全是机器人在动；人只做了两个动作——开 PR、点合并。所谓“维护者 review”，在这条链路上等于一次合并点击。
2. **三层机器人分工明确**：`barnacle` 按改动路径打领域标签和 size；`clawsweeper` 做语义评审、定优先级、给评级、置状态；`chatgpt-codex-connector` 再跑一遍独立的 Codex review 作交叉校验。ClawSweeper 自己的正文也标注了“Codex review notes: reasoning medium”，说明它内部同样调 Codex——同一模型走两条通道各评一次。
3. **硬闸门只对社区 PR 生效。** 评审骨架按作者身份二选一（`src/review-prompt-sections.ts:39-45`）：维护者不加载 `external_author` 段落，而那一节写着“real-behavior proof gates merge unless every changed file is under `docs/`”。少了这一节，证明是否足够就退回模型判断——可以放松（本例），也可以继续收紧（§3.3 的 #197427）。判定身份时还有一个坑：GitHub 对私有组织成员向 App 只返回 `CONTRIBUTOR`，所以代码会用仓库 admin/maintain 权限把它升级成维护者（`src/maintainer-review-policy.ts:27-31`）。
4. **机器人会自我纠错，但只在 intake 层。** 06:51:37 它把 PR 当 issue 读，打了 `bug` / `needs-environment` / `needs-repro`；5 分钟后主评审读完 diff，把这三个全部撤销。分类器和评审器是两套逻辑，最终以读 diff 的那套为准。
5. **它的否决权是软性的。** 正文写明了两个缺口（CI gate 未解决、缺 cold `scripts/pr review-init` 端到端验证），但 `Before merge` 一栏写的是 "None"，也没有落成阻断标签。缺口被记录，但没有被强制执行。
6. **人越过了机器人记录在案的警告。** `openclaw/ci-gate` 在 06:49:31 判 failure，15 分 38 秒后仍然合并。作者正文说明这是继承的 test-lines 基线债务（main 已超 25 行），不是本次改动引入——机器人负责把风险写下来，人负责判断它是否可以接受。

对照组是社区 PR #71885：同样“缺真实行为证据”，被判 `needs proof` 后没有补证，37 天后以 superseded 关闭。**结构差别是硬的：社区 PR 加载 `external_author` 闸门，维护者 PR 不加载。** 但闸门之后的松紧仍由模型判断，#197427 就是反例。

### 3.3 两个维护者 PR 的对照（#197593 vs #197427）

同为 2026-11-12、同为核心维护者，机器人的处理并不一样：

| 维度 | #197593（`steipete`） | #197427（`vincentkoc`） |
|---|---|---|
| GitHub `author_association` | `CONTRIBUTOR` | `MEMBER` |
| 首轮评级 | 🦐 gold shrimp 3/6 | 🦪 silver shellfish 4/6 |
| 是否被要求补证 | **否**，正文直接写“outside the ordinary contributor proof gate” | **是**，01:33 打 `status: 📣 needs proof` + `merge-risk: 🚨 security-boundary` |
| 补证轮次 | 0 | 2（01:27、02:22 两次 `@clawsweeper re-review`） |
| 终局 | gold shrimp 3/6，“Before merge: None” | 🦞 diamond lobster 5/6，`proof: sufficient` |
| 开 PR → 合并 | 24m51s | 2h05m59s |

同一个机器人、同一套骨架，对两个维护者给出了不同的证明要求。差别不在“是不是维护者”（两人都是），而在**模型对具体证据的判断**：#197427 在 01:33 那一轮确实被判证据不足，作者补了两轮测试日志才翻盘。

这也修正了一种过于简单的读法——不是“维护者 PR 一律放行”，而是“维护者 PR 没有硬闸门，只有模型判断”。软闸门可以被真实证据顶开，也可以被模型收紧。

---

## 4. 关闭端：谁在关（32 个样本，timeline 校验）

| 关闭者 | 样本 | 占比 | 外推至 24,432 |
|---|---:|---:|---:|
| 作者自关 | 16 | **50.0%** | 12,216 |
| ├ 其中维护者自关自己的 PR | 6 | 18.8% | 4,581 |
| ├ 社区作者自关 | 9 | 28.1% | 6,872 |
| └ 机器人自关（roboclaw） | 1 | 3.1% | 764 |
| 维护者关闭他人 PR | 9 | **28.1%** | 6,872 |
| ClawSweeper 关闭 | 6 | **18.8%** | 4,581 |
| 其他机器人关闭 | 1 | 3.1% | 764 |

> “作者自关”是父项，其下三行是拆分，不能与父项相加。表中两处 4,581、两处 6,872 分属不同桶（作者自关 vs 严格的关闭方），样本数相同纯属巧合，不是重复计数。

**交叉验证**：样本里“无 top-5 痕迹即被关”占 17/32 = **53.1%**，与全量搜索口径的 **56.5%** 吻合。

ClawSweeper 关闭的 6 个样本：作者全部是社区用户，其中 **3/6 没有任何人类评论**——这是真正意义上的 bot 独立关闭。用 GH Archive 事件流另算，ClawSweeper 在关闭事件中占 11.6%，对应约 2,800 个；两种口径给出区间 **2,800–4,600 个（3.0%–5.0%）**。

**合并端**（12 个样本）：10 个人类合并、2 个 `roboclaw-bot` 自并；14 个无损合并样本中 11 个是作者自并——这与“234 个名单外账号持有写权限”完全一致。

---

## 5. 三个结论

1. **不是“社区维护”，是“五人流水线 + 长尾协作者”。** 5 个账号完成 70.1% 的合并，官方 48 人名单只覆盖 23.3%，名单外 234 个账号贡献 17.3%。把维护者定义为 top-5 会高估集中度，定义为官方名单会低估活跃度——两者都对不上实际权力结构。
2. **ClawSweeper 接管的是“分流 + 拦截”，不是“合并”。** 93% 的 PR 被它评论过、50% 被标成“可以看”、16% 被打回“需要证据”，亲手关闭 3%–5%，亲手合并 0.8%。
3. **官方治理结构与实际执行已经脱节。** 名单上 48 人里有 7 人在样本中零合并，而名单外的 `steipete` 是最大合并者（54.1%）。任何以“官方维护者名单”为口径的统计都会系统性失真。

---

## 6. 局限（引用时需带上）

- **合并者身份来自 4% 事件样本**（2,567 / 64,786），比例可外推，个体计数不可外推；`clawsweeper[bot]` 的 21 次合并同理。
- **事件流的 `actor_login` 是执行合并动作的账号**，但它无法区分“本人操作”与“代账号操作”；同时 GH Archive 对 openclaw 的覆盖是抽样，不是全量。
- **官方名单以 2026-11-12 的 `openclaw.org/people` 为准**；名单会变，且 Foundation 18 人里有 6 人是运营岗，计入“维护者”会高估工程侧人数。
- status 标签是当前快照；23.9% 无 status 的 PR 很可能在合并后被清理过标签，不能解释为“机器人没处理”。
- 关闭者样本 n=32、合并者样本 n=12–14，外推值应作为区间而非精确值。
- 各分项来自独立查询，四舍五入后合计与 92,536 可能相差个位数。
