# 瞬时俯仰角速度平方修复：40分钟实测

实际PPO耗时 2409.381s；每5分钟完整PPO/Adam/RNG检查点。冻结综合父模型保持db6e9ccf…；本轮候选不自动替换实车默认。

实验候选 model_030m.pt，SHA cc539b52edac4ff9af5f613f82ecd79baa728cbcdceb01feacb2a2a1738c0493。

| 地形 | 父启动峰值° | 候选启动峰值° | 父急停峰值° | 候选急停峰值° | 父RMS° | 候选RMS° |
|---|---:|---:|---:|---:|---:|---:|
|random_uniform_for_rm|12.286|12.111|22.645|22.114|5.677|5.135|
|plane_for_rm|12.207|11.934|18.673|18.078|5.549|5.310|

固定平地 60/60，正向两级台阶 4/5，下阶 5/5，实际斜向 1/20。

完整结果、速度MAE、地图越界及所有中间检查点见 evidence/checkpoint_evals；不能把不同结束长度的RMS当严格等长对比，也不能把名义回放当fullDR毕业。

原因与奖励实现见 README.md、evidence/ROOT_CAUSE.json、evidence/diagnostic_original/ROUGH_PROBE.json。
