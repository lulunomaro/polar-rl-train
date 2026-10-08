"""Offline nominal force-law audit. This is neither hardware measurement nor SDK force proof."""
from pathlib import Path
import json,hashlib,time,ast,math
D=Path(__file__).resolve().parent;R=D/'reports'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
v=read(R/'ACTUAL_FROZEN_SPRING_SOURCE.json');contract=v['contract']
task=(D/'reviewed_sources/mod4_task.py').read_text(encoding='utf8')
skills=(D/'reviewed_sources/skills_isaac.py').read_text(encoding='utf8')
tree=ast.parse(skills);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='gas_spring_preload')
assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='set_joint_position_target' for n in ast.walk(fn))
assert 'effort_limit_sim=2000.0' in task and 'stiffness={n: gas[n]["stiffness_n_m"]' in task
rows=[]
for name,params in contract['gas_springs'].items():
    joint=contract['joints'][name];assert joint['type']=='slide'
    lo,hi=joint['limits_si'];k=params['stiffness_n_m'];d=params['damping_n_s_m'];target=params['target_position_m']
    assert 0<k and 0<=d and lo<0<hi and all(math.isfinite(x) for x in (lo,hi,k,d,target))
    qs=[lo+(hi-lo)*i/400 for i in range(401)]
    curve=[dict(q_m=q,elastic_model_force_N=k*(target-q),damping_model_force_N_at_positive_point2ms=-d*.2,total_model_force_N_at_positive_point2ms=k*(target-q)-d*.2) for q in qs]
    assert all(a['elastic_model_force_N']>b['elastic_model_force_N'] for a,b in zip(curve,curve[1:]))
    slope=(curve[-1]['elastic_model_force_N']-curve[0]['elastic_model_force_N'])/(hi-lo)
    assert abs(slope+k)<1e-8
    # Independent SI identity: one millimetre changes the elastic model by3.5N.
    assert abs((k*(target-.001)-k*target)+3.5)<1e-10
    rows.append(dict(joint=name,q_limit_m=[lo,hi],relative_slide_stroke_m=hi-lo,k_N_per_m=k,d_N_s_per_m=d,position_target_m=target,target_outside_joint_limits_is_existing_preload=True,elastic_model_force_N_at_q0=k*target,elastic_model_force_N_range=[curve[-1]['elastic_model_force_N'],curve[0]['elastic_model_force_N']],proposed_k_factor_range=[.9,1.1],proposed_uncalibrated_elastic_model_force_N_range=[.9*curve[-1]['elastic_model_force_N'],1.1*curve[0]['elastic_model_force_N']],original_config_drive_effort_limit_N=2000.0,drive_effort_vs_closed_chain_constraint_force_not_equated=True,curve=curve))
report=dict(epoch=time.time(),id='MOD4-D5-NOMINAL-MODEL-LAW-AUDIT-001',plan_sha256='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b',package=v['package'],actual_USD_sha256=v['actual_USD_sha256'],import_contract_sha256=v['contract_sha256'],scope='Exact frozen MOD4 software nominal force-law and SI-coordinate audit only',source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (D/'reviewed_sources').glob('*.py')},formula=dict(elastic_N='k_N_m*(position_target_m-q_m)',viscous_N='-d_N_s_m*qd_m_s',total_model_N='elastic+viscous before implicit integration/force saturation',not_measured_real_force=True,not_solver_constraint_force=True),joints=rows,hardware_force_stroke_measurement_available=False,actual_SDK_force_stroke_readback_completed=False,nominal_model_changed=False,D5_CPU_DR_component_or_learning_executor_deployed=False,new_GPU_PPO_or_budget_operation=0,decision=dict(no_300_700N_full_stroke_hardware_claim=True,actual_existing_model_differs_from_requested_hardware_range=True,do_not_modify_nominal_spring_to_force_requested_range=True,nominal_SDK_drive_q_qd_k_d_target_effort_readback_required=True,proposed_point9_1point1_is_engineering_candidate_only=True,hardware_calibration_or_explicit_uncalibrated_label_required=True,missing_calibration_does_not_hold_current_D4_training=True,may_progress_other_approved_verifiable_groups_without_claiming_full_real_DR_graduation=True))
(R/'D5_NOMINAL_MODEL_CURVE_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
small=[{k:value for k,value in row.items() if k!='curve'} for row in rows]
note='''从当前2.5ms D4 immutable包逐字读回真实MOD4 USD与import_contract，并核对gas_spring_preload/ImplicitActuator路径。两gas slide原软件名义k3500N/m、d3Ns/m、target约0.220639441m，q范围[-0.0267046843609,0.0352033350025]m，原drive effort_limit_sim2000N。target在joint范围外是已有预紧目标，不把它当实物气弹簧行程。静态软件F=k(target-q)在q0约772.238N，全关节范围约649.026–865.704N，1mm相对q变化对应3.5N；阻尼项-d*qd与弹性项分列，不将隐式驱动估计或闭链约束力称实测气弹簧力。401点离线数学曲线及单位/符号检查通过，不是实际SDK force-stroke测试。

计划首±10%若以后实施，只是未标定工程压力；按原软件模型全q范围弹性估计约584.124–952.275N，不据此宣称实物300–700N全行程一致，不为迎合范围改名义k/预紧/模型。实际SDK k/d/target/q/qd/drive力的readback与硬件force-stroke测量仍缺，D5组件与学习入口未部署，本次GPU/PPO/预算操作0。当前4090 D4不受本离线审查阻塞。下一独立接口需完整参数/units/episodeRNG与保存、新episode清状态、闭链与硬件合同；缺标定必须标明未标定，或先推进其它已批准可验证组，不能把旧3500N/m和更多训练变成实物认证。全部原源和raw保留。首次跨平台文本拷贝newline SHA reader错误已用base64字节传输修正，原错误保留，不是物理或训练故障。'''
(R/'D5_NOMINAL_MODEL_CURVE_REPORT.md').write_text(note+'\n',encoding='utf8')
print(json.dumps(dict(joints=small,decision=report['decision'],no_GPU_PPO_or_budget_operation=True)))
