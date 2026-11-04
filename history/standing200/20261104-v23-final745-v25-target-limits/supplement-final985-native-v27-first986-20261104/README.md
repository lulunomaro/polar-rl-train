V25已完整保存到985轮并安全退出，原owner立即完成80个独立200mm首episode。严格成功、整轮越沿和双轮台顶支持均为0；3例原contact/duration终止，77例完成10秒，平均9.88225秒。V23的平均3.86775秒、12例完整10秒已有改善，但200mm技能仍未通过。

当前模型已原生查看新实际四例八张侧俯姿态图、400Hz支撑曲线与髋目标/实际角图。样本留在低台区小幅移转，落地后机身高度约0.25–0.28米，没有上台阶。目标越限已消除，实际髋在上限1mrad内占比左0.680513%、右1.062511%；目标仍多为+0.5rad，实际多0.38–0.45rad。最初0.38米重置无支撑，不能把初始下降全部归因策略主动蹲下。

首次保存的review把support_force三列中任一支撑都计为nonwheel，原报告和源码保留。独立schema correction明确前两列为轮、第三列才为非轮，实际22个环境有非轮>1N事件。只修正分析解释，没有重评或更改生产。

V27复用V25的不可变实现与相同checkpoint FORMAT；只新增小包装、当前TASK和唯一窗口身份，未复制完整runtime，也未改变奖励、PPO、动作、重置或物理。准入经freshLOCAL精确CIM、四卡读数、原canonical及私有GPU/finite锁确认。实际一次完整恢复985轮actor/critic/STD、17组Adam（19700步）、LR1e-5、RNG、计数器debug0/common23640与原组件队列，然后一次fresh physical reset。FIRST986完成24 controls、98304 samples、192 physics ticks、20 Adam更新及完整保存；这不代表200mm成功。

V27 GO为2026-11-04 12:53:45.761251+08，SAVE13:53:45.761251，NOMINAL13:58:45.761251。原3900/save3600/exit300与reserve保持。FIRST collector已关闭SSH，serialFREE。原owner完整保存和安全退出后立即评测80例；仅未消费V27 closed取回，新actualpose有限渲染、原生审图和全80接触/目标实际核对后再决定接续。V25closed、评测和render均已消费，不再运行。

这是已记录V25目标接口修复phase的ordinary supplement；不新record/retag，不动其它scope。PT/NPZ/视频/图像及42MB CONTROL_CURVES只引用真实路径、大小和已有SHA。全部新报告、schema错误、关闭回执、冻结源、准入、启动、FIRST与自动化快照均入本索引。Git后的remote核验仅工具输出。
