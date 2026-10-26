"""Freeze existing implementation/results; no runtime or tests executed here."""
from pathlib import Path
import json,hashlib,datetime
D=Path(__file__).resolve().parent;T=D.parent.parent;W=T.parent
R=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2/job0/runtime/isaac/mod4'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
    with (D/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False)
files=['mild_dr.py','explicit_pd_sdk_adapter.py','explicit_pd_component.py','chassis_com_pose_roundtrip_sdk_adapter.py',
       'chassis_com_component.py','gas_damping_sdk_adapter.py','gas_damping_factor.py','gas_damping_training_env.py',
       'spring_pressure_index_runtime.py','spring_pressure_training_env.py','spring_pressure_component.py',
       'sensor_mild_math.py','action_delay_physics_queue.py','action_delay_sdk_adapter.py',
       'chassis_pd_training_env.py','spring_nominal_sdk_readback.py']
paths=[R/f for f in files]+[W/'MOD4_D6_DAMPING_SOURCE_PREPARE_20261008/reviewed_sources/installed_articulation_data.py',
    W/'MOD4_D5_SPRING_LAW_PREPARE_20261008/installed_sdk_sources/physx_articulation.py',
    D.parent/'agent_static_dynamic_delay_contract_candidate/static_dynamic_delay_contract_v1.py']
save('SOURCE_LINEAGE_AND_ERRORS_ACTUAL.json',dict(
    inputs=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in paths],
    source_getter_locations=dict(
       D0='mild_dr.py MildDR.__init__/__call__: mass/inertia baseline*factor, CPU materials/mu, episode_scale[N,4]+[N,2], reset_count',
       D7COM='chassis_com_pose_roundtrip_sdk_adapter.py ChassisCOMSDK.expected_full_pose: original_pose XYZ + component.delta_m on body_id',
       D7PD='explicit_pd_sdk_adapter.py ExplicitPDSDK.audit_parameters; explicit_pd_component.py coefficients()',
       D5='spring_pressure_index_runtime.py SpringPressureSDK; spring_pressure_training_env.py LearningSpringPressure.apply; component.actual_stiffness(nominal)',
       D6='gas_damping_sdk_adapter.py GasDampingSDK; component.actual_damping_Ns_per_m()',
       D4='action_delay_physics_queue.py PhysicsActionQueue.groups lag_steps/episode/applied/last_apply_tick/pending_valid',
       D1='sensor_mild_math.py SensorCorruption.bias/episode',
       SDK_parameter_buffers='installed_articulation_data.py joint_armature/joint_friction_coeff/joint_stiffness/joint_damping properties are existing parameter arrays'),
    errors_preserved=[dict(kind='rg_inventory_access_denied',path=str(W/'rmuc2026_work/unpack_verify_4zomhj13'),
        result='No access attempted beyond failed file inventory; used known saved installed SDK source instead.'),
        dict(kind='reader_output_truncated',result='Narrow explicit source reads followed; no missing text used as actual admission evidence.')],
    no_failed_CPU_tests=True,no_PT_raw_NPZ_or_USD_read_or_hashed=True,
    saved_SDK_source_note='Earlier local installed SDK source supports buffer codec review; exact future target SDK readback still required.'))

mapping=[
 ('material_static_friction','D0.materials selected CPU rows; wheel slots <- D0.mu','N,M'),
 ('material_dynamic_friction','same; original D0 sets static==dynamic mu','N,M'),
 ('material_restitution','baseline nonwheel; wheel0 from exact original D0 write','N,M'),
 ('body_mass','D0.mass * D0.factor','N,B'),
 ('body_inertia','D0.inertia * D0.factor','N,B,9'),
 ('body_com','D7 original_pose XYZ + delta_m at chassis body_id','N,B,3'),
 ('joint_armature','robot.data.joint_armature existing buffer','N,30'),
 ('joint_friction','robot.data.joint_friction_coeff static effort existing buffer','N,30'),
 ('joint_stiffness','existing implicit buffer + explicit legs/wheels actuator coefficients; D5 crosscheck','N,30'),
 ('joint_damping','existing implicit buffer + explicit legs/wheels actuator coefficients; D6 crosscheck','N,30'),
 ('motor_episode_scale','actual legs.episode_scale4 + wheels.episode_scale2','N,6'),
 ('gas_preload_target','cfg.events.gas_spring_preload.params.targets, exact gas joint order','N,2'),
 ('action_lag_steps','original queue legs/wheels groups.lag_steps','N,2'),
 ('leg_encoder_episode_bias','_sensor_mild.bias','N,4')]
