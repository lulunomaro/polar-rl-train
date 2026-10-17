"""One later read of only still-missing immutable models; reuse all complete native/startup PT locally."""
from pathlib import Path
import os,sys,time,json,getpass,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
from collect_new_H1_bounded_native_first_and_recovery85_native_only_finite_once import a,SOURCE,ROOTS,SNAP,get
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 old=json.loads((R/'H1_NEW_NATIVE_FIRST_AND_RECOVERY85_NATIVE_ONLY_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert old['actual_return_hands_transport_back']
 save('M_MISSING_FIRST_NATIVE_COMPLETE_SINGLE_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_all_transport=True,one_source_then_one_target_no_poll=True,only_missing_new_models_no_old_remote_PT_or_raw_hash=True))
 pw=getpass.getpass('Host72 still-missing source85 native complete only (hidden): ');c=None;v={};models={k:list(x) for k,x in old['downloaded_models'].items()}
 def readcode(key):
  token="[REDACTED]";assert token in SNAP
  allow={'h1':('job0/production/own_H1_startup0.pt','job0/production/model_update1.pt'),'recovery':('job0/native/own_native336.pt',)}[key]
  existing={Path(r['path']).name for r in models[key]};allow=tuple(x for x in allow if Path(x).name not in existing)
  return SNAP.replace(token," for rel,kind in candidates.items():\n  if rel not in "+repr(allow)+":continue\n  p=B/rel")
 try:
  c=a.t.connect();v['owner']=a.code(c,a.t.PY,SNAP,SOURCE,'metadata');v['h1']=a.code(c,a.t.PY,readcode('h1'),ROOTS['h1'],'collect');models['h1']+=get(c,v['h1'],'h1')
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None;v['recovery']=a.code(c,a.PY,readcode('recovery'),ROOTS['recovery'],'collect');models['recovery']+=get(c,v['recovery'],'recovery')
 finally:
  pw=None
  if c:c.close()
 v.update(epoch=time.time(),downloaded_models=models,actual_previous_complete_native_startup_PT_rows_reused_without_remote_hash_or_download=True,actual_return_hands_transport_back=True,only_new_missing_immutable_first_or_native_complete_read=True)
 save('M_MISSING_H1_FIRST_RECOVERY_NATIVE_COMPLETE_MERGED_BOUND_COLLECTION_ACTUAL.json',v)
 print(json.dumps(dict(models={k:[dict(kind=r['kind'],SHA=r['SHA']) for r in rows] for k,rows in models.items()},errors={k:v[k]['errors'] for k in ('h1','recovery')},H1_first_complete_present=v['h1']['first_complete_file_present'],actual_return_transport_handback=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('M_MISSING_IMMUTABLE_SINGLE_READ_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),read_only_no_task_replay_unknown_outcome=True));raise
