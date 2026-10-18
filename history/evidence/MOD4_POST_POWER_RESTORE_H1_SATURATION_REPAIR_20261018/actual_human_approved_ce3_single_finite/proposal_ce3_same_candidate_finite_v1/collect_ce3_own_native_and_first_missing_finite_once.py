"""One bounded connection for own new native/first, then source read-only handoff."""
from pathlib import Path
import os,sys,json,time,getpass,hashlib,traceback
import deploy_human_approved_ce3_new_native_then_one_finite1800_once as d
B=d.B;R=d.R;a=d.a;SOURCE=d.SOURCE;TARGET=d.TARGET

META=r'''
from pathlib import Path
import sys,json,time,psutil,subprocess,os
B=Path(sys.argv[1]);rows={}
names=['OWNER_IDENTITY.json','OWNER_CURRENT.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json','NODE_IDENTITY.json','NODE_CURRENT.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','NODE_ORIGINAL_ERROR.json','GO_PRODUCTION.json','job0/native/NATIVE180_PRELAUNCH_V2_COMPLETE_ACTUAL.json','job0/native/H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json','job0/native/FINAL.json','job0/production/STARTUP_H1_SOURCE_ACTUAL.json','job0/production/OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json','job0/production/PPO_POSITIVE_CURRENT.json','job0/production/FINAL.json','job0/production/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','job0/production/LEARN_ORIGINAL_ERROR_BEFORE_SAVE.json']
for name in names:
 p=B/name
 if p.is_file():rows[name]=json.loads(p.read_bytes())
errors=[]
for folder in (B,B/'job0/native',B/'job0/production'):
 if folder.is_dir():
  for p in folder.glob('*ORIGINAL_ERROR*.json'):
   errors.append(dict(path=str(p),value=json.loads(p.read_bytes())))
own=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  v=p.info
  if p.pid!=os.getpid() and any(s.startswith(str(B)+'/') for s in v['cmdline'] or []):own.append(v)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),rows=rows,errors=errors,own_processes=own,immutable_first_present=(B/'job0/production/model_update1.pt').is_file(),startup0_present=(B/'job0/production/own_H1_startup0.pt').is_file(),compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_memory','--format=csv,noheader,nounits']).decode())))
'''
HASH=r'''
from pathlib import Path
import sys,json,hashlib,os
p=Path(sys.argv[1]);h=hashlib.sha256()
with p.open('rb') as f:
 a=os.fstat(f.fileno())
 for part in iter(lambda:f.read(4194304),b''):h.update(part)
 b=os.fstat(f.fileno());assert a.st_size==b.st_size and a.st_mtime_ns==b.st_mtime_ns
print(json.dumps(dict(path=str(p),bytes=a.st_size,SHA=h.hexdigest())))
'''

def main():
 dispatch=json.loads((R/'HUMAN_APPROVED_CE3_OWN_NEW_NATIVE_SINGLE_FINITE_CHAIN_DETACHED_ACTUAL.json').read_bytes());assert dispatch['source_SHA']=='ce3c69bbcf56bd6c884681f23f527b9fe9e1884a7b5444ff90d3f7a2e28b2d90'
 d.put('CE3_NATIVE_FIRST_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,target_same_connection_metadata_wait_max900s=True,only_actual_CIM_creation_argv_alive_exclusive_all_transport=True,no_GPU_Task_or_account_write=True))
 pw=getpass.getpass('72 ce3 own native/first readonly (hidden): ');c=None;models=[]
 try:
  c=a.connect72(pw);pw=None;begin=time.monotonic()
  while True:
   target=a.code(c,a.PY,META,TARGET,timeout=60);p=R/'CE3_NATIVE_FIRST_FINITE_CURRENT_ACTUAL.json';tmp=p.with_suffix('.partial');tmp.write_text(json.dumps(target,indent=2),encoding='utf8');tmp.replace(p)
   if (target['immutable_first_present'] and target['startup0_present']) or target['errors'] or time.monotonic()-begin>=900:break
   time.sleep(min(15,max(0,900-(time.monotonic()-begin))))
  dest=B/'actual_own_native_first_models';dest.mkdir();requested=[]
  native=target['rows'].get('job0/native/NATIVE180_PRELAUNCH_V2_COMPLETE_ACTUAL.json')
  if native:
   for key,kind in [('initial','own_native_startup0'),('saved','own_native_complete')]:requested.append(dict(native[key],kind=kind))
  for name,kind,present in [('own_H1_startup0.pt','immutable_startup0',target['startup0_present']),('model_update1.pt','immutable_first',target['immutable_first_present'])]:
   if present:requested.append(dict(a.code(c,a.PY,HASH,TARGET+'/job0/production/'+name,timeout=90),kind=kind))
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   for row in requested:
    p=dest/Path(row['path']).name;assert not p.exists();tmp=p.with_suffix('.pt.partial');sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and hashlib.sha256(tmp.read_bytes()).hexdigest()==row['SHA'];tmp.replace(p);row.update(local_path=str(p),twohost_complete_SHA=True);models.append(row)
  finally:sf.close()
 finally:
  pw=None
  if c:c.close();c=None
 try:
  c=a.t.connect();owner=a.code(c,a.t.PY,META,SOURCE,timeout=60);account=a.code(c,a.t.PY,"from pathlib import Path;import json,time;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');print(json.dumps(dict(epoch=time.time(),original_canonical=json.loads(C.read_bytes()),readonly_no_account_write=True)))",timeout=30)
 finally:
  if c:c.close()
 d.put('CE3_OWN_NATIVE_FIRST_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json',dict(epoch=time.time(),target=target,owner=owner,original_account=account,downloaded_models=models,actual_transport_returned=True,only_own_new_missing_PT_no_old_case_replay_or_raw_hash=True))
 print(json.dumps(dict(downloaded_models=len(models),errors=bool(target['errors']),phase=owner['rows'].get('OWNER_CURRENT.json',{}).get('rows',{}).get('h1',{}).get('phase'),go=owner['rows'].get('OWNER_CURRENT.json',{}).get('go'),pending_first=not target['immutable_first_present'])),flush=True)

if __name__=='__main__':
 try:main()
 except BaseException:d.put('CE3_NATIVE_FIRST_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_budget_write=True));raise
