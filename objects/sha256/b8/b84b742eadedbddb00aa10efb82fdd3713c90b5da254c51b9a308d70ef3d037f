"""Executable geometric, dynamics and RL-interface acceptance checks."""
from pathlib import Path
import sys,json,time,hashlib,argparse
import numpy as np
import mujoco
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from kinematics import set_configuration,leg_configuration

def validate(detail=False):
    start=time.perf_counter()
    training='scene_headless.xml'
    visual='scene_training.xml'
    model=mujoco.MjModel.from_xml_path(str(ROOT/training))
    full=mujoco.MjModel.from_xml_path(str(ROOT/visual))
    data=mujoco.MjData(model);mujoco.mj_forward(model,data)
    assert model.nu==6 and np.sum(model.jnt_type==mujoco.mjtJoint.mjJNT_FREE)==1
    for attr in ['body_mass','body_inertia','body_ipos','body_iquat','body_parentid','jnt_pos','jnt_axis','jnt_type','actuator_ctrlrange','eq_data']:
        assert np.allclose(getattr(model,attr),getattr(full,attr)),attr+' differs between visual and training models'
    assert np.all(model.body_mass[1:]>0) and np.all(model.body_inertia[1:]>0)
    assert np.all(np.max(model.body_inertia[1:],axis=1)<=np.sum(model.body_inertia[1:],axis=1)/2+1e-10)
    rank=int(np.linalg.matrix_rank(data.efc_J.reshape(-1,model.nv)[:data.ne],tol=1e-8))
    assert model.nv-rank==12,(model.nv,rank)
    assert all(c.dist>=0 for c in data.contact),'Neutral assembly starts in penetration'
    pairs=[(model.site(s+'_'+a).id,model.site(s+'_'+b).id) for s in ['left','right']
           for a,b in [('proximal_a','proximal_b'),('distal_a','distal_b'),('gas_end','gas_mount')]]
    def closure():return max(float(np.linalg.norm(data.site_xpos[a]-data.site_xpos[b])) for a,b in pairs)
    initial_error=closure();assert initial_error<1e-8
    cases=[];pose_errors=[];accepted_differences=[]
    for diff in np.linspace(-.6,.6,121):
        try:
            mujoco.mj_resetData(model,data)
            set_configuration(model,data,left=(.25,diff),right=(-.25,-diff))
        except ValueError:continue
        pose_errors.append(closure());accepted_differences.append(float(diff))
    assert len(pose_errors)>20 and max(pose_errors)<2e-8,pose_errors

    def rollout(name,steps,seed,mode,drop=0.,tilt=0.,scale=1.,push=False):
        steps=int(round(steps*.001/model.opt.timestep))
        rng=np.random.default_rng(seed)
        model.body_mass[:]=full.body_mass*scale;model.body_inertia[:]=full.body_inertia*scale
        mujoco.mj_setConst(model,data);mujoco.mj_resetData(model,data)
        data.qpos[2]+=drop
        if tilt:
            axis=rng.normal(size=3);axis/=np.linalg.norm(axis)
            mujoco.mju_axisAngle2Quat(data.qpos[3:7],axis,tilt)
        data.qvel[:6]=rng.uniform(-.1,.1,6) if drop else 0
        mujoco.mj_forward(model,data)
        maxerr=0.;maxspeed=0.;maxdepth=0.;maxcontacts=0;maxrange=0.;depthpair=None
        per_joint_overshoot={model.joint(j).name:0. for j in range(model.njnt) if model.jnt_limited[j]}
        addresses=[model.joint(s+'_'+j).qposadr[0] for s in ['left','right'] for j in ['hip','crank','wheel_spin']]
        velocities=[model.joint(s+'_'+j).dofadr[0] for s in ['left','right'] for j in ['hip','crank','wheel_spin']]
        for i in range(steps):
            t=i*model.opt.timestep
            if mode=='random' and i%round(.020/model.opt.timestep)==0:data.ctrl[:]=rng.uniform(-1,1,6)*model.actuator_ctrlrange[:,1]
            elif mode=='saturation' and i%round(.300/model.opt.timestep)==0:data.ctrl[:]=rng.choice([-1.,1.],6)*model.actuator_ctrlrange[:,1]*10
            elif mode=='sine':
                target=np.array([.25*np.sin(t*2),.25*np.sin(t*2+.8),0,.25*np.sin(t*2),.25*np.sin(t*2+.8),0])
                data.ctrl[:]=np.clip(70*(target-data.qpos[addresses])-2.5*data.qvel[velocities],-model.actuator_ctrlrange[:,1],model.actuator_ctrlrange[:,1])
            if push and 1.5<t%3<1.65:data.xfrc_applied[model.body('chassis').id,:3]=[250.,150.,-150.]
            else:data.xfrc_applied[:]=0
            mujoco.mj_step(model,data)
            # Use forward at every step so reported site errors correspond to integrated positions.
            mujoco.mj_forward(model,data)
            if not np.isfinite(data.qpos).all() or not np.isfinite(data.qvel).all():raise AssertionError(name+': non-finite state')
            if any(w.number for w in data.warning):raise AssertionError(name+': MuJoCo warning '+str([w.number for w in data.warning]))
            maxerr=max(maxerr,closure());maxspeed=max(maxspeed,float(np.max(abs(data.qvel))))
            if data.ncon:
                c=min(data.contact,key=lambda c:c.dist)
                if -c.dist>maxdepth:
                    maxdepth=float(-c.dist);depthpair=[model.geom(c.geom1).name,model.geom(c.geom2).name]
            maxcontacts=max(maxcontacts,data.ncon)
            for j in range(model.njnt):
                if model.jnt_limited[j]:
                    q=data.qpos[model.jnt_qposadr[j]];lo,hi=model.jnt_range[j]
                    overshoot=float(max(lo-q,q-hi,0));maxrange=max(maxrange,overshoot)
                    per_joint_overshoot[model.joint(j).name]=max(per_joint_overshoot[model.joint(j).name],overshoot)
            assert maxerr<.002, (name,'closure',maxerr)
            assert maxspeed<1000,(name,'speed',maxspeed)
            assert np.linalg.norm(data.qpos[:3])<100,(name,'runaway translation')
        result={'name':name,'steps':steps,'seconds':steps*model.opt.timestep,'seed':seed,'mass_scale':scale,
                'max_closure_error_m':maxerr,'max_generalized_speed':maxspeed,
                'max_contact_penetration_m':maxdepth,'deepest_contact_pair':depthpair,'max_contacts':maxcontacts,
                'max_joint_limit_overshoot':maxrange,'per_joint_limit_overshoot_si':per_joint_overshoot,'warnings':[w.number for w in data.warning],
                'finite_state':True,'final_base_height_m':float(data.qpos[2])}
        assert max(per_joint_overshoot[s+'_knee'] for s in ['left','right'])<np.deg2rad(2), 'Impact consumed the CAD stop reserve'
        cases.append(result);print(json.dumps(result),flush=True)

    rollout('zero_torque_gravity',6000,0,'zero')
    rollout('joint_sine_tracking',10000,1,'sine')
    rollout('full_torque_random',12000,2,'random')
    rollout('commands_10x_clamped',6000,3,'saturation')
    rollout('external_push',6000,4,'random',push=True)
    for i in range(8):rollout('drop_'+str(i),4000,10+i,'random',drop=.25+.04*i,tilt=i*np.pi/7,scale=.8+.4*i/7)
    # Model reset API checks: keep closed loops consistent and observable.
    from robomaster_env import RoboMasterEnv
    from gymnasium.utils.env_checker import check_env
    env=RoboMasterEnv(domain_randomization=True,model_path=ROOT/training);check_env(env,skip_render_check=True)
    episode_count=0;rl_maxerr=0.;rng=np.random.default_rng(2026)
    obs,info=env.reset(seed=2026)
    for i in range(4000):
        obs,r,done,trunc,info=env.step(rng.uniform(-1,1,6))
        assert obs.shape==(39,) and np.isfinite(obs).all() and np.isfinite(r)
        assert not info['numerical_failure'],info
        rl_maxerr=max(rl_maxerr,info['closure_error_m'])
        if done or trunc:episode_count+=1;obs,info=env.reset()
    env.close()
    report={'status':'PASS','mujoco_version':mujoco.__version__,'nq':model.nq,'nv':model.nv,'nu':model.nu,
            'body_count_including_world':model.nbody,'equality_count':model.neq,'equality_jacobian_rank':rank,
            'independent_velocity_dofs':model.nv-rank,'initial_closure_error_m':initial_error,
            'analytic_pose_count':len(pose_errors),'analytic_max_closure_error_m':max(pose_errors),
            'visual_training_dynamics_identical':True,'tested_simulation_steps':sum(c['steps'] for c in cases)+4000*env.frame_skip,
            'maximum_closure_error_m':max(max(c['max_closure_error_m'] for c in cases),rl_maxerr),
            'rl_interface_steps':4000,'rl_completed_episodes':episode_count,'rollouts':cases,
            'elapsed_seconds':time.perf_counter()-start,
            'sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in [visual,training]},
            'scope':f'Numerical stability under the stated bounded loads and dt={model.opt.timestep}s. Mass, motor and gas-spring parameters remain uncalibrated.'}
    (ROOT/('reports/validation_detail_report.json' if detail else 'reports/validation_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='rollouts'},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--detail',action='store_true')
    validate(parser.parse_args().detail)
