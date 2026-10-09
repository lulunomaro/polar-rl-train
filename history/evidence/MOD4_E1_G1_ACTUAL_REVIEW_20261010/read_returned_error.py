from pathlib import Path
import hashlib,json,os,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/eval_results';jid='clk2500-closure-episode-d3-119-e1-g1-fullroute-anchor32053-flat'
secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
try:
 with c.open_sftp() as f:
  rows=[];root=E+'/'+jid
  names=f.listdir(root)
  for name in names:
   if not(name.endswith('.txt') or name.endswith('.json') or name.endswith('.log')):continue
   raw=f.open(root+'/'+name).read();p=R/'returned_rejection'/name;p.parent.mkdir(exist_ok=True)
   if p.exists():assert p.read_bytes()==raw
   else:p.write_bytes(raw)
   rows.append(dict(source=root+'/'+name,path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
   if 'error' in name:print(raw.decode(errors='replace'))
  (R/'RETURNED_ROUTE_REJECTION.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-119-RETURNED-ERROR-READ',files=rows,read_only=True,preceding_transport_attempt=dict(id='E1-G1-3060-ERROR-READ-01',error='connect_eval TCP TimeoutError before any read or mutation; retried by reading already returned evidence on4090',production_unchanged=True)),indent=2),encoding='utf8')
finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
