"""PairedTRAINofstopcapture/lowspinattitudecorrection. R26allfailurespreserved.
NoBSP orphysicslimitsaltered. Same26sscheduleandgrading.
"""
from pathlib import Path
import json,os,sys,subprocess,time,concurrent.futures
R=Path(__file__).resolve().parent;D=R/'batches/r27_spin_stop27';D.mkdir(parents=True,exist_ok=False)
with(D/'PREP.log').open('xb')as f:rc=subprocess.run([sys.executable,'-B',str(R/'prepare_spin_stop_runner_v1.py')],cwd=R,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT).returncode
assert rc==0;proto=json.loads((R/'SPIN_H2_K20_V1/PROTOCOL.json').read_bytes());schedule=json.loads((R/'batches/r26_transitions26/PROTOCOL.json').read_bytes())['schedules']['spin_cycle'];variants={'accel_only':(True,False),'capture_only':(False,True),'both':(True,True)};jobs=[(v,s)for v in variants for s in[0]+list(range(201,209))];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1');(D/'PROTOCOL.json').write_text(json.dumps(dict(kind='PAIRED_STOP_TRAIN_NOT_H2RETUNE',variants=variants,schedule=schedule,base_gate='unchangedR26transitiongrader',lowspin_gain_rule='gyro_z<2andshaped_w<2 ->accelgain1.5else0',capture_rule='command0/refw<2/estimatedw<2for10ticks->P25capture+200msconvexblend',new_ref_is_estimated_only=True),indent=2),encoding='utf-8')
for n in('spin_stop_capture_v1.py','run_spin_stop_v1.py','transition_grader_v1.py'):(D/n).write_bytes((R/n).read_bytes())
def run(j):
 v,s=j;adapt,capture=variants[v];case=f'r27_{v}_{s}';controller=dict(proto['controller'],stop_capture=capture);cfg=dict(case_id=case,seed=s,nominal=s==0,profile='spin',mode='custom_transition',duration_s=26.,controller=controller,schedule=schedule,feedback='sensors',upright_arming_prior=True,accel_reference='wheel_midpoint',accel_correction=0.,adaptive_accel_lowspin=adapt);cp=D/(case+'.json');cp.write_text(json.dumps(cfg,indent=2),encoding='utf-8');start=time.time()
 with(D/(case+'.log')).open('xb')as f:proc=subprocess.Popen([sys.executable,'-B',str(R/'run_spin_stop_v1.py'),'--config',str(cp),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT);rc=proc.wait()
 p=R/'results'/case/'result.json';r=json.loads(p.read_bytes())if p.exists()else{};row=dict(case=case,variant=v,seed=s,returncode=rc,start=start,end=time.time(),complete=r.get('complete'),pass_=r.get('transition_proposed_pass'),screen=r.get('proposed_gate_passed'),xy=r.get('xy_displacement_m'),phases=r.get('phase_metrics'));print(json.dumps(row),flush=True);return row
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
 for offset in range(0,len(jobs),4):
  chunk=list(pool.map(run,jobs[offset:offset+4]));rows.extend(chunk)
  if any(r['returncode']for r in chunk):
   (D/'SOFTWARE_ABORT.json').write_text(json.dumps(dict(rows=rows,remaining_unstarted=jobs[offset+4:]),indent=2),encoding='utf-8');raise RuntimeError('softwareerrorabortunstarted')
summary={v:dict(n_DR=8,complete_DR=sum(r['variant']==v and r['seed']!=0 and bool(r['complete'])for r in rows),pass_DR=sum(r['variant']==v and r['seed']!=0 and bool(r['pass_'])for r in rows))for v in variants};(D/'BATCH_RESULT.json').write_text(json.dumps(dict(kind='R27_PAIRED_SPIN_STOP_TRAIN',summary=summary,rows=rows),indent=2),encoding='utf-8');print('SUMMARY',json.dumps(summary),flush=True)
