候选已完成并冻结；旧 frozen/payload/runtime 完全未改。本目录是下一 native 版本的 source/CPU 合约，不是实际 SDK 准入，也不兼容旧 actor128 权重输入。

- static_dynamic_delay_contract_v1.py：具名静态 DR 目录、shape/dtype/device/finite 检查、复制式 episode snapshot、原子 selected_reset，以及动态辅助状态和可微目标队列展开。
- pack_dynamic_aux(contact_history[N,3,2,3], applied_torque[N,30], old_processed_applied[N,6]) -> [N,54]。偏移分别 0:18 / 18:48 / 48:54；unpack_dynamic_aux 反向。原 contact_capture.py 真实 history 是 18，不是早先抄写的12；没有静默截取。
- request_from_age(age:int64[N]) 保持100<=age<180；advance_age 在一控制结束后+1，再把 reset 行置零。request/age 不放固定 xi。动态 torque/contact 必须由下一模型监督和滚动演化，不得沿整个 imagination 冻结。
- task_relative_observation 输出7维：target-root XYZ、edge-rootX、platform_top-rootZ、request、age_s。各坐标必须同一 task/world frame。CPU 已验证同 proprio/不同任务 X 的距离可见，整体平移不改相对输入；本函数不改变目标或成功标准。
- static_layout 的14类字段是 material static/dynamic friction/restitution、body mass/inertia/COM、joint armature/friction/stiffness/damping、motor episode scale、gas preload target、legs/wheels lag、leg encoder episode bias。PD/弹簧刚度和阻尼来自真实 joint drive 字段。没有采样范围、名义值填充或伪造实际 getter。调用者明确给出实际 body/joint/material/gas 顺序；不可把动态 motor.step_scale 塞进 episode_scale。xi() 按 layout 顺序拼接，输出维数取决于实际组件数量。
- EpisodeStaticContext.selected_reset(ids,new_full_batch_readback,new_episode_ids) 要求完整读回；非 reset 行任一静态值改变即拒绝，episode 仅选中行+1，失败不修改 snapshot。assert_unchanged 检查回合内漂移。真实 DR 没有重新抽样：模块只保存原组件的值。
- unroll_processed_target_control 输入原 processed targets6 与 old_applied6，以及静态 lag[N,2]（legs,wheels）。必须是原10000us控制/2500us物理边界、无尚待执行命令；四个 apply-before-integration 子步使用 where(substep>=lag,new,old)。输出 applied_substeps[N,4,6] 和 next_old_applied。原 CAD/scale/offset/PD/queue 均不改。它精确建模队列的目标选择，不模拟电机、力、接触或物理。reset_old_applied 只对选中行使用真实 default leg q/zero wheel velocity，其他行保留。

新 CPU 测试23/23通过：与实际原 PhysicsActionQueue 源码比较所有9种腿轮lag组合，连续三控制，第3控制前选定reset；648个目标条目逐值相同，并核首应用延迟。原重复 submit/apply 回调保持一致。梯度为新目标4-lag、旧目标lag；还覆盖54维往返、request边界、相对任务位置、静态非reset拒绝/原子性，以及pending、错时钟、mid-control、坏lag、非有限、缺组件等负例。只用tiny synthetic，不运行actor/WM/physics或实际SDK。

实际准入仍 pending：read_actual_episode_parameters(env) 故意抛 NotImplementedError。必须补完整实际 getter、组件启用状态、实际顺序、所有 reset hook 结束后的采集与读回，才能提供真实静态 xi。任何实际存在的气阻、每步 motor gain、反馈延迟队列/缓存也须审查并分类，不能因为默认aux54而声称状态完全Markov或冻结这些量。根负责 tuple/base SO3 + aux54 的新网络、processed-action 可微路径、目标接口、保存/恢复与真实SDK准入；不能将本报告当作这些工作已完成。没有把状态伪装为虚拟关节，也没有旧128输入兼容声明。

原源码SHA和本次错误在 SOURCE_LINEAGE_AND_READER_ERRORS_ACTUAL.json；完整接口在 TYPED_INTERFACE_CONTRACT_ACTUAL.json。所有source lookup错误、PowerShell reader错误均保留；本轮CPU没有失败。归档由根负责，本 helper 未执行 Git/账本/SSH/GPU/PT/raw 操作。
