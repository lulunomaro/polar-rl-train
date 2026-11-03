"""New nominal disabled-actuator settling, not controlled self-righting success.
No pose writes after each case's one initial placement. Normal model gravity,
springs, all geoms and closed chains stay active; actuator ctrl is exactly zero.
"""
from pathlib import Path
import sys,json,hashlib,traceback,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));D=Path(__file__).resolve().parent/'passive_settle001';D.mkdir(exist_ok=False)
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
def rec(p):
    b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
src=[Path(__file__),R/'physics_bridge.py',R/'STARTUP_STAND_V1/geometry002/RESULT.json',R/'streamed_trace_rows_v1.py']
locked=[rec(p)for p in src];poses=json.loads(src[2].read_bytes())['poses']
protocol=dict(kind='NOMINAL_UNPOWERED_INITIAL_STATE_SETTLING_NOT_RECOVERY_SKILL',duration_s_each=2.,physics_dt_s=.0005,
    scheduled_cases=[p['name']for p in poses],max_physics_steps_total=12000,source=locked,
    controller_estimator_and_powered_driver_calls=0,all_actuator_commands_zero=True,
    upright_not_a_health_requirement_for_lying_setup=True,settled_classification_not_standup_pass=True,
    original_geoms_gravity_springs_and_constraints_unchanged=True)
dump(D/'PROTOCOL.json',protocol);outrows=[];total_steps=0
try:
    import numpy as np,mujoco
    from physics_bridge import model_factory,oldcore
    from streamed_trace_rows_v1 import StreamedRows
    from sensor_core_jump_v1 import rotation,rpy
    m=model_factory(False);pairs=[(m.site(a).id,m.site(b).id)for a,b in oldcore.PAIRS]
    names=[str(m.geom(i).name)for i in range(m.ngeom)]
    for p in poses:
        C=D/p['name'];C.mkdir();trace=StreamedRows(C/'physics.jsonl');d=mujoco.MjData(m)
        d.qpos[:]=p['qpos'];d.qvel[:]=p['qvel'];d.ctrl[:]=0.;mujoco.mj_forward(m,d)
        stop='complete';stable_s=0.;peak_closure=0.;peak_mimic=0.
        try:
            for tick in range(4000):
                pre=float(d.time);d.ctrl[:]=0.;mujoco.mj_step(m,d);total_steps+=1
                if total_steps>12000:raise RuntimeError('fixed initialization physics budget exceeded')
                angles=rpy(d.qpos[3:7]);contact=[];main=[0.,0.];guide=hard=0.
                for ci,ct in enumerate(d.contact):
                    a,b=int(ct.geom1),int(ct.geom2);aw=int(m.geom_bodyid[a])==0;bw=int(m.geom_bodyid[b])==0
                    if aw==bw:continue
                    robot=b if aw else a;env=a if aw else b;f=np.zeros(6);mujoco.mj_contactForce(m,d,ci,f)
                    fn=max(0.,float(f[0]));name=names[robot]
                    if name in('left_tire','right_tire'):main[int(name=='right_tire')]+=fn
                    elif name.startswith('guide_wheel_'):guide+=fn
                    else:hard+=fn
                    if fn>1.:contact.append(dict(robot=name,environment=names[env],normal_N=fn))
                closure=max(float(np.linalg.norm(d.site_xpos[a]-d.site_xpos[b]))for a,b in pairs)
                mimic=max(abs(float(d.joint(s+'_drive_'+k+'_spin').qpos[0]-d.joint(s+'_'+other).qpos[0]))for s in('left','right')for k,other in(('hip','hip'),('input','crank')))
                peak_closure=max(peak_closure,closure);peak_mimic=max(peak_mimic,mimic)
                finite=bool(np.isfinite(d.qpos).all()and np.isfinite(d.qvel).all())
                stationary=bool(np.linalg.norm(d.qvel[:3])<.03 and np.linalg.norm(d.qvel[3:6])<.1)
                stable_s=stable_s+.0005 if stationary else 0.
                trace.append(dict(physics_tick=tick,contact_cache_PRE_s=pre,root_POST_s=float(d.time),qpos_POST=d.qpos.tolist(),qvel_POST=d.qvel.tolist(),
                    rpy_POST_rad=angles.tolist(),main_normal_N2_PRE=main,guide_normal_N_PRE=guide,hard_normal_N_PRE=hard,
                    contacts_over1N_PRE=contact,ctrl6=[0.]*6,closure_PRE_m=closure,mimic_POST_rad=mimic,finite=finite,stationary_tail_s=stable_s))
                if not finite or closure>.01 or mimic>.01:stop='physics_health';break
            final=trace[-1];pitch=abs(final['rpy_POST_rad'][1]);roll=abs(final['rpy_POST_rad'][0])
            classification=('NOT_SETTLED_YET'if stable_s<.5 else 'PASSIVELY_NEAR_UPRIGHT_NOT_CONTROLLED_STANDUP'if max(pitch,roll)<.3 else 'LYING_SETTLED_CANDIDATE')
            result=dict(kind=protocol['kind'],case=p['name'],complete=len(trace)==4000 and stop=='complete',stop=stop,physics_steps=len(trace),
                controller_calls=0,final_classification=classification,stationary_tail_s=stable_s,initial_pose=p,
                final_qpos=d.qpos.tolist(),final_qvel=d.qvel.tolist(),final_rpy_rad=final['rpy_POST_rad'],final_root_xyz_m=d.qpos[:3].tolist(),
                final_contact_identities=final['contacts_over1N_PRE'],max_closure_m=peak_closure,max_mimic_rad=peak_mimic,
                trace_artifact=dict(path=str(trace.path),bytes=trace.bytes,SHA=trace.sha.hexdigest(),producer_streamed_once=True),
                root_overwrites_after_initialization=0,assist_forces=0,natural_zero_torque_model_only_not_real_poweroff_electrical_model=True,standup_skill_pass_not_claimed=True)
            dump(C/'result.json',result);outrows.append(result)
        except BaseException:
            dump(C/'ERROR.json',dict(error=traceback.format_exc(),physics_steps=len(trace),total_physics_steps=total_steps,
                trace_prefix=dict(path=str(trace.path),bytes=trace.bytes,SHA=trace.sha.hexdigest())));raise
    assert [rec(p)for p in src]==locked
    batch=dict(status='NOMINAL_UNPOWERED_SETTLING_COMPLETED_NOT_SELF_RIGHTING',rows=outrows,total_physics_steps=total_steps,model_compiles=1,controller_estimator_calls=0)
    dump(D/'BATCH_RESULT.json',batch)
    print(json.dumps(dict(status=batch['status'],total_physics_steps=total_steps,rows=[{k:v for k,v in x.items()if k not in('initial_pose','final_qpos','final_qvel')}for x in outrows]),indent=2))
except BaseException:
    dump(D/'ERROR.json',dict(error=traceback.format_exc(),total_actual_physics_steps=total_steps,completed_cases=len(outrows)));raise
