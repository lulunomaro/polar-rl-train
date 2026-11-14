# MOD4v3 第二次复查：两处附带代码修复

用户要求继续检查，并质疑是否为补丁不断扩展范围。本次检查沿华南虎固定源码调用和原v2姿态设置路径，确认两处已发布附带代码错误。MJCF、USD和PhysX wrapper均与R2字节相同，未更改机构、参数、坐标或奖励。

1. `kinematics.set_configuration`：左腿已写入qpos后，右腿目标越界抛出ValueError，留下部分姿态和旧缓存。原v2已有正确写法；现恢复先计算/检查两腿、收集赋值，再统一写入和mj_forward。原复现10个qpos改变，最大0.4rad；修后异常保持qpos/xpos完整。
2. R2刚加的未知关节属性检查抛AttributeError，会被华南虎_get_dynamic_priv_obs实际使用的getattr(...,None)吞掉，_select_entity_features随即生成零刚度/阻尼观测。改为NotImplementedError，实际getattr路径明确报错。它仍是只读状态视图，未扩展成完整华南虎环境适配。

最终验证1707项通过，新增针对第二腿拒绝不改状态的回归，已有字段拒绝测试改用原调用getattr模式。独立REGRESSION也通过。这次没有重复远端PyTorch梯度测试；映射运算未变，R2证据只保留其原范围。

原先1706项通过没有证明所有附带接口或训练流程可用。以往把这些数字当主要完成证据不充分。当前资产仍保留front3跨树切口，必须用对应坐标转换；MOD4缺失的云台和导轮没有伪造。未做本版PhysX或Warp GPU原生动力学、控制器和完整华南虎任务验收，不能据此称已根治奖励漏接或可零改动训练。

修复直接进入现有四个源码文件（实际运行代码只涉及kinematics.py与semantics.py），不新增运行框架。原失败、R2包、R2源码和检查报告保留。
