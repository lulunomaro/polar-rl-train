"""Collect closed/new scope report bytes; never launch, signal, replay or account."""
from pathlib import Path
import hashlib,json,os,sys,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOTS=('MOD4_S3_E1_G3_COMMAND_RETENTION_20261010','MOD4_S3_E1_G3_COMMAND_RETENTION_SDK_REVIEWED_20261010','MOD4_S3_E1_G3_COMMAND_RETENTION_ASSIGNMENT_REVIEWED_20261010')
def main():
 secret,_=recover('RM_SSH_PASSWORD');os.environ['RM_SSH_PASSWORD']=secret;c=connect();rows=[]
 try:
  with c.open_sftp() as f:
   for name in ROOTS:
    root='/home/egde/rl_candidates/'+name
    candidates=[root+'/'+n for n in f.listdir(root) if n.endswith(('.log','.error','.json'))]+[root+'/reports/'+n for n in f.listdir(root+'/reports') if n.endswith('.json')]
    for src in candidates:
     b=f.open(src).read();h=H(b);p=D/'remote_evidence'/name/(Path(src).name+'.'+h[:12]);p.parent.mkdir(parents=True,exist_ok=True)
     if p.exists():assert p.read_bytes()==b
     else:p.write_bytes(b)
     rows.append(dict(source=src,bytes=len(b),sha256=h,local_capture=str(p.resolve()),byteexact=True,raw_data_index_only=len(b)>2_000_000))
  p=R/('REMOTE_EVIDENCE_COLLECTED_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),read_only=True,files=rows,no_replay_signal_or_budget_mutation=True),indent=2),encoding='utf8')
  print(json.dumps(dict(report=str(p),byteexact_files=len(rows))))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
