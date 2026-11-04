# 单200mm跳跃：final263结果与重试/上升修复

2026-11-05 04:44实际覆盖：retry-ascent已完整保存113新PPO/54.24M样本/final376/17Adam7520，03:16:14原owner ownwait/settled/released；正式回传03:48:39。独立80全部7.98s timeout，69局2–6次请求/共300次，push平均world-vz .449606m/s，但0真实向上离地/越沿/台顶/稳定落地；全部4图已当前模型审看，0closure/mimic/数值异常。两hip目标持续+.5rad。已加奖励项`jump200_target_projection=-2`，按真实actionterm scale/offset和原CAD→motorlimits/CAD投影惩罚不可执行请求；动作/限位/D4/物理/完整学习状态保持。19项jump200＋8项旧阶梯CPU检查通过，4module/59sharedrefs候选准备完成。唯一local16444/create04:40:09.633017已排队，当前仅等待真SSH读者39496；其W10仍PREGO，当前known canonicalowner为SCUT32/1633096，SAVE05:11:31.777429/NOMINAL05:16:31.777429。sole16444负责补齐final376完整日志、核actualrelease/原余额/四卡、唯一新launch→FIRST377→postround。尚无新INDEX/LAUNCH/GO，健康只本地，不第二SSH/rebind/重训。100h授权持续。详见`JUMP200_FINAL376_AND_TARGET_PROJECTION.md`。下文早期等待/未返回均为历史。

2026-11-05 03:26实际覆盖：重试/上升修复版已返回有效FIRST264/480,000样本/20新Adam、actorcritic梯度均1.0、FULL_V4首存40,717,335B/SHA `fc8eeb0d344d3f33c16c9f0b21c73b63cdb86d37b39707f66b1293a247555e72`；完整恢复source263/17Adam5260，首轮完整日志0实际错误。旧4416已结束，唯一collector70820/create02:21:49.885529负责回传。actualGO02:14:24.739725、SAVE03:14:24.739725/NOMINAL03:19:24.739725不延长；当前在网络前等待另一聊天真实SSH读者68888/create02:46:51.916175退出，stderr0、尚无FINAL/80/ownexit正式回执，不能凭另一任务已GO判本聊天成功关闭或跳跃技能。原sole70820自行接续，不第二SSH/重bind/新训练。下文FIRSTpending/4416均为历史。

2026-11-05 02:15。接近/上推奖励修复一小时已完整结束：113新PPO、54,240,000样本、21,696physics callbacks、2,260新Adam，source150→final263，17项Adamstep5260；FULL_V4 final40,717,335B，SHA `c6aefd9727884461f3b5f19ba5a220fece62ac01f41e35fb7c3a461d03c1d183`。actor/critic/STD/Adam/LR、7组件、RNG/动作队列/全局计数器已一次必要完整CPU诊断，只有此前已核的3个permission NaN未设置哨兵，其它学习张量有限；不重置STD、单轴或Adam。

实际GO00:40:50.069379，SAVE01:40:50.069379/NOMINAL01:45:50.069379。完整final01:40:02.865784、训练关闭01:40:28.391130，原owner立即独立80局，01:42:53.548382完成、01:42:54.380771 ownwait/settled/released，正式本地回传01:43:12.797826；没有延长原窗。旧collector20700已结束。

实际80局全部399controls/7.98s timeout，0接触终止/闭链/mimic/数值/raw异常重置；全部动作目标/CAD合规。80/80触发请求，较上轮41/80增加；平均前进速度.06496m/s较.03730提高，低速比例从51.77%降到28.19%，idle平均每步回报-.00948较旧.08248下降。四张actualpose已用当前模型审看：四选例从出生位置前进，最后rootx约.50–.53m，在x.8m台沿前停住，轮子始终支持地面，0真正向上离地、0整轮越沿、0实际台顶触地、0稳定成功。接近改进不能称跳跃技能。

每局恰好只有1次请求。原StepUp只根据前向ray时间差分发出单次事件；第一次推蹬失败后，当前仍看见同一台阶，却不会再次请求。push/tuck有效端点仅2.97%；push平均每步回报.112，接近静止push仍能拿完整姿态/追踪正奖励。hip目标上限命中100%/99.906%，保持原学习状态，不擅自重置输出或放宽目标限位。

本次仅改config.py/rewards.py：保留原时间差事件；在phase idle、原冷却结束、尚未真正落台时，当前真实前向ray相对chassis ground rays仍为.18–.22m抬高才允许重试，flat/top/非有限ray不触发。不启用已关闭的Stair机器或新的物理助推。active起跳阶段四项正tracking(flat_orientation_x/y_exp、track_lin_vel_xy、track_ang_vel_z)再乘实测world向上速度clamp0..1；保留原直接上升、pushheight/pushvelocity/peak与真落台奖励。没有改变观测/动作/200mm几何/验收/物理/DR/PD/DC/CAD/PPO。

15项jump200必要CPU检查和8项旧阶梯回归通过，0生产PT/physics；包含持续可见台阶重试、冷却约束、平地/台顶/NaN拒绝、向上与静止奖励排序及落台保留。新candidate env20000_jump200_retry_ascent_1h_20261105仅两module＋owner/entry/PLAN共5小文件、57sharedSHArefs，完整final263续训。

原完整日志第一次回传被另一聊天真实collector39092在网络前拒绝，false完整保留，未消费readonce、0SSH。该collector随后自然退出，唯一continuation4416复用原有限读者补回完整WORKER481,520B/SHA `ef73ec2a6e839d7327ec38e4cff7804e0d7f3256aa8fd89d9e25f5143970e330`和EVAL15,595B/SHA `39f12dcd4f3712d93f91c84d12370c7636d9ed26ee1b75f0fa8c536d1cdb6b34`，实际errors均0；原owner已真实退出。初版分析报告的complete_log_pending由补充FINAL_COMPLETE_LOG_VALIDATION_SUPPLEMENT解除，不改原raw。

当前另一E3W8原owner1626926已02:09:09.507206提前ownwait/settled/released并outerreaped；原canonicalNone/三锁free。02:14fresh四卡72两4090free24,203MiB、无compute，选择GPU1；RAM532GB/disk249.9GB，原remaining215404.60276913643/reserve86412.86069250107。210有已核Windows数据盘但RAM43.25GB仍低64GiB，86有compute占21,602MiB。全客户端按原finally关闭。

新originalowner1628379/create1793816063.98已实际launch，唯一local4416/create2026-11-05T02:13:54.906218+08 continue_segment负责原FIRST并自动绑定唯一postround。FIRST尚未返回，不称有效新PPO或技能；actualGO/SAVE/NOMINAL由sole FIRST确认，初始化计入3600save+300exit。100小时持续授权、同一原余额/reserve保持，不再逐小时询问。
