# 2026-10-03 22:08：5rad/s 中间档正式试训已核验

本段优先于旧“继续4档/16450直接预检5档/5候选尚未开训”的说明。用户授权“你看着情况弄”，当前优先原地小陀螺；移动、FPS和地形延期。目标2转/秒仍未达到。

## 当前实际运行

- 唯一生产root：`/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002`。
- 独立父进程2888037/start_ticks19114965，入口`isaac/mod4/supervise_targeted_mature5.py`；guardian2888078/start19115034；单一正式trainer2889497/start19120268。这些仅定位，下一轮仍核实真实/proc的cwd/argv/start_ticks。
- 父日志`supervisor_targeted_mature5_retry1_20261003.log`；训练日志`auto_0033_intermediate5_trial45_cap5_white_v2.log`；run `logs/2026-10-03_22-03-12_auto_0033_intermediate5_trial45_cap5_white_v2`。
- 实际cap5rad/s≈47.75rpm，white_v2，站10%/直线60%/纯自转30%，左右1–5rad/s，自转平移0。物理、硬件、完整闭链reset、奖励、PPO和DR范围保持。
- 首次正式完整保存`model_16425.pt` SHA `f26f01774d483876165a6673b84a43dda24c793bcab167f52f2d2cd33a000be0`；CPU回读actor/critic/optimizer/std/iter共68浮点张量有限。不要与同名旧源或128预检权重混淆。正式manifest核实start16425、KEEP_STD1、cap5、white_v2、精确init_checkpoint路径与SHA；104源指纹全部实际一致。证据`reports/TARGETED_MATURE5_PRODUCTION_VERIFIED_20261003.json`。
- 首45分钟有效PPO段截止epoch1791038723.885104，约北京时间22:45:23，以实时status/账本为准。后续已有父进程完整保存、顺序flat/rate15秒评测，不能重复探针。当前仅正式训练和完整保存证据，不是5档确定性技能毕业。
- Rich1551130/start9346210仍读同root/status/active_log/canonical，5秒只本地文件刷新；不另开窗口。

## 为什么选择成熟16425完整策略

最新16450在5档20k×1.2秒原物理验收中tilt15.265189deg>原15deg，未启动128或正式PPO，保存拒绝报告。隔离的同16450、同seed20260927、white_v2、完整root/q精确相同的cap4/cap5对照，均在env6065/group5的直线+1.5m/s、yaw0、step34（约.35秒）发生完全相同峰值；非±5自转组导致此对照差异。控制实验只支持该具体事件与5档指令变化无关，不能推广为硬件因果或删失败样本。

预先登记的last paired mature16425（不是遍历挑权重）此前auto0023两个seed20261002/3、nominal/white_v2各flat/spin8份15秒门槛及完整初态配对通过。旧正式源：`logs/2026-10-03_19-33-07_auto_0021_autonomous_continued_cap4_white_v2/model_16425.pt`，SHA `63662952ea6be6ca6c259a0563fe2495cefc0ebadf9eb729c69ec1e92aba9075`，CPU68浮点有限。在同初态的5档20k实际物理/材料读回中最高tilt12.399391deg，原physical_smoke合同通过；旧combined=false仍保留，高差70.949mm警告未改，不声称15秒技能或实车毕业。

因此显式回退25个iteration到16425完整actor/critic/optimizer/std/iter，保留所有16450与旧6档权重。完成新的22env3秒物理检查（物理true、旧短技能false保留），明确复用上述已经完成的16425/5档20k报告，再完成新的128env两轮PPO，预检16426权重弃用，正式仍从旧16425完整续训。复用不是再次执行20k；原8份成熟配对也复用，不能记作新回放或策略改善。

## 入口和错误恢复

读取`reports/TARGETED_MATURE5_ENTRY_RETRY1_20261003.json`、`AUTONOMY_STATE.targeted_mature5`及实际进程。入口SHA `49f8d3e6f1afe53cf2ea8ac22a6fd95e7cfadbaf89633604f2ee0026da3d60d1`，104源已冻结。首次入口因为guardian的start_ticks整数未转字符串，在任何probe/PPO/账本变动前TypeError退出；原错误和原entry保留。唯一`recover_targeted_mature5_guardian_args.py`核验无孩子/无active段后仅修argv类型，并用唯一retry1 receipt启动。不能再运行此恢复、原entry、retry启动或旧一次性交接。

当前`targeted_mature5.phase=trial45`、`pending_intermediate5=null`。45分钟保存后转`saved_pending_assessment`，释放本入口锁后调用已部署的sleep_v4_intermediate5_bounded控制器进行已有验收与最长2小时PPO块。两份不同完整正式策略当前技能+flat通过，再同候选两seed nominal/white_v2的flat/spin严格初态配对，全通过才称5成熟。

原`rate_rejected=[6,5]`保留：5记录16450源预检拒绝；本次是有明确成熟源与原验收证据的单独接续，不删历史、不自动重试拒绝档。6档真实滑移/卸载问题仍未解决。5成熟后下一6仍被拒绝则`targeted_repair_hold`保留预算/权重，不能无证据恢复父或无限叠成熟4/5。三个新档连续失败回paired成熟4/white_v2。物理或旧能力退化也完整回退成熟源，保留失败权重。不得因目录名字或cached最高iteration误选PPO预检/拒绝策略。

## 6档诊断与边界

读`SUBSTEP_REPORT_20261003.md`和本机`SUBSTEP_REVIEW.json`。COM/link参考点已修且legacy并列保留，修正未消除6档失败。model16929/white_v1的3秒0.5ms actual PhysX接触读回：88/88存活、6000回调，原初态及旧逐环境数组bit-exact；低载轮缘贡献明显，但受载子步仍有滚动残余和力/滑移脉动。筛选接触诊断不是原0.15m/s全时网格代理门槛，不据此称6毕业或真实硬件认证；不把未受载轮缘代理直接加生产奖励。旧6档16929/17382/17834及拒绝记录保留，后续必须专项验收。

## 预算、恢复和巡检

唯一canonical为`/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json`，252000有效PPO秒/70小时，原36000+三条已应用72000扩展`USER_ADD20H_20261001_2341`、`USER_ADD20H_20261002_1520`、`USER_ADD20H_20261003_3RD`。此次无新增授权/扩展/清零/复制预算。22:08实际剩约86055秒（23小时54分）仅快照，实时减active尾段。冻结诊断与修复停机不计PPO，当前128和正式PPO场景加载/保存退出计同一账本。

旧父2490960、2829322及其guardian均已退出，不恢复；不能盲跑supervise_autonomy的旧一次性交接或本显式entry。突停先查实际孩子、targeted阶段、canonical.active_segment、S.active_training、PID绑定latest_complete和最后健康/log/shutdown上界，不重复结账。trainer活跃父故障先修监督，不双开trainer/20k；NaN/OOM/Xid保留完整现场/权重/账本诊断。

两小时线程巡检、健康无实质变化安静；远端父独立运行。本次真实诊断、拒绝、修复与正式部署用polar-rl-train唯一annotated trial标签归档，健康未变不造标签。预算到点原子完整保存、flat/currentDR spin/nominal spin终验、实际finished后才删除mod4-10；targeted_repair_hold有预算不删除自动化。
