# MOD4v2全关节位置检查＋200mm台阶

这是本地MuJoCo真实渲染的手动姿态工具，不加载专家权重，不运行训练，也不启动原生PhysX。使用已交付的MOD4v2-HW300N60机械定义，旧v1与v2发布资产不修改。

## 场景

- [交互场景](<interactive_scene.xml>)从[MOD4v2场景](<../mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/mjcf/scene.xml>)独立派生。
- 新增可碰撞200mm台阶：底z=0、顶z=.2m，近面x=.4m、远面x=1.1m、y宽1.3m。不是把截图贴到画面里，台阶是MuJoCo box geom。
- 31个机器人body、30个单轴关节、原10个闭链/传动等式。硬件gas眼距140～200mm、标称300N。
- [场景尺寸与模型加载证据](<SCENE_RECEIPT.json>)；mesh继续引用本地原v2包，无新增网格变形。

## 交互边界

默认姿态编辑模式只执行`mj_forward`，没有动力学积分。拖动关节可查看真实几何、闭链/接触状态；手动设姿态不等于机器人能在动力学中走到该状态，台阶碰撞也不会自动把手动qpos弹出。

- hip/crank是绝对主动角，连续多圈；UI角度滑条窗口不是物理限位，数值输入可表达更大角度。
- 勾选保持差角时，hip带crank同角转动，实现整腿联动；否则按各自目标检查机构差角。
- drive follower不是独立电机，编辑会映射对应主动轴。
- 被动铰链及gas滑条通过同源闭链支路反求差角，不逐个硬掰断闭环；没有“放宽真实限位”开关。
- 气缸硬件最短140mm，但现机构低折止挡先在约152.606mm触发；140～152.606mm不是本连续机构支路可达区间。UI应提示而不是伪造可达。
- Root位置/姿态可调整；默认不偷偷抬高机器人。几何落地/落台阶须显式按按钮，和真正动力学碰撞解算分开。
- 鼠标拖画面旋转，滚轮缩放；显示碰撞体/闭链锚点用于检查，不改变实际关节范围。

## 本次实际启动与核验

16:35:33本次窗口真实启动，运行约100.428秒、实际渲染408帧，记录到关节调节；16:37:13正常关闭，未记录GUI错误。launcher PID73384为Windows venv redirector，实际GUI child PID75688；第一次HWND核验错查launcher，第二次核验时窗口已正常退出，所以没有伪造当前可见窗口或窗口截图。见[实际生命周期](<WINDOW_VERIFICATION.json>)和[原关闭记录](<CLOSED.json>)。程序正常关闭后没有由助手擅自重开。

另在独立metadata目录、隐藏Tk窗口进行了[setter功能验证](<FUNCTIONAL_CHECK.json>)：hip超旧.5界、被动膝反求闭链、跟随轴多圈、gas机构先挡且qpos不变、轮和导轮、root调节、闭链精度、30控件均通过；未更改已关闭用户会话的姿态。初始真实场景渲染见[预览](<INITIAL_SCENE_PREVIEW.png>)，这是初始场景图片，不冒充用户窗口截图。

需要重新打开时双击[OPEN_WINDOW.cmd](<OPEN_WINDOW.cmd>)，或运行正常GUI入口（不是once构建/训练脚本）：

```powershell
& 'C:/Users/lulu/Desktop/claude/mjcf/.venv/Scripts/pythonw.exe' -B 'F:/RMPOLAR-RL/mod4v2_joint_step_probe_20261105/joint_step_viewer.py'
```

关闭窗口结束本工具；不影响旧任务或专家。Git归档保存本轮源码/场景/启动/关闭/实际核验证据及失败，CURRENT为一次实时状态快照；后续用户交互不自动提交。归档不重放物理、不读取权重。
