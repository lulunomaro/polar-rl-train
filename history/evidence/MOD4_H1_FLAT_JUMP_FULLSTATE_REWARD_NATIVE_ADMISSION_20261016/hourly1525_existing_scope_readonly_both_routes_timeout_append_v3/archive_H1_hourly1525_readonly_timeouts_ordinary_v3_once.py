"""Ordinary append to the already recorded H1 stage; never records or tags again."""
from pathlib import Path
import sys,time,json,hashlib,importlib.util,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train';BASE='1f11de5f6107c93729701651f3e63fd220d972eb';DEST=REPO/'history/evidence'/D.name/'hourly1525_existing_scope_readonly_both_routes_timeout_append_v3';PRIOR=REPO/'history/evidence'/D.name/'first1800_local_dual_SSH_timeout_last_actual_precheck_handoff_append_v2/REPORT_CAPTURE_INDEX.json'
spec=importlib.util.spec_from_file_location('h1_ordinary_pure_git',W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/archive_three_gpu_single_PPO_seven_hour_stage_once.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);git=g.git;H=g.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();old[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(old)==1355 and old['refs/tags/trial-20261016-h1-full20k-public-request-reward-native-admission']==('61a760191b146e10bbb2b33d0c81560d4e8145f7','c444d829c9c0081a5b6f9dfead5a02569fe71033')
 assert json.loads((R/'H1_COMPLETE_FULL20K_NATIVE_ALL_ROWS_TWOHOST_MODELS_LOCAL_CPU_ADMITTED_ACTUAL.json').read_bytes())['passed'];assert (R/'H1_FIRST1800_ACTUAL_ORIGINAL_OWNER_NODE_DISPATCH.json').exists();bysha={x['sha256']:x for x in json.loads(PRIOR.read_bytes())['entries']};sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[]
 for p in sorted(x for x in D.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.name.endswith('.partial'):deferred.append(dict(path=str(p.resolve()),bytes=p.stat().st_size,reason='Incomplete actual write/transport retained, not credited complete; later append.'));continue
  if p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip','.gz','.mp4','.dmp') or p.stat().st_size>8*1024*1024:size=p.stat().st_size;h=H(p);raw=None
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
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,ordinary_append_no_new_trial_tag=True,local_dual_SSH_route_timeout_current_production_FINAL_canonical_unknown=True,actual_native300_allrow_CPU_and_complete_twohost_models=True,source_first1800_granted_actual_fresh_process_prechecks_not_inferred_production_or_jump_pass=True,all_native_raw_target_SHA_and_CPU_admitted_indexes_retained=True,raw_target_CPU_verified_not_falsely_claimed_local_raw_byte_replay=True,later_current_and_models_cost_final_receipts_need_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix());git('add','--',*files);git('commit','-m','Archive hourly H1 existing-scope read-only dual route timeouts');head=git('rev-parse','HEAD');git('push','origin','HEAD:main');g.n.m.cap.a.gitio.g=git;g.n.m.cap.a.verify(rows,old,head);print(json.dumps(dict(commit=head,ordinary_no_new_tag=True,actual_remote_main_all1355_original_tag_objects_peels_and_tracked_SHA_verified=True,sources=len(rows),deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('H1_HOURLY1525_READONLY_ORDINARY_APPEND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_HEAD_capture_before_continuation_only_existing_objects_no_repeat_commit_record_tag=True),indent=2),encoding='utf8');raise
