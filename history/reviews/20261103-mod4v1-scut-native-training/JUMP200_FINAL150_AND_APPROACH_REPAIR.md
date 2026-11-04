# 单200mm跳台阶：final150实际结果与停滞奖励修复

2026-11-05 00:44授权接续覆盖：人类回复“允许100小时”。按累计最多100小时、每小时完整保存/安全退出/独立80与实际回放、据证据修复后接续，不再逐小时询问；仍受原canonical真实余额/reserve约束，不给账本加时。00:40实际余额220,552.54286623秒、reserve86,412.86069250107秒，扣reserve约37.26小时可用，安全退出也计费。修复版首segment已于fresh空闲GPU1创建owner1624598，20,000scene已完成，FIRST尚待唯一local61200/session54368。下文candidate待批是原准备时状态，已由本段覆盖。

2026-11-05 00:32。本轮训练与原生80局已完整结束，结果是**0真实起跳、0整轮越沿、0台顶落地、0稳定成功**。四张新实际早晚姿态图已由当前模型查看。任务仍是从地面跳上单个200mm直角台阶；原地站稳、少摔倒与到达8秒上限都不算完成。

原授权小时从2026-11-04 22:11:34.580026开始，固定SAVE23:11:34.580026、NOMINAL23:16:34.580026。首attempt的命令模式恢复失败0PPO已保留；修复attempt02只用了原窗剩余。实际final于23:10:11.472083完整保存，训练关闭23:10:37.489821；原owner随后立即独立80，于23:12:59.195682完成，23:13:00.160949 ownwait/settled/released。此前等待另一聊天读者仅延迟了本地结果回传：2026-11-05 00:13:43完成正式传输，训练窗没有延长。

有效训练为70新PPO、33,600,000条样本、13,440个physics callbacks、1,400新Adam步，iteration80→150、原Adam1600→3000。FULL_V4 final40,556,699B，SHA `d0735d97edcfed6dd627e810f2a75e355674339713fb6e28955535a95e11b2f2`，actor35/critic78/STD/17项Adam/LR、7个组件、命名与全局RNG、动作队列及全局计数器均保存。新constructor nominal保护保持。完整WORKER316,853B SHA `d967a78fe6feeaa5b4faafd6152f07ac8d6a3fc030d53619292b1aa4d73d4973`，EVAL15,592B SHA `3f35d670458c87bdee10edc02da95abdd97c408ddf7e8fe8d5231cfed3f5e1de`，均0实际错误。

独立80使用新DR、seed9137、400Hz实际接触和姿态，全部399controls=7.98s原任务timeout，0接触终止/闭链/mimic/数值/raw异常重置。目标与CAD差值全部合规。41局触发过起跳请求，只有1.7419%的有效端点处于push/tuck阶段；真实地面支持后的flight_id均0。root最远x0.53253m，未越过x0.8m台沿，实际台顶接触力全0。选例env0/40/41几乎留在出生点；env1缓慢前进到x约.511m后停止。出生后从.38m落到约.25m是落地，不是向上起跳。

实际平均前进速度0.03730m/s，51.77%的控制端点水平速度低于.03m/s，固定前进命令仍为.6m/s。原地idle端点平均每步仍有0.082479奖励；五项姿态/速度/偏航/高度正奖励贡献为主，上推/峰值奖励稀少。这支持“停在台沿前仍能得高回报”的任务奖励缺口；不能归为原生solver失败，也不能把训练loss下降当跳跃进展。

完整模型诊断第一次错误地要求所有保存张量有限，遇到原SCUT三个permission命令覆盖向量中的NaN哨兵而退出。原失败与该版本源码SHA保留；修正读者后完成缺失诊断，总生产PT decode2次，0优化/physics。actor/critic/Adam均有限；三个NaN字段由固定源明确初始化/重置为NaN，实际应用时使用mask与isfinite，属于未设置命令覆盖的合法状态。没有修改模型或生产源码掩盖失败。

修复候选只改`config.py`与`rewards.py`：

- 接近阶段，即phase0且尚未真实落台，用`clamp(vx_body / command_vx, 0, 1)`乘五项正奖励：flat_orientation_x_exp、flat_orientation_y_exp、track_lin_vel_xy、track_ang_vel_z、track_height_exp_tight。停住不再拿满这些奖励；push/tuck和真实落台阶段保留原奖励。
- push阶段增加固定SCUT已有`takeoff_vel_z`奖励，截断3m/s、权重2。实际向上速度0时该项为0，1m/s时加权50Hz奖励为.04；保留原pushheight/pushvelocity/peak项。

没有改变动作/观测、出生关系、真实ray触发、200mm几何、起跳/越沿/台顶稳定验收、增强物理/DR/PD/DC/CAD或PPO。12项jump200必要CPU检查通过，包括原地与向前回报排序、起跳/落台不被进度门抑制、真实向上速度区分、爬台与出生坠落反例；8项旧阶梯回归通过。CPU合成检查不是新原生技能证据。

保存轨迹的有限离线核算得到：新进度门在旧实际轨迹上的平均值0.08659，在idle低速端点平均0.01182。原五项奖励只保存了active平均，没有逐环境完整项，不能据此声称精确的新总回报或新动作；离线核算0NN/0physics/0PT。

候选目录`N/env20000_jump200_approach_push_1h_20261105`已准备两module+owner/entry/PLAN共5小文件、55个sharedSHA引用。source为本轮有效原生fullfinal150/Adam3000，完整same20k恢复，不重置STD或单轴，不使用原生失败权重。它当前`pending_human_additional_hour=true`，0INDEX/0LAUNCH/0GO，入口在准入前拒绝未批准的新小时。原批准窗口已结束；新的3600save+300exit需要人类另行批准，同一原canonical余额/原reserve/锁不变。

实际证据位于attempt02/reports/POSTROUND_FULL_RETURNED、POSTROUND_FORMAL_TRANSFERS、FINAL_COMPLETE_LOG_ACTUAL、ACTUAL_JUMP200_FINAL_LEARNING_AND_ALL80_REVIEW、FINAL_REVIEW_LOCAL_FINITE_ASSUMPTION_ERROR、FINAL_REVIEW_PERMISSION_SENTINEL_SOURCE_CLASSIFICATION、JUMP200_APPROACH_STALL_REWARD_REPAIR_CPU与JUMP200_STALL_REPAIR_OLD_STAIRS_REGRESSION_CPU；四图见evaluation/recorded_native与recorded_native_late。所有文本按NATIVE_EVIDENCE_INDEX收录，PT/NPZ/图只真实路径、大小、SHA索引；归档不再读PT或重跑评测。
