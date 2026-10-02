# 自主增加科目的实际进度（20:35 北京时间）

名义生产仍在原目录，trainer 7901 / supervisor 7861；未暂停、未改生产源码，
36000 秒账本未增加。最后核对 model9450，源 task SHA 24091dc3... 不变。

model9425（SHA 7f6790b227f0242ea1532d1d42a943e8396c513035f0a4fd4bde0cbf207b93d3）
完整 CPU 回读通过：actor/critic/optimizer/iter/std、68 个浮点张量有限。
独立 seed20261001、80env×15s 名义回放已通过全部已训练速度组的试训准入；
旧窗口严格门槛仍 false，不是把旧门槛改成毕业。

新候选 `/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001` 仅用于预检，
**尚未进行轻 DR 生产训练**。显式白名单已经实现：共同质量/惯量 .95–1.05，
主轮摩擦 .8–1.0，六电机输出 .95–1.05，约20%名义样本；保留原硬件转矩-转速裁剪。
遗留整套 DR 仍关闭，其余 PD、弹簧、COM、armature、关节摩擦、噪声、延迟不变。
33 个离散材质桶，先验证大规模而非假定 20k 一定能过。

`mild_parameter_readback_v3.json` 已通过 80 环境两次 reset 和 .5s 动力学预检：
质量误差约8.4e-8，惯量误差约8.9e-8，轮摩擦、非轮材质、局部 COM、
PD、armature、关节摩擦的读回符合预期，motor step noise 为0，reset重新采样。
v1/v2审计程序比较整个惯性 COM pose 的四元数导致误判；报告保留。
v3改查有明确局部坐标语义的 body_com_pos_b 和惯量张量，未修改真实COM或门槛。
DR使用独立 RNG，以免随机参数采样改变名义姿态库的随机序列。

后台 `run_mild_small_preflights.py` 已启动。读取同目录 small_preflight_status.json
并查实际进程。首份DR配对44878已在生产监督器发出9475例行回放（46597）时安全结束。
原始日志保留。v4监督器已经重新后台启动，先等待现有回放完成；之后使用
mild_paired_model9425_seed20261001_retry1.json，不覆盖首份日志。
随后在候选中关闭white_v1重放同seed名义15s，核对物理开始前完整root/q精确相同，
再补同一9425的seed20260927名义回放。读实际status，不使用已经退出的44878。
不要重复发这些探针。
此脚本只做小规模冻结评测，不启动 PPO、不暂停生产、不写训练预算。
若现有生产监督器另开回放，它会停止自己的探针并留错误记录，优先保留生产评测。

下一次完成后查看两种 nominal seed、DR配对、实际参数 readback、个体卸载/间隙/滑移。
尚未完成：128env×2轮PPO、20k材质/有限数验收、预算安全接管、新阶段30–60min试训、
Ubuntu终端新阶段对齐。不能只凭本文件宣布 DR 已开始或已鲁棒。
切换前停旧 supervisor 的后续启动权限，完整保存后结清 canonical 账本，再做大规模
预检；不要启动复制过来的旧一次性 supervisor，也不要复制新36000秒预算。

注意 DR gain 会使 computed-minus-applied 出现有意的输出差。候选已追加
wheel/leg_rating_clip_fraction、longest_wheel_rating_clip_s和独立
speed_safety_pass_gain_compensated；比较请求PD力矩×输出增益与实际裁剪后力矩。
原raw字段与旧speed_safety_pass全部保留，两种口径并列，仍为10ms采样而非子步峰值。
这次修正的是诊断，不是删掉硬件裁剪或放宽旧门槛。
最新候选源码指纹见 CANDIDATE_SOURCE_FREEZE_v2.json。生产旧源和检查点全部保留。
