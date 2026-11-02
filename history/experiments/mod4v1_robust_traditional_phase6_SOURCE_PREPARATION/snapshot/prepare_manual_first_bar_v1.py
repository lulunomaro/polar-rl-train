"""Write bounded manual-first-bar TRAIN protocol and run zero-step admission.
No old episode is replayed. Main trial is a separate explicit launcher.
"""
from pathlib import Path
import ast,copy,hashlib,json,types,traceback
import numpy as np,mujoco
R=Path(__file__).resolve().parent;D=R/'MANUAL_FIRST_BAR_V1';A=D/'preflight001';A.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
files=['prepare_manual_first_bar_v1.py','run_manual_first_bar_v1.py','MANUAL_FIRST_BAR_V1/grade_rows.py',
       'run_minihop_landing_v4.py','MINIHOP_LANDING_V3/controller.py','MINIHOP_OBSERVER_V2/controller.py','MINIHOP_V1/controller.py',
       'MINIHOP_AUDIT_V2/physics_bridge_minihop_flat_v2.py','MINIHOP_AUDIT_V2/physics_bridge_minihop_rm_v2.py']
dump(A/'SOURCE_PREEXEC.json',dict(files=[dict(path=str(R/f),SHA=sha(R/f))for f in files],purpose='0step admission, not new physics'))
checks=0;calls=0
old_step=mujoco.mj_step
def forbidden(*a,**k):
    global calls;calls+=1;raise AssertionError('Integrator forbidden during admission')
