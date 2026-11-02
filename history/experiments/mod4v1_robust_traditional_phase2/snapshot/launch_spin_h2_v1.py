"""64freshprospectivepositive4piholdouts. FrozenK20model; noadaptivetuning."""
from pathlib import Path
import json,hashlib,os,sys,subprocess,time,concurrent.futures,math,shutil
R=Path(__file__).resolve().parent;D=R/'batches/r12_spin_H2_64';D.mkdir(parents=True,exist_ok=False);assert shutil.disk_usage(R).free>2*1024**3
with(D/'PREP.log').open('xb')as f:rc=subprocess.run([sys.executable,'-B',str(R/'prepare_spin_h2_v1.py')],cwd=R,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT).returncode
assert rc==0,('H2prep',rc);P=R/'SPIN_H2_K20_V1/PROTOCOL.json';p=json.loads(P.read_bytes());protocolsha=hashlib.sha256(P.read_bytes()).hexdigest();env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
def run(seed):
 for f in p['source']:assert hashlib.sha256((R/f['name']).read_bytes()).hexdigest()==f['SHA'],('frozen_source_changed',f['name'])
 case=f'r12_spin_H2_{seed}';cfg=dict(case_id=case,seed=seed,nominal=False,feedback='sensors',duration_s=p['duration_s'],command_at_s=p['command_at_s'],controller=p['controller'],accel_reference='wheel_midpoint',accel_correction=0,upright_arming_prior=True,mode='spin',yaw_rad_s=p['target_yaw_rad_s'],cohort='prospective_spin_H2_20000to20063');cp=D/(case+'.json');cp.write_text(json.dumps(cfg,indent=2),encoding='utf-8');start=time.time()
 with(D/(case+'.log')).open('xb')as f:proc=subprocess.Popen([sys.executable,'-B',str(R/'run_spin_h2_v1.py'),'--config',str(cp),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT);rc=proc.wait()
 fp=R/'results'/case/'result.json';r=json.loads(fp.read_bytes())if fp.exists()else{};a=dict(case=case,seed=seed,returncode=rc,start=start,end=time.time(),complete=r.get('complete'),pass_=r.get('spin_h2_pass'),D3=r.get('DR',{}).get('D3',{}).get('requested_delay_us'),v_rmse=r.get('tail_v_tracking_RMSE'),w=r.get('tail_yawrate_mean_rad_s'),xy=r.get('xy_displacement_m'),peak_xy=r.get('peak_xy_displacement_m'),hold_s=r.get('continuous_yaw_pose_hold_s'),turns=r.get('actual_yaw_turns'),protocol_SHA=r.get('spin_h2_protocol_SHA'));return a
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
 for i,r in enumerate(pool.map(run,p['seeds']),1):
  rows.append(r)
  with(D/'LIVE_RECEIPTS.jsonl').open('a',encoding='utf-8')as f:f.write(json.dumps(r)+'\n')
  if i%8==0 or not r['pass_']:print(json.dumps({'n':i,'total':64,**r}),flush=True)
n=64;k=sum(bool(r['pass_'])for r in rows);z=1.959963984540054;den=1+z*z/n;cent=(k/n+z*z/(2*n))/den;half=z*math.sqrt((k/n*(1-k/n)+z*z/(4*n))/n)/den;summary=dict(n=n,complete=sum(bool(r['complete'])for r in rows),passed=k,wilson95=[cent-half,cent+half],delay0={'n':sum(r['D3']==0 for r in rows),'pass':sum(r['D3']==0 and bool(r['pass_'])for r in rows)},delay10ms={'n':sum(r['D3']==10000 for r in rows),'pass':sum(r['D3']==10000 and bool(r['pass_'])for r in rows)});(D/'BATCH_RESULT.json').write_text(json.dumps(dict(kind='H2_FROZENPOSITIVE4PI_INDEPENDENT_HOLDOUT',protocol_SHA=protocolsha,heldout_tuning=False,summary=summary,rows=rows),indent=2),encoding='utf-8');print('SUMMARY',json.dumps(summary),flush=True)
