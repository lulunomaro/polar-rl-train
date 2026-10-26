"""Index this bounded candidate, including lookup/reader errors; no new tests."""
from pathlib import Path
import json, hashlib, datetime
D=Path(__file__).resolve().parent
T=D.parent.parent
B=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2'
R=B/'job0/runtime/isaac/mod4'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
    with (D/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False)
cpu=json.loads((D/'STATIC_DYNAMIC_DELAY_CONTRACT_CPU_V1_ACTUAL.json').read_bytes())
put('SOURCE_LINEAGE_AND_READER_ERRORS_ACTUAL.json',dict(
    source_only=True,
    inputs=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in [
        R/'action_delay_physics_queue.py',R/'action_delay_sdk_adapter.py',R/'action_delay_training_env.py',
        R/'contact_capture.py',R/'mod4_task.py',R/'spring_pressure_training_env.py',
        R/'sensor_mild_math.py',B/'source/h1_supermimic_bridge_v1.py',B/'h1_step270_sdk_runtime_candidate.py']],
    errors_preserved=[
        dict(kind='source_lookup_missing',path=str(R/'actions.py'),correction='Actual processed-target adapter is action_delay_sdk_adapter.py; no guessed file created.'),
        dict(kind='PowerShell_reader_error',error='Select-Object -Index with comma-separated ranges produced Object[] to Int32 conversion error',correction='Read requested source array slices directly; no source mutation.'),
        dict(kind='source_lookup_missing',path=str(R/'integrated_contact_capture.py'),correction='rg located contact_capture.py; actual history is N,3,2,3.'),
        dict(kind='source_lookup_missing',path=str(R/'mild_dr_runtime.py'),correction='No guessed file used; complete actual DR mapping explicitly pending.'),
        dict(kind='source_lookup_missing',path=str(R/'feedback_delay_math.py'),correction='No guessed file used; actual sensor-delay mapping explicitly pending.'),
        dict(kind='reader_output_truncated',correction='Bounded follow-up source reads used; no missing-text inference used to claim SDK admission.')],
    no_failed_CPU_test=True,CPU_report_preserved='STATIC_DYNAMIC_DELAY_CONTRACT_CPU_V1_ACTUAL.json',
    no_PT_raw_NPZ_actor_WM_physics_GPU_SSH_training_or_Git=True))

put('TYPED_INTERFACE_CONTRACT_ACTUAL.json',dict(
    candidate=True,actual_SDK_admitted=False,version='native_static_dynamic_delay_v1_new_interface',
    module='static_dynamic_delay_contract_v1.py',module_SHA=H(D/'static_dynamic_delay_contract_v1.py'),
    dynamic_aux=dict(dim=54,fields=[dict(name='contact_history',offset=0,width=18,shape=['N',3,2,3],order='newest5msbin_first,left_right,xyz'),
        dict(name='applied_torque',offset=18,width=30,shape=['N',30],order='actual_runtime_ordered_joint_names'),
        dict(name='old_processed_applied',offset=48,width=6,shape=['N',6],order='original legs4 then wheels2')]),
    request=dict(api='request_from_age(age_int64_N)',rule='100 <= age < 180',static_xi=False),
    age_advance=dict(api='advance_age(age,reset_mask)',rule='after completed control increment once, then selected reset to0'),
    task_relative=dict(api='task_relative_observation(root_xyz,target_xyz,edge_x,platform_top_z,age)',dim=7,
        fields=['target_dx','target_dy','target_dz','edge_dx','platform_top_dz','public_request','age_s'],
        same_position_coordinate_frame_required=True),
    delay=dict(api='unroll_processed_target_control(processed_targets,old_applied,lag_steps,issue_tick=...,last_apply_tick=...,pending_valid=...)',
        input_shapes=dict(processed_targets=['N',6],old_applied=['N',6],lag_steps=['N',2]),
        lag_order=['legs','wheels'],lag_values=[0,1,2],lag_unit_us=2500,control_us=10000,
        output_shape=['N',4,6],clock_boundary='issue_tick multiple4; last_apply_tick==issue_tick-1; no pending command',
        formula='target if substep_index>=group_lag else old_applied',
        next_old_applied='applied_substeps[:,-1,:]',original_queue_unchanged=True,
        processed_target_units='legs original position rad; wheels original angular velocity rad/s'),
    static=dict(api='static_layout(...); EpisodeStaticContext(layout,values,episode_ids)',
        reset_api='selected_reset(ids,new_full_batch_readback,new_episode_ids)',
        update_atomic=True,nonselected_values_exact=True,randomization_implemented=False,
        getter='read_actual_episode_parameters(env) raises NotImplementedError',
        no_component_default_values=True,no_dynamic_contact_torque_request_in_xi=True),
    CPU=dict(passed=cpu['passed'],passed_count=cpu['passed_count'],total=cpu['total']),
    pending=['Actual component getter/readback and ordered SDK body/joint/material mapping',
        'After-all-reset-hooks static capture timing and real selected/nonselected readback',
        'Any active aerodynamic, per-step motor gain or sensor-delay component mapping; do not silently freeze dynamic randomness',
        'Root-owned augmented WM/learner/action-processing integration and new checkpoint/input schema',
        'Actual installed SDK and plant admission; no fixture may serve as that proof']))

handoff='''候选已完成并冻结；旧 frozen/payload/runtime 完全未改。本目录是下一 native 版本的 source/CPU 合约，不是实际 SDK 准入，也不兼容旧 actor128 权重输入。

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
'''
with (D/'FROZEN_CANDIDATE_HANDOFF.md').open('x',encoding='utf8') as f:f.write(handoff)
rows=[dict(path=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='FROZEN_STATIC_DYNAMIC_DELAY_SHA_INDEX.json']
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
put('FROZEN_STATIC_DYNAMIC_DELAY_SHA_INDEX.json',dict(schema='mod4.source_CPU_candidate.complete_index.v1',
    frozen_at_UTC=stamp,source_only=True,directory=str(D),files_excluding_this_index=rows,
    files_excluding_index=len(rows),actual_SDK_admission=False,old_directories_untouched=True,
    ordinary_archive_by_parent_pending=True))
print(json.dumps(dict(frozen_at_UTC=stamp,files_excluding_index=len(rows),module_SHA=H(D/'static_dynamic_delay_contract_v1.py'),
    index_SHA=H(D/'FROZEN_STATIC_DYNAMIC_DELAY_SHA_INDEX.json'),CPU=f"{cpu['passed_count']}/{cpu['total']}")))
