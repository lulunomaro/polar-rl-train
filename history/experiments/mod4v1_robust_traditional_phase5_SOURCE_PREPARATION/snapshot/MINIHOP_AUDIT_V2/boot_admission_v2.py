"""New full-model boot admission only, after v2 unit passes. NO integration."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import ast,gc,hashlib,json,shutil,traceback
import numpy as np
import mujoco
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
CHECKS=0

def check(value,message=''):
    global CHECKS
    CHECKS+=1
    if not bool(value):raise AssertionError(f'check {CHECKS}: {message}')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
def state_bytes(p):return{n:getattr(p.d,n).tobytes()for n in ('qpos','qvel','ctrl','xmat','subtree_com','geom_xpos','geom_xmat')}|{'model_mass':p.m.body_mass.tobytes(),'model_inertia':p.m.body_inertia.tobytes(),'time':float(p.d.time),'tick':p.tick_phys}

def main():
    unit=json.loads((HERE/'UNIT_RESULT_02.json').read_bytes());check(unit['failures']==0 and unit['physics_steps']==0)
    check(unit['calls']['step']==unit['calls']['forward']==0 and not unit['full_model_constructed'])
    for n,wanted in unit['sources'].items():check(sha(HERE/n)==wanted,'exact unit-qualified source '+n)
    out=HERE/'boot_attempt_01';out.mkdir(exist_ok=False)
    for n in ('boot_admission_v2.py','contact_grade_v2.py','schema_v2.py','provenance_v2.py','run_minihop_case_v2.py','physics_bridge_minihop_flat_v2.py','physics_bridge_minihop_rm_v2.py'):
        shutil.copy2(HERE/n,out/n)
    integration_names=[n for n in ('mj_step','mj_step1','mj_step2','mj_Euler','mj_RungeKutta','mj_implicit')if hasattr(mujoco,n)]
    old={n:getattr(mujoco,n)for n in integration_names};forward=mujoco.mj_forward;calls={n:0 for n in integration_names};calls['mj_forward']=0
    def forbid(name):
        def f(*a,**kw):calls[name]+=1;raise AssertionError(name+' prohibited in 0step full-model admission')
        return f
    def observed_forward(*a,**kw):calls['mj_forward']+=1;return forward(*a,**kw)
    for n in old:setattr(mujoco,n,forbid(n))
    mujoco.mj_forward=observed_forward
    records=[]
    try:
        from physics_bridge import geometry,load_gain,FullDR,MODEL_SHA
        from sensor_core_jump_v1 import StateEstimator
        from MINIHOP_V1.controller import MiniHop,EFFORT
        from MINIHOP_AUDIT_V2.provenance_v2 import source_manifest
        from MINIHOP_AUDIT_V2.run_minihop_case_v2 import arrays
        bank=json.loads((ROOT/'JUMP270_V1/GAIN_BANK.json').read_bytes());start=arrays(bank['gains']['crouch']);end=load_gain(ROOT/'TALL_ROUGH_BANK_V1/gain_delta20.json')
        for scene in ('flat','rm'):
            cfg=dict(scene=scene,seed=314159,nominal=False,end_gain_file='TALL_ROUGH_BANK_V1/gain_delta20.json',hop={})
            if scene=='rm':
                from rm_grid_terrain_v1 import configure
                configure(9001,1.)
                from MINIHOP_AUDIT_V2.physics_bridge_minihop_rm_v2 import MiniHopAuditPlant
            else:from MINIHOP_AUDIT_V2.physics_bridge_minihop_flat_v2 import MiniHopAuditPlant
            manifest=source_manifest(scene,cfg);dump(out/f'{scene}_SOURCE_PREEXEC.json',manifest)
            plant=MiniHopAuditPlant(False);dr=FullDR(314159,nominal=False);drmeta=plant.attach_dr(dr);plant.reset(start['symmetric'],0.)
            check(plant.tick_phys==0 and float(plant.d.time)==0. and len(plant.audit)==0,'boot did not step')
            check(plant.dt==.0005 and not plant.instrumentation_error)
            geom=geometry();geom.radius=.0625
            estimator=StateEstimator(geom,plant.imu_offset,upright_prior=True,accel_reference='wheel_midpoint',innovation_limit=1.)
            hop=MiniHop(start,end,geom,{})
            hop.prepare_estimator(estimator,0.);packet=plant.sensor_packet();estimate=estimator.update(packet)
            requested=hop.command(estimate,packet,0.,estimator.q)
            check(requested.shape==(6,)and np.isfinite(requested).all()and np.all(np.abs(requested)<=EFFORT))
            check(not hop.launched and hop.log['phase']=='supported_approach'and not hop.log['contact_or_flight_trusted'],'operator disabled by default')
            check(np.isfinite(estimate.state14).all()and not hop.fault)
            # Only read current real-model caches; no apply_torque_request,
            # actuator ctrl assignment, fake elapsed time, or grade-row creation.
            snapshot=state_bytes(plant);actual_mass=float(plant.m.body_mass.sum());cached_mass=float(plant.mass)
            plant._capture_drivepoint(plant.d.qvel[plant.vids].copy(),np.zeros(6))
            check(snapshot==state_bytes(plant),'private hook is read-only on actual model/data')
            check(plant._private_pre['actual_model_body_mass_sum_kg']==actual_mass)
            check(plant._private_pre['root_rotation_world_from_body33_pre']is None,'post-refreshed caches deliberately not sampled early')
            envelope=plant.exact_support.envelopes(plant.d)
            check(len(envelope)==2 and all(np.isfinite(e['world_vertices']).all()for e in envelope.values()))
            check(plant.tick_phys==0 and float(plant.d.time)==0. and not plant.audit)
            check(not any('contact_external_force'in n or 'private_contact'in n for n in vars(packet)))
            loaded=[dict(module=n,path=str(Path(getattr(m,'__file__','')).resolve()))for n,m in sorted(sys.modules.items())if getattr(m,'__file__',None)and Path(m.__file__).resolve().is_relative_to(ROOT)]
            check(not any(Path(x['path']).name.startswith('world_leg')for x in loaded),'active root world_leg not imported')
            check(not any('active_qp_stdio'in x['module']for x in loaded),'blocked SDK not imported')
            records.append(dict(scene=scene,kind='REAL_FULLMODEL_BOOT_ONLY_NOT_TRAJECTORY',model_SHA=MODEL_SHA,model_dimensions=dict(nq=plant.m.nq,nv=plant.m.nv,nbody=plant.m.nbody,ngeom=plant.m.ngeom,nmesh=plant.m.nmesh),DR_seed=314159,nominal=False,actual_model_body_mass_sum_kg=actual_mass,cached_legacy_self_mass_kg=cached_mass,hook_mass_used_actual_model_not_legacy=True,scene_metadata=getattr(plant,'scene_metadata',None),physics_steps=0,physics_grade_rows=0,drive_capture_is_boot_probe_not_applied_actuation=True,control_cycle_executed=False,operator_default_disabled=True,contact_force_private_not_sensor=True,loaded_workspace_modules=loaded,source_manifest_SHA=sha(out/f'{scene}_SOURCE_PREEXEC.json')))
            del plant;gc.collect()
        check(all(calls[n]==0 for n in integration_names),'all integration entry points unused')
        result=dict(kind='NEW_MINIHOP_V2_UNIT_THEN_REAL_BOOT_ADMISSION',status='ADMITTED_ZERO_STEP_ONLY',checks=CHECKS,failures=0,unit_receipt_SHA=sha(HERE/'UNIT_RESULT_02.json'),mujoco_version=mujoco.__version__,calls=calls,physics_steps=0,old_preflight_executed=False,runner_executed=False,trajectory_qualified=False,PH5_and_later_pending=True,current_PH4_cutoff_excludes_v2=True,records=records)
        dump(HERE/'BOOT_ADMISSION_01.json',result)
        print(json.dumps({k:v for k,v in result.items()if k!='records'},indent=2))
        print(json.dumps([dict(scene=r['scene'],dimensions=r['model_dimensions'],actual_mass_kg=r['actual_model_body_mass_sum_kg'],legacy_cached_mass_kg=r['cached_legacy_self_mass_kg'])for r in records],indent=2))
    except BaseException:
        dump(out/'ERROR.json',dict(kind='BOOT_ADMISSION_FAILED_NOT_ADMITTED',error=traceback.format_exc(),checks=CHECKS,calls=calls,completed_records=records));raise
    finally:
        for n,f in old.items():setattr(mujoco,n,f)
        mujoco.mj_forward=forward
if __name__=='__main__':main()
