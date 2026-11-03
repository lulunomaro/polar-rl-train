475独立80评测仍0严格成功、0首次飞行整轮footprint越沿；2例双轮轮胎前缘先后越沿，79腾空，50姿态终止、30完成8s，mean3.78725s。实际400Hz台顶接触42环境、any-wheel>1N共1439环境拍，7环境双轮同时>1N共166环境拍；最大单轮3023.057N。env34双轮累计68拍/最长连续0.1175s，env20累计54拍/最长0.0575s；env20/21虽轮胎前缘越沿，wholeclear均false。任何这些接触均不等于严格落台或稳定。

当前模型已原生审8early+env40两late实际pose以及6项运动曲线。0/1/41起跳后接近台沿并短暂触顶，随后负俯仰增大、旋转而终止；env40前向不足，后期台前下方支撑到8s无恢复。0.4s pitch12.52–14.61°较473约20°减小，yaw−1.51至−12.03°，后三例仍有yaw退化。低轮底峰值估计0.15746/0.25048/0.25421/0.26789m，均不足0.27m；env40首次轮地面1.0975s前最前轮心0.57045m，其他三例在姿态终止前未再次触地，不能把无ground误称成功。奖励项重建max1.6505e-5。

四例前20controls targetlimitcost由7.079–7.382减至3.442–5.240，下降约28–51%；右hip目标均值由1.020–1.031rad减至0.816–0.885rad，仍有85–100%超+.5，旧overflow仍0。首次修复在实际目标、俯仰、净空与触台产生响应，故476从完整final474继续一窗相同奖励，未添加新项。严格0与寿命下降如实保留，不能按接触数量宣布成功。非pairedDR不作唯一因果；未保存全nonwheelmanifold，不排除其它碰撞。最佳top环境20/34无完整savedposes，不制造视觉证据。

474已完整保存/安全退出/正式传回/CPU1294finite，final38433417B SHAe9e5ebb9f622f45094679c133aea8d2425b18bc1cd37dfd5eab6e2b6f8386a3e，Pi44/newWM5676total75210，5707controls456560ownpairs，actorAdam56937critic13997/三Adam/teacherSTD17Adam42940/EMA/normRNG/saved389origin完整。sole46060正常完成，owner/node/worker ownwaited、settled/private共享释放、SSHclosedSESSIONrestoredFREE。费用3605.10924243927、closing297532.6591668129只历史快照。旧once全消费不重放。

476仅3source+4control/小eval与108共享SHA引用，直接共用原474奖励模块/参考/模型，不整树或模型复制。必要final474一次fullrestoreCPUfixture通过，75保存坐标重复128加新syntheticlatents，非实际onpolicy；actorgrad2.294807critic1.414048，nominalLR候选KL.004965835/delta.036424011，候选weightsAdam完整回退、生产优化0。保持全部物理/动作/PPO与原canonical3900save3600exit300/strictreserve；收尾后立即独立477。

判据补充：first_flight_both_cross在评测源码中由previous highX<0/current highX>=0且wheel lowZ>=.27定义，是轮胎前缘越沿；不是轮心越沿。first_flight_whole_footprint_clear按rear lowX越沿定义，475全部为false。原README文字和本次纠正回执同时保留。
