"""Ordinary supplement of existing V2 trial, never a second experiment/tag."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train';BASE='b5ff9c40959f021511a61e3f31e5ef3526e77bb1';PRIOR=REPO/'history/evidence'/D.name/'grounded_reward_V2_source_target_CPU_native_started_actual_v1/REPORT_CAPTURE_INDEX.json';DEST=REPO/'history/evidence'/D.name/'postcapture_native_actual_readers_monitor_append_v1'
spec=importlib.util.spec_from_file_location('existing_stage_git_pure_helpers',W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/archive_three_gpu_single_PPO_seven_hour_stage_once.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);git=g.git;H=g.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();old[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(old)==1356 and old['refs/tags/trial-20261016-h1-ground-prelaunch-progress-v2-native-finite-first1800']==('71f1e3142d83a5a6003e8573a210de6deaa0aad0',BASE);bysha={x['sha256']:x for x in json.loads(PRIOR.read_bytes())['entries']};sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[]
 for p in sorted(x for x in D.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.name.endswith('.partial'):deferred.append(dict(path=str(p.resolve()),bytes=p.stat().st_size,reason='Actual incomplete temporary preserved; not credited complete; later supplement'));continue
  if p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip','.gz','.mp4','.dmp') or p.stat().st_size>8*1024*1024:raw=None;size=p.stat().st_size;h=H(p)
  else:raw=p.read_bytes();size=len(raw);h=hashlib.sha256(raw).hexdigest()
  row=dict(source_path=str(p.resolve()),bytes=size,sha256=h);previous=bysha.get(h)
  if previous:
   row.update(capture='same_SHA_previous_stage_reference',prior_index=PRIOR.relative_to(REPO).as_posix(),original_retained=True)
   if previous.get('Git_path'):assert H(REPO/previous['Git_path'])==previous['archived_sha256'];row.update(Git_path=previous['Git_path'],archived_sha256=previous['archived_sha256'])
  elif raw is None:row.update(capture='large_or_binary_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:clean,count=redact(raw.decode('utf8'))
   except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   data=clean.encode('utf8') if count else raw;out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rel=out.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if count else 'complete_single_read_snapshot_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=count)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,ordinary_append_no_new_trial_tag=True,original_source_native_CPU_PPO_and_final_stages_credited_only_by_actual_receipts=True,later_results_costs_errors_receipts_require_further_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix());git('add','--',*files);git('commit','-m','Archive H1 grounded V2 actual admission reader and monitor continuation');head=git('rev-parse','HEAD');git('push','origin','HEAD:main');g.n.m.cap.a.gitio.g=git;g.n.m.cap.a.verify(rows,old,head);print(json.dumps(dict(commit=head,ordinary_no_new_tag=True,actual_remote_main_all1356_original_tag_objects_peels_and_tracked_SHA_verified=True,sources=len(rows),deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:(R/('V2_POSTCAPTURE_ORDINARY_APPEND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),only_actual_existing_objects_recovery_no_repeat_record_tag_commit=True),indent=2),encoding='utf8');raise
