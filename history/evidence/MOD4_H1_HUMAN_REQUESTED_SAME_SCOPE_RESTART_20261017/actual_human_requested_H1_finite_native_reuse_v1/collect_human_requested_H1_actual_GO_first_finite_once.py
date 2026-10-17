"""Bounded existing-chain status over one source connection, then only new target PTs."""
from pathlib import Path
import sys,os,time,json,getpass,traceback
B=Path(__file__).resolve().parent;R=B/'reports';M=B.parent/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';sys.path.insert(0,str(M))
from collect_new_H1_bounded_native_first_and_recovery85_native_only_finite_once import SNAP
from deploy_human_requested_H1_new_finite_strict_native_reuse_once import a,SOURCE,TARGET
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert (R/'HUMAN_REQUESTED_H1_STRICT_NATIVE_REUSE_NEW_FINITE_PPO_DETACHED_ACTUAL.json').is_file();save('HUMAN_REQUESTED_H1_FIRST_FINITE_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_all_transport=True,source_connection_bounded300seconds_then_one_target=True,no_GPU_task_or_native_replay=True));pw=getpass.getpass('Host72 human-requested H1 new immutable first only (hidden): ');c=None;v={};models=[]
 try:
  c=a.t.connect();begin=time.monotonic()
  while True:
   owner=a.code(c,a.t.PY,SNAP,SOURCE,'metadata',timeout=60);cur=next((x['value'] for x in owner['files'] if x['path'].endswith('/OWNER_CURRENT.json')),{});row=(cur.get('rows') or {}).get('h1') or {};v['owner']=owner
   snapshot=dict(epoch=time.time(),source_owner=owner,current_slot=row,actual_snapshot_not_future_FINAL_or_PPO_CPU=True);p=R/'HUMAN_REQUESTED_H1_FIRST_FINITE_CURRENT_ACTUAL.json';tmp=p.with_suffix('.json.partial');tmp.write_text(json.dumps(snapshot,indent=2));tmp.replace(p)
   latest=row.get('latest_save') or {};first=latest.get('phase')=='production' and int(latest.get('updates',0))>=1
   if first or row.get('original_error') or owner['errors'] or any(x['path'].endswith('/OWNER_EXIT_ACTUAL.json') for x in owner['files']) or time.monotonic()-begin>=300:break
   time.sleep(min(15,max(0,300-(time.monotonic()-begin))))
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None;v['h1']=a.code(c,a.PY,SNAP,TARGET,'collect',timeout=90);sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in v['h1']['models']:
    p=B/'actual_new_native_first_models'/Path(row['path']).name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();part=p.with_suffix('.pt.partial');assert not part.exists();sf.get(row['path'],str(part));assert part.stat().st_size==row['bytes'] and a.H(part)==row['SHA'];part.replace(p);models.append(dict(row,local_path=str(p),twohost_complete_SHA=True))
  finally:sf.close()
 finally:
  pw=None
  if c:c.close()
 v.update(epoch=time.time(),downloaded_models=models,actual_return_hands_all_transport_back=True,no_old_complete_PT_raw_remote_hash_or_download=True);save('HUMAN_REQUESTED_H1_IMMUTABLE_FIRST_BOUND_COLLECTION_ACTUAL.json',v)
 print(json.dumps(dict(epoch=v['epoch'],models=[dict(kind=x['kind'],SHA=x['SHA']) for x in models],errors=v['h1']['errors'],actual_transport_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('HUMAN_REQUESTED_H1_FIRST_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_actual_no_blind_GPU_replay=True));raise
