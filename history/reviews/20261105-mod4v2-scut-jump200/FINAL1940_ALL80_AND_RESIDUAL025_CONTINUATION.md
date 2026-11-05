# SuperMimic final1940与残差修复接续

2026-11-06原一小时SuperMimic已完整保存、安全退出、立即独立80并正式回传。完整final2328856863字节，SHA `087c357ddc77f8e860d553b5ee13df8e7299b418a2c7541c9b7e3c3e047a559d`。实际iteration1940、1908次验证H32 BPTT、7760WM、7760aux、7632critic，4914真实controls、98.28M环境转移。四Adam分别14/16/6/6个状态，步数7760/1908/7632/7760，模型及优化器有限；64×20000 replay1279998有效/2无效样本，原streamcut完整，7组件/DR/RNG/queues/counters完整。唯一最终学习诊断已完成，不为归档再次解模。

原full881 PPO仍作冻结teacher完整来源保留，新四Adam不是原PPO17Adam接续。当前源父模型没有逐轮持久化progress历史，只有FIRST/LATEST及最终计数；不补造中间学习曲线。原完整WORKER1393640字节SHA `5e8d6d98e608d4b01207e24debd46c88ec081bdfa53e15342995626db5f90746`，EVAL21378字节SHA `dd3ee40eea7155ab28b2d071a9f2559eea9e161d4f27411988cda2c71b905a1c`，全文错误0；仍有7369次solver32上限警告与893条单环境重置event。训练最后计数361numerical/778constraint，不能说生产数值全部通过。

原owner实际3615.761822秒完成保存、退出与80后释放GPU，0canonical读写。以98.28M/该实际总时长为约27181控制sample/s，包含初始化、保存和评测；不是只测collection，也不是物理8substep。没有原逐轮采样时间历史，因此不编造整轮collection平均或3x提速。

独立80/seed9137/400Hz/0优化器全部在34–52controls，即0.68–1.04秒终止，0数值/约束重置、0越沿/落台/成功/台顶力。真实rootx最大0.4361m，台沿0.8m；8环境有upwardflight flag但没有跳跃毕业。全部终止时导轮06接地，未超过40度pitch/roll；四张early/late侧顶实际wxyz姿态图均原生审阅，早期spawn下降、随后前倾和腿伸长，尚未到台沿。实际mesh env41完整0.8秒视频与4关键帧已生成并原生审阅、Codex打开，SHA `52283dd204d2e0e2cde3b0b7c981fc72e3121d92839f31fd8b854b2058997c11`。回放只已存Newton姿态与原USD可视mesh/mj_forward，0NN/physics/PT/SSH。

据此仅将BPTT相对冻结teacher的动作残差输出尺度1.0→0.25；不改复旦16项公式/权重、物理、CAD、20k、DR、命令或验收。原learned weights、四Adam、replay、RNG和teacher完整恢复，未清空策略或回退模型。单独候选实际80评测使用同final1940，明确标policy_adapter，绝不覆盖原失败80；本地5070Ti/CUDA13.2与原4090/CUDA12.2不同，不作同硬件性能结论。候选平均276.7controls即5.534秒、39/80满399controls，0数值/约束重置，仍0越沿/落台。候选全部4实际姿态图原生审阅：早期更平，后期接近台沿、小跳或接地，仍未通过200mm。完整保存恢复后第二次H32及residual_scale字段持久化测试通过。

新独立段 `supermimic_final1940_residual025_1h` 只传7个小文件，引用原资产/learner/2.3GB源模型。段前累计51875.4152269秒，仍在累计最多100h内；只实际空闲GPU私有EX/noledger，不等其它chat本地controller，不动foreign账本或进程。实际FIRST1941从source1940新增1次H32 BPTT（1908→1909）、4WM/4aux/4critic，跨时间与WM路径梯度非零、参数变化非零，全量首存2328856927字节，SHA `0070897dbf618063b2f243d6ffdf7120bb914b8d52e5d555f435ab28445802e7`。恢复收据实际四优化器/replay环指针50与全部RNG/7组件，target residual0.25。首轮未裁剪paramgrad1335.14、imagined loss313.61仍有限，实际策略梯度继续原norm1/value0.1裁剪；高loss或梯度不是技能进步，后续需实评。

实际GO2026-11-06 06:23:33.074197、SAVE07:23:33.074197、NOMINAL07:28:33.074197（北京时间），soleSAVE+45=07:24:18.074197有限回传。原launch38088完成，唯一collector75124/parent38088/创建06:24:33.81431；原owner1697594/create1793917412.47、worker1697604/create1793917412.86，实际receipt优先。健康只查本地exact/错误/正式返回，不第二SSH/reader/PTdecode/重launch或hotpatch。保存后原owner立即独立80，再用SuperMimic专用唯一诊断和当前模型原生回放决定下一步；真200mm达标前不换地图。

全部原失败、source reader路径错误、video wrapper缺__file__、错误Python缺pxr、候选与原80及全部完整状态报告保留。状态读取融合整步退化候选继续不启用。当前新冻结INDEX不变，旧once不重放，原Newtontrial不record/retag。
