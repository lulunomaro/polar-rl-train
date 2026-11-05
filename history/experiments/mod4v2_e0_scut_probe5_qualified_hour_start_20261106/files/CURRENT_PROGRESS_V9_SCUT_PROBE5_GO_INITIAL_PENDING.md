# E0 SCUT Flat-v0：probe5 已GO，U000及一次更新仍待实证

2026-11-06 06:18 +08:00 的时间点状态。Goal664 rev5 active/armed，E0单卡串行；不启动其余八专家，不访问86，不称技能通过。

- 第三次SCUT probe已真实关闭/实际wait/原账结算/租约释放，但失败于模型结构观察器；actor实际打印35→256→128→64→6、critic38→256→128→64→1，三处ELU和Identity norm。源码及标准API支持共享ELU由默认named_modules去重这一观察缺陷；没有测得运行时对象去重数量，未删除尺寸/3ELU/alpha/完整state验收。
- `worker_e0_scut_v14_probe_v4.py`/hour_v2只改变注册路径枚举及cached Proxy快照；A4已源暂存但从未派发，保留该root和源码。其generic快照把Warp shape等同Torch向量展开shape有潜在错误，未作为失败GPU实验记分。
- 新probe_v5/hour_v3只把快照验证改成Torch view的原Warp维度前缀相等；零拷贝actual ProxyArray `.torch`、dtype/完整CPU clone保留。奖励各字段及contact历史[N,3,B,3]、网络4层/3ELU、norm/STD/Adam/LR/iter、源码ABI、native及close检查未变，没改奖励/阈值/物理/额外reset/观测/RNG。逆向源码仅这一表达式不同。`SCUT_PROBE4_UNDISPATCHED_VECTOR_VIEW_PREFLIGHT.json`保留事实；新stage通过SFTP仅确认旧A4的OWNER_STARTED/outer identity/GO文件均不存在。
- probe5非PTstage297共享文件+E0472全runtime/lib/staticNPZ；实际Linux verify_sources preflight0。新root：`/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SCUT_PROBE_ADMISSION5_FULL_LEARNER_MIGRATION_20261106_061556_1793916956983409700`。
- dispatch1793917090.0059226/controller1697223；唯一observer `pwsh-7cdb487dc583455c`。第一快照1793917093.5105917：GO=true/native_before_PT=false/learner_loaded=false/new_updates=null/error=false/parent_wait=null/qualified=null，owner未退出。GO仅资源准入，尚无U000/更新/保存/关闭成功证据。
- 只允许N20000/T24、SCUT原37权重26活跃、命令/终止/PPO原配方下的一次真实更新、20Adam、24controls；初始U000必须正式6cd全learner/normalizer等逐项完全一致并一次源IO，随后U001完整保存和实际父wait/原账结算释放。禁将probe/AST/GO当小时训练、技能或毕业。
- 原singlewriter/authority两EX/GPU0privateEX/trainfiniteSH/reserve86412.86069250107/3900-save3600-headroom300/preGO1800不变，无foreign signals/清锁/C复制/退款/扩预算。只当前E0。
- `prepare_e0_scut_original_hour_entries_v2_once.py`仅新条件生成器，绑定probe5实际闭合与所有初始验收/1更新，再选择修正的hour_v3；未执行，小时未stage/dispatch。不能使用旧错误的第三/第四probe或未修正hour_v1/v2作为新小时准入。
- 最近verified Git `83d9178063bc6901da670fc3f1fa94cc13667e95` / `trial-20261106-mod4v2-serial-e0-scut-source-probe`。之后SDK源、Proxy/terminated alias、第三模块观察器失败、A4未派发、probe5修复及真实结果待下一meaningful feature-only归档；main只读，不为Git开权重或重放旧once/物理，不造verification链。
