"""Audit saved MPC controls against the existing state-reference handoff; no simulation."""
from pathlib import Path
import ast, hashlib, json, math, statistics, time, xml.etree.ElementTree as ET

P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
S=Path('F:/RMPOLAR-RL/traditional_control_20261101')
E=S/'results/FINAL_EVIDENCE_V2'
N=T/'REFERENCE_H8_DIRECT_TRACKING_PRODUCTION_V345_20261102'
Q=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def meta(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))
def put(name,value):
    with(R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)

trajectory=E/'fullDR_mpc/trajectory.json';rows=read(trajectory)
config=read(E/'fullDR_mpc/config.json');result=read(E/'fullDR_mpc/result.json')
assert result['success'] and result['stable_at_end']>=.5 and len(rows)==500
assert all(len(r['tau'])==len(r['applied_torque'])==6 for r in rows)
assert all(abs((r['time']-(rows[i-1]['time']if i else 0.))-.01)<1e-10 for i,r in enumerate(rows))
reference=N/'source/tracking_reference345.py';reftext=reference.read_text('utf8');tree=ast.parse(reftext)
prepare=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='prepare')
readkeys=sorted({n.slice.value for n in ast.walk(prepare)if isinstance(n,ast.Subscript)and isinstance(n.slice,ast.Constant)and isinstance(n.slice.value,str)})
assert 'tau'not in readkeys and 'applied_torque'not in readkeys and 'qpos'in readkeys and 'qvel'in readkeys
assert 'selected=rows[1::2]'in reftext
probe=T/'REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V311_20261102/source/evaluate311.py'
probetext=probe.read_text('utf8');assert 'label_action[:,18:48][:,legmotor]'in probetext
assert '/sdk.task.LEG_ACTION_SCALE' in probetext and "controller='plannedjointq/dqtargets; not LQR/MPCtorquecloning'"in probetext
core=E/'control_core.py';coretext=core.read_text('utf8')
for fragment in ('target=q+(tau+self.KD*qd)/self.KP','target[i]=qd[i]+tau[i]/self.wKD','def torque_control(self,symmetric_tau,dt=.01)','make_model(step=True,dt=.0005)'):
    assert fragment in coretext,fragment
