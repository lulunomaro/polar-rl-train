本目录已冻结，旧模块与所有 payload/runtime 未修改。actual_DR_memory_getter_v1.py 可读原 D0-D7 内存，无 SDK 导入、参数 setter、后端 material getter、随机采样、actor 或物理执行。

用法：创建 RuntimeOrderBinding，明确 pin actual body/joint30、四腿/双轮/双气簧顺序和材料 shape 数；创建 ActualDRMemoryGetter(env,binding)，在整个原 reset chain 完成后 capture_initial()。之后仅在 reset 交接处 refresh_after_resets(ids)；它验证8组 epoch 同选中行+1，拒绝遗漏/重复/未完成 reset，仅重新读取选中行并原子更新缓存。无 reset 时不传 CPU friction，选中 reset 只传所选 CPU materials/mu 行；snapshot()/xi() 从设备缓存返回，不访问 CPU friction。非reset xi保留缓存原值；不声称它重新核验了未重置物理参数，实际组件/SDK审查仍需独立完成。

14字段映射见 ACTUAL_DR_MEMORY_MAPPING_CONTRACT.json。重要纠正：原 MildDR 对6个电机分别采 episode gain，legs[N,4]+wheels[N,2]，所以 motor_episode_scale 必须是6维；旧冻结候选catalog的2维占位不可直接用。新 getter 的 field_shapes() 给出真实 shape，其余14字段名保持。PD stiffness/damping读取显式 actuator 参数覆盖隐式 drive零槽，并与原 ExplicitPD.component.coefficients()逐值核对；气簧两项与D5/D6 factor值核对。COM用原 pose XYZ+真实delta，不触碰principal-axis quaternion；mass/inertia用原nominal memory乘当前D0 factor。摩擦复用原CPUcache，wheel restitution0来自原D0明确写法，非缺字段默认值。joint_friction取SDK现有joint_friction_coeff静态effort缓存，未伪造dynamic/viscous值。gas preload取原实际事件targets及原气簧顺序，无fixture数值补缺。

read_old_processed_applied(env,issue_tick)直接返回原 queue.groups 的 applied4+2，核原2500/10000us、控制边界、last_apply、pending。它不取env.action_manager.action，也不将最后新policy动作误当全4个子步的实际目标。

CPU15/15通过：使用真实原 ChassisCOM、ExplicitPD、SpringPressure、GasDamping、SensorCorruption、PhysicsActionQueue 的tiny CPU实例；D0为明确标注的duck内存，原MildDR需要SDK，未冒充实际实例。覆盖14字段映射、显式PD/implicit0区别、6motor gain、selected reset与非reset缓存、无reset不传摩擦、实际queue applied读取、缺字段/错维度/错顺序/非有限、动态gain拒绝、D5/PD不一致、未完成/错过reset，以及失败更新不发布partial cache。没有实际 SDK 准入证据。

剩余：根需要将此getter安装在完整reset之后，绑定目标实际SDK/order/material数量，做一次真实backend值/组件memory相符的准入，并使用新的真实static维度接模型保存/恢复。缓存不会每step主动核查无epoch变化的非reset静态漂移；这一点是明确限制，不是已通过的runtime保证。所有来源SHA、reader inventory错误和完整文件索引已保存，helper未Git/SSH/GPU/PT/raw/账本操作，归档由根负责。
