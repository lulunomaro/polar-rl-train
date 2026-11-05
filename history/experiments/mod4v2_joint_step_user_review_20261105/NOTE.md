# MOD4v2关节/200mm台阶窗口：用户重新查看后的补充记录

用户明确要求重新打开，随后说“我看完了，继续git”。本次是独立GUI查看会话，不是新训练、策略评测、PhysX或实车验收；“看完”不改写为“工程通过”。

## 实际启动和结束

- 新会话：[reopen_20261105_164916](<sessions/reopen_20261105_164916/STARTED.json>)，同一未改动的关节工具与场景，新metadata目录保存，不覆盖首次查看记录。
- launcher PID67000，实际GUI child PID57612；实际读取到HWND135135562和标题“MOD4v2 HW300N60 关节位置探针 | 200mm台阶 | 静态”。这次不是把venv redirector当窗口进程。
- 16:49:18.838实际启动；16:50:04.089正常关闭，渲染205帧，关闭reason=window_closed，无ERROR文件、stderr为空；用户完成查看后进程已退出，未再重开。
- [最后状态](<sessions/reopen_20261105_164916/CURRENT.json>)与[关闭记录](<sessions/reopen_20261105_164916/CLOSED.json>)完整保留。静态mj_forward、不积分、不自动抬root、无policy/训练。

## 本次调节状态（描述，不是毕业分数）

- 30个关节位置控件，实际200mm碰撞台阶，原v2资产未改。
- 左hip=-.09948376736367678rad，crank=-1.1857055452612375rad，差角=-1.0862217778975607rad，接近CAD低折边界；左gas眼距152.606617514445mm。
- 右hip=crank=-.24783675378319478rad，差角0；右gas眼距179.3605589098706mm。
- 当前闭链最大误差约7.2797683e-13m、接触数0，仅静态检查结果，不声称真实止挡网格接触或动态可达。
- 无新输入拒绝记录；完整各joint/root已记录字段以原JSON为准，不补造未保存的操作过程。

## Git范围

上次源码/场景/首次查看/控制器功能验证已在639d6543a3002eb133c03bd85cac27b86e750389，tag trial-20261105-mod4v2-joint-step-interactive-ui。本补充只保存本次重新查看会话六个源文件/日志和本说明/新归档源码，保留旧记录，不重跑GUI/模型/物理为Git取证。main只读；使用原record_experiment完整validation/redaction/hash、唯一annotated trial及真实远端branch/tag/peeled核验。后续原生PhysX、100Hz与实物曲线状态保持原pending，不因人工查看自动改变。
