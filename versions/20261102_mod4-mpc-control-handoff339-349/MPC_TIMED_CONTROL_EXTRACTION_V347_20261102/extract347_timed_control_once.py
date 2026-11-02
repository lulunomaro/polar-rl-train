"""Bounded local MuJoCo control trace extraction; no NN, Isaac, GPU, SSH or budget."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
from pathlib import Path
import hashlib,json,sys,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports';S=Path('F:/RMPOLAR-RL/traditional_control_20261101')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
    with(R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)
try:
    assert not (R/'EXTRACTION347_ONCE_CONSUMED.json').exists()
    for row in json.loads((N/'INDEX347_SOURCE_FROZEN.json').read_bytes())['files']:
        p=Path(row['path']);assert p.stat().st_size==row['bytes']and H(p)==row['SHA']
    put('EXTRACTION347_ONCE_CONSUMED.json',dict(epoch=time.time(),pid=os.getpid(),purpose='new missing target/control timestamp extraction, not reclassification or repeat evaluation of existing source success',NN=0,SDK=0,SSH=0,GPU=0,account=0))
    sys.path.insert(0,str(N/'source'))
    import numpy as np,mujoco,scipy
    import control_core as core,full_lqr,hybrid_trial
    core.ROOT=S # Frozen controller source, original model/assets; no source or asset mutation.
    versions=dict(mujoco=mujoco.__version__,numpy=np.__version__,scipy=scipy.__version__)
    original_versions=json.loads((S/'results/FINAL_EVIDENCE_V2/manifest.json').read_bytes())
    cfg=json.loads((N/'source/config347.json').read_bytes())
    commands=[];physics=[];holder={};original_control=core.Plant.torque_control;original_step=mujoco.mj_step
    deadline=time.monotonic()+180.
    def control(plant,symmetric_tau,dt=.01):
        assert time.monotonic()<deadline
        holder['plant']=plant
        q=plant.d.qpos[plant.qids].copy();dq=plant.d.qvel[plant.vids].copy()
        actualq=q.copy();actualdq=dq.copy()
        if plant.observed is not None:
            q[[1,0,4,3]]=plant.observed['legq4'];dq[[1,0,4,3]]=plant.observed['legqd4'];dq[[2,5]]=plant.observed['wheelqd2']
        tau=np.array(symmetric_tau,float).copy();assert tau.shape==(6,)and plant.use_full_lqr
        target=q+(tau+plant.KD*dq)/plant.KP
        for i in(2,5):target[i]=dq[i]+tau[i]/plant.wKD
        before_projection=target.copy()
        target[[0,1,3,4]]=np.clip(target[[0,1,3,4]],-3,3)
        for i in(0,3):target[i+1]=np.clip(target[i+1],target[i]-1.0843,target[i]+.85)
        target[[2,5]]=np.clip(target[[2,5]],-60,60)
        command_index=len(commands);at=float(plant.d.time)
        commands.append(dict(control=command_index,issued_time=at,hold_seconds=dt,physics_tick=int(plant.tick_phys),tau_requested=tau.tolist(),observed_motor_q=q.tolist(),observed_motor_dq=dq.tolist(),actual_motor_q=actualq.tolist(),actual_motor_dq=actualdq.tolist(),raw_inversePD_target=before_projection.tolist(),processed_target=target.tolist(),qpos_initial=plant.d.qpos.copy().tolist(),qvel_initial=plant.d.qvel.copy().tolist()))
        holder['command']=command_index;holder['requested']=target.copy()
        if plant.dr and not getattr(plant.dr,'_trace347_installed',False):
            dr=plant.dr;original_targets=dr.process_targets
            def targets(value,tick_phys):
                assert np.max(np.abs(value-holder['requested']))<1e-12
                out=original_targets(value,tick_phys);holder['applied_target']=out.copy();return out
            dr.process_targets=targets;dr._trace347_installed=True
        return original_control(plant,symmetric_tau,dt)
    def step(model,data,*args,**kwargs):
        plant=holder.get('plant')
        if plant is not None and model is plant.m and data is plant.d:
            assert time.monotonic()<deadline
            physics.append(dict(command=holder['command'],tick=int(plant.tick_phys),time=float(data.time),requested_target=holder['requested'].copy(),applied_target=holder.get('applied_target',holder['requested']).copy(),applied_torque=data.ctrl.copy(),motor_q=data.qpos[plant.qids].copy(),motor_dq=data.qvel[plant.vids].copy()))
        return original_step(model,data,*args,**kwargs)
    core.Plant.torque_control=control;mujoco.mj_step=step
    try:result,rows=hybrid_trial.run(cfg,True)
    finally:core.Plant.torque_control=original_control;mujoco.mj_step=original_step
    assert len(commands)==len(rows)>0 and len(physics)==len(commands)*20
    put('SOURCE347_RESULT_WITH_TIMED_COMMANDS.json',dict(result=result,versions=versions,original_versions={k:original_versions[k]for k in('mujoco','numpy','scipy')},same_engine_version=versions['mujoco']==original_versions['mujoco'],source_model_changed=False,not_a_PhysX_reproduction=True,not_training=True))
    put('SOURCE347_100HZ_PROCESSED_MOTOR_COMMANDS.json',dict(order=list(core.ORDER),target_units=['rad','rad','rad/s','rad','rad','rad/s'],source_engine='MuJoCo',source_physics_dt=.0005,control_dt=.01,commands=commands))
    path=N/'SOURCE347_PHYSICS_MOTOR_APPLICATIONS.npz'
    np.savez_compressed(path,**{k:np.stack([r[k]for r in physics])for k in physics[0]})
    recorded=json.loads((S/'results/FINAL_EVIDENCE_V2/fullDR_mpc/trajectory.json').read_bytes())
    count=min(len(rows),len(recorded));maxpos=max(float(np.linalg.norm(np.array(a['xyz'])-b['xyz']))for a,b in zip(rows[:count],recorded[:count]))
    legids=[0,1,3,4];wheelids=[2,5]
    gap=np.array([np.array(c['processed_target'])-np.array(c['actual_motor_q'])for c in commands])
    wheelgap=np.array([[c['processed_target'][i]-c['actual_motor_dq'][i]for i in wheelids]for c in commands])
    put('ACTUAL347_TIMED_MPC_CONTROL_EXTRACTION_SUMMARY.json',dict(epoch=time.time(),passed=True,purpose_completed=True,source_controller_success=result['success'],stable_at_end=result['stable_at_end'],source_controls=len(commands),physics_steps=len(physics),motor_application_npz=dict(path=str(path),bytes=path.stat().st_size,SHA=H(path)),versions=versions,same_engine_version=versions['mujoco']==original_versions['mujoco'],saved_source_endpoint_max_position_difference_m=maxpos,compared_endpoints=count,
        source_original_success_preserved=True,not_identical_old_trial_claim=True,processed_target_minus_state_leg_RMSE_rad=np.sqrt((gap[:,legids]**2).mean(0)).tolist(),processed_wheel_target_minus_actual_velocity_RMSE_rad_s=np.sqrt((wheelgap**2).mean(0)).tolist(),
        controller_output_not_equal_joint_state=True,NN=0,IsaacSDK=0,GPU=0,SSH=0,optimizer_steps=0,account=0,new_training_GO=0,PhysX_reproduction=False,next='Use exact timed source target as planned feedforward in a separate finite original-actuator-path comparison before training; respect policy50/feedback100/physics400 and original queue/limits.'))
    print(json.dumps(dict(passed=True,source_controller_success=result['success'],stable_at_end=result['stable_at_end'],controls=len(commands),physics_steps=len(physics),same_engine_version=versions['mujoco']==original_versions['mujoco'],compared_source_position_max_m=maxpos,report=str(R/'ACTUAL347_TIMED_MPC_CONTROL_EXTRACTION_SUMMARY.json'))),flush=True)
except BaseException:
    put('EXTRACTION347_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_once=True));raise
