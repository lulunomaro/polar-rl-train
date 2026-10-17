"""One later bounded read of only missing native/first PTs; reuse complete native0 locally."""
from pathlib import Path
import os,sys,time,json,getpass,traceback
B=Path(__file__).resolve().parent;R=B/'reports';M=B.parent/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';sys.path.insert(0,str(M))
from collect_new_H1_bounded_native_first_and_recovery85_native_only_finite_once import SNAP
from deploy_H1_closed24_target72_new_native_original_handoff_once import a,SOURCE,TARGET
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 old=json.loads((R/'H1_TARGET72_NEW_NATIVE_IMMUTABLE_FIRST_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert old['actual_return_hands_all_transport_back'];models=list(old['downloaded_models']);existing={Path(x['path']).name for x in models};save('H1_TARGET72_MISSING_NATIVE_FIRST_READER_V2_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_all_host_transport=True,source_one_connection_bounded600seconds_then_target_one_connection=True,only_missing_new_PT_no_old_GPU_task_replay=True));pw=getpass.getpass('Host72 only missing H1 native/first after actual handback (hidden): ');c=None;v={};priorphase=None
 try:
  c=a.t.connect();begin=time.monotonic()
  while True:
   owner=a.code(c,a.t.PY,SNAP,SOURCE,'metadata',timeout=60);cur=next((x['value'] for x in owner['files'] if x['path'].endswith('/OWNER_CURRENT.json')),{});row=cur.get('rows',{}).get('h1') or {};v['owner']=owner;last=row.get('latest_save') or {};snap=dict(epoch=time.time(),source_owner=owner,current_slot=row,original_go=cur.get('go',{}).get('h1'),actual_snapshot_not_future_FINAL=True);p=R/'TARGET72_H1_MISSING_NATIVE_FIRST_FINITE_CURRENT_V2_ACTUAL.json';t=p.with_suffix('.json.partial');t.write_text(json.dumps(snap,indent=2));t.replace(p)
   phase=row.get('phase')
   if phase!=priorphase:print(json.dumps(dict(epoch=time.time(),phase=phase,go=cur.get('go',{}).get('h1'),latest=last)),flush=True);priorphase=phase
   if last.get('phase')=='production' and int(last.get('updates',0))>=1 or row.get('original_error') or owner['errors'] or any(x['path'].endswith('/OWNER_EXIT_ACTUAL.json') for x in owner['files']) or time.monotonic()-begin>=600:break
   time.sleep(min(15,max(0,600-(time.monotonic()-begin))))
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None;needle=" for rel,kind in candidates.items():\n  p=B/rel";assert SNAP.count(needle)==1;code=SNAP.replace(needle," for rel,kind in candidates.items():\n  if Path(rel).name in "+repr(existing)+":continue\n  p=B/rel");v['h1']=a.code(c,a.PY,code,TARGET,'collect',timeout=90);sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in v['h1']['models']:
    p=B/'actual_new_native_first_models'/Path(row['path']).name;assert not p.exists();t=p.with_suffix('.pt.partial');assert not t.exists();sf.get(row['path'],str(t));assert t.stat().st_size==row['bytes'] and a.H(t)==row['SHA'];t.replace(p);models.append(dict(row,local_path=str(p),twohost_complete_SHA=True))
  finally:sf.close()
 finally:
  pw=None
  if c:c.close()
 v.update(epoch=time.time(),downloaded_models=models,prior_complete_native0_local_reused_without_remote_hash_or_download=True,actual_return_hands_all_transport_back=True,only_new_missing_native_complete_first_startup0_no_raw_hash=True);save('H1_TARGET72_MISSING_NATIVE_FIRST_COMPLETE_MERGED_BOUND_COLLECTION_V2_ACTUAL.json',v);print(json.dumps(dict(epoch=v['epoch'],models=[dict(kind=x['kind'],SHA=x['SHA']) for x in models],errors=v['h1']['errors'],actual_transport_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('H1_TARGET72_MISSING_NATIVE_FIRST_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_no_blind_GPU_replay=True));raise
