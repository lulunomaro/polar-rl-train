from pathlib import Path
import os,sys,json,time,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect();root='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
try:
 with c.open_sftp() as f:
  raw=f.open(root+'/reports/PLAN_APPROVAL.json').read();v=json.loads(raw)
  report=dict(epoch=time.time(),approval=v,approval_sha256=hashlib.sha256(raw).hexdigest(),central_root_files=f.listdir(root),report_plan_files=[n for n in f.listdir(root+'/reports') if 'PLAN' in n or 'MASTER' in n],read_only=True)
  (R/'PLAN_MASTER_LOCATION_READ.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(approval_keys=list(v),central_root_files=report['central_root_files'],report_plan_files=report['report_plan_files'],path_fields={k:x for k,x in v.items() if 'path' in k or 'plan' in k or 'sha' in k}),ensure_ascii=True))
finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
