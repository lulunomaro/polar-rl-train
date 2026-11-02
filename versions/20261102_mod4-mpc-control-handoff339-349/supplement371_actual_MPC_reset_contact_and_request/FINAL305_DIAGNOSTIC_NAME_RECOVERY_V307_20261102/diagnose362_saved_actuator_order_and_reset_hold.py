"""Use existing355/357 captures to separate telemetry ordering and reset holds.

No simulator, checkpoint, network, random sampling or physics is used here.
Historical359/360 are retained, including their unsupported actuator-order label.
"""
from pathlib import Path
import hashlib,json,time
import numpy as np

P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
read=lambda p:json.loads(p.read_bytes())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)

runtime=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4'
sdk=T.parent/'MOD4_3060_DIRECT_FACTOR_20261013/sdk_readonly_source/17_isaaclab_physx__assets__articulation__articulation.py'
text=sdk.read_text('utf8')
assert 'joint_ids, joint_names = self.find_joints(actuator_cfg.joint_names_expr)'in text
assert 'preserve_order: bool = False'in text
source=T/'MPC_TIMED_CONTROL_EXTRACTION_V347_20261102/source/control_core.py'
assert 'self.dr.reset(initial)'in source.read_text('utf8')
cases=[];source_order=['left_hip','left_crank','left_wheel_spin','right_hip','right_crank','right_wheel_spin']
for phase,name in((355,'MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V355_20261102'),(357,'MPC_ACTUAL20MS_PREDICTION_CLOCK_V357_20261102')):
    root=T/name;full=read(root/f'reports/ROOT{phase}_EVALUATION_FULL_RETURNED.json')
    trace=next(json.loads(v['UTF8'])for v in full['full_UTF8']if v['path'].endswith(f'ACTUAL{phase}_CURRENT_STATE_MPC_CONTROL_TRACE.json'))
    initial=next(json.loads(v['UTF8'])for v in full['full_UTF8']if v['path'].endswith(f'ACTUAL{phase}_INITIAL_PHYSX_STATE.json'))
    # Installed SDK resolves an actuator's matching joints in articulation order.
    # This source-based inference is independently checked by named SDK readback363.
    legnames=[n for n in initial['joint_names']if n in('left_crank','left_hip','right_crank','right_hip')]
    actual_order=legnames+['left_wheel_spin','right_wheel_spin']
    assert actual_order==['left_hip','left_crank','right_hip','right_crank','left_wheel_spin','right_wheel_spin']
    perm=[actual_order.index(n)for n in source_order]
    for env in(0,1,40,41):
        rows=[dict(control=r['control'],**v)for r in trace['rows']for v in r['rows']if v['env']==env]
        first=rows[0]if rows else None
        tick0=trace['physics_selected'][0];slot=tick0['selected_envs'].index(env)
        applied=np.array(tick0['actual_applied_torque6'][slot])[perm]
        z=np.load(root/f'replay/REPLAY{phase}_env{env}.npz',allow_pickle=False)
        correct=[];old=[];comparison=[]
        for c in rows[:60]:
            ticks=[v for v in trace['physics_selected']if(c['control']-1)*8<v['tick']<=c['control']*8]
            if not ticks:continue
            a=np.mean([v['actual_applied_torque6'][slot]for v in ticks],axis=0);tau=np.array(c['tau_requested'])
            correct.append(np.square(a[perm]-tau));old.append(np.square(a[[1,0,4,3,2,5]]-tau))
            if c['control']<=3:comparison.append(dict(control=c['control'],requested_source_order=tau.tolist(),actual_mean_source_order=a[perm].tolist()))
        # Independent numerical consistency check: previous endpoint q/dq/target
        # predict the next pre-integration PD effort up to D4 change/D7/gain/clip.
        # It is a diagnostic comparison, not an exact identity claim.
        same=[];swapped=[]
        for k in range(min(len(z['root13'])-1,60)):
            q=z['motor_q'][k,[0,1,3,4]];dq=z['motor_dq'][k,[0,1,3,4]];target=z['motor_pos_target'][k,[0,1,3,4]]
            pd=60*(target-q)-2*dq
            a=np.array(trace['physics_selected'][(k+1)*8]['actual_applied_torque6'][slot])[:4]
            same.append(np.square(pd-a));swapped.append(np.square(pd-a[[1,0,3,2]]))
        q0=np.array(initial['q'][env]);ids=[initial['joint_names'].index(n)for n in legnames]
        initial_leg=q0[ids]
        cases.append(dict(phase=phase,env=env,first_request=None if first is None else first['tau_requested'],first_tick_applied_source_order=applied.tolist(),
            initial_actual_leg_q_actuator_order=initial_leg.tolist(),nominal_zero_hold_PD_before_gain=-60*initial_leg,
            nominal_zero_hold_PD_units='Nm; D7/output gain/actual speed not reconstructed',
            sourcebased_actuator_order=actual_order,permutation_to_source=perm,
            first60_request_vs_interval_mean_RMSE_correct=None if not correct else float(np.sqrt(np.mean(correct))),
            first60_request_vs_interval_mean_RMSE_old360=None if not old else float(np.sqrt(np.mean(old))),
            heldtarget_PD_consistency_RMSE_actuator_model_order=float(np.sqrt(np.mean(same))),
            heldtarget_PD_consistency_RMSE_oldlabel_swapped=float(np.sqrt(np.mean(swapped))),first3=comparison,
            no_exact_requested_applied_identity_expected='D4/D7/gain/DCclip/currentstate and 20ms hold remain',skill_result_unchanged=True))
        cases[-1]['nominal_zero_hold_PD_before_gain']=cases[-1]['nominal_zero_hold_PD_before_gain'].tolist()

put(R/'ACTUAL362_SAVED_ACTUATOR_ORDER_RESET_HOLD_DIAGNOSIS.json',dict(epoch=time.time(),kind='SAVED362_MPC_HANDOFF_DIAGNOSIS',passed=True,
    original359360_preserved=True,telemetry_correction='355/357 concatenated actuator-local effort, incorrectly labeled crankhipcrankhip; SDK source and recorded PD consistency support hipcrankhipcrank. Correct source conversion is [0,1,4,2,3,5]. Fresh363 must record actual joint_indices/names before comparing torque.',
    reset_difference='source347 resets D4 applied target to actual planned q;355/357 original_reset clears queue to default_joint_pos, then planned_initial_reset writes nonzero physical q without rebinding held target. Until queued command is due, PD can pull toward old default pose.',
    observed_scope='Selectedfirst2.5ms hip efforts approximately -26to-30Nm. This is a concrete transfer discrepancy; it is not proven the sole cause of later tipping.',
    exact_source_evidence=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in(source,sdk,runtime/'action_delay_sdk_adapter.py',runtime/'action_delay_physics_queue.py')],
    cases=cases,next='Independent363: same actual20ms MPC50Hz/fullDR/physics/PD/limits;40legacydefaultqueue vs40 actualplannedq heldtarget. Preserve lags/RNG/episodes/ticks/pending semantics; record actual names, parameters, initial queue and pre/post actuator efforts. No learnedtraining345.',
    NN=0,SDK=0,network=0,physics=0,checkpoint_reads=0,optimizer=0,account=0))
print(json.dumps(dict(passed=True,report=str(R/'ACTUAL362_SAVED_ACTUATOR_ORDER_RESET_HOLD_DIAGNOSIS.json'),sourcebased_permutation=[0,1,4,2,3,5],cases=len(cases),no_new_physics=True)))
