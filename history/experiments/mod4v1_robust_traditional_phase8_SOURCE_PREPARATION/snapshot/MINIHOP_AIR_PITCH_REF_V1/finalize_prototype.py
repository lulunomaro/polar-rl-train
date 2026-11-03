"""Saved evidence only: no controller/test/entry/physics execution or raw read."""
from pathlib import Path
import ast,hashlib,json,re
T=Path(__file__).resolve().parent;D=T/'attempt002'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s1=load(T/'SOURCE_LOCK.json');s2=load(D/'SOURCE_LOCK.json');m1=load(T/'METHOD.json');m2=load(D/'METHOD.json')
l1=load(T/'attempt001/LIMITS_RESULT.json');l2=load(D/'LIMITS_RESULT.json');u=load(D/'UNIT_RESULT.json');en=load(D/'ENTRY_RESULT.json');at=load(D/'ENTRY_AST.json')
assert sha(T/'METHOD.json')==s1['method_SHA']and sha(T/'ARCHITECTURE.md')==s1['architecture_SHA']
assert sha(D/'METHOD.json')==s2['method_SHA']and sha(D/'ARCHITECTURE.md')==s2['architecture_SHA']
assert sha(T/'SOURCE_LOCK.json')==s2['original_precode_source_lock_SHA']and sha(T/'attempt001/LIMITS_RESULT.json')==s2['attempt001_failed_result_SHA']
for x in s2['sources']:assert sha(Path(x['path']))==x['SHA']
assert s1['sources']==s2['sources']and len(s2['sources'])==26
for key in ['pitch_coefficient','pitch_rate_coefficient_s','rate_limit_rad_s','period_s','air_pitch_ref_enable_default','operator_enable_default']:
    assert m1['fixed_parameters'][key]==m2['fixed_parameters'][key]
assert m1['synthetic_config']==m2['synthetic_config']and m1['budgets']==m2['budgets']
assert l1['status']=='NOT_READY_DOMAIN'and l1['violating_offset_count']==14 and l1['offsets']==51 and l1['math_gate_pass']and not l1['limits_gate_pass']
assert l2['limits_gate_pass']and l2['math_gate_pass']and l2['offsets']==51 and l2['violating_offset_count']==0
assert u['math_gate_pass']and u['reference_limits_gate_pass']and u['default_ticks']==u['enabled_ticks']==600 and u['reference_FK_rows']==416
assert sha(D/'controller.py')==u['core_SHA']==en['core_SHA']and sha(D/'run_manual_air_pitch_ref_v1.py')==en['entry_SHA']==at['entry_SHA']
assert en['status']=='PASS_TWO_CONTROLLED_REAL_ENTRY_PRELOOP_INVOCATIONS_NOT_FULLMODEL_ADMISSION'and len(en['rows'])==2
assert u['first_capture']['weight']==0. and len(u['fault_scenarios'])==16
assert at['control_loop_AST_identical']and at['entire_main_AST_identical_except_three_result_metadata_fields']
# Original and each executed-source snapshot stay byte-identical, no rerun.
for x in load(T/'attempt001/PREEXEC.json')['files']:
    assert sha(T/'attempt001'/x['path'])==x['SHA']==sha(T/x['path'])
for folder in [D/'limits_preexec',D/'unit_attempt001',D/'entry_attempt001']:
    pre=load(folder/'PREEXEC.json')
    for x in pre['files']:
        source=(T/'fk_limits.py')if x['path']=='fk_limits.py'else D/x['path']
        assert sha(folder/x['path'])==x['SHA']==sha(source)
for x in en['rows']:
    p=D/x['output'];assert sha(p/'ERROR.json')==x['expected_stop_ERROR_SHA']and sha(p/'SOURCE_MANIFEST.json')==x['source_manifest_SHA']
    err=load(p/'ERROR.json');assert err['controls']==err['physics_steps']==0
    assert err['trace_prefix']['actual_prefix_matches_producer']and err['physics_prefix']['actual_prefix_matches_producer']
    assert (p/'trace.jsonl').stat().st_size==(p/'physics.jsonl').stat().st_size==0 and not(p/'result.json').exists()
