"""Read only: bounded job receipts/log tails and actual main-training identity."""
from pathlib import Path
import sys,json,hashlib,time,base64
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect();w=connect_eval();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';W='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 with c.open_sftp() as f,w.open_sftp() as wf:
  def read(sf,p):
   try:return json.loads(sf.open(p).read())
   except FileNotFoundError:return None
  ids=['clk2500-closure-episode-d3-92-d7-com-reset-performance-sdk']
  if (R/'ROTATION_READER_SDK_PUBLISHED.json').exists():ids.append(json.loads((R/'ROTATION_READER_SDK_PUBLISHED.json').read_text(encoding='utf8'))['job']['job_id'])
  if (R/'DEVICE_ALIGNED_SDK_PUBLISHED.json').exists():ids.append(json.loads((R/'DEVICE_ALIGNED_SDK_PUBLISHED.json').read_text(encoding='utf8'))['job']['job_id'])
  pub=R/'COLLECTION_PUBLISHED.json'
  if pub.exists():ids+=json.loads(pub.read_text(encoding='utf8'))['jobs']
  jobs=[]
  for job in ids:
   folder=R/job;folder.mkdir(exist_ok=True);row=dict(job_id=job)
   for name in ('manifest.json','ACTIVE.json','result.json','complete.json'):
    v=read(wf,W+'/jobs/'+job+'/'+name)
    if v:row[name]=v;(folder/name).write_text(json.dumps(v,indent=2),encoding='utf8')
   if row.get('complete.json'):
    for name in ('probe.json','result.json'):
     try:raw=wf.open(W+'/jobs/'+job+'/'+name).read()
     except FileNotFoundError:
      row[name+'_missing']=True;continue
     try:bridge=f.open(E+'/eval_results/'+job+'/'+name).read()
     except FileNotFoundError:bridge=None
     if bridge is not None:assert bridge==raw
     (folder/name).write_bytes(raw);row[name+'_bridge_byte_exact']=bridge==raw
    if row['complete.json'].get('phase')!='complete':
     raw=wf.open(W+'/jobs/'+job+'/probe.log').read();(folder/'probe.log').write_bytes(raw);row['error_tail']=raw.decode('utf8',errors='replace')[-2000:]
   else:
    try:
     with wf.open(W+'/jobs/'+job+'/probe.log') as log:
      size=log.stat().st_size;log.seek(max(0,size-1800));row['log_tail']=log.read().decode('utf8',errors='replace')
    except FileNotFoundError:pass
   jobs.append(row)
  worker={name:read(wf,W+'/'+name+'.json') for name in ('SDK_PREPARATION_ISOLATION_WORKER_STATE','SDK_PREPARATION_ISOLATION_WORKER_ATTENTION','SDK_PREPARATION_HELD_JOBS')}
  main='/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009'
  state=read(f,main+'/reports/D7_STATE.json');actual=None
  child=(state or {}).get('child')
  if isinstance(child,dict):pid=child.get('pid')
  else:pid=child
  if pid:
   try:
    st=f.open('/proc/'+str(pid)+'/stat').read().decode().rsplit(')',1)[1].split()
    actual=dict(pid=pid,start_ticks=int(st[19]),state=st[0],argv=f.open('/proc/'+str(pid)+'/cmdline').read().decode().split('\0'))
   except FileNotFoundError:pass
  hashes={}
  for name in ('chassis_com_pose_roundtrip_sdk_adapter.py','chassis_pd_training_env.py','explicit_pd_sdk_adapter.py'):
   hashes[name]=hashlib.sha256(f.open(main+'/isaac/mod4/'+name).read()).hexdigest()
  v=dict(epoch=time.time(),jobs=jobs,worker=worker,main_state=state,main_actual=actual,main_source_SHA=hashes,no_mutation=True)
  (R/'CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
  print(json.dumps(dict(epoch=v['epoch'],jobs=[dict(id=r['job_id'],phase=(r.get('complete.json') or {}).get('phase'),active=(r.get('ACTIVE.json') or {}).get('pid'),error_tail=r.get('error_tail') if 'device-' in r['job_id'] else None,log_tail=r.get('log_tail')) for r in jobs],
      current_worker_attention=worker['SDK_PREPARATION_ISOLATION_WORKER_ATTENTION'],main_phase=(state or {}).get('phase'),main_child=actual)))
finally:c.close();w.close()
