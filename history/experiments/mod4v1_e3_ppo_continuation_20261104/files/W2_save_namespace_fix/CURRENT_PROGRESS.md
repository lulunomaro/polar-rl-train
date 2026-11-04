# E3 单独续训：当前接管点

## 当前请求和 Goal
用户2026-11-04 14:06要求“继续训e3”。新 Goal `goal-5e9cd92c-d0a3-40d1-92e9-33913df2683d` revision1，active/armed，max8轮。只续E3原PPO/fullDR，首个成功窗最多20实际更新，随后原N80科目及MuJoCo后收上电对比；不恢复旧SuperMimic重构/其它专家。旧九专家评测Goal已complete revision20。

## 实际进展
- W1曾进入原20k恢复和首个保存，但旧保存器要求源检查点没有`posttrain_finite20_v1`，候选67ee已经带该字段，故在PPO调用前报错。producer实际更新计数缺失(null)，代码位置表明尚未调用PPO；不是一个技能失败率。W1实际关闭、内外wait、计费结清与释放均已保存，成本不退回。
- W2仅把本轮保存元数据换成按run_id唯一的命名空间，旧元数据和未知根仍完整保留；其它PPO/恢复/保存状态操作不变。没有改奖励、DR、命令或物理。
- W2实际parent `1599468`，controller `1599461`，worker `1599480`，单4090 UUID `GPU-16828f91-2b45-b646-8dc0-9481138e2842`。
- W2 root：`/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_PPO_CONTINUE67EE_W2_SAVENAMESPACE_20261104_142648_1793773608384136500`。
- 最近读取的生产回执：epoch1793774310，已完成6真实PPO更新/120 optimizer.step/2,880,000 transitions；iter43116/Adam866580；完整保存SHA `7c445702986d576126c3777e1fd6d79336931c903a8aaf2ad63a44cfd3a0d9d5`。这是当时快照，后续以CURRENT/最终回执为准，不推算更新数。
- 当前选中母版/演示模型1cd不变；续训输入是上一轮完整PPO候选67ee（iter43110/Adam866460/LR.0002562890625000001），避免重复母版已跑的20步。不是失败的SM模型。

## 正在运行的唯一相关 job
`pwsh-76d0e0ca11a34bf0`：本目录[collect_e3_window_once.py](<mod4v1_e3_continue_v2_20261104/collect_e3_window_once.py>)，30秒一次有限元数据观察；最终写TRAIN_CLOSED_RESULT。先用job_output收取，勿重开collector/parent/旧root。
W1 stage/dispatch/collector和W2 stage/dispatch的所有job都已经collected。旧MuJoCo回放窗口不属于训练job，保持不动。

## 完整关闭后的下一步
1. 检查[TRAIN_CLOSED_RESULT.json](<mod4v1_e3_continue_v2_20261104/TRAIN_CLOSED_RESULT.json>)真实存在且training_execution_qualified，producer完整保存、内外实际wait、原成本结清/释放，RC0不单独算成功。
2. General Python314运行本目录stage_e3_frozen_after_close_once.py，然后dispatch_e3_frozen_once.py、collect_e3_frozen_once.py，各仅一次。已准备好E3-only原N80/seed20260928/160controls。复用原9评测源；parent及parallel_eval_safe只把组成员数9改1并更名结果标签；所有物理/接受代码不变。完整静态依赖仍拷贝，不裁剪N80运行树。
3. 可同时General Python314运行prepare_mujoco_candidate_after_close_once.py一次；它仅为新候选的功能评测读取/核验/转移一次新权重。然后用`C:/Users/lulu/Desktop/claude/mjcf/.venv/Scripts/python.exe -B -X utf8`运行mujoco_startup/test_candidate_startup.py。只重测activeE3，未重跑旧zero-torque。场景、22关节后收姿态、0–8s恢复/8–13s vx.2完全沿用基线；生产器直接写compact SUMMARY，勿为制表/Git重开轨迹。
4. 对比原E3 recovery74/normal6和本地上电诊断。旧1cd原N80为0/74；本地8s后退.85653755m、8s tilt.619625deg、5s行驶世界x+1.201986m、13s tilt1.85183deg。本地case不是Isaac/fullDR/实机资格，.36s只是一时高度/角度穿越，不是稳定起身时间。
5. 写E3_CONTINUATION_RESULTS.md及必要紧凑JSON，保留原母版及全部候选；无改善不盲目追加窗口/晋升。用record_e3_continuation_once.py合并W1/W2源码和真实失败/结果归档一次；feature-only/唯一annotated trial/远端核验，main只读。当前全部新文件Git pending，勿为归档重跑任何物理/模型/旧once。

## 固定边界
原canonical单writer/charge_values、authorityEX/privateGPU_EX/finite trainSH-evalEX；reserve86412.86069250107、3900/3600/300、1800preGO。W2单GPU0原准入，原预算+7800保守门保留。入场前C remaining247559.25129890442仅历史快照，不是当前余额；不复制/扩/退账、不清锁/外国signal。父源唯一功能变化是候选真实GPU完整保存历史准入（明确不伪装为此前已重载候选），worker仍先实际完整恢复验证再进入PPO。源码/模型/H1/Registry及原接受门均保持各自版本，不hotpatch旧源。
