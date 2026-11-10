# Step7 DR范围纠正：本轮继续记录

日期2026-11-11，Asia/Shanghai。用户指出“加的dr应该是step7的dr吧”。此前0/5ms只覆盖过渡延迟，不能称完成Step7。本阶段在旧轮完整015m checkpoint已保存/SHA核实后发SIGINT，确认旧PID退出、GPU无compute owner后，从该checkpoint恢复actor/critic/STD/Adam/RNG，另立运行目录继续。原始884cd07b谱系保留。旧轮15m之后约4次更新未恢复，实际消耗仍计入预算。

## 当前实际范围

原Step7继承轻量质量/惯量/增益/材料、关节摩擦50%、弹簧阻尼25%、外力/力矩25%、观测噪声25%。这些保持集中修复版实现。延迟依据华南虎保存trained_env.yaml配置act=[1,3]、obs=[1,4]与base_env.py reset处torch.randint(lo,hi)的上界不含语义，以5ms物理时间量子实现：动作两个组独立从{5,10}ms选，传感器四个组独立从{5,10,15}ms选；env reset采样，episode固定。底层physics2.5ms、PD10ms、policy20ms不变，缓冲历史按物理子步推进。传感器槽4:22延迟；原始动作槽22:28保留。此范围与旧错误20ms policy tick/inclusive sampling不同，不恢复旧bug。

这只补齐了Step7延迟范围，质量/质心不是华南虎fullrange实现。当前质量：每env同一factor~U(.9,1.1)，所有body质量/惯量同倍缩放；质心仅base XYZ各±.01m，基于名义COM无累积。华南虎保存配置：startup按body随机，base.9–1.3、选中的腿部连杆/轮子.9–1.1；COM也只base，X±.04、Y/Z±.02m。用户此轮只询问差别，未因此改动正在跑的质量/质心。

## 本轮预算与恢复

原总训练预算2400s。旧段训练起点和进程退出观察的差949.00135s全额计入（含最后保存后弃用更新及停止等待），余1450s继续；合计2399.00135s，完整PPO update边界允许数秒收尾。新段4096env，每300s完整保存并检查，结束额外final；恢复iteration21036，source SHA f4960781490a4de9e45fc97a477d890ab4b3a717edbd39c43581fa059278e483。没有新开额外40min。新段只运行约24m10s，整轮不能称40min完整Step7 DR。

保持单项平方惩罚-.5e²/秒，LR3e-5 fixed、clip.1、3epochs，原plant/接口/solver/命令分布不变。新段FIRST_UPDATE保存iteration21037，SHA bbda858b1ff7286d3b5f4e44d22c21a5b0780129fa6861b4bf52bc5e1e52ef7b；STARTUP/RESTORE/PPO_EFFECTIVE实测已收集。完整延迟效果和任务通过尚待结束后的同源PhysX配对固定任务，训练回报不是毕业。

旧段没有SAFE_CLOSED/FINAL收据：SIGINT后Kit直接退出，不能伪造正常结束；退出与GPU释放已实查，最后完整checkpoint独立SHA存在。原日志/全部5m回放、handoff request、停止时progress保留在旧目录追加证据，旧训练启动报告不改。

## 检查方法与局限

每5m保存后下载、SHA核对、既有MuJoCo物理5ms名义固定7任务10初态CPU回放；训练中的forward_tracking混有随机高度/瞬态，不能当固定任务成绩。训练结束后空出的目标GPU执行一次原884parent/过渡015m/新5m权重/最终权重在名义与实际Step7DR下的配对PhysX回放，300steps、tail120、相同10初态与物理随机样本。所有真实失败保留，不自动晋升/导出/部署。


## 用户要求提前接入质量 DR 后的实际结束状态

2026-11-11用户“最新检查点如何了？觉得差不多就加上吧”后，本延迟段在完整015m保存后中止，未跑满原1450s；实际最后progress904.437s。该段不是40min完成，也没有FINAL/SAFE_CLOSED。SIGINT记录与日志保留；退出/GPU释放实际查验后做700env配对回放，再继续新独立质量DR轮。上一段949.001s已计，本延迟段退出观察上界约937.98s；剩余预算未伪报消费，也未偷加回新质量轮。

配对回放模型及原始结果见evidence/PAIRED_MODELS.json、paired_select_r1_RESULT.json、INITIAL_DR、日志与SAFE_CLOSED。全部700env300steps无reset/numerical、motorenvelopeviolation0、actionmemoryerror0，真实joint速度峰值约106.7rad/s不触发数值异常。COM32次reset仍≤.01m、externalhold9..0、zerotorquefinal0。Step7_015的实际DR2.0=>1.86193(6/10)，2.2=>2.03808(4/10)，其余4门槛均10/10；名义MuJoCo2.0=>2.2120、2.2=>2.4780均0/10。不同引擎前进差仍未解决，不能说Step7毕业。用户指定质量DR已另立MOD4V3_STEP7_BODY_MASS_20261111接续。
