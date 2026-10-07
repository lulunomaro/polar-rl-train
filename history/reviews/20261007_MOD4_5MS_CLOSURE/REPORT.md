# MOD45ms闭链完整分布诊断

用户要求在3060用自己的模型/参数测量中位数、P95、最大值、超过2mm的采样和单个闭链连续超过2mm的最长时间。本次只冻结推理，不做PPO或预算交易，不调整4090正式1ms训练。

## 实际结果

| 指标 | MOD4 5ms | SCUT原模型5ms参考 |
|---|---:|---:|
| 中位误差 | 2.090600 mm | 0.068648 mm |
| P95 | 5.882711 mm | 1.805160 mm |
| 最大误差 | 6.251494 mm | 10.250406 mm |
| 超过2mm采样比例 | 52.145312% | 3.757986% |
| 单闭链连续超过2mm最长 | 20.000 s | 5.530 s |

MOD4实际6000个物理帧×32环境×6闭链=1152000个距离样本，超限600714个。每5ms读取原始物理链接位姿并通过独立float64四元数旋转核验全部帧，最大距离公式差0.001851301mm。数据/动作/reward均有限，原任务终止0次，正常timeout32次；终止原因完整保留。mimic最大0.001691456rad。最长事件{'env': 0, 'joint': 'left_gas_closure', 'start_frame': 0, 'end_frame': 3999}，遇实际reset中断累计，未跨episode拼接。

## 明确范围与限制

- 来源是已验证sensor正式24061，SHA6457195e25682c8059e2a9be7c7fb4531299216874ab8100014a9cf75f7f8b7b。完整生产USD SHA694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87及import_contract/引用原样。
- 207个immutable源码/资产文件逐字核验。物理dt从1ms诊断改为5ms、decimation从10改为2，控制仍100Hz，TGS/solver16/4、原PD/弹簧/硬件torque-speed限幅保持；原接触5ms积分窗口/三history保持。
- white_v3质量惯量.9–1.1、六输出.9–1.1、轮μ.7–1和D1+D2噪声/四腿episode零偏按现有recipe，原站/直线/pure/world命令混采，没有地形/DR扩大或训练。
- 仅在本冻结诊断把原2mm closure终止变成shadow记录，六闭链仍真实启用，共192条；其余原任务终止完整保留。这样不因2mm立即重置而截掉持续超限数据。不是production admission，不能据此改2mm正式合同或恢复已拒绝2ms。
- 本policy是在1ms训练的，结果是直接移到5ms的响应，不是5ms专门适应训练或策略毕业。
- SCUT参照来自已归档独立32环境30秒原V14_2/model15000/savedcfg测试，控制50Hz、solver12/6、不同模型/DR/任务/原训练来源；共同使用5ms距离采样和当前Isaac6.0.1/IsaacLab6.1.14。不是同一机器人/策略的因果A/B，也不是原作者发动机版本复现。
- 长持续误差在最长已观察窗口内成立，不能把未结束的片段称完整持续寿命。全窗口/各闭链/所有reset保留，不用剔除初态或失败片段替换主结果。

## 诊断入口修正

第一SSH子启动在无borrow/GPU/worker变化前退出，随后使用Windows隐藏detached启动。首GPU入口模块路径顺序误选旧0.5ms模块，首次reward计算拒绝，原错误保留。path_review及health_reader漏用了原RslRlVecEnvWrapper clip_actions6，原始动作反馈在.41秒放大到2.2e19并造成action_rate/action_acc溢出；这两份结果不是有效生产参数比较，不能推断是5ms导致物理NaN。当前有效clip_contract_review恢复了原torch.clamp(actions,-6,6)，用实际wrapper源码逐字证明，6000帧全部有效。launch读取SSH45s超时并不代表detached探针失败，按自己的实际进程/receipt继续读回，没有重复launch。

完整weight/NPZ/USD/ZIP仅SHA索引，原raw在隔离诊断目录及本机保存。本次GPU锁仅借用本线程已经闲置且无孩子的3060 worker；每次退出后恢复原demand-start评测任务。无4090操作、正式配置修改、PPO或canonical账本交易。
