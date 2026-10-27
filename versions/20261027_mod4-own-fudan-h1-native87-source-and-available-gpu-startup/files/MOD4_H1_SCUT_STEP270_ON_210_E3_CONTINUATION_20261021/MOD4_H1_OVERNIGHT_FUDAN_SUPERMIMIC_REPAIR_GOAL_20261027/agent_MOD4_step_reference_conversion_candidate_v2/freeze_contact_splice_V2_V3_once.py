"""Freeze successful static splice and source/reporting errata; no IK rerun."""
from pathlib import Path
import json,hashlib,datetime
D=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
    with (D/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
result=json.loads((D/'V2_POSTCONTACT_IK_SOURCE_CPU_RESULT_ACTUAL.json').read_bytes())
wall=json.loads((D/'V2_ORIGINAL_WHOLE_PATH_SIDEWALL_CHECK_ACTUAL.json').read_bytes())
erratum=json.loads((D/'V3_EXISTING_TABLE_SIDEWALL_REPAIR_AND_METADATA_ERRATUM_CPU_ACTUAL.json').read_bytes())
final=D/'OWN_STEP_REFERENCE_TABLES_V3_SIDEWALL_REPAIRED_CANDIDATE_NOT_ADMITTED.json'
table=json.loads(final.read_bytes());m=table['metadata']
assert result['source_CPU_passed'] and wall['passed'] and erratum['passed']
put('FINAL_OWN_STEP_REFERENCE_HANDOFF_CONTRACT_ACTUAL.json',dict(
    candidate_table=dict(path=str(final),bytes=final.stat().st_size,SHA=H(final)),
    schema_fields=['ages','control_dt_s','packed73','mask73','phase','joint_names','metadata'],
    ages=[table['ages'][0],table['ages'][-1]],control_dt_s=.01,packed_state_shape=[len(table['ages']),73],
    mask_root_XY_and_velocity_enabled=True,source_kinematic_only=True,actual_SDK_admitted=False,
    static_checks=dict(original_IK_all21_fit=True,source_air_preserved_before_age145=True,
        max_closure_m=m['closure_max_m'],min_postcontact_wheel_bottom_m=m['min_postcontact_wheel_bottom_m'],
        no_sidewall_intersection=wall['passed'],first_front_cross_age=[130,130],
        straddle_min_bottom_m=[w['min_bottom_during_straddle_m'] for w in wall['wheels']],
        source_contact_used_as_own_contact=False),
    contact_phase=dict(first_touch_age=145,interpolated_original_144_to145_fraction=m['first_touch_interpolation_fraction'],
        first_touch_bottom_m=m['first_touch_bottom_left_right_m'],contact_transition_controls=20,
        support_age=165,support_root_z_m=m['support_root_z_m'],
        final_masked_q_max_rad=m['final_masked_joint_abs_max'],
        final_center_height_error_to_platform_plus_radius_m=m['final_center_height_error_to_platform_plus_radius_m']),
    numerical_trajectory_changed_after_V2_IK=False,
    filename_note='V3_SIDEWALL_REPAIRED basename is generic: actual delayed_approach_repair.changed=false; only metadata label corrected.',
    metadata_reporting_error=dict(original_field='entry_masked_motor_q_abs_max',original_field_really_all30_joint_max=True,
        includes_unobserved_wheelspin=True,original_source_and_reports_preserved=True,
        corrected_entry_masked_q_max_rad=m['entry_masked_joint_abs_max'],
        corrected_final_masked_q_max_rad=m['final_masked_joint_abs_max'],
        canonical_IK_source_AST_identical_except_metadata_assignment=True),
    pending=['Actual actuator/torque/power/impulse feasibility and real training/model admission',
        'Actual single-wheel to dual-wheel support, postcontact physical correction and original event/callback skill standard',
        'Full body nonpenetration and non-wheel/roller authored transform equivalence',
        'Reference contact-stage floor targets are kinematic plans, not measured contact or force',
        'Near-standing endpoint q differs from exact zero by up to .004628rad under original1mm wheel-center IK tolerance; this is explicit, not literalq0 claim',
        'Explicit goal handling beyond age300 and future10 window boundary must be declared by root provider; no silent clip change',
        'Delayed-approach fallback source branch was not exercised because actual path already passed sidewall check']))
handoff=f'''V2/V3静态转换候选已冻结，V1及所有旧目录未改。

根可直接使用最终镜像表：{final.name}。SHA {H(final)}。含 ages0..300、control_dt_s=.01、packed73/mask73、phase、own joint_names30及metadata.phase_contract；rootXY与velocity槽包含独立own前进goal。basename带SIDEWALL_REPAIRED，但本次实际changed=false：数值轨迹没有变，只更正metadata标签。numpy future10接口沿用冻结V1 own_step_reference_tables_v1.py；实际接Torch/MDP与age300后的hold/boundary规则由根声明。

V1拒绝全部保留。V2首次touch在原下降age144->145的0.342354插值，不把非neutral姿态瞬间改为q0；最先轮底[.27000000022,.32259748067]m，明确单轮先到，未假装双轮同时接触。source-air直到age144的Z/R/q/Vz/omega/qd逐字保持；独立own XY前进goal按V1参数改变，真实command仍.8/request100..179/source时钟不改。

age145..165共21帧，用原OwnUsdKinematics.solve(max_iterations40及原容差)逐帧解motor/passive闭链。接触阶段20controls逐渐使wheelcenter高度趋向.27+r，rootR回identity、rootZ回spawn+.27=.607742301121。没有在flight整体加.27m，也没有直接对30joint线性插值当闭链解。全帧IK STATIC_KINEMATIC_FIT；closure最大.0001683545768m，接触后wheelbottom最低.27000000022m，无平台穿透。末端center高度偏差[.000686169,.000043425]m；受mask关节max.00462826rad，是原1mm wheel-center IK容差下near-standing，不声称字面q30全零。未观测wheelspin保留并被mask排除。

初touch的max q跳变.0220555rad，小于原source相邻两帧.0644229；接触段max q步长.0293806rad。这只是静态连续性尺度，不是motor速度/力矩合格。自己的forward goal平均1.02521m/s、峰1.37969m/s与真实.8command差异完全保留；到达前目标峰ax10.208m/s²，驱动可行pending。

按根补充要求，已用生成表重算全段前缘/后缘侧壁窗口，未重IK：双轮首次前缘cross age130，straddling130..140；左最低bottom.299855894m、右.316101469m，分别高于平台29.8559/46.1015mm，violating ages均[]。故没有实施delayed-approach修改。sidewall_forward_repair_v3.py保留严格检查和必要时的XY修复代码；其修复分支此次未执行，不冒充已测试。

已保存一项真实报告命名错误及更正：初V2 metadata.entry_masked_motor_q_abs_max实际取了全部30q，包含unobserved wheelspin1.19601；真实受mask entrymax.3192155、endmax.00462826。原源码存为contact_splice_own_IK_v2_before_metadata_review.py，原表/CPU报告未覆盖；当前module只改metadata表达式，AST其余完全相同，未重IK。最终表采用正确字段。完整source/报告SHA见索引。

严格限制：这是候选own几何参考，不是actor动作、接触证据或技能毕业。实际电机/冲量/功率、全body非穿透、single->dual真实接触、物理接触后校正与原callback成功标准均pending。source contact从未当own接触，原物理/动作/年龄/command/成功条件未改。无PT/raw/NPZ/USD/mesh资产读取，无actor/WM/physics/GPU/SSH/Git/账本操作。归档由根负责。
'''
with (D/'FROZEN_CONTACT_SPLICE_V2_V3_HANDOFF.md').open('x',encoding='utf8') as f:f.write(handoff)
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
files=[dict(path=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='FROZEN_CONTACT_SPLICE_V2_V3_SHA_INDEX.json']
put('FROZEN_CONTACT_SPLICE_V2_V3_SHA_INDEX.json',dict(frozen_at_UTC=stamp,files_excluding_this_index=files,
    count_excluding_index=len(files),all_original_errors_and_source_preserved=True,actual_SDK_admitted=False,parent_archive_pending=True))
print(json.dumps(dict(frozen_at_UTC=stamp,files_excluding_index=len(files),final_table_SHA=H(final),
    IK_module_SHA=H(D/'contact_splice_own_IK_v2.py'),index_SHA=H(D/'FROZEN_CONTACT_SPLICE_V2_V3_SHA_INDEX.json'))))
