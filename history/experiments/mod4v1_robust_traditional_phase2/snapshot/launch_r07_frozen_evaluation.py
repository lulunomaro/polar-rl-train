"""MPCTRAIN16 then FROZEN normalP25independentHOLDOUT128, max4CPUworkers.
No tuning fromholdout inthisscript. Unusedexclusiveoutputs, immutable sourceguard.
"""
from pathlib import Path
import json,os,sys,subprocess,concurrent.futures,time,hashlib,shutil,math
R=Path(__file__).resolve().parent;D=R/'batches/r07_mpc_train16_normal_holdout128';D.mkdir(parents=True,exist_ok=False);assert shutil.disk_usage(R).free>3*1024**3
with(D/'PROTOCOL_PREP.log').open('xb')as f:rc=subprocess.run([sys.executable,'-B',str(R/'prepare_r07_protocol.py')],cwd=R,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT).returncode
assert rc==0,('protocolprepfailed',rc);P=R/'NORMAL_P25_HOLDOUT_V1/PROTOCOL.json';protocol=json.loads(P.read_bytes());protocol_sha=hashlib.sha256(P.read_bytes()).hexdigest();env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1');basec=dict(yaw_kp=.8,yaw_ki=.5,yaw_integral_limit=15.,yaw_rate_ff=.052)
jobs=[('mpc_train',mode,seed)for seed in range(201,209)for mode in('stand','forward')]+[('normal_holdout',mode,seed)for seed in protocol['seeds']for mode in('stand','forward')];start=time.time();rows=[]
def run(job):
 family,mode,seed=job;case=f'r07_{family}_{mode}_{seed}'
 for item in protocol['source']:assert hashlib.sha256((R/item['name']).read_bytes()).hexdigest()==item['SHA'],('frozenguard',item['name'])
 if family=='normal_holdout':c=protocol['controller'];duration=20. if mode=='stand'else 12.;runner=R/'run_normal_holdout_v1.py';cohort='independentnormalholdout_10000to10063'
 else:c={**basec,'position_leash':1.};duration=8.;runner=R/'run_mpc_ground_v1.py';cohort='MPC_train201to208_not_holdout'
 cfg=dict(case_id=case,seed=seed,nominal=False,feedback='sensors',duration_s=duration,command_at_s=1.,controller=c,accel_reference='wheel_midpoint',upright_arming_prior=True,cohort=cohort,mode=mode)
 if mode=='forward':cfg['forward_m_s']=2.
 cp=D/(case+'.json');cp.write_text(json.dumps(cfg,indent=2),encoding='utf-8');started=time.time()
 with(D/(case+'.log')).open('xb')as f:proc=subprocess.Popen([sys.executable,'-B',str(runner),'--config',str(cp),'--out',str(R/'results'/case)],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT);code=proc.wait()
 rp=R/'results'/case/'result.json';r=json.loads(rp.read_bytes())if rp.exists()else{};row=dict(case=case,family=family,mode=mode,seed=seed,returncode=code,start=started,end=time.time(),complete=r.get('complete'),pass_=r.get('holdout_gate_pass')if family=='normal_holdout'else r.get('proposed_gate_passed'),original_screen=r.get('proposed_gate_passed'),D3=r.get('DR',{}).get('D3',{}).get('requested_delay_us'),v=r.get('tail_velocity_mean_m_s'),v_rmse=r.get('tail_v_tracking_RMSE'),w=r.get('tail_yawrate_mean_rad_s'),xy=r.get('xy_displacement_m'),stop=r.get('stop_reason'),trace=r.get('trace_artifact'),usage=r.get('controller_usage'),protocol_SHA=r.get('holdout_protocol_SHA'));return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
 for i,row in enumerate(pool.map(run,jobs),1):
  rows.append(row)
  with(D/'LIVE_CASE_RECEIPTS.jsonl').open('a',encoding='utf-8')as f:f.write(json.dumps(row)+'\n')
  if i%16==0 or not row['pass_']:print(json.dumps({'progress':i,'total':len(jobs),'case':row['case'],'complete':row['complete'],'pass':row['pass_'],'v_rmse':row['v_rmse'],'xy':row['xy']}),flush=True)
summary={}
for family in('mpc_train','normal_holdout'):
 summary[family]={}
 for mode in('stand','forward'):
  a=[r for r in rows if r['family']==family and r['mode']==mode];n=len(a);k=sum(bool(r['pass_'])for r in a);z=1.959963984540054;den=1+z*z/n;center=(k/n+z*z/(2*n))/den;half=z*math.sqrt((k/n*(1-k/n)+z*z/(4*n))/n)/den;summary[family][mode]={'n':n,'complete':sum(bool(r['complete'])for r in a),'pass':k,'wilson95':[center-half,center+half],'delay0':{'n':sum(r['D3']==0 for r in a),'pass':sum(r['D3']==0 and bool(r['pass_'])for r in a)},'delay10ms':{'n':sum(r['D3']==10000 for r in a),'pass':sum(r['D3']==10000 and bool(r['pass_'])for r in a)}}
(D/'BATCH_RESULT.json').write_text(json.dumps(dict(kind='R07_FROZEN_PROSPECTIVE_EVALUATION',protocol_SHA=protocol_sha,source_frozen=True,holdout_used_for_tuning=False,worker_limit=4,wall_s=time.time()-start,summary=summary,rows=rows),indent=2),encoding='utf-8');print('SUMMARY',json.dumps(summary),flush=True);print('CLOSED',D/'BATCH_RESULT.json',flush=True)
