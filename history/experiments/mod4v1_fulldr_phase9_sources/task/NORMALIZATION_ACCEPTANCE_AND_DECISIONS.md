# MOD4v1统一：验收分层与后续决定

## 证据来源与新旧阈值

本表依据当前项目的[专家原验收定义](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/FROZEN_EXPERTS_400N50_SKILL_SUPERMIMIC_CONTINUATION_V189_20261031/reports/EXPERT189_SAVED_FORMALS_AND_SKILL_GAPS_ACTUAL.json#L118-L139>)及[当前根约定](<C:/Users/lulu/Desktop/claude/mjcf/AGENTS.md>)。历史报告2mm保留；新任务按人类更新使用10mm单环境episode reset，mimic保持0.01rad，2.5ms/TGS32,4/F32不变。没有新增全批微米/FP64/逐位物理健康门槛。

## 四个独立状态

1. **新资产身份**：真实载入USD2c421a8e…与契约bae3203a…，不是旧资产重命名。计数、质量/COM/惯量与新资产对应；geometry/时钟/硬件包络明确。nominal native8通过只支持这一层。
2. **完整DR/恢复协议**：实际目标SDK已安装原D0–D7，原命令/随机源/队列/反馈/PD/弹簧/COM逻辑执行；源权重、critic、STD、17Adam、保存LR、原固定SI保持；源缓存一次byte/hash/decode、ONE原fresh reset；新constructor nominal未换回旧值。Fresh80无PT只能支持组件/配置应用，不等于原20k checkpoint恢复。
3. **任务保留与技能表现**：在每个专家原任务上执行完整独立评测，记录自然command UID、完整episode/command、失败pre-reset端点与union、曝光和窗口完整性。执行通过、保存格式通过、partial窗口、旧技能缺口均不是技能毕业。
4. **合格派生冻结**：真实新任务保存/安全退出→立即运动回放→独立评测→依据原标准决定继续/修复/冻结。旧冻结不覆盖；新派生明确原模型SHA、新plant SHA、新DR/命令/时钟和真实评测引用。SuperMimic端口/学生转换另列，不从上述层次自动推出。

## 各专家的范围

| 专家 | 保留任务与恢复范围 | 当前证据范围 | 仍需观察 |
|---|---|---|---|
| E0 | 原平地/all，站立、移动、纯转、world与transition；原133bank按height过滤74并随机选择；不混入H1跳跃 | 专属新源CPU静态完成，GPU1 fresh80部署；attempt1因本任务W35原EX资源等待退出，未SDK | 新runtime真实DR/完整恢复、原各模式完整command/cycle、运动回放与独立评测 |
| W35 | 原RM70/CAD70起伏域、原低速body命令/stand比例、原pose34与脚印witness；新plant2c/bae | nominal native8、RM70 fresh80实际DR/native24、原20k全状态/ONE reset/newnominal/35,38,6已通过 | 当前1600controls/32s SAMEUID窗口、源/17Adam末端不变、telemetry完整、真实route/失败事实；其余原flat/world/signedyaw/pure/transition域未曝光则仍未知 |
| E2 | 原world-direction/signed4、phase_elapsed/private_mode_rng，再接原D7链 | 新源精确producer/入口核对中，当前不是实际运行结果；保存LR用0.00022500000000000002 | 正/负yaw完整周期、world方向、直行/零yaw原缺口、完整DR与新plant保留 |
| E3 | 原13种fallen recipe、phase/effort-owner/命令/随机源，非E0或W35配置 | 原selected源元数据；新派生未实际运行 | 每个原recipe曝光、控制所有权与真实恢复/失败边界，不能从少数recipe推广全部13种 |

## 原技能标准，不新增任意毕业率

- world along/cross误差使用 `max(0.03, 0.1*V)`。
- signed yaw误差容许 `0.2rad/s`，要求完整同一command的有符号周期。
- 观察catalog route goal只是事实，不追加新奖励、reset或技能门槛。
- 原观察器将W35 rough32s的 `full_expert_skill` 固定保留UNKNOWN，并明确未曝光域；审查时不把它强改成全专家合格。
- 原E0“18”是评测矩阵，不是18个独立actor。剩余H1_normal_PPO86B、E1_CURB20、E1_SLOPE5是须join当前exact producer的历史线索，保留pending，不能悄悄从“全部冻结专家”范围删除。

## 按实际结果行动

- **恢复/SDK失败**：保存raw错误、当前来源与一次读取计数；仅针对真实API/依赖/协议问题另建新unused版本与purpose。原once不重放，原false不覆盖。
- **执行完成但32s/字段/曝光不完整**：标partial/unknown，保留失败prefix与实际窗口，不制造全32s或全技能通过。下一轮沿既有边界/原指标补足，而非添数值健康关卡。
- **执行完整且原技能保留达标**：可以形成明确范围的MOD4v1派生冻结；如果没有需要修复的性能退化，不为“适配”字面要求凭空增加PPO更新。
- **真实性能不足**：用新Task/Ready/GO、唯一原canonical owner和实际资源启动有限PPO适配；不改原奖励/协议来伪装通过。source/deadline/学习计数/保存/childwait/费用真实记录；保存后立即回放独评再决定下一轮。

## 两张GPU与账本

找空卡只赋予资源使用，不增加授权秒数。每个任务须实际private锁/原finite环境租约和fresh资源检查。当前W35 evaluator持有原finite EX时，E0等待其自然退出，不偷改EX/SH；E0 attempt2纯元数据waiter不持卡不读预算，不会把等待当模型验证。学习仍只能唯一原writer，禁止第二canonical或并立费用表。

原D6是gas damping，并非全部joint friction覆盖；MOD4v1质量/COM/I来自本轮已声明的修正与点质量近似，不宣告完整新CAD分组校准或真实车鲁棒性已经证明。
