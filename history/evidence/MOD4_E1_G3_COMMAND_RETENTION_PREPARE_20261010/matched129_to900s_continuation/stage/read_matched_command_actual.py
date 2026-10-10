"""Read only new source348 actual processes, current receipts and original budget."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
NEW='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010'
def main():
 secret,_=recover('RM_SSH_PASSWORD');os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  code=r'''from pathlib import Path
import json,hashlib,os,time
D=Path(NEW_VALUE);H=lambda b:hashlib.sha256(b).hexdigest();j=lambda p:json.loads(p.read_bytes())
def compact(v):
 if isinstance(v,list):
  if len(v)>128:return dict(large_list_index_only=True,rows=len(v),value_sha256=H(json.dumps(v,separators=(',',':')).encode()),full_original_retained=True)
  return [compact(x) for x in v]
 if isinstance(v,dict):return {k:compact(x) for k,x in v.items()}
 return v
def actual(pid):
 q=Path('/proc')/str(pid)
 if not q.exists():return None
 try:
  s=(q/'stat').read_text().split(') ',1)[1].split();return dict(pid=pid,state=s[0],start_ticks=int(s[19]),cwd=os.readlink(q/'cwd'),argv=(q/'cmdline').read_bytes().decode().split('\0'))
 except OSError:return None
reports={p.name:compact(j(p)) for p in (D/'reports').glob('*.json')};s=reports.get('E1_STATE.json',{});g=reports.get('E1_GUARDIAN_STARTED.json');locators=[s.get('owner'),s.get('child'),g]
native={p.name:dict(path=str(p),bytes=p.stat().st_size,sha256=H(p.read_bytes()),summary=compact(j(p))) for p in D.glob('RETENTION_*.json')}
runs=[]
for folder in ('discard_logs','learning_logs'):
 for p in (D/folder).glob('*'):
  if not p.is_dir():continue
  rows={q.name:compact(j(q)) for q in p.glob('*.json') if q.name in ('latest_complete.json','run_manifest.json','rolling_source_freeze.json','CLOCK_TRAINING_HEALTH.json','RETENTION_COMMAND_ACTUAL.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json')};runs.append(dict(path=str(p),files=rows))
b=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=j(b);a=v['active_segment'];left=v['authorized_training_seconds']-v['charged_training_seconds'];unaccounted=None
logs={p.name:p.read_text(errors='replace')[-8000:] for p in D.glob('*.log')}
errors={str(p):p.read_text(errors='replace') for p in list(D.glob('*.error'))+list((D/'discard_logs').glob('*.error.txt'))+list((D/'learning_logs').glob('*.error.txt'))}
originals=[dict(path=str(p),bytes=p.stat().st_size,sha256=H(p.read_bytes())) for p in D.rglob('retention_prefix_*.npz')]
print(json.dumps(dict(epoch=time.time(),root=str(D),reports=reports,native=native,runs=runs,actual=[actual(x['pid']) if x else None for x in locators],logs=logs,errors=errors,large_trace_originals=originals,canonical=dict(authorized=v['authorized_training_seconds'],remaining_accounted_snapshot=left,remaining_after_actual_unaccounted_tail=left-max(0,time.time()-a['accounted_through_epoch']) if a else left,active=a,own_completed=[x for x in v['completed_segments'] if x['kind'].startswith('S3_E1_retention_') or x['kind'].startswith('S3_E1_e1_G3_command_retention_matched_')]),read_only=True,no_reaccount_or_tail_mutation=True)))
'''.replace('NEW_VALUE',repr(NEW))
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');v=json.loads(b);p=R/('COMMAND_MATCHED_ACTUAL_'+str(int(v['epoch']))+'.json');assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
  print(json.dumps(dict(report=str(p),phase=v['reports'].get('E1_STATE.json',{}).get('phase'),actual=v['actual'],attention=v['reports'].get('E1_ATTENTION.json'),native=list(v['native']),runs=len(v['runs']),active=v['canonical']['active'],completed=len(v['canonical']['own_completed']),errors=v['errors'],log_tails=v['logs'] if v['errors'] or v['reports'].get('E1_ATTENTION.json') else {})))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:(R/('COMMAND_MATCHED_READER_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),read_only=True,no_remote_mutation=True)),encoding='utf8');raise