for x in [l1,l2,u]:assert x['model_boots']==x['forward_calls']==x['integrator_calls']==0
assert all(v==0 for k,v in en['counts'].items()if not k.startswith('fake_'))
# Check active controller imports are sensor-estimate-only; no new plant access.
ct=ast.parse((D/'controller.py').read_text(encoding='utf-8'))
imports=[]
for n in ct.body:
    if isinstance(n,ast.Import):imports += [x.name for x in n.names]
    elif isinstance(n,ast.ImportFrom):imports.append(n.module)
assert imports==['math','numbers','numpy','MINIHOP_POSITION_TRIGGER_V1.controller']
bad=[x for x in l1['rows']if not x['within_limits']]
first_bad=bad[0]['h'];max_excess=max(z['excess']for x in bad for z in x['violations'])
summary=dict(status='PROTOTYPE_READY_FOR_PARENT_INDEPENDENT_REVIEW_ZERO_STEP_ONLY_NOT_PHY_ADMISSION',
    attempt001=dict(status=l1['status'],offsets=51,violating_offsets=14,FK_failures=l1['FK_failures'],first_bad_h=first_bad,max_limit_excess_rad=max_excess,original_source_and_locks_preserved=True),
    attempt002=dict(parameters=m2['fixed_parameters'],offsets=51,violating_offsets=0,nominal_positive_endpoint_hip_margin_rad=l2['minimum_joint_margins']['left_hip'],
        max_common_rotation_error_m=l2['max_common_rotation_error_m'],max_delta_error_rad=l2['max_delta_error_rad'],
        old_sources_unchanged=26,unit_assertions=u['assertions'],legacy_nodes_compared=u['legacy_nodes_compared'],
        default_ticks=600,enabled_ticks=600,enabled_approach_push_ticks=u['enabled_approach_push_ticks'],flight_wheel_bit_same_ticks=u['flight_ticks'],
        capture_ticks=u['capture_ticks'],actual_reference_FK_limits_rows=u['reference_FK_rows'],max_rate_step_rad=u['max_rate_step_rad'],
        max_capture_ref_continuity_error_rad=u['max_capture_ref_continuity_error_rad'],first_capture=u['first_capture'],final_reference4=u['final_reference4'],
        finite_clock_faults=u['fault_scenarios'],phase_events=u['phase_events'],fixed_K0_K1_ff0_ff1_eq1_unchanged=True,finally_restores_on_inner_exception=True,
        core_SHA=u['core_SHA'],entry_SHA=en['entry_SHA'],entry_AST=at,entry_counts=en['counts'],entry_preloop_rows=en['rows']),
    qualification=dict(fullmodel_and_asset_admission='UNKNOWN_NOT_ATTEMPTED',DR_actual_joint_limit_safety='UNKNOWN_NOT_PROVEN_BY_NOMINAL_REFERENCE_MARGIN',
        dynamic_stability_or_performance='UNKNOWN_NO_PHY_OR_NEW_EPISODE',capture_wheel_bit_invariance='NOT_A_GATE_DO_NOT_EXTRAPOLATE_FLIGHT_ONLY_RESULT',
        gain_fit=False,gain_range_or_timing_fitted_to_DR=False,raw_H5_R60_read=0,old_QA_replay=0,new_model_linearization=0,C_compile=0,Git_actions=0,new_agents=0,
        permission_or_contact_confidence_promoted=False,PH7_pending=True,no_THIRD_hypothesis=True))
