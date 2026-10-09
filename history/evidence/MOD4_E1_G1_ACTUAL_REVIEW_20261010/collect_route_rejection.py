from pathlib import Path
import hashlib,json,os,sys,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
WIN='D:/MOD4_async_eval/closure_episode_clock2500_v15';jid='clk2500-closure-episode-d3-119-e1-g1-fullroute-anchor32053-flat'
secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret;c=connect_eval()
try:
 with c.open_sftp() as f:
  files=[]
  for name in ('probe.json.error.txt','result.json','manifest.json','physics.log'):
   try:raw=f.open(WIN+'/jobs/'+jid+'/'+name).read()
   except FileNotFoundError:continue
   p=R/'rejections'/jid/name;p.parent.mkdir(parents=True,exist_ok=True)
   if p.exists():assert p.read_bytes()==raw
   else:p.write_bytes(raw)
   files.append(dict(path=str(p),source=WIN+'/jobs/'+jid+'/'+name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
   if name=='probe.json.error.txt':print(raw.decode(errors='replace'))
  for name in ('eval_worker_e1_curriculum_interface_review.py','eval_worker_closure2500.py'):
   raw=f.open(WIN+'/'+name).read();p=D/'worker_reference'/name;p.parent.mkdir(exist_ok=True);p.write_bytes(raw)
  (R/'FULL_ROUTE_ACTUAL_REJECTION_FILES.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-FULLROUTE-119-ACTUAL-REJECTION',files=files,original_failed_retained=True,no_GPU_PPO_or_canonical_mutation=True),indent=2),encoding='utf8')
finally:c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