hybrid=E/'hybrid_trial.py';hybridtext=hybrid.read_text('utf8')
assert 'p.torque_control(tau)'in hybridtext and 't=k*.01'in hybridtext
assert "x[0]>=launch_x and x[7]>=cfg.get('launch_min_speed',.7)"in hybridtext
task=read(N/'TASK345_FROZEN.json')
assert not (N/'reports/ROOT345_START_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
assert not (N/'reports/ROOT345_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').exists()

xml=ET.parse(S/'model/mod4_400N.xml').getroot()
jointnames=[j.get('name')for j in xml.find('worldbody').iter('joint')if j.get('name')]
order=['left_hip','left_crank','left_wheel_spin','right_hip','right_crank','right_wheel_spin']
last=rows[-1];motorq=[last['qpos'][7+jointnames.index(n)]for n in order];motordq=[last['qvel'][6+jointnames.index(n)]for n in order]
# This is an algebraic clean-state illustration, NOT the original noisy/delayed inverse-PD target.
offset=[(last['tau'][i]+2.*motordq[i])/60. if i not in (2,5)else last['tau'][i]/.6 for i in range(6)]
illustration=dict(source_time=last['time'],torque_order=order,desired_tau_Nm=last['tau'],actual_last_physics_tau_Nm=last['applied_torque'],q=motorq,dq=motordq,
    nominal_inverse_PD_target_minus_state=offset,units=['rad','rad','rad/s','rad','rad','rad/s'],
    exact_original_target=False,scope='clean endpoint algebraic illustration; original command used pre-step noisy/delayed/predicted feedback and subsequent target queue; no exact replay claim')
phases={name:dict(controls=sum(r['phase']==name for r in rows),seconds=.01*sum(r['phase']==name for r in rows),
    state_reference50_samples=sum(r['phase']==name for r in rows[1::2]))for name in dict.fromkeys(r['phase']for r in rows)}
bodymass={b.get('name'):float(b.find('inertial').get('mass'))for b in xml.find('worldbody').iter('body')if b.find('inertial')is not None}
contract=read(Q/'payload/job0/runtime/isaac/mod4/import_contract.json')
contractmass={name:row['mass_kg']for name,row in contract['bodies'].items()}
massdiff={name:dict(mpc=mass,training_contract=contractmass.get(name),delta=None if name not in contractmass else contractmass[name]-mass)for name,mass in bodymass.items()if name not in contractmass or abs(contractmass[name]-mass)>1e-5}
audit=dict(epoch=time.time(),kind='MPC_CONTROL_TO_STATE_REFERENCE_HANDOFF_AUDIT346',passed=True,
    user_steering='2026-11-02 human asks why fully tuned MPC and full timed motor trajectory do not transfer; establish control reproduction before more objective/horizon training',
    source_success=dict(trajectory=meta(trajectory),result=meta(E/'fullDR_mpc/result.json'),config=meta(E/'fullDR_mpc/config.json'),success=result['success'],stable_at_end=result['stable_at_end'],cross=result['cross']),
    actual_reference_pipeline=dict(source=meta(reference),prepare_read_keys=readkeys,state_samples=250,source_controls=500,source_control_dt=.01,reference_dt=.02,source_initial_t0_not_saved=True,first_saved_endpoint=rows[0]['time'],first_reference_endpoint=rows[1]['time'],torque_fields_discarded=True,actual_processed_motor_target_not_saved_in_source_trace=True,per_physics_applied_torque_history_not_saved=True),
    control_semantics=dict(source=meta(core),controller=meta(hybrid),source_physics_dt=.0005,current_training_physics_dt=.0025,source_controller_hz=100,current_actor_hz=50,current_feedback_hz=100,
        source_output='closed-loop desired torque in actuator order -> nominal inversePD -> target projection -> D4 target queue -> explicitPD -> signedDCclip -> motor gain -> signedDCclip',
        current_actor_output='four normalized leg position targets, then two normalized wheel velocity targets; .5rad and10rad/s scales; original D4 and explicitPD retained',
        source_actuator_order=order,policy_order=['left_crank','left_hip','right_crank','right_hip','left_wheel_spin','right_wheel_spin'],
        source_phase_switch='launch_x AND minimum measured speed, then measured launch pose; landing switches from measured contact',current_reference_phase='fixed elapsed episode steps, lookahead0/10; no source closed-loop event controller invoked',
        faithful_source_controller_reproduction_in_PhysX=False,do_not_change_original_physics_or_PD_from_this_audit=True),
    previous311_scope=dict(source=meta(probe),models=0,controller='joint state q position + wheel dq velocity copied as PD targets, not original inversePD motor commands',referencefullinit_did_not_make_it_stable=True,not_a_faithful_MPC_command_replay=True),
    phase_sample_counts=phases,stationary_endpoint_inversePD_illustration=illustration,
    static_asset_mass_comparison=dict(source_model=meta(S/'model/mod4_400N.xml'),training_contract=meta(Q/'payload/job0/runtime/isaac/mod4/import_contract.json'),mpc_total=sum(bodymass.values()),training_contract_total=sum(contractmass.values()),differences_over_1e5kg=massdiff,actualSDK_current_nominal_readback=False,no_mass_cause_inferred=True),
    conclusions=['The saved MPC is a real successful closed-loop controller in its source plant.','The learning path consumed state references; it did not execute or learn from saved MPC motor commands.','Copying joint state into PD targets is not equivalent to the MPC inversePD control path.','State-reference BPTT can in principle discover suitable commands, but success in the source controller is not evidence that this policy has learned them.','Clock, event feedback, initial-state and plant equivalence still need a bounded actual reproduction comparison; none alone is proven causal.'],
    decision=dict(launch345=False,GO=False,existing345frozen_package_preserved=True,reason='Establish faithful motor control handoff and actual same-task reproduction before more H8direct training.',next='Extract or regenerate source processed target and pre-control feedback traces with explicit timing/order; compare source vs current plant from matching planned state through original actuator limits/queues; no direct unbounded torque bypass or torque cloning.'),
    model_reads=0,optimizer_steps=0,network=0,SDK=0,physics_steps=0,account_access=0)
put('ACTUAL346_MPC_CONTROL_HANDOFF_AUDIT_NO_MODEL.json',audit)
put('ACTUAL346_NATIVE339_REVIEW_AND_CONTINUATION_DECISION.json',dict(epoch=time.time(),model_SHA=task['model_SHA'],source_eval=str(T/'FINAL324_IMPORT_CIM_REPAIR_EVAL_V339_20261102/reports/ROOT339_EVALUATION_FULL_RETURNED.json'),native_image=str(T/'FINAL324_IMPORT_CIM_REPAIR_EVAL_V339_20261102/RECORDED339_NATIVE_FRAMES/ACTUAL339_FINAL324_BODY_POSE_SEQUENCE.png'),native_review_completed=True,observations='4casesx3 recorded PhysX poses with platform visible: env1/env0 rotate and leave approach direction; env10/.32s and20/.46s tilt/fall before platform; no visual crossing.',eval339=dict(cases=80,cross=0,strict=0,orientation=56,full8s=24,mean_seconds=3.35625),comparison305=dict(orientation=70,full8s=10,mean_seconds=1.45675),decision='Do not repeat324 unchanged or launch345 before MPC control-handoff audit; survival improved but skill unachieved.',hypothesis344_cpu_only=True,not_a_skill_pass=True))
print(json.dumps(dict(passed=True,report=str(R/'ACTUAL346_MPC_CONTROL_HANDOFF_AUDIT_NO_MODEL.json'),source_success=True,source_control_hz=100,reference_hz=50,controls_discarded=True,launch345=False,model_reads=0,physics_steps=0,phases=phases,mass_difference_bodies=len(massdiff),last_inversePD_illustration=illustration),ensure_ascii=False))
