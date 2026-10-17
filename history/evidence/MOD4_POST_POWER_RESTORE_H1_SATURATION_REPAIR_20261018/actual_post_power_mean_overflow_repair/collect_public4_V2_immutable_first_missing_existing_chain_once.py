"""One target wait <=600s, then original source metadata; only two missing immutable PTs."""
from pathlib import Path
import json,time,sys,os,getpass,traceback,hashlib
ROOT=Path(__file__).resolve().parent;B=ROOT/'paid_mean_public4_v2';R=B/'reports';sys.path.insert(0,str(B))
from deploy_public4_repair_V2_new_native_then_original_finite1800_once import a,SOURCE,TARGET
META=r'''
from pathlib import Path
import sys,json,time,psutil,subprocess
B=Path(sys.argv[1]);rows={};names=['OWNER_CURRENT.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json','OWNER_IDENTITY.json','NODE_CURRENT.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','GO_PRODUCTION.json','job0/production/STARTUP_H1_SOURCE_ACTUAL.json','job0/production/OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json','job0/production/PPO_POSITIVE_CURRENT.json','job0/production/FINAL.json','job0/production/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','job0/production/LEARN_ORIGINAL_ERROR_BEFORE_SAVE.json']
for name in names:
 p=B/name
 if p.is_file():rows[name]=json.loads(p.read_bytes())
own=[]
for proc in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  v=proc.info
  if any(s.startswith(str(B)+'/') for s in (v['cmdline'] or [])):own.append(v)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),rows=rows,own_processes=own,immutable_first_present=(B/'job0/production/model_update1.pt').is_file(),startup0_present=(B/'job0/production/own_H1_startup0.pt').is_file(),compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_memory','--format=csv,noheader,nounits']).decode(),not_later_rolling_full_model_CPU=True)))
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
def save(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def main():
 save('PUBLIC4_V2_FIRST_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_creation_argv_alive_only_exclusive_all_host_transport=True,target_same_connection_metadata_wait_max600_seconds=True,no_GPU_or_Task_or_budget_mutation=True))
 pw=getpass.getpass('72 mean repair first models readonly (hidden): ');c=None;downloaded=[]
 try:
  c=a.connect72(pw);pw=None;begin=time.monotonic()
  while True:
   target=a.code(c,a.PY,META,TARGET,timeout=60);p=R/'PUBLIC4_V2_FIRST_FINITE_CURRENT_ACTUAL.json';tmp=p.with_suffix('.partial');tmp.write_text(json.dumps(target,indent=2),encoding='utf8');tmp.replace(p)
   errors=any('ORIGINAL_ERROR' in k for k in target['rows'])
   if (target['immutable_first_present'] and target['startup0_present']) or errors or time.monotonic()-begin>=600:break
   time.sleep(min(15,max(0,600-(time.monotonic()-begin))))
  dest=B/'actual_immutable_first';dest.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   for name,kind,exists in [('own_H1_startup0.pt','immutable_startup0',target['startup0_present']),('model_update1.pt','immutable_first',target['immutable_first_present'])]:
    if not exists:continue
    row=a.code(c,a.PY,HASH,TARGET+'/job0/production/'+name,timeout=90);p=dest/name;assert not p.exists();tmp=p.with_suffix('.pt.partial');sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and hashlib.sha256(tmp.read_bytes()).hexdigest()==row['SHA'];tmp.replace(p);row.update(kind=kind,local_path=str(p),twohost_complete_SHA=True);downloaded.append(row)
  finally:sf.close()
 finally:
  pw=None
  if c:c.close();c=None
 try:
  c=a.t.connect();owner=a.code(c,a.t.PY,META,SOURCE,timeout=60);account=a.code(c,a.t.PY,"from pathlib import Path;import json,time;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');print(json.dumps(dict(epoch=time.time(),original_canonical=json.loads(C.read_bytes()),readonly_no_account_write=True)))",timeout=30)
 finally:
  if c:c.close()
 out=dict(epoch=time.time(),target=target,owner=owner,original_account=account,downloaded_models=downloaded,actual_transport_returned=True,only_missing_immutable_PT_collected_no_native_raw_or_later_rolling_hash=True)
 save('PUBLIC4_V2_H1_MISSING_FIRST_PROGRESS_V2_BOUND_COLLECTION_ACTUAL.json',out);print(json.dumps(dict(models=len(downloaded),target_errors=errors,go=owner['rows'].get('OWNER_CURRENT.json',{}).get('go'),loss=target['rows'].get('job0/production/OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json'))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('PUBLIC4_V2_FIRST_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_model_replay=True));raise