save('ACTUAL_DR_MEMORY_MAPPING_CONTRACT.json',dict(candidate=True,actual_installed_SDK_admitted=False,
    module='actual_DR_memory_getter_v1.py',module_SHA=H(D/'actual_DR_memory_getter_v1.py'),
    api=['RuntimeOrderBinding(body_names,joint_names,leg_joint_names,wheel_joint_names,gas_joint_names,material_shape_count)',
         'ActualDRMemoryGetter(env,binding).capture_initial()',
         'reset_ids_since_capture(); refresh_after_resets(ids=None)',
         'snapshot(); xi(); field_shapes()',
         'read_old_processed_applied(env,issue_tick)'],
    xi_order=[dict(name=n,memory_source=s,shape=shape) for n,s,shape in mapping],
    correction=dict(old_frozen_catalog_motor_episode_scale_dim=2,actual_motor_episode_scale_dim=6,
        old_frozen_file_unchanged=True,new_layout_required=True,
        caller_rule='Use actual getter.field_shapes(), not old static_layout motor-group width2; all14 field names retained.'),
    reset_contract=dict(after_all_original_reset_hooks=True,
        epochs=['D0','D1','D4legs','D4wheels','D5','D6','D7COM','D7PD'],
        rule='Each selected epoch increments exactly1; nonselected epoch unchanged; refuse missing/multiple/partial reset',
        no_reset_friction_transfer=True,selected_rows_only_CPU_material_transfer=True,
        nonreset_cache_bytes_preserved=True,
        limitation='Unselected source parameter drift without an episode-count change is not reread by this cache; original component selected-reset guards and actual admission remain required.'),
    dynamic_queue=dict(fields='queue.groups legs.applied4 + wheels.applied2',
        request_policy_action_not_used=True,clock='before submit, issue multiple4, last_apply=issue-1, no pending',
        first_initial_neutral_allowed=True),
    pending=['Actual target SDK source/order/material-shape binding and backend equality qualification',
        'Install getter only after complete original reset chain; constructor-time getters cannot preempt D7 reset',
        'New model input/checkpoint schema must use motor gain6 and actual field dimensions',
        'This is component-memory readout, not a fresh PhysX material/parameter readback or hardware calibration',
        'Static catalog joint_friction is static effort; additional dynamic/viscous coefficients are outside these14 fields and must not be silently relabeled',
        'No per-step motor noise supported here; active step_scale!=1 rejects, matching pinned MildDR audit']))

handoff='''本目录已冻结，旧模块与所有 payload/runtime 未修改。actual_DR_memory_getter_v1.py 可读原 D0-D7 内存，无 SDK 导入、参数 setter、后端 material getter、随机采样、actor 或物理执行。

用法：创建 RuntimeOrderBinding，明确 pin actual body/joint30、四腿/双轮/双气簧顺序和材料 shape 数；创建 ActualDRMemoryGetter(env,binding)，在整个原 reset chain 完成后 capture_initial()。之后仅在 reset 交接处 refresh_after_resets(ids)；它验证8组 epoch 同选中行+1，拒绝遗漏/重复/未完成 reset，仅重新读取选中行并原子更新缓存。无 reset 时不传 CPU friction，选中 reset 只传所选 CPU materials/mu 行；snapshot()/xi() 从设备缓存返回，不访问 CPU friction。非reset xi保留缓存原值；不声称它重新核验了未重置物理参数，实际组件/SDK审查仍需独立完成。

14字段映射见 ACTUAL_DR_MEMORY_MAPPING_CONTRACT.json。重要纠正：原 MildDR 对6个电机分别采 episode gain，legs[N,4]+wheels[N,2]，所以 motor_episode_scale 必须是6维；旧冻结候选catalog的2维占位不可直接用。新 getter 的 field_shapes() 给出真实 shape，其余14字段名保持。PD stiffness/damping读取显式 actuator 参数覆盖隐式 drive零槽，并与原 ExplicitPD.component.coefficients()逐值核对；气簧两项与D5/D6 factor值核对。COM用原 pose XYZ+真实delta，不触碰principal-axis quaternion；mass/inertia用原nominal memory乘当前D0 factor。摩擦复用原CPUcache，wheel restitution0来自原D0明确写法，非缺字段默认值。joint_friction取SDK现有joint_friction_coeff静态effort缓存，未伪造dynamic/viscous值。gas preload取原实际事件targets及原气簧顺序，无fixture数值补缺。

read_old_processed_applied(env,issue_tick)直接返回原 queue.groups 的 applied4+2，核原2500/10000us、控制边界、last_apply、pending。它不取env.action_manager.action，也不将最后新policy动作误当全4个子步的实际目标。

CPU15/15通过：使用真实原 ChassisCOM、ExplicitPD、SpringPressure、GasDamping、SensorCorruption、PhysicsActionQueue 的tiny CPU实例；D0为明确标注的duck内存，原MildDR需要SDK，未冒充实际实例。覆盖14字段映射、显式PD/implicit0区别、6motor gain、selected reset与非reset缓存、无reset不传摩擦、实际queue applied读取、缺字段/错维度/错顺序/非有限、动态gain拒绝、D5/PD不一致、未完成/错过reset，以及失败更新不发布partial cache。没有实际 SDK 准入证据。

剩余：根需要将此getter安装在完整reset之后，绑定目标实际SDK/order/material数量，做一次真实backend值/组件memory相符的准入，并使用新的真实static维度接模型保存/恢复。缓存不会每step主动核查无epoch变化的非reset静态漂移；这一点是明确限制，不是已通过的runtime保证。所有来源SHA、reader inventory错误和完整文件索引已保存，helper未Git/SSH/GPU/PT/raw/账本操作，归档由根负责。
'''
with (D/'FROZEN_MEMORY_GETTER_HANDOFF.md').open('x',encoding='utf8') as f:f.write(handoff)
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
rows=[dict(path=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='FROZEN_ACTUAL_DR_MEMORY_GETTER_SHA_INDEX.json']
save('FROZEN_ACTUAL_DR_MEMORY_GETTER_SHA_INDEX.json',dict(frozen_at_UTC=stamp,files_excluding_index=rows,
    files_excluding_index_count=len(rows),old_frozen_and_payload_untouched=True,actual_SDK_admitted=False,parent_archive_pending=True))
print(json.dumps(dict(frozen_at_UTC=stamp,module_SHA=H(D/'actual_DR_memory_getter_v1.py'),
    index_SHA=H(D/'FROZEN_ACTUAL_DR_MEMORY_GETTER_SHA_INDEX.json'),files_excluding_index=len(rows))))
