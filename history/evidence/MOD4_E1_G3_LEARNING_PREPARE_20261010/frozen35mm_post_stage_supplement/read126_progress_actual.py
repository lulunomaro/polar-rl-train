"""Bounded current frozen126 progress, not a new periodic monitor or learning command."""
from pathlib import Path
import hashlib,json,os,sys,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
WIN='D:/MOD4_async_eval/closure_episode_clock2500_v15';JID='clk2500-closure-episode-d3-126-e1-g3-35mm-source32058-manifest-reviewed-fullroute-flat'
secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret;c=connect_eval()
try:
 with c.open_sftp() as f:
  attrs=f.listdir_attr(WIN+'/jobs/'+JID);files=[];tails={}
  for a in attrs:
   row=dict(name=a.filename,bytes=a.st_size,mtime=a.st_mtime)
   if a.filename in ('stdout.log','stderr.log','stdout.txt','stderr.txt','process.json','result.json','error.json'):
    b=f.open(WIN+'/jobs/'+JID+'/'+a.filename).read();row['sha256']=hashlib.sha256(b).hexdigest();tails[a.filename]=b[-16000:].decode('utf8',errors='replace')
   files.append(row)
  try:attention=json.loads(f.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_ATTENTION.json').read())
  except FileNotFoundError:attention=None
  state=json.loads(f.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_STATE.json').read())
  value=dict(epoch=time.time(),trial_id='E1-G3-126-PROGRESS-READER-05',files=files,tail_text=tails,current_attention=attention,current_worker_state=state,read_only=True,no_training_or_canonical_write=True)
  p=R/('G3_126_PROGRESS_'+str(int(value['epoch']))+'.json');assert not p.exists();p.write_bytes(json.dumps(value,indent=2).encode());print(json.dumps(dict(report=str(p),files=files,tails=tails,current_attention=attention),ensure_ascii=True))
finally:c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
