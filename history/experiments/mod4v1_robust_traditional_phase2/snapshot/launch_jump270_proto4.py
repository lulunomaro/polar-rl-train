"""Fourfreshnominaltimedjumpfeasibilitycases; notcontactFSM/fullDRqualification."""
from pathlib import Path
import json,os,sys,subprocess,time,concurrent.futures
R=Path(__file__).resolve().parent;D=R/'batches/r13_jump270_timed_proto4';D.mkdir(parents=True,exist_ok=False)
with(D/'PREP.log').open('xb')as f:rc=subprocess.run([sys.executable,'-B',str(R/'prepare_jump_estimator_v1.py')],cwd=R,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT).returncode
assert rc==0,('jumpestprep',rc)
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1');jobs=[(.3,.72),(.4,.72),(.3,.55),(.4,.55)]
for n in('run_jump270_timed_v1.py','sensor_core_jump_v1.py'):(D/n).write_bytes((R/n).read_bytes())
def run(j):
 distance,recovery=j;case=f'r13_jump_d{int(distance*100)}r{int(recovery*100)}';c=dict(case_id=case,seed=0,nominal=True,duration_s=7.,command_at_s=.6,launch_distance_m=distance,recover_after_push_s=recovery,speed=1.4);p=D/(case+'.json');p.write_text(json.dumps(c,indent=2),encoding='utf-8');start=time.time()
 with(D/(case+'.log')).open('xb')as f:proc=subprocess.Popen([sys.executable,'-B',str(R/'run_jump270_timed_v1.py'),'--config',str(p),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT);rc=proc.wait()
 p=R/'results'/case/'result.json';r=json.loads(p.read_bytes())if p.exists()else{};row=dict(case=case,returncode=rc,start=start,end=time.time(),complete=r.get('complete'),stop=r.get('stop'),launch=r.get('launch_time'),clear=r.get('first_full_mesh_clearance'),top_controls=r.get('top_bearing_controls'),ever_stable=r.get('max_stable_s'),end_stable=r.get('end_stable_s'),nonwheel=r.get('nonwheel_contact_control_samples'));print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(run,jobs))
(D/'BATCH_RESULT.json').write_text(json.dumps({'kind':'NOMINAL_TIMED_JUMP_FEASIBILITY_ONLY','rows':rows},indent=2),encoding='utf-8');print('CLOSED',D/'BATCH_RESULT.json',flush=True)
