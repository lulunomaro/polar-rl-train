# MOD4v3俯仰短时预测修复：40分钟实测

本段PPO耗时 1381.904s；两段累计2401.152s（原40分钟授权）；每5分钟完整PPO/Adam/RNG检查点。冻结综合父模型保持db6e9ccf…；本轮候选不自动替换实车默认。

实验候选 model_020m.pt，SHA 9575c3d0eb5dd063e7f9746e699b88fbc373ad5d5430cab35b7f57316e3eb779。

| 地形 | 父启动峰值° | 候选启动峰值° | 父急停峰值° | 候选急停峰值° | 父RMS° | 候选RMS° |
|---|---:|---:|---:|---:|---:|---:|
|random_uniform_for_rm|12.286|12.054|22.645|19.100|5.677|5.071|
|plane_for_rm|12.207|11.800|18.673|17.569|5.549|5.196|

固定平地 60/60，正向两级台阶 5/5，下阶 5/5，实际斜向 0/20。

完整结果、速度MAE、地图越界及所有中间检查点见 evidence/checkpoint_evals；不能把不同结束长度的RMS当严格等长对比，也不能把名义回放当fullDR毕业。

原因与奖励实现见 README.md、evidence/ROOT_CAUSE.json、evidence/diagnostic_causal/ROUGH_PROBE.json。
