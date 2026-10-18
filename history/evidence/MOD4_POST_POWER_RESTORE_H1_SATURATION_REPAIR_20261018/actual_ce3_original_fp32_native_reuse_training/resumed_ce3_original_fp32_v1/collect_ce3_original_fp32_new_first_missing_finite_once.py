"""Bounded single connection; collect only new production startup0/first, no old native."""
from pathlib import Path
import os,sys,time,json,getpass,hashlib,traceback
import deploy_ce3_original_fp32_existing_native_same_segment_once as d
B=d.B;R=d.R;a=d.a
sys.path.insert(0,str(d.E));from collect_ce3_own_native_and_first_missing_finite_once import META,HASH
def main():
 dispatch=json.loads((R/'CE3_ORIGINAL_FP32_SAME_SEGMENT_FINITE_DETACHED_ACTUAL.json').read_bytes());assert dispatch['Adam']==646100
 d.put('CE3_ORIGINAL_FP32_NEW_FIRST_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,exact_CIM_creation_argv_alive_only_exclusive_all_transport=True,max_metadata_wait_seconds=600,same_connection=True,only_new_production_missing_two_PT=True))
 pw=getpass.getpass('72 new ce3 first model collection (hidden): ');c=None;models=[]
 try:
  c=a.connect72(pw);pw=None;begun=time.monotonic()
  while True:
   target=a.code(c,a.PY,META,d.TARGET,timeout=60);p=R/'CE3_ORIGINAL_FP32_CURRENT_ACTUAL.json';tmp=p.with_suffix('.partial');tmp.write_text(json.dumps(target,indent=2),encoding='utf8');tmp.replace(p)
   if (target['immutable_first_present'] and target['startup0_present']) or target['errors'] or time.monotonic()-begun>=600:break
   time.sleep(min(15,max(0,600-(time.monotonic()-begun))))
  requested=[]
  for name,kind,present in [('own_H1_startup0.pt','immutable_startup0',target['startup0_present']),('model_update1.pt','immutable_first',target['immutable_first_present'])]:
   if present:requested.append(dict(a.code(c,a.PY,HASH,d.TARGET+'/job0/production/'+name,timeout=90),kind=kind))
  dest=B/'actual_new_first_models';dest.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in requested:
    p=dest/Path(row['path']).name;assert not p.exists();tmp=p.with_suffix('.pt.partial');sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and hashlib.sha256(tmp.read_bytes()).hexdigest()==row['SHA'];tmp.replace(p);row.update(local_path=str(p),twohost_complete_SHA=True);models.append(row)
  finally:sf.close()
 finally:
  pw=None
  if c:c.close();c=None
 try:
  c=a.t.connect();owner=a.code(c,a.t.PY,META,d.SOURCE,timeout=60);account=a.code(c,a.t.PY,"from pathlib import Path;import json,time;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');print(json.dumps(dict(epoch=time.time(),original_canonical=json.loads(C.read_bytes()),readonly_no_account_write=True)))",timeout=30)
 finally:
  if c:c.close()
 d.put('CE3_ORIGINAL_FP32_NEW_FIRST_BOUND_COLLECTION_ACTUAL.json',dict(epoch=time.time(),target=target,owner=owner,original_account=account,downloaded_models=models,actual_transport_returned=True,no_old_native_PT_raw_hash_or_download=True))
 print(json.dumps(dict(new_models=len(models),errors=bool(target['errors']),phase=owner['rows'].get('OWNER_CURRENT.json',{}).get('rows',{}).get('h1',{}).get('phase'),go=owner['rows'].get('OWNER_CURRENT.json',{}).get('go'),first_present=target['immutable_first_present'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:d.put('CE3_ORIGINAL_FP32_FIRST_COLLECTION_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_native_replay_or_account_write=True));raise
