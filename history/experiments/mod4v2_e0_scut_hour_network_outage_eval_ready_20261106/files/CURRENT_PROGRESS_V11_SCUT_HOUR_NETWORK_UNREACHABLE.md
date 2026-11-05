# E0 SCUT小时窗：网络观测中断，远端最终状态待核

2026-11-06，Etc/GMT-8（UTC+08:00）。Goal664 rev5仍active/armed；当前只E0/GPU0/72，其余八专家、86、正式母版和旧Registry不动。该文记录观测事实，不是训练失败、训练完成或技能验收。

## 已有事实与证据等级

- 同一训练root：`/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SCUT_HOUR_FULL_LEARNER_MIGRATION_20261106_062902_1793917742719982000`。实际已观察GO、N20000 native-before-PT、正式6cd全learner加载和U000 actor/critic/normalization/STD/Adam17/LR/iter七项exact。最后收到的实际更新数为**18**；这只是连接断开前的时点，不是最终更新数。
- 原observer `pwsh-2e580d242d3c4fa8`已exit1/fulloutput collected；错误为socket10054/Paramiko SSHException: Server connection dropped。没有证据据此判远端worker退出或失败。原marker/snapshot全部保留。
- recovery1 `pwsh-2f3fe6392b7a4b50`在SSH sock.connect超时，exit1/fulloutput collected；没有重启远端训练。
- [30分钟网络恢复结果](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/E0_SCUT_HOUR_NETWORK_RECOVERY2_RESULT.json>)：1800秒有界观察中，针对已授权10.24.0.72:22的**15次TCP连接均TimeoutError**；最终epoch1793922229.3534582、reachable=false。`pwsh-45701953f3b74932`已exit1/fulloutput collected。该结果不定位主机、路由或SSH服务的具体故障原因，也不推断训练状态。
- [有界交接结果](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_HOUR_EVAL_RECOVERED_HANDOFF_RESULT.json>)：`DEFERRED_HOST72_NETWORK_UNREACHABLE_REMOTE_TRAINING_STATE_UNKNOWN`，`steps=[]`、training_relaunches=0。`pwsh-5ffa8c889f974f93`已exit0/fulloutput collected；这表示本地条件交接已如实延期，**不表示训练或评测成功**。
- 当前没有取得同一训练的`E0_SCUT_HOUR_CLOSED_RESULT_PATH.json`，没有最终完整候选、owner/child/outer实际wait、账结清或释放的新读回证据。全部保持unknown，而非0或pass。未启动新的网络巡检循环，未改远端源/奖励/物理/预算，未复制C、清锁、发信号或重放训练。

## 已完成但未执行的评测准备

唯一生成器交付后，由原始preparer两次literal源定位错误（stage原entry语句、parent env-close语句）分别fail-closed；[v1定位失败](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_HOUR_EVAL_PREPARER_V1_SOURCE_LOCATOR_ERROR.json>)和[v2定位失败](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_HOUR_EVAL_PREPARER_V2_PARENT_LOCATOR_ERROR.json>)均保留。新的v3 finisher只按实际AST坐标调整生成器字符串缩进；逆向文本检查、原资源函数AST等价和发布前全部语法/嵌入源编译检查保持。

已独占发布六个新source：[stage](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_E0_HOUR_FROZEN_stage.py>)、[parent](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_E0_HOUR_FROZEN_parent.py>)、[worker](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_E0_HOUR_FROZEN_worker.py>)、[factory](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_E0_HOUR_FROZEN_factory.py>)、[dispatcher](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_E0_HOUR_FROZEN_dispatch_once.py>)和[collector](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_E0_HOUR_FROZEN_collect_once.py>)。未stage、未dispatch、未执行评测，未创建该评测once marker。

它们只允许同一root真实合格CLOSED和FINAL.latest_complete_save==FINAL.fullsave.latest_complete_save；直接读取同一live_core迭代/Adam/LR，U000 exact7与实际资源关闭/回收证据为前提。真实SCUT hour factory+cmd配置/绑定、候选iteration、原sole reset之后reward_v4.bind保持；无20k native初始化重放/额外zero/obs/RNG，N80/1000ctrl/20260928 fullDR，原资源privateEX+finiteEX/ownerNone/reserve/1800-900-2400、actualwait/cleanup/GPUsettle保持。原grader和毕业为null，源码检查不是SDK或技能通过。

新[实际结果publisher](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/publish_scut_e0_hour_outcome_once.py>)仅完成源码写入，尚未执行；将从真实CLOSED读取实际更新、计时、候选和原生评测，缺失项保持null，不预设成功或改Registry。当前没有用它生成任何最终质量报告。

## 下一动作

恢复到10.24.0.72:22后，先只读获取**同一root**的最终元数据，检查候选完整保存、SDKclose、原child/owner/outer实际wait、费用结算和租约释放；未知时不重启、不停止、不另起同源hour。不从墙钟到时推断已保存或已释放。

实际资格全部成立后，以六个已准备source的独立新评测purpose只派发一次；原资源门重新核查；实际评测关闭后执行publisher并给真实健康/连续指标，完整E0 binary/profile grader仍null。若元数据表明失败，保留失败并停止交接，不把网络丢包改写成训练错误或pass。

本阶段网络失败/有界延期、六个source及其生成失败/修复、未执行publisher和本交接待有意义feature-only唯一annotated归档。上次已核验54530bba88477afe2e6ce480c871d3aadcb051bf；main只读，不为Git开模型/raw/geometry或重放旧once。Goal未完成；不以当前两轮的网络问题提前调用blocked。
