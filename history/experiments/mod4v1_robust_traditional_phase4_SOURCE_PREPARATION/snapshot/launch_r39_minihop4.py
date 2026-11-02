"""Four NEW operator-commanded flat mini-hop profiles. Max2 workers/failfast."""
from pathlib import Path
import concurrent.futures,hashlib,json,os,subprocess,sys,time
R=Path(__file__).resolve().parent;B=R/'batches/r39_minihop4';B.mkdir(exist_ok=False)
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
pre=json.loads((R/'MINIHOP_V1/preflight001/RESULT.json').read_bytes());assert pre['failures']==0 and pre['physics_steps']==0
cases=[]
for push in(.10,.14):
    for delta in(0,20):
        name=f'r39_flat_d{delta}_p{round(push*100):02d}'
        c=dict(scene='flat',seed=0,nominal=True,duration_s=6.,start_x_m=0.,forward_m_s=0.,end_gain_file=f'TALL_ROUGH_BANK_V1/gain_delta{delta}.json',
               hop=dict(operator_enable=True,trigger_time_s=1.5,push_for_s=push,predicted_air_after_push_s=.35,capture_blend_s=.10,push_kp=300.,push_kd=3.,wheel_push_Nm=0.,max_trigger_speed_m_s=.2))
        cp=B/(name+'.json');dump(cp,c);cases.append((name,cp))
source=[]
for name in('launch_r39_minihop4.py','run_minihop_case_v1.py','MINIHOP_V1/controller.py','MINIHOP_V1/contact_grade.py','physics_bridge_minihop_flat_v1.py'):
    p=R/name;raw=p.read_bytes();source.append(dict(path=str(p),SHA=hashlib.sha256(raw).hexdigest()))
dump(B/'PROTOCOL.json',dict(kind='NEW_TRAIN_OPERATOR_MINIHOP_IMPULSE_CHARACTERIZATION',cases=[n for n,_ in cases],source_before_physics=source,
     physics_dt_s=.0005,control_dt_s=.01,max_workers=2,old_H1_H2_H4_unchanged=True,scene='original_full_geometry_flat_no_RM_pass_claim',
     changed='manual_leg_profile_and_predicted_flight_observer_toggles_only',nominal_only=True,fullDR_followup_pending=True,
     contact_grading='read_only_per_0p5ms_all_world_surfaces_contact_fn_gt1N_then_operational_fullair20ms',
     engineering_screen_not_user_ratified='complete_and_main_mesh_in_operational_fullair_clearance_ge80mm_no_posttrigger_guide_or_hard_contact_and_endstable2s',
     no_new_contact_or_flight_trusted_cue=True,no_assist_no_postreset_root_writes=True))
rows=[];env=dict(os.environ);env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8')
def run(item):
    name,cp=item;out=R/'results'/name;log=B/(name+'.log');assert not out.exists();start=time.perf_counter()
    with log.open('xb')as f:
        done=subprocess.run([sys.executable,'-B',str(R/'run_minihop_case_v1.py'),'--config',str(cp),'--out',str(out)],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
    row=dict(case=name,rc=done.returncode,wall_s=time.perf_counter()-start,log=str(log))
    rp=out/'result.json'
    if rp.is_file():
        v=json.loads(rp.read_bytes());row.update({k:v[k]for k in('complete','stop','controls','physics_steps','first_all_world_air_s','max_all_world_air_s','maximum_main_mesh_clearance_during_full_air_m','end_stable_s','proposed_flat_clear80mm_recover2s','after_trigger_hard_contact_physics_ticks','after_trigger_guide_contact_physics_ticks','max_pitch_rad','max_roll_rad','trace_artifact','physical_artifact')})
    elif (out/'ERROR.json').is_file():row['error']=json.loads((out/'ERROR.json').read_bytes())
    return row
for offset in(0,2):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
        wave=list(pool.map(run,cases[offset:offset+2]))
    rows+=wave;print(json.dumps(wave,indent=2),flush=True)
    if any(r['rc']!=0 for r in wave):break
result=dict(kind='R39_NOMINAL_MINIHOP_PROFILE_TRAIN',scheduled=len(cases),executed=len(rows),unstarted=[n for n,_ in cases if n not in{r['case']for r in rows}],rows=rows,not_RM_or_fullDR_qualification=True)
dump(B/'BATCH_RESULT.json',result)
if any(r['rc']!=0 for r in rows):raise SystemExit(1)
