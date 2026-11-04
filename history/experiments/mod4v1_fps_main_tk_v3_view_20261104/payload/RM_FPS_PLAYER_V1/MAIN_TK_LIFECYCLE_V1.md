# FPS入口：Tk主线程生命周期修复

[Start_RM_FPS.bat](<Start_RM_FPS.bat>)已切换到[player_main_tk_v1.py](<player_main_tk_v1.py>)；用户目录既有LQR面板wrapper沿用。未自动打开新可见窗口，J200回放不受影响。

## 实际变更

- Tk/root/全部Variable与widget创建、读写、mainloop和销毁都归进程主线程；GLFW窗口、OpenGL/MuJoCo渲染和Engine归一个非daemon工作线程。
- 跨边界只传普通数据：面板输入不可变替换快照、动作deque、状态/地图/消息队列。工作线程不调用Tk.get/set/after/destroy。
- 面板关闭先通知停止，主线程继续泵消息；等待GL工作线程释放上下文/窗口并发done后，主线程再销毁Tk并join，不让Tcl对象在GL线程结束时析构。
- 复用冻结[player.py](<player.py>)的布局、渲染、原纯GLFW事件处理；其旧线程构造/run未调用。Engine/控制器/K/KF/PD/D4/DC/模型/物理参数保持原样，非新增控制候选。

## 一次真实隐藏暂停检查

入口参数：`--scene latest_rm --controller c2_fps --hidden-smoke-seconds 3`。

实际PID69912、Tk主线程69916、GL工作线程70356；真实最新CAD47600geoms/37nq。隐藏窗口，Engine始终暂停，且检查路径跳过tick：**controls=0、physics_steps=0、sim_time=0.0**。日志顺序为READY→HIDDEN_LIFECYCLE→VIEWER_WORKER_CLOSED→主Tk clean exit。进程**exit0、stderr空**，job `pwsh-6fa0199ec9db4ebe`已收。

证据：[stdout](<main_tk_lifecycle001.stdout.log>)、[stderr](<main_tk_lifecycle001.stderr.log>)。原退出失败[stderr](<player_c2fps_tkowner_20261104_205204.stderr.log>)与[源码备份](<revisions/player_c2fps_before_main_tk001.py>)保留。

范围：只验证该隐藏暂停打开/关闭路径与完整CAD构建，不冒充所有交互、长时间实际驾驶、性能改善、T01接触门或全控制资格；T01原严格支持失败仍保留。不重跑旧机器人case/holdout。
