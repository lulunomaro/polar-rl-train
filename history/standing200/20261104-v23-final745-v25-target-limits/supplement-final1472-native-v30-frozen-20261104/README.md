V28已实际完整保存至1472轮，新增238轮PPO与45696个本窗physics ticks。原owner在2026-11-04安全退出，error为null，all_own_waited、原成本结算和原锁释放均为true。先前foreign collector造成的取回延迟及network0/once0拒绝保留。该collector实际结束且fresh LOCAL释放后，V29精确GUI分类入口委托唯一原V28closed，已成功取回26文件；原closed once现已消费，不能重传、重评或重渲染。

独立200mm评测80个首episode，seed9137、每例最多500 controls/10秒。strict、整轮footprint、双轮台顶支持均0/80，全部台顶支持力0。64例跑满10秒，16例均因原contact>1N和duration counter20终止，平均9.05秒。全部roll/pitch、closure、mimic与numerical重置标志为0。400Hz实际记录289600条；非轮接触只取support_force第三列，33个环境出现>1N。初始0.38米前20ms无支撑，不能把初始下降全解释为策略蹲下。

当前模型已用原生view_image查看env0/1/40/41八张真实侧俯图、400Hz支撑曲线和髋目标/实际角度。env0约3秒靠边后停留，env40约2秒靠另一边后停留，5秒附近姿态更低；env1和41反复绕圈，41在约8.5秒后向另一边移动。均没有登上升高表面。右髋目标99.9917%在+0.5rad、左髋26.7983%，越限均0；受载实际角低于目标，不能称接口问题是唯一失败原因。相较final1234的9.20775秒/68完整10秒，本轮寿命下降，落地后高度中位约0.29685米，仍无200mm技能。

V30仅冻结同配方接续，计划从final1472的完整actor/critic/STD、17Adam、LR、全部RNG、保存scalars和原队列恢复，再一次fresh physical reset；不是PhysX续帧。V25接口、原SCUT flat向8000、随后原rough weights-only/freshAdam，以及奖励、reset、PPO、rawGaussian、轮路径、物理和D0-D7均保持。只保存小包装和当前TASK，源码按冻结SHA引用，不复制runtime。V29是取回入口版本，无新训练配方。

本次fresh LOCAL发现foreign scut_stair_continue08.py launch，60636/parent50984；其本地OWNER_LAUNCH发布远owner初始Popen1609081。V30没有启动、没有消费四卡检查或launch/FIRST once，也没有为此建立SSH。foreign controller/collector存在时只读本地已发布metadata。实际释放后fresh broad exact CIM通过，再检查四卡和唯一原canonical/privateGPU/finite；foreign canonical active时继续保持V30未启动，不能凭空闲卡并开。

本次为V25已record phase的ordinary supplement，不能重record/retag。全部新源码、实际回执、原拒绝、评测、原生分析、冻结、交接和自动化快照入Git。模型/NPZ/USD/媒体和42MB CONTROL_CURVES仅实际path/bytes/已发布SHA；不为Git再读模型或运行物理。保护全部历史tags/peels/lqr。
