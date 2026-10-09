"""Read actual entry, own children, receipts and sole canonical segment."""
from pathlib import Path
import os,sys,json,hashlib,shlex,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G1_REPAIR_20261009'
def main():
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  code="""from pathlib import Path
import json,os,time,hashlib
D=Path(ROOT);j=lambda p:json.loads(p.read_text())
def actual(pid):
 p=Path('/proc')/str(pid)
 if not p.exists():return None
 try:
  s=(p/'stat').read_text().split(') ',1)[1].split();return dict(pid=pid,state=s[0],start_ticks=int(s[19]),cwd=os.readlink(p/'cwd'),argv=(p/'cmdline').read_bytes().decode().split('\\0'))
 except OSError:return None
reports={p.name:j(p) for p in (D/'reports').glob('*.json') if p.name!='E1_PLANNED_BEHAVIOR_PUBLISHED.json'}
state=reports.get('E1_STATE.json',{});owner=state.get('owner');child=state.get('child');guardian=reports.get('E1_GUARDIAN_STARTED.json')
b=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');ledger=j(b)
logs={p.name:p.read_text(errors='replace')[-5000:] for p in D.glob('*.log')}
run_data=[]
for folder in ('discard_logs','learning_logs'):
 for run in (D/folder).glob('*'):
  if not run.is_dir():continue
  row=dict(path=str(run),files={})
  for name in ('run_manifest.json','latest_complete.json','rolling_source_freeze.json','CLOCK_TRAINING_HEALTH.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json'):
   if (run/name).exists():row['files'][name]=j(run/name)
  run_data.append(row)
def compact(v):
 if isinstance(v,list):
  if len(v)>128:return dict(large_list_index_only=True,rows=len(v),json_value_sha256=hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest(),original_report_retained=True)
  return [compact(x) for x in v]
 if isinstance(v,dict):return {k:compact(x) for k,x in v.items()}
 return v
native={p.name:dict(original_report=dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()),summary=compact(j(p))) for p in D.glob('G1_*.json')}
print(json.dumps(dict(epoch=time.time(),root=str(D),reports=reports,actual=dict(owner=actual(owner['pid']) if owner else None,child=actual(child['pid']) if child else None,guardian=actual(guardian['pid']) if guardian else None),logs=logs,native=native,runs=run_data,canonical=dict(sha256=hashlib.sha256(b.read_bytes()).hexdigest(),authorized=ledger['authorized_training_seconds'],charged=ledger['charged_training_seconds'],remaining=ledger['authorized_training_seconds']-ledger['charged_training_seconds'],active_segment=ledger['active_segment'],own_new_segments=[x for x in ledger['completed_segments'] if 'g1_' in x['kind'].lower()]),read_only=True)))
""".replace('ROOT',repr(ROOT))
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace')
  v=json.loads(b);p=R/('G1_ACTUAL_'+str(int(v['epoch']))+'.json');assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
  print(json.dumps(dict(snapshot=str(p),phase=v['reports'].get('E1_STATE.json',{}).get('phase'),actual=v['actual'],attention=v['reports'].get('E1_ATTENTION.json'),native=list(v['native']),run_count=len(v['runs']),remaining=v['canonical']['remaining'])))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