mujoco.mj_step=forbidden
try:
    from physics_bridge import geometry,load_gain
    from run_manual_first_bar_v1 import arrays,load_landing_gain,source_manifest,MiniHop,BoundsRows
    from rm_grid_terrain_v1 import configure,authored_boxes
    base=dict(scene='flat',seed=0,nominal=True,duration_s=8.,start_x_m=.8,forward_m_s=1.,brake_at_s=2.,
        end_gain_file='TALL_ROUGH_BANK_V1/gain_delta20.json',landing_gain=dict(file='nominal_gain_v1.json'),
        hop=dict(operator_enable=True,trigger_time_s=1.,push_for_s=.14,predicted_air_after_push_s=.35,capture_blend_s=.1,
                 push_kp=300.,push_kd=3.,wheel_push_Nm=0.,max_trigger_speed_m_s=1.2,observer_quarantine_after_push_s=.5,
                 landing_transition_enable=True,landing_transition_s=.2),cohort='NEW_MANUAL_LOCAL_FIRST_BAR_TRAIN_NOT_H5')
    configs=[]
    for name,scene,trig in [('r48_moving_flat_t100','flat',1.),('r48_rm6_t100','rm',1.),('r48_rm6_t110','rm',1.1)]:
        c=copy.deepcopy(base);c.update(case_id=name,scene=scene);c['hop']['trigger_time_s']=trig
        if scene=='rm':c.update(terrain_seed=9001,terrain_difficulty=1.)
        configs.append((name,c))
    protocol=dict(kind='NEW_MANUAL_LOCAL_FIRST_BAR_MOVING_HOP_TRAIN',case_names=[n for n,c in configs],configs=configs,
        physical_trials_started=False,new_physics_steps=0,max_workers=2,source_hypothesis='preH5 TRAIN l20 plus public SCUT geometry; not H5 tuning',
        scope='first6cm transverse bar and flat moving admission, not whole9m RM traversal/270mm/autonomous obstacle',
        controls_are_frozen_V3_hop_equations=True,only_forward_stop_and_operator_configuration_changed=True,
        private_grading='all collision-geom compiled conservative sphere union at explicitly cached stage; exact tire rear crossing separate',
        gates='complete AND main_mesh_air>=.08 AND all-guide/hard-ticks==0 AND endstable>=2 AND maxY<=.3 AND progress>=.5; RM additionally full collision bbox behind firstback and never reached nextfront',
        raw_physics_producer_SHA=True,software_error_stops_remaining_waves=True,H5_unchanged=True,PH6_pending=True)
    dump(D/'PROTOCOL.json',protocol)
    for f in files:ast.parse((R/f).read_text(encoding='utf-8'));checks+=1
    start=arrays(json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes())['gains']['crouch']);end=load_gain(R/base['end_gain_file']);landing=load_landing_gain(base['landing_gain'])
    geom=geometry();geom.radius=.0625;boots=[]
    for scene in('flat','rm'):
        c=next(c for n,c in configs if c['scene']==scene)
        if scene=='flat':
            from MINIHOP_AUDIT_V2.physics_bridge_minihop_flat_v2 import MiniHopAuditPlant as Plant
        else:
            configure(9001,1.)
            from MINIHOP_AUDIT_V2.physics_bridge_minihop_rm_v2 import MiniHopAuditPlant as Plant
        p=Plant(False);p.reset(start['symmetric'],.8);rows=BoundsRows(A/(scene+'_static_geometry_only.jsonl'));rows.bind(p)
        grade=p.grade();assert all(k in grade for k in ('xyz','pitch_true','roll_true','body_velocity','finite','closure','mimic','upright_cos'));checks+=8
        assert p.tick_phys==0 and p.d.time==0.;checks+=2
        rows.append(dict(stage_time_s=0.,air_qualified=False,static_geometry_only_no_contact_grade=True))
        assert np.isfinite(rows.last_bounds['min_xyz_m']).all();checks+=1
        if scene=='rm':
            assert rows.first_bar['name']=='rm_bar_011'and rows.first_bar['top_z_m']==.06;checks+=2
            assert rows.next_bar['front_x_m']>rows.first_bar['back_x_m'];checks+=1
        source=source_manifest(scene,c)
        boots.append(dict(scene=scene,collision_geoms=int(rows.ids.size),bounds=rows.last_bounds,first_bar=rows.first_bar,next_bar=rows.next_bar,
                          source_files=len(source['files']),model_SHA=source['model_SHA'],controls=0,physics_steps=0))
    for name,c in configs:
        hop=MiniHop(start,end,geom,c['hop'],landing_gain=landing)
        est=types.SimpleNamespace();x=np.r_[start['q'],np.zeros(7)];x[7]=.8
        e=types.SimpleNamespace(state14=x,roll=0.,omega_body=np.zeros(3),sensor_age_s=0.)
        q4=np.array([x[3],x[3]+x[4],x[5],x[5]+x[6]])
        packet=types.SimpleNamespace(joint_pos4=q4,joint_vel4=np.zeros(4))
        for k in range(800):
            now=k*.01;hop.prepare_estimator(est,now);cmd=c['forward_m_s']if now<c['brake_at_s']else 0.
            tau=hop.command(e,packet,now,np.array([1.,0.,0.,0.]),cmd)
            assert np.shape(tau)==(6,)and np.isfinite(tau).all()and not hop.fault;checks+=1
            assert np.all(np.abs(tau)<=np.array([40.,40.,5.775909774436091]*2));checks+=1
        assert hop.launched and hop.captured;checks+=1
        assert hop.landing_weight==1.;checks+=1
    assert calls==0
    dump(A/'RESULT.json',dict(status='PASS_ZERO_INTEGRATOR_ADMISSION',checks=checks,integrator_calls=calls,new_physics_steps=0,
        synthetic_command_calls=2400,synthetic_not_robot_trajectory=True,real_model_static_boots=boots,source_preexec_SHA=sha(A/'SOURCE_PREEXEC.json')))
    print(json.dumps(dict(status='PASS_ZERO_INTEGRATOR_ADMISSION',checks=checks,integrator_calls=calls,planned_cases=[n for n,c in configs]),indent=2))
except BaseException:
    (A/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
finally:mujoco.mj_step=old_step
