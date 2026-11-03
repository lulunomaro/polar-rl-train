"""New laid-body initialization candidates, retaining the known-valid leg chart.
geometry001 did NOT produce a lying pose: deeper folds were outside its admitted
joint-chart domain. Preserve those errors; do not loosen any old model limits.
"""
from pathlib import Path
import sys,json,hashlib,traceback,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));D=Path(__file__).resolve().parent/'geometry002';D.mkdir(exist_ok=False)
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
locked=[]
for p in(Path(__file__),R/'physics_bridge.py',R/'PRIVATE_COLLISION_SUPPORT_V1/support.py',R.parent/'traditional_control_20261101/kinematics.py'):
    b=p.read_bytes();locked.append(dict(path=str(p),SHA=hashlib.sha256(b).hexdigest()))
specs=[('front_rest_065',.65),('back_rest_065',-.65),('front_rest_125',1.25)]
dump(D/'SOURCE_PREEXEC.json',dict(files=locked,poses=specs,hip=.45417412979711813,delta=-.4956839978694916,
    model_compiles_max=1,forward_max=6,integrator_max=0,old_limits_not_changed=True,root_placement_initial_only=True,settling_and_standup_not_tested=True))
counts=dict(model_compile=0,forward=0,integrator=0);rows=[]
try:
    import numpy as np,mujoco
    from physics_bridge import model_factory,oldcore
    from PRIVATE_COLLISION_SUPPORT_V1.support import CompiledCollisionSupport
    import kinematics as kin
    saved={n:getattr(mujoco,n)for n in('mj_step','mj_step1','mj_step2','mj_Euler','mj_RungeKutta','mj_implicit')}
    def forbidden(*a,**kw):counts['integrator']+=1;raise RuntimeError('No startup physics in static geometry study')
    for n in saved:setattr(mujoco,n,forbidden)
    oldforward=mujoco.mj_forward
    def forward(*a,**kw):
        counts['forward']+=1
        if counts['forward']>6:raise RuntimeError('fixed6 forward budget exceeded')
        return oldforward(*a,**kw)
    mujoco.mj_forward=forward
    m=model_factory(False);counts['model_compile']+=1;d=mujoco.MjData(m);support=CompiledCollisionSupport(m)
    pairs=[(m.site(a).id,m.site(b).id)for a,b in oldcore.PAIRS]
    for name,pitch in specs:
        mujoco.mj_resetData(m,d);d.qpos[:3]=[0,0,1];d.qpos[3:7]=[math.cos(pitch/2),0,math.sin(pitch/2),0]
        kin.set_configuration(m,d,(.45417412979711813,-.4956839978694916),(.45417412979711813,-.4956839978694916),True)
        before=support.bounds(d,stage_time_s=0.);d.qpos[2]+=.001-before['raw_min_xyz_m'][2];mujoco.mj_forward(m,d)
        b=support.bounds(d,stage_time_s=0.);low=b['raw_min_xyz_m'][2]
        rows.append(dict(name=name,initial_pitch_rad=pitch,root_xyz_m=d.qpos[:3].tolist(),qpos=d.qpos.tolist(),qvel=d.qvel.tolist(),
            lowest_geoms=[g['geom_name']for g in b['per_geom']if g['min_xyz_m'][2]<=low+.002],all_robot_min_z_m=low,
            closure_m=max(float(np.linalg.norm(d.site_xpos[a]-d.site_xpos[c]))for a,c in pairs),
            initial_only_not_a_fall_or_recovery=True,natural_unpowered_settling_not_yet_tested=True,time_s=float(d.time)))
    for n,v in saved.items():setattr(mujoco,n,v)
    mujoco.mj_forward=oldforward
    assert counts['integrator']==0
    for z in locked:assert hashlib.sha256(Path(z['path']).read_bytes()).hexdigest()==z['SHA']
    result=dict(status='VALID_STATIC_LAID_BODY_CANDIDATES_NOT_DYNAMIC_STANDUP',counts=counts,poses=rows,
        model_shapes=dict(nbody=int(m.nbody),ngeom=int(m.ngeom),nmesh=int(m.nmesh)),old_physics_or_QA_replayed=False,
        model_limits_removed_or_contacts_deleted=False,controller_estimator_calls=0)
    dump(D/'RESULT.json',result);print(json.dumps(result,indent=2))
except BaseException:
    dump(D/'ERROR.json',dict(status='STATIC_INITIALIZATION_PREPARATION_ERROR_NOT_ROBOT_TRIAL',error=traceback.format_exc(),counts=counts,poses=rows));raise
