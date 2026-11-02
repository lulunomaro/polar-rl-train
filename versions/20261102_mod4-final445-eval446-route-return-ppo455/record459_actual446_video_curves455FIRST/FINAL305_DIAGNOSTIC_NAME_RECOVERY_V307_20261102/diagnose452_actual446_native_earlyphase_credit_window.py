"""Saved actual446/native review and explicit GAE timing audit; no NN, SDK or newphysics."""
from pathlib import Path
import hashlib
import io
import json
import time
import numpy as np

P=Path(__file__).resolve().parent;T=P.parent
C=T/'RL445_ACTUAL446_REPLAY_RECOVERY_V451_20261102'
N=T/'RL_SATURATION_ACTUAL_PPO_PRODUCTION_V445_20261102'
read=lambda path:json.loads(path.read_bytes())
receipt=read(C/'reports/ROOT451_ACTUAL446_SELECTED_REPLAY_TRANSFERS.json')
assert receipt['passed']and receipt['model_SHA']=='056410f592d07ff63c3acc6adac4d1ebb0357bc154e817568bec56ba155f18ed'
table=np.asarray(read(N/'feedforward389.json')['commands'])[:,[1,0,4,3,2,5]]/np.asarray([.5,.5,.5,.5,10.,10.])
with np.load(N/'reference389.npz',allow_pickle=False)as packet:reference=packet['state78'].copy()
cases=[]
for row in receipt['cases']:
    raw=Path(row['local_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['SHA']
    with np.load(io.BytesIO(raw),allow_pickle=False)as packet:values={key:packet[key].copy()for key in packet.files}
    count=row['controls'];phase=np.arange(count);base=table[np.minimum(phase,249)].copy();base[phase>249,4:]=0
    delta=values['action6']-np.clip(base,-6,6);root=values['root13'];position=root[:,:3]-np.asarray(row['origin'])
    x,y,z,w=root[:,3:7].T;pitch=np.arcsin(np.clip(2*(w*y-z*x),-1,1));yaw=np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z))
    samples=[]
    for step in(0,9,19,29,31,39,49,59,74,99,127,149,249,399):
        if step>=count:continue
        samples.append(dict(control=step+1,seconds=(step+1)*.02,root_position=position[step].tolist(),
            reference_position=(reference[min(step,249),:3]+[.8,0,0]).tolist(),pitch=float(pitch[step]),yaw=float(yaw[step]),
            residual=delta[step].tolist(),motor_q=values['motor_q'][step].tolist(),motor_dq=values['motor_dq'][step].tolist(),
            motor_position_target=values['motor_pos_target'][step].tolist(),motor_velocity_target=values['motor_vel_target'][step].tolist()))
    first=lambda mask:float((np.flatnonzero(mask)[0]+1)*.02)if np.any(mask)else None
    cases.append(dict(env=row['env'],seconds=row['seconds'],first_pitch_abs_over02_s=first(np.abs(pitch)>.2),
        first_yaw_abs_over02_s=first(np.abs(yaw)>.2),first_rootz_over035_s=first(position[:,2]>.35),
        max_root_height=float(position[:,2].max()),max_rootx=float(position[:,0].max()),
        last_root_position=position[-1].tolist(),first20_signed_residual_mean6=delta[:20].mean(0).tolist(),
        nearbound_residual095_counts6=(np.abs(delta)>.95).sum(0).tolist(),samples=samples))
gamma=.99;lam=.95
timing=[dict(control_delay=delay,seconds=delay*.02,old_GAE_trace_weight=(gamma*lam)**delay,
             gamma_only_fullwindow_weight=gamma**delay,within_old32sample=delay<32)for delay in(16,31,35,40,49,56,63,99,127)]
report=dict(epoch=time.time(),passed=True,modelSHA=receipt['model_SHA'],actual446cases=cases,
    native_review=dict(current_model_native_viewed=True,
        image=str(C/'RECORDED451_ACTUAL446_NATIVE_FRAMES/ACTUAL451_FINAL445_EVAL446_BODY_POSE_SEQUENCE.png'),
        actual_saved446_twohost_SHA_verified=True,oldcopied437_not_used=True,
        selected_envs=[row['env']for row in receipt['cases']],
        observation='env0/1/41 all8s end tilted bracing below frontedge; env40 remains on ground and turnsaway. None selected lands on top; all80 actualmanifold separately0',
        all80_visual_claim=False),
    original_actor_learning=dict(rollout_controls=32,seconds=.64,gamma=.99,GAElambda=.95,
        oneepoch=True,actualrewarddone=True,bootstrap_at_batch_boundary=True,
        no_direct_actor_gradient_through_future_physics_or_WM=True),
    timing_math=timing,source_code=str(N/'source/actual_transition_learner442.py'),
    conclusion='Actualselected takeoff/edgeevent follows32control boundary; no full launch-to-landing actor return in one32batch. This identifies temporalcredit risk, not proof it is solefailurecause or a measuredcriticerror.',
    next_candidate=dict(rollout_controls=128,seconds=2.56,GAElambda=1.,gamma=.99,
        same_actualrewarddone=True,no_rewardchange=True,no_PD_solver_DR_asset_change=True,
        saturationaware_exploration_kept=True,postAdam_fullGaussianKL_bound_kept=True,
        full445network_Adam_EMA_origin_RNG_restore_required=True,
        CPU_delayed_event_and_done_mask_fixture_required=True,physicalskill_unproven=True),
    decision='No unchanged445hour; test full launch/landing actual-return algorithm first, then independentproductionversion onlyafterCPUadmission',
    modelreads=0,network=0,SDK=0,physics=0)
path=P/'reports/DIAG452_ACTUAL446_NATIVE_EARLY_YAW_PITCH_AND_GAE_TIMING.json'
with path.open('x',encoding='utf8')as stream:json.dump(report,stream,indent=2,ensure_ascii=False,allow_nan=False)
print(json.dumps(dict(passed=True,nativeviewed=True,cases=[{key:row[key]for key in('env','first_pitch_abs_over02_s','first_yaw_abs_over02_s','first_rootz_over035_s','last_root_position')}for row in cases],timing=timing,modelreads=0)),flush=True)
