# Final881与SuperMimic显存修复

2026-11-06，Newton上一完整小时从620到881：261次PPO、125.28M真实样本、5220新Adam、50112 physics callbacks。完整final34970233字节，SHA `1ef8b57ae5ad3bae01f1f8febe948896480cbad575a57f9121d0eb32e205e03e`。唯一完整学习诊断确认17Adam17620、LR0.0008649755859375004、STD与7组件/RNG/队列/counter21144完整有限；原owner完成等待并释放。

261轮日志step/s算术均37325.7969、末37692；按480000除以平均采样加学习时间的吞吐约35648。不能将算术均值、累计吞吐或物理substep混称同一测速。此前PhysX+Warp完整小时24557.616；新缓存候选与SuperMimic尚需实际生产测速。

独立80和4张新实际姿态侧/顶图已原生审阅，0整轮越沿/双轮台顶成功。旧训练1824次数值重置；eval6/14/23存在严重有限约束或速度异常，原始flight flags不能当真实技能。选中环境接近台前或小幅跳动，未跳上台。原1.598GB正式返回及1.397GB完整WORKER日志保留，约7758314条线搜索警告；本地流式拆分日志并SHA核对，Git只索引大型原件，其余metadata和全部80完整保留。CRLF边界reader错误与两次提高solver迭代仍发散的失败也保留。

具体物理修复在400Hz执行原10mm闭链/.01rad mimic单环境重置，清除warmstart及旧接触力，验收/reward/replay均标无效。没有降低阈值、环境数或碰撞精度。80环境完整8秒验证0非有限、2次约束重置，守卫后闭链峰1.0513mm、mimic1.8736mrad、root速度1.3275m/s；这是有限测试，不称生产20k无数值异常。随后真实H32/完整恢复通过。

SuperMimic首个20k段 `supermimic_final881_1h` 在第一次物理步碰撞工作区申请491520000字节时OOM，0BPTT/0WM更新。实际55.7626896秒，原owner退出释放；中断full checkpoint2316846811字节、SHA `7be84c7f20e6e83f75ad78f86de26287366735a7438eb9e1f876d3bbcb32cc29` 留在原远端，0归档解模。旧sole55380只是等旧SAVE的本地睡眠进程，经完整PID/parent/创建时间/exe/argv与子进程核验后只退出本聊天该进程，有限补齐失败正式返回，不重训、不重评测、不重放once。

显存修复只改replay存放和临时无用PPO存储：完整64controls、2261760000字节、全float32/原字段放CPU，抽中的WM/aux/H32 batch送GPU；冻结来源actor及四个新优化器在GPU。原完整PPO checkpoint保留，未使用的runner rollout/critic/Adam释放。原pinned vendor/source未改。测试覆盖环形写满回绕、全部三种采样、CPU保存恢复逐项相同、无效标签排除；4环境真实64controls、24WM24aux、H32完整保存恢复后第二次H32通过，0数值重置。

独立新段 `supermimic_final881_host_replay02_1h` 只传6个小文件，复用既有资产、learner和full881来源。累计实际48259.6534045秒后开始下一窗，仍在最多100h授权内。实际FIRST/H32梯度/fullsave、GO/SAVE和sole以WORK_ORDER及原收据为准；启动不是实际BPTT验证成功。训练后仍立即独立80和原生实际姿态回放，真实200mm成功前不换地图。

05:02实际FIRST通过：iteration33、146controls、2.92M真实环境转移，132WM132aux、1次验证H32 BPTT和4critic。跨时间梯度0.0036354559、WM路径梯度0.0026822591、参数梯度0.8185082、参数变化0.0055425214。完整首存2328856863字节，SHA `95fd0c5adc0ae00163b8b30dcb942279c41dbfcd9b92ce7addf47e56db0b2d32`。正式返回时已iteration38、6次验证BPTT；这是当时快照，不称当前瞬时值。原PPO完整来源保留，新BPTT四优化器独立。

真实GO2026-11-06 04:59:59.327921、SAVE05:59:59.327921、NOMINAL06:04:59.327921（北京时间）。原launch74652退出、sole15096/parent74652/创建05:02:16.52242负责原窗结束有限回传。FIRST记录numerical69、constraint395及原生线搜索overflow；计数范围仍按源状态/新段核对，不能说20k数值全部通过。当前训练继续，0canonical读写；保持真实空闲GPU私有锁。
