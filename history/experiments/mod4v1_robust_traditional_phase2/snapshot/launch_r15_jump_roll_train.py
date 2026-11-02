"""PairedTRAIN: countertakeoffroll/pitch, keepDC/effort/sourcegeometryfixed."""
from pathlib import Path
import json,os,sys,subprocess,time,concurrent.futures
R=Path(__file__).resolve().parent;D=R/'batches/r15_jump_roll_train33';D.mkdir(parents=True,exist_ok=False)
with(D/'PREP.log').open('xb')as f:rc=subprocess.run([sys.executable,'-B',str(R/'prepare_jump_roll_v2.py')],cwd=R,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT).returncode
assert rc==0
variants={'roll':dict(push_reserve_Nm=8.),'roll_long':dict(push_reserve_Nm=8.,push_for=.11),'roll_long_pitchD':dict(push_reserve_Nm=8.,push_for=.11,push_pitch_d=10.)};jobs=[(v,s)for v in variants for s in(0,101,102,201,202,203,204,205,206,207,208)];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
for n in('run_jump270_roll_v2.py','sensor_core_jump_v1.py'):(D/n).write_bytes((R/n).read_bytes())
def run(j):
 v,s=j;case=f'r15_{v}_{s}';cfg=dict(case_id=case,seed=s,nominal=s==0,duration_s=9.,command_at_s=.6,launch_distance_m=.3,recover_after_push_s=.72,speed=1.4,**variants[v]);cp=D/(case+'.json');cp.write_text(json.dumps(cfg,indent=2),encoding='utf-8');start=time.time()
 with(D/(case+'.log')).open('xb')as f:proc=subprocess.Popen([sys.executable,'-B',str(R/'run_jump270_roll_v2.py'),'--config',str(cp),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT);rc=proc.wait()
 p=R/'results'/case/'result.json';r=json.loads(p.read_bytes())if p.exists()else{};row=dict(case=case,variant=v,seed=s,returncode=rc,start=start,end=time.time(),complete=r.get('complete'),stop=r.get('stop'),clear=r.get('first_full_mesh_clearance'),end_stable=r.get('end_stable_s'),end2s=r.get('proposed_end_stable_2s'),nonwheel=r.get('nonwheel_contact_control_samples'),final_roll=r.get('last',{}).get('roll_true'),final_pitch=r.get('last',{}).get('pitch_true'));print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows=list(pool.map(run,jobs))
summary={v:{'n_DR':10,'DR_clear':sum(r['variant']==v and r['seed']!=0 and r['clear']is not None for r in rows),'DR_end2s':sum(r['variant']==v and r['seed']!=0 and bool(r['end2s'])for r in rows),'DR_zero_nonwheel_end2s':sum(r['variant']==v and r['seed']!=0 and bool(r['end2s'])and r['nonwheel']==0 for r in rows)}for v in variants};(D/'BATCH_RESULT.json').write_text(json.dumps(dict(kind='R15_JUMP_ROLLVMC_TRAIN',summary=summary,rows=rows,variants=variants),indent=2),encoding='utf-8');print('SUMMARY',json.dumps(summary),flush=True)
