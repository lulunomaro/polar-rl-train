V27已完整保存至1234轮，新增249轮PPO与47808 physics ticks，原owner安全关闭并结算释放。独立200mm评测80个首episode：strict、整轮footprint与双轮台顶支持均为0，全部台顶力为0；12例均因原contact/duration条件终止，68例撑满10秒，平均9.20775秒。roll/pitch、closure、mimic与numerical重置均为0。相较final985的9.88225秒与77个完整10秒，本轮寿命下降，落地后root高度中位升到0.29273米；这些都不表示技能通过。

当前模型已原生查看实际四例八张侧俯图、400Hz支撑曲线与髋目标/实际角图。env0长时间接近原地；env1和41靠到低台区边界后停留，有非轮接触；env40约5秒转向并靠另一边。env41在8.72秒因原接触条件终止。没有双轮台顶支撑或实际登阶。初始0.38米重置无支撑，不能把早期下降全部归因主动蹲下。髋目标仍在关节范围内，左髋目标开始变化，右髋目标保持+0.5rad；负载下实际角度仍低于目标，不主张唯一失败原因。

V27原closed首次准入遇到另一scope的E3collector16548/59752，network0、once0拒绝原报告保留。其本地publishedclosed且exact进程消失后，新的freshLOCAL准入调用唯一原closed成功取26份文件，SSHclosed/SESSIONrestored/serialFREE。V27closed、评测与render已消费，禁止重跑。rawcourse残留270mm标签保留，实际stepheight/raisedboxes为0.2米。

V28沿用V25的原配方与硬件目标接口，从1234轮完整学习状态继续flat向8000，不提前rough，不改reward、reset、rawGaussian、轮路径、PPO或物理。仅生成小包装、当前TASK和新窗口身份，公共实现按SHA引用；未复制runtime。新fourGPU及原canonical/privateGPU/finite准入通过。实际单次恢复actor/critic/STD、17组Adam各24680步、LR1e-5、RNG、debug0/common29616和原组件队列，再一次fresh physical reset；不是PhysX续帧。

FIRST1235完成24 controls、98304 samples、192 physics ticks、20次Adam和完整保存，梯度有限非零。GO2026-11-04 14:56:11.035646+08，SAVE15:56:11.035646，NOMINAL16:01:11.035646。原3900/save3600/exit300与strict reserve保持。FIRSTcollector已结束且SSHclosed/serialFREE。FIRST是训练/保存证据，V28尚未独立评200mm。原owner安全关闭后立即独立80评测；actualOWNEXIT、collectorclosed、freshLOCALFREE后原V28closed仅一次，取新实际姿态并原生审图与全80manifold后再决定。

本次为V25已记录phase的ordinary supplement，不重record/retag。新报告、实际失败、关闭回执、分析、原生评审、冻结源、准入、启动、FIRST及自动化快照均进入索引。权重、NPZ、图像、视频与大型CONTROL_CURVES仅真实路径/大小/已有SHA，不为Git操作模型或物理。Git后的远端验证仅工具输出。
