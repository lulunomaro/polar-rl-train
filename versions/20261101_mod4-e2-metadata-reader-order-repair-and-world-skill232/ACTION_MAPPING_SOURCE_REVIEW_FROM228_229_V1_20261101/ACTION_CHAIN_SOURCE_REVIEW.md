已证实存在更窄的静态 joint 范围：hip 为±0.5rad，crank为[-1.2,0.9]rad。
已消费的项目 process 只夹 crank−hip 的差，不改 hip。当前资料不能证明
hip目标被软件夹到±0.5，更不能把q接近0.5判为已观测clip或唯一原因。
本包只冻结源码核对；没有改模型、225副本、训练、奖励、物理或guard。

actual229验证了原 bound receiver，并保存mod4_task.py原字节SHA
7e326cdd9c3507f16109b3503c3cffd37c6f5fa312b42451d2de513af9e2b993。
210本地源码相同SHA。actual228保存的action_delay_sdk_adapter.py SHA
0053820a778b3c956bf1bd8754b269de28a35c7ea9fe2fb93f75061bf142b375也匹配。
228旧original_action_guard=false保留；229对原process receiver的核实为true。
这些元数据purpose没有执行物理control，不提供新的clip/扭矩观测。

actual228/229的真实policy顺序与0.5/offset0是：

|policy索引|关节|term内部索引|静态joint q范围(rad)|reward命名序索引|
|---:|---|---:|---|---:|
|0|left_crank|legs0|[-1.2,0.9]|0|
|1|left_hip|legs1|[-0.5,0.5]|1|
|2|right_crank|legs2|[-1.2,0.9]|3|
|3|right_hip|legs3|[-0.5,0.5]|4|
|4|left_wheel_spin|wheels0|连续转动；无有限q界|2|
|5|right_wheel_spin|wheels1|连续转动；无有限q界|5|

腿scale=.5rad、实际default offset四个0；轮scale=10rad/s、offset0。
导出contract里的旧action_slot_order_raw从hip开始，并非本次已核实的policy顺序，
不能再次盲用[1,0,3,2,4,5]交换。CONTRACT六motor名单顺序也不是完整30DOF索引。
Jump194原reward命名序[LC,LH,LW,RC,RH,RW]来自action_manager.action[:,
[0,1,4,2,3,5]]；它是请求action重排，不能当已投影/延迟后的物理target。

消费路径与各范围的作用分别如下：

1. 原RSL调用配置clip_actions=6。它是raw action范围，并非6rad joint范围。
2. ActionsCfg按名字、preserve_order=True分4腿+2轮；SDK仿射处理scale/default。
   实际0.5/offset0已记录。继承SDK的optional cfg.clip分支另见下述未知项。
3. DelayedJointPositionAction.process_actions在super后，只写pa[:,0]和pa[:,2]：
   crank'=min(max(crank,hip−1.0843),hip+0.85)。hips两列不被这段投影写入。
   training下界−1.0843与静态机械止挡−1.0863195404360622不同；+0.85来自
   原diff_max，actual229已记录。这不是各关节自身q范围投影。
4. D4 wrapper在原process后提交四腿coherent processed targets；旧control-step
   delay要求_max_lag=0。原物理队列只选/保持整组目标，延迟0/2500/5000µs，
   在2.5ms apply回调前给原apply，不夹target幅值。它暂换_processed_actions，
   调原apply后恢复；源码还会比较articulation target与队列值。该比较在本次
   source audit没有执行，不能冒称新实测PASS。
5. 原apply继承SDK JointPositionAction。历史已读SDK源码是set position target
   API，不是直接设置实际q。当前72这一继承方法与setter源码SHA本次未采集。
6. 项目显式PD名义腿Kp60/Kd2、轮Kp0/Kd0.6；D7因子各自[.95,1.05]，写
   actuator模型系数，保留motor implicit drive K/D=0。它不修改target或电机包络。
7. 历史SDK IdealPD参考为Kp(qtarget−q)+Kd(vtarget−v)+feedforward；DCMotor
   保存joint velocity，再进行带速度的torque clipping。D3只处理actor观测，
   没有把它的噪声/延迟反馈写进电机模型。当前72基类具体实现仍受下述未知项限制。
8. 已核实项目Mod4DCMotor._clip_effort顺序是super clip→episode_scale×step_scale→
   white_v3下再super clip。名义腿peak envelope40Nm、voltage截距53.333333Nm、
   no-load16.755160819rad/s；轮5.775909774/28.185328947/55.3557。它们是原
   工程模型参数，不是本次测得的扭矩。历史DC公式按速度上下包络clip，非target角度clip。
9. PhysX最后解动力学、joint限制与闭链；实际q不等于target，也不是软件clamp数组。
   2mm闭链和原倾倒/低底盘等guard未改。

对ROOT给出的近似左hip mean1.67..2.08：仿射部分是0.835..1.04rad。
它们没碰raw±6，却已经高于静态hip上界0.5。项目CAD差值投影不改变hip列。
若继承SDK没有额外clip，该目标仍会进入后续PD/动力学；这是条件推导，非实测target。
q接近0.5与静态joint上界相容，但也没有据此测出接触反力、实际PD误差、扭矩clip
比例或独立因果。目标越界也不自动等于torque饱和。

静态limit来源为实际asset旁import_contract.json，SHA
517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49；全joint
limits与mechanical_stop被索引到配套JSON。未打开USD/NPZ，也未新读PhysX限位。
原CAD stop的hip0.450290972/crank−0.636028568是一个机械姿态，不能把它
误作hip目标上限；−1.08631954是crank−hip差界。

SDK参考joint_actions.py SHAa3dd734c...来自旧210的IsaacLab3.0-beta已保存源码；
actuator_pd.py SHA105f0341...也是历史已读源。其optional cfg.clip与apply/PD/DC
公式只作为有来源的参考，不能替代当前72 exact-SHA证明。actual228/229没有保存
resolved cfg.clip、当前SDK基类process/apply/position setter/PD源码SHA，也没有
新target、q、torque序列；这些保持UNKNOWN，不构成停止健康训练的新gate。

独立draft review_action_path_source_once.py已写但未执行。ROOT随后要求只冻结，
因此没有创建/消费新边界CPU purpose，也没有运行其scalar例子或旧fixture。
本包包含静态报告/来源SHA与查询错误记录，待ROOT普通Git归档。它不是新修复或学习。
