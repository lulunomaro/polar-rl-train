# FSM v1 — 原始尝试、错误与修正

所有检查均为合成传感器fixture或C header语法，physical steps=0、robot episodes=0。expected-negative输入/配置守卫属于通过的测试，不伪列为真实设备故障。

|独立尝试|原结果/源码|实际状态|
|---|---|---|
|001|[RESULT](<attempts/001/RESULT.json>) / [完整日志](<attempts/001/python_unittest.log>) / [执行前源码](<attempts/001/sources/fsm_detector.py>)|49 methods，48通过/1失败、0error；865次合成FSM调用，覆盖11状态；C99header syntax通过|
|002|[RESULT](<attempts/002/RESULT.json>) / [完整日志](<attempts/002/python_unittest.log>) / [源码](<attempts/002/sources/fsm_detector.py>)|61 methods，0失败/0error；1027次合成FSM调用；C99header syntax通过|
|003|[RESULT](<attempts/003/RESULT.json>) / [完整日志](<attempts/003/python_unittest.log>) / [源码](<attempts/003/sources/fsm_detector.py>)|最终63 methods，0失败/0error；1042次合成FSM调用；全部11状态；C99header syntax通过|

## 001真实失败

`test_approach_timeout_no_launch_and_no_same_obstacle_retry`在配置50ms的边界看到STEP_APPROACH而非DEGRADED。相对float秒相减在该fixture得到略小于0.05的表示值，直接`>=duration`晚一更新触发。原AssertionError、测试、旧核心源码与每个SHA都在001，未覆盖。

修正是在phase dwell/deadline比较使用1e−12秒表示余量，与原contact/stability窗口一致；没有改变50ms配置、机械状态阈值或用户验收规则，也没有把旧失败改成pass。C proposal的未来实现使用uint64微秒，当前未实现或运行native C状态机。

001核心SHA256：`1b4760c3dfdc8001afe3346f1bb86a4022909b834cfc785773441f63a73bb1f0`。

## 002静态审查补充

在修正deadline后，补充了start-pose envelope、reference算术溢出硬返回、双向force/COM模型冲突、可选电气monitor覆盖说明、config tuple不可变性、driver-fault与reset优先级等合成边界。并非新增物理试验。

002核心SHA256：`d1790c364e4868bbc1ed1d373678bc0260f1048ddd8c9c873571fbf6f1b8531b`。

## 003静态审查补充

RECOVERY中失去可靠支撑时撤销关节阶段参考、转DEGRADED，不继续绑定姿态轨迹；auto-step launch显式要求approach enable。新增两个fixture，保留002的61/61原结果。

003核心SHA256：`8aa2eb817cc095f2b3c470d37e24bbe91ba13a5e5a77b06e75aa54e45cce0b2e`。

## 读者事件

- 新目录创建前首次glob：exit2，路径`FSM_DETECTOR_V1`尚不存在（os error2）。这是初始目标不存在记录，不是传感器/机器人错误。
- 没有权限扩大、重放旧unit、模拟器/硬件接入、SSH或Git操作。已有SPR Cgate和父传感器/physics源码的五个保护SHA在各次运行前后均匹配。

## 封存metadata尝试01

首次封存脚本在README链接扫描时，把待生成的VALIDATION.json当作应已存在的文件，产生AssertionError；当时INDEX尚未创建，core/test/header未变。原脚本与SHA、[完整stderr](<metadata_attempts/001/STDERR.txt>)及[记录](<metadata_attempts/001/ERROR.json>)保留在[metadata_attempt01](<metadata_attempts/001/finalize_fsm.py>)。修正仅承认两个计划生成的metadata容器，并在写完后复核实际存在；对已导出的阈值只校验等值而不覆盖。未重跑003单测、未修改最终core。

此包只证明指定prototype/fixture的行为，不证明contactproxy已标定、实际飞行/落地、270mm越阶、闭环恢复或真实板资格。
