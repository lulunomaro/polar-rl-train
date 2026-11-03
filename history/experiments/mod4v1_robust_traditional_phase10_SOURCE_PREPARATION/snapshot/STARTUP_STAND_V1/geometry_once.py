"""NEW static low-lying initialization geometry, not startup/physics success."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));D=Path(__file__).resolve().parent/'geometry001'
D.mkdir(exist_ok=False)
def dump(p,x):
    with Path(p).open('x',encoding='utf-8')as f:json.dump(x,f,indent=2,allow_nan=False)
def record(p):
    raw=Path(p).read_bytes();return dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
source=[Path(__file__),R/'physics_bridge.py',R/'PRIVATE_COLLISION_SUPPORT_V1/support.py',R.parent/'traditional_control_20261101/kinematics.py']
locked=[record(p)for p in source]
dump(D/'SOURCE_PREEXEC.json',dict(files=locked,question='Find valid closed-chain low-lying placements; no gravity settling/standup success claim',
    poses=[dict(name='crouch_reference',hip=.45417412979711813,delta=-.4956839978694916),dict(name='fold080',hip=.45,delta=-.8),dict(name='fold100',hip=.45,delta=-1.)],
    model_compiles_max=1,forward_max=6,integrator_max=0,root_placement_clearance_m=.001,old_QA_reexecuted=False))
counts=dict(model_compile=0,forward=0,step=0);rows=[]
try:
    import numpy as np,mujoco
    from physics_bridge import model_factory,oldcore
    from PRIVATE_COLLISION_SUPPORT_V1.support import CompiledCollisionSupport
    import kinematics as kin
    originals={n:getattr(mujoco,n)for n in('mj_step','mj_step1','mj_step2','mj_Euler','mj_RungeKutta','mj_implicit')}
    def forbidden(*a,**k):counts['step']+=1;raise RuntimeError('No integrator in startup geometry preflight')
    for n in originals:setattr(mujoco,n,forbidden)
    forward=mujoco.mj_forward
    def counted(*a,**k):
        counts['forward']+=1
        if counts['forward']>6:raise RuntimeError('predeclared forward budget')
        return forward(*a,**k)
    mujoco.mj_forward=counted
    m=model_factory(False);counts['model_compile']+=1;d=mujoco.MjData(m);support=CompiledCollisionSupport(m)
    pairs=[(m.site(a).id,m.site(b).id)for a,b in oldcore.PAIRS]
    specs=[('crouch_reference',.45417412979711813,-.4956839978694916),('fold080',.45,-.8),('fold100',.45,-1.)]
    for name,hip,delta in specs:
        before=counts['forward']
        try:
            mujoco.mj_resetData(m,d);d.qpos[:3]=[0.,0.,1.];d.qpos[3:7]=[1.,0.,0.,0.]
            kin.set_configuration(m,d,(hip,delta),(hip,delta),True)
            b=support.bounds(d,stage_time_s=0.);dz=.001-b['raw_min_xyz_m'][2]
            d.qpos[2]+=dz;mujoco.mj_forward(m,d)
            b=support.bounds(d,stage_time_s=0.)
            closure=max(float(np.linalg.norm(d.site_xpos[a]-d.site_xpos[c]))for a,c in pairs)
            mimic=max(abs(float(d.joint(s+'_drive_'+kind+'_spin').qpos[0]-d.joint(s+'_'+other).qpos[0]))for s in('left','right')for kind,other in(('hip','hip'),('input','crank')))
            low=b['raw_min_xyz_m'][2]
            close=[g['geom_name']for g in b['per_geom']if g['min_xyz_m'][2]<=low+.002]
            rows.append(dict(name=name,status='VALID_STATIC_CANDIDATE_NOT_SETTLED',hip=hip,delta=delta,root_xyz_m=d.qpos[:3].tolist(),
                qpos=d.qpos.tolist(),qvel=d.qvel.tolist(),closure_m=closure,mimic_rad=mimic,lowest_geoms=close,
                all_robot_min_z_m=low,first_lowest_geom=b['argmin_geoms_xyz'][2],model_nq=int(m.nq),model_nv=int(m.nv),
                support_contacts_not_measured=True,root_placement_initial_only=True,time_s=float(d.time),forward_used=counts['forward']-before))
        except ValueError:
            rows.append(dict(name=name,status='STATIC_POSE_DOMAIN_ERROR_NO_PHYSICS',error=traceback.format_exc(),forward_used=counts['forward']-before))
    for n,v in originals.items():setattr(mujoco,n,v)
    mujoco.mj_forward=forward
    assert counts['step']==0 and counts['forward']<=6 and [record(p)for p in source]==locked
    out=dict(status='STATIC_STARTUP_INITIALIZATION_CANDIDATES_ONLY_NOT_SELF_STANDING',counts=counts,poses=rows,
        model_shapes=dict(nbody=int(m.nbody),ngeom=int(m.ngeom),nmesh=int(m.nmesh)),controller_or_sensor_estimator_calls=0,
        physical_settling_or_standup_trials=0,model_or_gains_modified=False)
    dump(D/'RESULT.json',out);print(json.dumps(out,indent=2))
except BaseException:
    dump(D/'ERROR.json',dict(status='GEOMETRY_PREPARATION_ERROR_NOT_ROBOT_TRIAL',error=traceback.format_exc(),counts=counts,poses=rows));raise
