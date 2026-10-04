# 10档21075首份15秒真实回归通过v4学习准入

核验2026-10-05T05:00:45.940393+08:00。精确PID绑定正式21075 SHA717d4450e5824f25996c25e560719f135caf5343569eb49e01ca15850ab5c1cf，CPU actor/critic/optimizer/std/iter68浮点完整有限；正式从20919完整暖启动，累计当前cap有效暴露2724.084s。

auto0103实际80env flat与88env contact-spin各1500步15秒完成，80/80、88/88存活、64个已训练平地环境全存活；v4 learning_admission_pass=true，MOD4真实任务重置、模型/数值、接触/参数数据完整性通过。原spin/legacy false、flat strict_window=false保留，有限性能量只诊断。

纯+10实测组均9.923336rad/s，纯-10为-10.023193rad/s，约1.58/1.60转每秒；纯正/反逐环境最坏peak tilt2.428015/2.125964deg，最高每环境平均XY速度0.175010/0.184326m/s，最大XY excursion0.138131/0.132253m分别保留。滑移代理均值、载荷脉动、控制gap/低载完整记录，不把均值当瞬时峰或材料点/实车证明。

读取时auto0104双seed nominal/white八份配对已有4份完整报告通过，正在seed20261003站跑。父98524/start29475344、guardian98567/start29475412独立session正常；无trainer/active_segment是计划内冻结，未称10档完整配对接受或4π已开训。实际回滚源已为通过v4配对的20919/cap8/white_v2。

唯一总324000有效PPO秒90h与四扩展不变，冻结余79486.879s约22小时4分是读取快照。没有本次额外probe/PPO、暂停重启、奖励/DR/物理/硬件/PPO/验收变更或预算追加。下一步由已有主机父完成配对后独立4π预检和45min学习；2转/秒目标需实际左右signed yaw双seed和final确认，当前尚未达到。