with(T/'SUMMARY.json').open('x',encoding='utf-8')as f:json.dump(summary,f,indent=2,allow_nan=False);f.write('\n')
lines=[
'# MINIHOP_AIR_PITCH_REF_V1 — 001反证保留；002仅零步prototype ready',
'',
'## 版本与预锁，不改旧结果/模型',
'- [001原架构](<attempt001/ARCHITECTURE.md>) / [原参数](<attempt001/METHOD.json>) / [原小源锁](<attempt001/SOURCE_LOCK.json>)在code前固定±.10；实际[51点](<attempt001/LIMITS_RESULT.json>)得到**14点超限、FK失败0、NOT_READY_DOMAIN**，[exit1原log](<limits_001.log>)保留，不以FK通过冒称READY。首超限h='+f'{first_bad:.6f}'+'，最大超出原上限'+f'{max_excess:.9f}'+'rad。',
'- 父随后仅授权[002新架构](<attempt002/ARCHITECTURE.md>) / [METHOD](<attempt002/METHOD.json>) / [新锁](<attempt002/SOURCE_LOCK.json>)：hGoal=clip(.25*estimated14[2]+.04*estimated14[9], **[-.10,+.03]rad**)，100Hz、rate1rad/s。kp/kd/rate、既有gain/时序/observer/轮公式均不改；这是公开crouch/机械model上限修domain，不从DR/GT或unitddot拟gain。没有第三版。',
'- 002实际[51点gate](<attempt002/LIMITS_RESULT.json>)：0超限/FK0失败，共旋转误差'+f"{l2['max_common_rotation_error_m']:.3g}"+'m，delta误差0，左右reference对称；正端名义hip余量'+f"{1000*l2['minimum_joint_margins']['left_hip']:.9f}"+'mrad。**参考在名义限位内，不证明DR实际关节/动态跟踪也在限位内。**',
'',
'## 实际prototype语义',
'- [002 controller](<attempt002/controller.py>)继承原Position→Landing V3→Observer V2→V1。air_pitch_ref_enable缺省False时literal delegate原prepare/command；operator缺省仍False，没有新接触/air/世界位置/许可。启用要求显式原V3 landing_transition_enable，不偷偷开启它。',
'- flight仅super前临时q_start=original+h*ones4，finally恢复原对象；super实际算原140/3腿PD和25*pitch+4*pitchrate wheel项。没有在super后改tau，目标日志来自实际super。delta与L/R对称保持；仅16种坏输入提前INHIBIT/fault，不把NaN带入h/anchor。',
'- 首timedcapture冻结last h，eq0仅hip indices3/5平移，delta4/6不动；**super前**真实ctrl.eq/ref[3:7]设anchored eq0，覆盖V3首capture u=0不写ref陷阱。K0/K1/ff0/ff1/eq1不变，原landing_weight自然到eq1，h不突然清零。',
'- 这是air-ref反馈+连续capture anchor，不只是改空中τ。capture应看真实landing_position_ref4/ctrl.ref，不拿旧legacy target_q4冒充。flight轮τ位同结论不外推capture：新ref可能经原P25 LQR耦合影响capture轮输出；轮公式、K/ff没有改，也不事后补偿。',
'',
'## 一次预声明synthetic验证，不是旧QA/PHY',
'- [原始UNIT_RESULT](<attempt002/UNIT_RESULT.json>) / [执行前source snapshot](<attempt002/unit_attempt001/PREEXEC.json>) / [log](<attempt002/unit_001.log>)：'+str(u['assertions'])+'结构/数值断言0fail（含'+str(u['legacy_nodes_compared'])+'legacy节点比较，不是这么多个独立case）。',
'- **缺省off600tick**与原Position全部legacy math/state及log逐bit相同。仅harness将非控制的perf_counter_ns固定0以比对wall诊断；未替换任何控制数学。',
'- **enabled600tick**中approach/push '+str(u['enabled_approach_push_ticks'])+'tick逐bit同；预测flight '+str(u['flight_ticks'])+'tick的wheel τ逐bit同，h独立clip/rate oracle通过。最大每tickΔh='+repr(u['max_rate_step_rad'])+'rad，原1e−14容差未动。',
'- 实际'+str(u['reference_FK_rows'])+'行flight/capture reference均做双腿公开pure FK/原XML限位，0violation；16 finite/type/clock故障均先于ref/scheduler mutation锁存，异常finally恢复亦通过。0模型/forward/integrator/线性化；unit连MuJoCo模块也未导入。',
'- 真实首capture '+f"{u['first_capture']['t']:.2f}"+'s、V3 landing_weight=0，anchor='+repr(u['first_capture']['anchor'])+'rad；进入实际GroundController.command前ref已偏移，非补造log。与末flight4-ref最大差'+f"{u['max_capture_ref_continuity_error_rad']:.3g}"+'rad，保留浮点运算次序差，不宣称逐bit连续；原1e−12预算内。最后eq1/K1/ff1及leg目标逐bit正确。',
'',
'## 新entry与受控零步入场',
'- [新entry仍在attempt002树内](<attempt002/run_manual_air_pitch_ref_v1.py>) / [AST receipt](<attempt002/ENTRY_AST.json>)：由原run_manual_position_v4派生，constructor call/control loop完全AST同，完整main仅3个result元数据字段差；另改package bootstrap/import/source manifest，未改actuator/grade。未做generic basename launcher兼容，父独立集成。',
'- [ENTRY_RESULT](<attempt002/ENTRY_RESULT.json>)：实际main() flagFalse/True各一次，真实新controller、geometry、StateEstimator、loaders和StreamedRows初始化；plant/DR/bounds/上游大asset-manifest明确受控fake，在首for-loop body前停止。实际model/forward/6integrator/其它dyn/packet/actuator/loop-body尝试全0。',
'- [OFF预期stop ERROR](<attempt002/entry_attempt001/actual_main_off/ERROR.json>) / [ON预期stop ERROR](<attempt002/entry_attempt001/actual_main_on/ERROR.json>)及空trace/physics prefix SHA原样保留：这是预期的controlled stop，不是PHY失败补档或成功trial；无result.json。**完整model boot/大asset复核、动态/driver准入均UNKNOWN。**',
'',
'## 交付资格',
'- [小SUMMARY](<SUMMARY.json>)和本报告是**READY_FOR_PARENT_INDEPENDENT_REVIEW，ZERO_STEP_ONLY**；001仍NOT_READY_DOMAIN。26个旧小源最终SHA不变，原模型上限、gain/observer/grade/旧结果/H5/R60 raw均未动；无新PHY/编译/Git/agent/旧QA/模型线性化。',
'- 没有从本结果选择稳定gain、证明闭环稳定或DR安全，没有新contact/FSM/MPC许可。父R62尚为独立DRAFT/后续审查与PHY决定，本任务未读该计划或R60raw，不代执行。**PH7 pending，整个候选树不扩大既有cutoff。**',
]
text='\n'.join(lines)+'\n';assert len(lines)<=m2['budgets']['report_max_lines']
with(T/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write(text)
for dest in re.findall(r'\]\(<([^>]+)>\)',text):assert(T/dest).is_file(),dest
files=['REPORT.md','SUMMARY.json','SOURCE_LOCK.json','METHOD.json','ARCHITECTURE.md','limits_001.log','attempt001/PREEXEC.json','attempt001/LIMITS_RESULT.json',
       'attempt002/SOURCE_LOCK.json','attempt002/METHOD.json','attempt002/ARCHITECTURE.md','attempt002/LIMITS_RESULT.json','attempt002/UNIT_RESULT.json','attempt002/ENTRY_RESULT.json',
       'attempt002/controller.py','attempt002/run_manual_air_pitch_ref_v1.py','attempt002/ENTRY_AST.json','attempt002/run_unit.py','attempt002/run_entry_admission.py','attempt002/unit_001.log','attempt002/entry_001.log','finalize_prototype.py']
receipt=dict(status=summary['status'],report_lines=len(lines),old_small_sources_unchanged=26,original_failed_attempt_preserved=True,
    parent_explicit_domain_amendment_only=True,original_method_and_budgets_not_rewritten=True,new_fixed_parameters=m2['fixed_parameters'],
    attempt001='NOT_READY_DOMAIN_14_OF_51',attempt002='PURE_SYNTHETIC_AND_NOMINAL_REFERENCE_DOMAIN_PASS',
    actual_controlled_entry_invocations=2,actual_model_forward_integrator_actuator_calls=0,no_additional_queries_tests_or_entry_rerun_by_finalizer=True,
    fullmodel_dynamic_driver_qualification='UNKNOWN',PH7_pending=True,
    files=[dict(path=p,bytes=(T/p).stat().st_size,SHA=sha(T/p))for p in files])
with(T/'RECEIPT.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps(dict(status=receipt['status'],report_lines=len(lines),old_sources_unchanged=26,attempt001_violating_offsets=14,attempt002_violating_offsets=0,
    unit_assertions=u['assertions'],default_ticks=600,enabled_ticks=600,actual_reference_FK_rows=416,controlled_entry_invocations=2,actual_physics_calls=0,
    report_SHA=sha(T/'REPORT.md'),summary_bytes=(T/'SUMMARY.json').stat().st_size,summary_SHA=sha(T/'SUMMARY.json'),receipt_SHA=sha(T/'RECEIPT.json'),
    core_SHA=u['core_SHA'],entry_SHA=en['entry_SHA']),indent=2))
