# 唯一训练记账权迁到双4090：待确认方案

双4090上的两路实际源码、SDK、RSL、复旦参考目标CPU检查及原valid_ready均已通过；没有启动owner、节点、GO、GPU学习或新计费。H1新实验采用复旦跳跃轨迹重定向后的部分模仿目标，通过原生SuperMimic在MOD4真实环境中学习。另一张卡准备继续E3 PPO。

单卡主机已由人类确认切换为Windows，旧Linux原始账本当前不可达。本方案不将旧SSH密钥替换为Windows密钥，也不把旧账本摘要称为完整逐字节迁移。

## 拟执行的唯一权威交接

- 旧权威：210 Linux的 `/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json`。确认后将其退役为历史来源，之后不得再由旧owner计费或开训；以后恢复Linux也不得恢复该旧权威。
- 新唯一权威：双卡72的 `/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json`。新owner的两把独立记账锁位于同一state目录，原两张GPU的private锁和共享环境准入锁继续使用。
- 从已核真的完整83B结清余额接续：**595256.8240613937秒**。已计费累计 **1672743.1759386063秒**；总授权 **2268000秒**、**9次扩额**，没有新增预算、退款、取整、空档费、重扣83B费用。
- 历史费用和原始报告继续以既有Git完整归档为依据。新账本明确标注“历史余额接续”，不虚构当前没有完整收下的旧账本正文、completed_segments或原扩额对象。
- 最后核真的83B独立费用合计10943.796510219574秒，original owner及子进程全部退出、canonical active=None、原锁释放。当时原账本SHA为 `fa47cf989898d9c771f35dcaa1e25330456694fda044502aaf82a5887b205bb1`；这些均为历史闭合证据，不冒充今天从旧Linux读到了新账本。
- 双卡各任务仍由同一个新owner从实际GO到实际terminal分别计费且只记一次。3900秒生命周期、3600秒保存、300秒退出边界不变；真实超界也必须照实际费用记录、duration标false，不截断、不拒绝计费、不退款，也不冒正常source资格。
- 保留严格预算底线86412.86069250107秒、64800安全余量、Windows待结9400.860692501068秒和unknown512秒，其他物理、完整保存、非有限、硬件、源模型和成功门槛不变。
- 先完成新权威源码检查、目标路径无旧权威/owner冲突、两把新锁和GPU资源核真，才能启动双卡任务。任一步失败保留原错，不创建第二个权威或第二writer。

## 当前授权状态

**待人类明确确认此唯一记账权迁移与旧Linux账本退役。** 当前没有创建、复制或激活新canonical，没有启动新训练。此前“在双卡工作”已授权源码/SDK和训练准备；本方案单独说明原AGENTS禁止复制canonical的例外边界，避免两个账本并行。

需要本次确认的原文依据：工作区 `AGENTS.md` 要求“不要为了归档……修改预算/复制canonical”；`polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md` 要求“不复制或清canonical”。本方案超出原固定210记账路径，不能把普通部署授权写成已获迁权批准。
