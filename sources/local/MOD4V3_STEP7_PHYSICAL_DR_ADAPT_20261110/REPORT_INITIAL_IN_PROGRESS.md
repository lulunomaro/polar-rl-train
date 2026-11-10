# Step7 physical-delay DR adaptation — work in progress

用户要求从7a实际父权重加入DR继续训练并达到原任务指标。本次沿用原PhysX/PPO框架，使用独立试验目录，不改原冻结模型与旧7a结果。父权重SHA256：884cd07b3942df9c8484b905994e302906c84151f6f9c5d079a417ec98158f24。

已修正动作/传感器延迟为2.5ms物理步维护；策略仍20ms，PD仍10ms。执行目标延迟，actions槽保持原策略输出。DR保持父系摩擦50%、弹簧阻尼25%、外力25%、观测噪声25%及原有mild DR。当前适应窗的动作/传感器延迟为每回合各组采样0或5ms。本试验是既有模型的能力适应，不宣称完整SCUT DR parity。

PPO先使用固定学习率3e-5、clip 0.1、3 epochs；完整继承actor/critic/STD/Adam和RNG，加载后明确覆盖LR。没有改奖励、模型资产、电机包络、命令组合和终止逻辑。训练4096环境，时序探针4，能力评测10。

已完成的实际尝试：

- timing_probe_r1：独立support目录遗漏flat_terrain.py，尚未进入仿真；保留ERROR并补齐原有依赖。
- timing_probe_r2：通过。32次动作物理tick、33次传感器采样，actions槽误差0；三个动作切换均缓冲5ms/PD10ms。
- parent_fixed10_r1：第一科目后，评测奖励缓存的inference tensor被在inference_mode外重置；修正整个评测套件的推理上下文。
- parent_fixed10_r2：完成但初态使用了wxyz helper写入原生xyzw数组，全部能力结论无效；已改为isaaclab.utils.math.quat_from_euler_xyz。原报告保留，不转成pass。
- parent_fixed10_r3：原生四元数修正后完成基线。前进2.0/2.2为0/10，后退10/10，自转2/10，高度0.20/0.40各10/10，全部无终止。这些PhysX+训练DR结果不替代此前MuJoCo名义参数回放。

4096环境首个300秒适应窗已启动。首个完整PPO更新iteration=20839，actor确实更新、Adam17 entries保留、LR实际为3e-5，完整checkpoint SHA b79fd4db6040881386a38c713bacbb5bdfb74987982d119b906a1b04e7ef6b25。尚未完成训练后能力验收。
