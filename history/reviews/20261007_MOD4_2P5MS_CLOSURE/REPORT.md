# MOD42.5ms闭链分布与SCUT原5ms参考

用户明确要求“测试一下2.5mm的跟华南虎对比一下”，按本会话物理步长2.5ms解释并实际执行冻结诊断。当前正式1ms训练、所有旧2ms/2.5ms随机PPO拒绝和原2mm合同保持，无PPO/预算交易或生产修改。

| 指标 | MOD4 2.5ms全部物理帧 | MOD4此前5ms | SCUT原5ms参考 |
|---|---:|---:|---:|
| 中位数 | 0.532108mm | 2.090600mm | 0.068648mm |
| P95 | 1.505245mm | 5.882711mm | 1.805160mm |
| 最大值 | 1.596579mm | 6.251494mm | 10.250406mm |
| >2mm采样比例 | 0.000000% | 52.145312% | 3.757986% |
| 单闭链连续>2mm最长 | 0.0000s | 20.0000s（超时截断） | 5.5300s |

完整32env×30秒×6闭链×12000物理帧，共2304000个采样，超限0。没有非有限值；保留的原其他task终止0次，timeout32次。mimic最大0.001691456rad。独立每帧原始PhysX transform+float64四元数旋转，距原task公式最大差0.001880558mm。最大位置{'frame': 1013, 'env': 22, 'joint': 'right_gas_closure'}，各闭链全窗口和reset边界完整保存；连续超限不能跨reset拼接。没有超限时最长值0，不虚构事件。

## 采样可比性

主结果使用2.5ms每物理帧，MOD4旧5ms/SCUT原5ms使用5ms每物理帧，均覆盖完整30秒和32env/6闭链。另取本次2.5ms数据中每个共同5ms端点e[1::2]，没有挑选失败或半段：median0.532001mm、P951.505255mm、max1.596579mm、>2mm0.000000%、最长0.0000s。这个统一端点列只有5ms采样分辨率，不能替代主结果所有更细物理帧。

## 来源和实际参数

来源仍已验证24061 SHA6457195e25682c8059e2a9be7c7fb4531299216874ab8100014a9cf75f7f8b7b，完整USD694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87/import_contract/全部引用原样。实际31body/30treejoint/6闭链，每机器人solver16/4，192闭链真实启用。202原runtime+alias/资产共207个immutable文件逐字核验；新probe以已有效的5ms修正入口为基线，只修改请求dt、decimation、帧计数和持续时间单位，反向替换逐字exact。生产clip_actions6仍执行，真实硬件gain后torque-speed限幅保持。

MOD4两次使用相同checkpoint、seed20261002、white_v3、D1D2 sensor噪声/episode偏置、原站/直线/pure/world平地命令范围。初始完整root/q、实际模型参数及sensor recipe独立重算exact。控制100Hz；现在dt2.5ms×4，原5ms×2；5ms积分bin/三history保持，PD/COM/3500N每米弹簧/armature/reward公式不改。只在隔离冻结诊断将2mm终止变成shadow，所有物理闭链和其他实际任务终止保留。不是production admission。

SCUT列明确复用已实际完成并Git登记的原V14_2/model15000/savedcfg32env30s试验，不新重跑。SCUT仍dt5ms×4=50Hz、solver12/6、其原模型/任务/DR/noise/delay；共同当前Isaac6.0.1/IsaacLab6.1.14。这不是同一机器人/策略/参数的纯因果对照，也不是SCUT作者原engine build。不能把SCUT10.25mm最大值当MOD4放宽阈值的授权。

本MOD4策略是在1ms学习的，此处是冻结推理直接换2.5ms的响应。30秒确定性回放不覆盖20k随机PPO、随机动作或长期失效概率；历史2.5ms PPO closure失败与2ms长段失败原样保留，不能据本单次诊断恢复采用。正式训练仍1ms。

只有本线程已闲置且无孩子的3060评测slot被借用，共享单GPU锁，诊断结束后恢复原demand-start任务。可能有刚发布的正式stable结果在队列中，恢复后自然继续，不干预4090。完整NPZ/weight/USD/ZIP仅SHA索引，源和JSON读回归档；凭据不归档。
