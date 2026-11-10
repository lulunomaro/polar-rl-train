# 40分钟平方惩罚适应训练启动

日期2026-11-11，Asia/Shanghai。用户明确授权：“你可以开训，老规矩五分钟一次检查点保存40分钟一轮每五分钟看看一下”。训练已启动，后续检查在当前对话执行，不创建自动化。

起点原父884cd07b，iteration20838；4096环境；实际奖励-.5e²；原修正版DR、0/5ms物理时序；原solver、PD、接口与其它奖励不变。PPO恢复actor/critic/std/Adam/RNG，固定LR3e-5、clip.1、3epochs。40分钟预算按训练循环墙钟2400秒（启动初始化另计），每个5分钟截止点在一次完整更新后保存，完整checkpoint原子写入、SHA回执；训练结束保存final。

已保存首个完整checkpoint，iteration20839，SHA cc64222afda3d811d6b9eeeb133dd4d506a3fcea99f291aefe2391f55dd40976；首个更新确认actor改变、numerical0、恢复SHA与recipe一致。该首步不是能力毕业。未来每5分钟下载新checkpoint到本地tmp、校验SHA，并做既有nominalMuJoCo物理5ms、10初态固定任务CPU回放；训练DR PhysX科目在训练结束空出GPU后做同源对比。每5分钟还读日志/保存完整性/数值与真实前向指标。不同引擎、nominal与DR不得混为一套成绩。

训练中新增仅记录向量统计：cmd_vx>=1.5、|cmd_wz|<=1、当步未终止样本的实际vx/命令/绝对误差。它包含随机高度与瞬态，只反映训练分布趋势，不能替代固定任务判定。保存期限改为固定300/600/.../2400秒；不因checkpoint写盘推迟下一截止点。

`monitor_round.py`是本轮本地当前任务助手，SSH只读运行收据/下载已完成checkpoint，使用既有回放代码CPU评估；无周期任务/消息投递/新训练。训练源冻结在TRAINING_SOURCE_READBACK，运行期间不修改其行为。用户未授权自动晋升，保留全部检查点与失败结果。本文件记录启动阶段；40分钟结论待最终补充归档。
