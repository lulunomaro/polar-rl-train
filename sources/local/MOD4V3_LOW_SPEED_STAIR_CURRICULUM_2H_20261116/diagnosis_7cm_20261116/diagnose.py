"""Frozen nominal diagnostic only; never imports or updates the running trainer."""
from pathlib import Path
import sys,json,hashlib,time,math,importlib.util,types,gc
import numpy as np
import torch,mujoco,trimesh
T=Path(__file__).resolve().parent.parent
R=T.parents[2]
OUT=Path(__file__).resolve().parent/'results_r2_contactfix'
OUT.mkdir(exist_ok=False)
torch.set_num_threads(1)
spec=importlib.util.spec_from_file_location('diagnostic_showcase',R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/viewer/showcase.py')
show=importlib.util.module_from_spec(spec);spec.loader.exec_module(show)
show.Simulation.step.__globals__['CMD_SLEW']=.02
sys.path.insert(0,str(T/'manual_replay'))
from replay_guards import policy_step_without_flat_reset
advance=policy_step_without_flat_reset(show.Simulation)
cases=[('parent_7cm_low',T/'weights/parent_comprehensive.pt',.07,.4,None),
       ('45m_7cm_low',T/'weights/model_045m.pt',.07,.4,None),
       ('45m_5cm_low',T/'weights/model_045m.pt',.05,.4,None),
       ('45m_7cm_high_stance',T/'weights/model_045m.pt',.07,.4,.40),
       ('45m_7cm_faster',T/'weights/model_045m.pt',.07,1.2,None),
       ('45m_2cm_low',T/'weights/model_045m.pt',.02,.4,None)]
rows=[];arrays={};started=time.time()
for name,model,h,command,height_override in cases:
    show.CKPT=model;show.EXPECTED=hashlib.sha256(model.read_bytes()).hexdigest()
    B=OUT/name;(B/'tiles').mkdir(parents=True)
    base=trimesh.creation.box((9.,9.,.1));base.apply_translation((0,0,-.05))
    top=trimesh.creation.box((3.,3.,h));top.apply_translation((0,0,h/2))
    mesh=trimesh.util.concatenate([base,top])
    np.savez_compressed(B/'tiles/r00_c00.npz',vertices=mesh.vertices,faces=mesh.faces)
    show.B=B
    s=show.Replay();e=s.env;m=e.m;d=e.d
    s.args.vx=command;s.cmd_vx=s.cmd_wz=s.cmd_vy=0.
    d.qpos[:3]=[-2.25,0.,e.bank_z+.01];d.qpos[3:7]=[1.,0.,0.,0.];d.qvel[:]=0.
    mujoco.mj_forward(m,d);e.state();s.reset_count=1
    wb=[m.body(n).id for n in ('left_wheel_link','right_wheel_link')]
    guides={int(m.geom_bodyid[i]) for i in range(m.ngeom) if m.geom(i).name.startswith('guide_wheel_')}
    upper_geom_ids={i for i in range(m.ngeom) if m.geom(i).name.startswith('step_') and abs(float(m.geom_pos[i,2]+m.geom_size[i,2])-h)<1e-6}
    if not upper_geom_ids:raise RuntimeError('Missing upper platform collider')
    maxclosure=0.;max_tau=np.zeros(6);last_act=np.zeros(6)
    def physics(env,act):
        global maxclosure,max_tau,last_act
        act=act.clamp(-env.action_clip,env.action_clip);last_act=act.numpy().reshape(-1).copy()
        for j in range(env.decim):
            tau=env._torque(act).detach().numpy().reshape(-1)
            if j%4==0:d.ctrl[env.act_ids[:4]]=tau[:4]
            d.ctrl[env.act_ids[4:]]=tau[4:]
            max_tau=np.maximum(max_tau,np.abs(d.ctrl[env.act_ids]))
            mujoco.mj_step(m,d)
            if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all():raise show.SafetyStop('nonfinite')
            cl=max(float(np.linalg.norm(d.site_xpos[u]-d.site_xpos[v])) for u,v in s.pairs)
            maxclosure=max(maxclosure,cl)
            if cl>1.:raise show.SafetyStop('catastrophic closure>1m')
        env.a_prev=act.detach().to(env.device)
        return env.state()
    e.step=types.MethodType(physics,e)
    trace=[];entry=None;speedmax=0.;hold=0.;physical_hold=0.;max_physical_hold=0.
    any_top=False;landed=[False,False];wall_frames=0;reason='timeout';tiltsteps=contactsteps=0
    first_wall=None;first_upper=None;peak_wheel_z=np.zeros(2);wheel_geometry=[]
    for wi in wb:
        wheel_geometry.append([dict(name=m.geom(i).name,type=int(m.geom_type[i]),size=m.geom_size[i].tolist()) for i in range(m.ngeom) if int(m.geom_bodyid[i])==wi])
    try:
        for k in range(800):
            age=k*.02;target=height_override if height_override is not None else .28+.4*h
            s.set_height(min(target,.28+.06*age))
            try:advance(s,{'w'} if age>=1.5 else set())
            except show.SafetyStop as exc:reason=str(exc);break
            force=np.zeros((m.nbody,3));supported=[False,False];wallforce=np.zeros(2)
            for ci in range(d.ncon):
                c=d.contact[ci];g1,g2=int(c.geom1),int(c.geom2);b1,b2=int(m.geom_bodyid[g1]),int(m.geom_bodyid[g2])
                cf=np.zeros(6);mujoco.mj_contactForce(m,d,ci,cf)
                world=np.asarray(c.frame).reshape(3,3).T@cf[:3];force[b1]-=world;force[b2]+=world
                terrain,body,sgn=(g1,b2,1.) if b1==0 else (g2,b1,-1.) if b2==0 else (-1,-1,0.)
                if terrain>=0 and terrain in upper_geom_ids and body in wb:
                    normal=sgn*np.asarray(c.frame).reshape(3,3)[0];i=wb.index(body)
                    if cf[0]>5. and normal[2]>.7 and abs(float(c.pos[2])-h)<.012:supported[i]=True
                    if cf[0]>5. and abs(normal[2])<.7:wallforce[i]+=cf[0]
            wheel=d.xpos[wb].copy();x=-wheel[:,0];y=wheel[:,1];z=wheel[:,2]
            vx=float(np.linalg.norm(d.qvel[:2]));near=float(np.min(np.abs(x-1.5)))<.45
            if age>=1.5:
                if entry is None and min(x)<1.7:entry=vx
                if near or entry is not None:speedmax=max(speedmax,vx)
            tol=max(.012,min(.025,.3*h))
            upper=np.array(supported)&(x<1.475)&(x>-1.4)&(np.abs(y)<1.4)&(np.abs(z-(h+.0625))<tol)
            for i in range(2):landed[i]|=bool(upper[i])
            rot=d.xmat[e.base_id].reshape(3,3);pitch=math.asin(float(np.clip(-rot[2,0],-1,1)));roll=math.atan2(float(rot[2,1]),float(rot[2,2]))
            ang=np.zeros(6);mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,e.base_id,ang,1)
            badcontact=bool(np.linalg.norm(force[e.base_id])>1. or (any(np.linalg.norm(force[g])>1. for g in guides) and not near))
            contactsteps=contactsteps+1 if badcontact else 0
            tiltsteps=tiltsteps+1 if max(abs(pitch),abs(roll))>math.radians(40) else 0
            if contactsteps>=10:reason='chassis_or_nonexempt_guide_contact_0.2s';break
            if tiltsteps>=10:reason='roll_or_pitch>40deg_0.2s';break
            if max(abs(float(d.qpos[0])),abs(float(d.qpos[1])))>4.1:reason='boundary';break
            top=bool(upper.all() and -1.3<-float(d.qpos[0])<1.38);any_top|=top
            pose_ok=top and max(abs(pitch),abs(roll))<math.radians(25) and np.linalg.norm(ang[:2])<1.5 and abs(float(d.qvel[2]))<.25 and not badcontact
            physical_hold=physical_hold+.02 if pose_ok else 0.;max_physical_hold=max(max_physical_hold,physical_hold)
            stable=pose_ok and entry is not None and .1<=entry<=.6 and speedmax<=.6
            hold=hold+.02 if stable else 0.
            if wallforce.any():
                wall_frames+=1
                if first_wall is None:first_wall={'time_s':age,'root_xyz':d.qpos[:3].tolist(),'wheel_xyz':wheel.tolist(),'pitch_deg':math.degrees(pitch),'wall_force_n':wallforce.tolist()}
            if upper.any() and first_upper is None:first_upper=age
            if near:peak_wheel_z=np.maximum(peak_wheel_z,z)
            trace.append([age,*d.qpos[:3],*d.qvel[:3],pitch,roll,*wheel.reshape(-1),*upper.astype(float),*wallforce,s.height,*d.ctrl[e.act_ids],*last_act])
            if hold>=.4-1e-7:reason='qualified_success';break
        a=np.asarray(trace);arrays[name]=a
        row={'case':name,'model_sha256':show.EXPECTED,'height_m':h,'command_vx':command,'height_target':height_override if height_override is not None else .28+.4*h,'completed_s':k*.02,'reason':reason,'qualified_success':reason=='qualified_success','ever_physical_top':any_top,'each_wheel_upper_landed':landed,'max_stable_hold_ignoring_speed_s':max_physical_hold,'entry_speed':entry,'max_approach_speed':speedmax,'max_root_x':float(a[:,1].max()),'max_wheel_z_near_edge':peak_wheel_z.tolist(),'wheel_top_center_target_z':h+.0625,'sidewall_contact_frames':wall_frames,'first_wall':first_wall,'first_upper_s':first_upper,'max_abs_pitch_deg':float(np.rad2deg(np.abs(a[:,7])).max()),'motor_abs_peak_env_order':max_tau.tolist(),'max_closure_m':maxclosure,'wheel_geoms':wheel_geometry}
        rows.append(row)
        (OUT/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n')
        print(json.dumps({k:v for k,v in row.items() if k not in ['wheel_geoms','first_wall']},ensure_ascii=False),flush=True)
    finally:s.close();del s,e,m,d;gc.collect()
np.savez_compressed(OUT/'trajectory.npz',**arrays)
result={'contact_protocol':'SINGLE_STEP_TOP_GEOMETRY_V2','method':'Frozen nominal MuJoCo diagnostic; same MOD4v3, motor envelope, 2.5ms/100/400/50Hz, 2mm diagnostic only. High stance/speed/2cm are diagnostic interventions only; no PPO or live configuration edits. Single centered start, not graduation.','trace_columns':['time','root_x','root_y','root_z','world_vx','world_vy','world_vz','pitch','roll','left_wheel_x','left_wheel_y','left_wheel_z','right_wheel_x','right_wheel_y','right_wheel_z','left_upper','right_upper','left_wall_N','right_wall_N','height_cmd',*[f'torque_{i}' for i in range(6)],*[f'action_{i}' for i in range(6)]],'rows':rows,'wall_seconds':time.time()-started}
(OUT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
