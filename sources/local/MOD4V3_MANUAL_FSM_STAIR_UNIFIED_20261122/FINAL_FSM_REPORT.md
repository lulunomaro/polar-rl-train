# MOD4v3 手工 FSM 第二阶段实测报告

**第二阶段完整验收未通过；候选保持实验状态。** UTC：2026-11-22T10:15:37.883899+00:00。

第一阶段完整报告保留于 `STAGE1_R9_REPORT.md`（SHA256 `e7af69a27ce776cca06f683849a6c35cd40df0ee5bdd9fe67efa0f1332e98a47`），根文件及视频历史保存在 `evidence/stage1_r9_archive/`、`evidence/videos_stage1_r9/`。

正式承载合同采用原始 400 Hz 有符号法向力，每 8 子步构成一个不重叠的 20 ms 窗口；左右轮分别均载 >5 N。双阶一级至少 5 窗口，末段顶面接回 E0 后至少 20 窗口；双轮及车身真正进入最终顶面，全程无摔倒或滑落。原始 2.5 ms 连续计数并列保留，未作为正式门槛。

| 验收 | 实测 |
|---|---:|
| flat60 | 60/60 |
| flat / rough L9 | 16/16 / 16/16 |
| 0.8–3.0 m/s 关 C 巡航 | 10/10；台阶泄漏 0.000% |
| 20 ms 窗口严格上阶 | 60/320；0-DR 57/80；Full-DR 3/240 |
| 物理越阶无摔 / 无摔且无滑落 | 122/320 / 118/320 |
| 原始子步诊断通过 | 0/320 |
| 未按 V 的矩阵提前激活违规 / 留出违规 | 0 / 0 |
| 实速跳跃 | 5/5 |
| 四支原速视频 | 通关全部通过=True；逐帧解码=True |
| 启动器 12 图 / 受保护资产 | True / 6586 份通过=True |

| 地形 | DR | 窗口严格通过 | 无摔物理越阶 | 原始子步诊断 |
|---|---|---:|---:|---:|
| curb_11 | 0 | 27/28 | 28/28 | 0/28 |
| curb_11 | Full | 2/84 | 49/84 | 0/84 |
| oblique_20 | 0 | 0/4 | 2/4 | 0/4 |
| oblique_20 | Full | 0/12 | 0/12 | 0/12 |
| oblique_20_negative | 0 | 1/4 | 2/4 | 0/4 |
| oblique_20_negative | Full | 0/12 | 2/12 | 0/12 |
| rm27_east | 0 | 0/3 | 0/3 | 0/3 |
| rm27_east | Full | 0/9 | 0/9 | 0/9 |
| rm27_east_400 | 0 | 1/3 | 2/3 | 0/3 |
| rm27_east_400 | Full | 0/9 | 0/9 | 0/9 |
| rm27_west | 0 | 0/3 | 1/3 | 0/3 |
| rm27_west | Full | 0/9 | 0/9 | 0/9 |
| rm27_west_400 | 0 | 0/3 | 2/3 | 0/3 |
| rm27_west_400 | Full | 0/9 | 0/9 | 0/9 |
| step_20 | 0 | 28/32 | 29/32 | 0/32 |
| step_20 | Full | 1/96 | 5/96 | 0/96 |

受控训练 `fsm_r10c`：1198.912 秒，86 PPO / 1032 Adam；末段 target DR=1.0，实际启用完整 DR 的环境 2015/2048。所选快照本轮计数为 67 PPO / 804 Adam，未将末轮或目标 DR 标签当作独立毕业。
前 3 次完整更新只预热 critic；actor 从第 4 次更新开始变化，首次真实变化证据见 `evidence/FIRST_R10_ACTOR_UPDATE.json`。
原生轮中心粗边界提前激活计数为 442100，原始值完整保留；CPU 全几何预接触矩阵另列，二者不混为同一个指标。

最终入口：`D:\claude2\fangzhen\Run_MOD4v3_ManualFSM_Unified_WASD.bat`。候选 `weights\E_stair_stage2_gate_final_fsm_r10c_model_015m.pt`，SHA256 `3a95e86e50b25eac19e8e1b5dfe22745534a20eeee1b3ea8685b650592deb3cd`。选择依据见 `evidence/STAGE2_CHECKPOINT_SELECTION.json`，没有把最后保存自动当作最优。

E0 现完整加载冻结 `c874a1af` 与 `b271cafb`，按 0.32–0.40 m 混合并左右对称化。160 个正反标定点的最大拟合误差为 0.0248 m/s。高速低姿会平滑升至 0.32 m，高速倒车会平滑降至 0.32 m，避开已测出的倒车折返；因此高速下的有效站高与滑杆站高可能不同。DECK_SETTLE 为 0.31 m，阶面腿目标只在 50 Hz 策略侧平滑。物理 400 Hz、腿 PD 100 Hz、轮 400 Hz、电机包络、六维动作和机器人资产均未更改。

完整 RM 原图仍用于 CPU 验收。GPU 精修采用原图走廊的离线碰撞剖面，不向 FSM/actor 输入地图位置、射线或真值；FSM 仅使用 obs35 和操作者意图，actor 仅使用 obs35+420 历史。

首次高密度训练网格预检烘焙失败，零更新记录和显存释放证据保留；后续合格的 600 步零更新预检及受控训练分别记录。`evidence/TRAINING_CLOSURE_STAGE2.json` 列明真实 PPO、Adam、时长及关闭状态，不能将失败预检算作训练。

首轮完整 CPU 矩阵为 60/320，保留在 `evidence/stage2_full_before_integral_gate_fix/`；其中唯一 dr1729 提前激活有 14 个原始子步。随后将受阻积分的平均俯仰下限由 -0.02 收紧到 +0.02，重新比较受影响的 Full-DR 检查点，并重新模拟最终整套验收。最终门控另做 600 步、零优化器的 GPU 复核，通过且已关闭=True；未追加 PPO。

训练安全关闭=True。原始窗口重算 320/320 通过=True。

完整 RM 名义六点的出生航向未见错误；中心一级踏面长度西/东约 0.730/0.736 m，短于 A–A 的 1.20 m。原图采用分块高度场。多例二次触阶时 E1 已激活，东入口 1.2 m/s 的 TREAD_BRIDGE→E1 重接手约 45 ms；仍出现转向漂移、二级越阶不足或上台后没有恢复 E0 承载。不能统一归因于“未二次触发”。逐点证据见 `evidence/STAGE2_RM27_FAILURE_DIAGNOSIS.json`。

原始 2.5 ms 连续性诊断仍为 0/320，真实高频腿颤的彻底消除尚未验收通过。

详见 `FSM_STAIR_BENCHMARK.json`、`PREMATURE_SQUAT_AUDIT.json`、`FSM_JUMP380_CHECK.json`、`evidence/videos_final/VIDEO_MANIFEST.json` 及全部逐点原始轨迹。

尚未达成：严格上阶失败 260 例，矩阵提前激活违规 0 例，留出违规 0 例；四视频全部通过=True。具体失败保留，未宣布毕业。
