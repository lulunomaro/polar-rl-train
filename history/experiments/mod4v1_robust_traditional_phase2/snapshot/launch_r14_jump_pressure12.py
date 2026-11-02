"""Genuinelylongerrecovery9s+firstfullDRjumptraining; notbookkeepingreplay.
AllR13seven-second/parsefailurespreserved. No contactFSMqualification claim.
"""
from pathlib import Path
import json,os,sys,subprocess,time,concurrent.futures
R=Path(__file__).resolve().parent;D=R/'batches/r14_jump9s_pressure12';D.mkdir(parents=True,exist_ok=False);jobs=[('nominal_extend',0,True,.72),('nominal_landlate',0,True,.85)]+[('DR',s,False,.72)for s in(101,102,201,202,203,204,205,206,207,208)];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
for n in('run_jump270_timed_v1.py','sensor_core_jump_v1.py'):(D/n).write_bytes((R/n).read_bytes())
def run(j):
 name,seed,nominal,recovery=j;case=f'r14_jump_{name}_{seed}';cfg=dict(case_id=case,seed=seed,nominal=nominal,duration_s=9.,command_at_s=.6,launch_distance_m=.3,recover_after_push_s=recovery,speed=1.4);cp=D/(case+'.json');cp.write_text(json.dumps(cfg,indent=2),encoding='utf-8');start=time.time()
 with(D/(case+'.log')).open('xb')as f:proc=subprocess.Popen([sys.executable,'-B',str(R/'run_jump270_timed_v1.py'),'--config',str(cp),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT);rc=proc.wait()
 p=R/'results'/case/'result.json';r=json.loads(p.read_bytes())if p.exists()else{};row=dict(case=case,seed=seed,nominal=nominal,returncode=rc,start=start,end=time.time(),complete=r.get('complete'),stop=r.get('stop'),launch=r.get('launch_time'),clear=r.get('first_full_mesh_clearance'),top_controls=r.get('top_bearing_controls'),ever_stable=r.get('max_stable_s'),end_stable=r.get('end_stable_s'),end2s=r.get('proposed_end_stable_2s'),nonwheel=r.get('nonwheel_contact_control_samples'));print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(run,jobs))
(D/'BATCH_RESULT.json').write_text(json.dumps({'kind':'JUMP9S_NEWASSET_NOMINAL_AND_FIRST_FULLDR_TRAIN_ONLY','rows':rows},indent=2),encoding='utf-8');print('CLOSED',D/'BATCH_RESULT.json',flush=True)
