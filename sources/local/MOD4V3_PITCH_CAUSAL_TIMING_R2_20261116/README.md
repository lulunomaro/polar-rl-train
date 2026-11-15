# MOD4v3俯仰时序修正R2

用户提供审查后，已在实际训练SDK源码中确认：pre_physics后执行物理，再episode_length_buf+=1，再_get_rewards。第一阶段新预测窗口据此提前20ms。

修正：在发出动作时捕获episode age，奖励和阶段统计只读取该age，reset清空。其余奖励权重、指令、35/78/6、模型、电机、solver、DR、保留教师均不变。

继承第一阶段安全保存的完整PPO/Adam/RNG；本段只用原40分钟剩余额度：

{
  "original_authorized_seconds": 2400,
  "phase1_seconds": 1019.2484555244446,
  "phase2_seconds_cap": 1380,
  "sum_requested_phase_seconds": 2399.2484555244446,
  "phase1_trial": "MOD4V3_PITCH_CAUSAL_REPAIR_40M_20261115",
  "reason": "Confirmed actual SDK increments episode_length_buf before rewards; fix20ms transition cost alignment; do not grant new40m",
  "phase1_final_sha256": "8ef93eb9cb06dfcef23f20713b4890400d53d4cfc69b60849d23b6d33512ae2c",
  "no_new_training_authorization_needed": "Only unused portion of original explicitly requested40min",
  "phase1_original_launch": "2026-11-15T23:44:29.659133+08:00"
}

附加物理对照已推翻“20度为已证实硬极限”的说法：0.4m/2.2m/s，反应式100ms轮动作配合可将首停峰值22.64→16.41度、18.67→15.63度，0.5s速度亦未恶化。该对照仅诊断，不叠加到本轮策略或部署输出。

Critic loss跨配方比较不能证明严重发散；teacher MSE下降不能单独证明梯度主导。5分钟台阶3/5为真实回归，不计为通过。当前没有俯仰修复成功结论，不自动晋升。

另修正float32余数边界导致窗口多一拍的问题：所有阶段判断使用50Hz整数tick。边界回归确认2/3/5/6/8/9秒切换均覆盖恰好20个动作，不提前罚上一条命令。

实际PPO开始：2026-11-16T00:06:13.071270+08:00；计划结束：2026-11-16T00:29:13.071270+08:00。首迭代actor已改变，完整17项Adam恢复，新增0.2秒预测俯仰成本系数60已在原生奖励实际生效。
