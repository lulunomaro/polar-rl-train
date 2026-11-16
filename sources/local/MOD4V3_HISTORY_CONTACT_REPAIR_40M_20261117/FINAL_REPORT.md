# 触墙修复40分钟最终实测：未达低速上阶目标，不采用

最终正式低速200mm仍0/5；真实双轮越边及>=0.4s物理稳态事件各2/5，末端均无连续稳定保持。normal保底60/60，原双阶5/5、斜向10/20、下阶5/5。保底隔离有效，上阶闭环尚未修好，不晋升、不追加训练。

本轮只在独立目录改变actor。默认c874、CURRENT指针、原010m、原8391帧保护检查：True。不自动晋升、不延长。

本轮初始normal60/60；原10229帧保留，加18条合格现场纠偏共15645帧/65个episode。CPU实际优化22000步，最终继承路径13000步；本轮encoder新预训练0，复用旧3000步编码器。PPO小批次另计。

PPO时间：1794857663.6778688 → 1794860000.1111484；elapsed=2336.4332797527313秒；原生安全关闭=True；错误=False。

实际新增PPO迭代与Adam小批次见FINAL及LATEST_PROGRESS；中止或未完成项不计通过。

|检查点|normal flat60|严格低速200mm|真实双轮越边|物理稳态事件|原双阶|斜向|下阶|
|---|---:|---:|---:|---:|---:|---:|---:|
|model_005m|60|0|1|1|未测|未测|未测|
|model_010m|60|0|3|3|未测|未测|未测|
|model_020m|60|0|0|0|未测|未测|未测|
|model_final|60|0|2|2|5|10|5|

正式速度线始终<=0.6m/s；训练放宽档位的完成数不能充当正式成绩。教师辅助为0。nominal冻结回放不等于full-DR毕业。

## 最终200mm各起点

|起点mm|严格通过|双轮越边|最大物理稳态s|入阶m/s|近阶峰速|首秒位移m|首秒峰速|峰值俯仰deg|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|-60|False|False|0.0|0.4974426240713035|0.4974426240713035|-0.017155203599419286|0.04864272891172067|16.464580546283877|
|-30|False|False|0.0|0.25693932358993227|0.48035749814815426|-0.017155203910439662|0.04864272891169322|10.662802268853937|
|0|False|False|0.0|0.4714797581983797|0.6655957505576479|-0.0171552036022826|0.04864272891173355|27.29145125383974|
|30|False|True|0.7000000000000003|0.47078147069604204|1.3034633845077557|-0.017155203912266152|0.04864272891170572|13.079653177346492|
|60|False|True|1.3800000000000008|0.47015662746685266|0.7218704273347798|-0.01715520385861493|0.048642728911719536|18.904256342855366|

急停/原双阶/斜向/下阶原始数据：evidence/checkpoint_evals/model_final/。视频：同目录single_step/STUDENT_CENTER_1X.mp4。历史实验与方案：REPAIR_PLAN.md。所有失败预检、训练错误与未通过评测均保留。

## 收尾核验与补测记录

实际PPO 2026-11-17 03:34:23.677869 → 04:13:20.111148，2336.433秒；352轮PPO、4224次Adam小批次，原生已安全关闭且训练PID已退出、GPU释放，早于2400秒硬上限。

最终normal/STD完整参数变化0，所有保护SHA一致。训练累计DR5553+nominal1326=6879次尝试，阶段/严格完成均0，819全部仍1.3首速度档。不能把nominal回放的2次物理事件说成原生DR通过。

原final评测的急停/楼梯/下阶因缺失manual_replay依赖，在仿真前失败；补入旧已归档字节一致的三个guard模块后，只补跑缺失三项，单阶与flat60原有效结果未重跑。初次失败日志/partial目录、初次EVALUATION与报告已全部保留，不改写历史。

补测原始结果：evidence/checkpoint_evals/model_final/pitch_retry01/RESULT.json、stairs_retry01/RESULT.json、descent_retry01/RESULT.json。补测记录：evidence/final_regression_repair01/REPAIR_RECEIPT.json。

低俯仰急停峰值：崎岖11.5863°、平地11.8534°；均沿原normal协议，不等于新技能fullDR毕业。当前没有单独隔离PPO、encoder与历史门控变化的因果贡献，不由小loss推定技能已学会。

视频：evidence/checkpoint_evals/model_final/single_step/STUDENT_CENTER_1X.mp4；五点实测曲线：evidence/FINAL_FIVE_STARTS.png。默认c874/CURRENT、原010m37dbe178、原8391及既有归档继续保护。

实际训练速度课程计数（不能当独立成绩）：{"checkpoint": "D:\\claude2\\fangzhen\\_mod4v2_src_20261106\\sources\\local\\MOD4V3_HISTORY_CONTACT_REPAIR_40M_20261117\\weights\\model_final.pt", "iteration": 25839, "PPO_updates": 352, "optimizer_minibatches": 4224, "training_speed_course": {"limits_m_s": [1.3, 1.0, 0.8, 0.6], "stair_population": [819, 0, 0, 0], "completions_by_stage": [0, 0, 0, 0], "strict0p6_completions": 0, "speed_penalty_sum": 10.357529640197754, "source": "actual checkpoint counters, not frozen independent score"}}
