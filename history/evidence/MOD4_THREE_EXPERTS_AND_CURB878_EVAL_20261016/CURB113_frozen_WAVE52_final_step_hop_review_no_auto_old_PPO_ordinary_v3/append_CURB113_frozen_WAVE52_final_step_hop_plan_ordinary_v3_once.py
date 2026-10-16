"""Ordinary append to existing actual stage. Preserve all errors, false and originals."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train';BASE='cf077e803f8d994ab3c5b726d5d33d7e542450d9'
DEST=REPO/'history/evidence'/D.name/'CURB113_frozen_WAVE52_final_step_hop_review_no_auto_old_PPO_ordinary_v3'
s=importlib.util.spec_from_file_location('stage_archive_pure_helpers',D/'archive_three_experts_CURB878_eval_and_wave_reader_repair_stage_once.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);git=g.git;H=g.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists()
 idx=REPO/'history/evidence'/D.name/'CURB113_CPU_prepared_and_human_subject_priority_no_old_auto_retrain_ordinary_v2/REPORT_CAPTURE_INDEX.json'
 prior=json.loads(idx.read_bytes())['entries'];by_path={r['source_path']:r for r in prior};by_sha={r['sha256']:r for r in prior if r.get('Git_path')}
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();old[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(old)==1352
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[]
 for p in sorted(x for x in D.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':raise AssertionError('Incomplete transfer must be explicitly deferred before archiving')
  h=H(p);size=p.stat().st_size;row=dict(source_path=str(p.resolve()),bytes=size,sha256=h);prev=by_path.get(str(p.resolve()))
  if not prev or prev['sha256']!=h or not prev.get('Git_path'):prev=by_sha.get(h)
  if prev and prev.get('Git_path') and prev['sha256']==h:
   assert H(REPO/prev['Git_path'])==prev['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=prev['Git_path'],archived_sha256=prev['archived_sha256'])
  elif size>8*1024*1024 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip','.gz','.mp4','.dmp'):row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   raw=p.read_bytes()
   try:clean,count=redact(raw.decode('utf8'))
   except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   data=clean.encode('utf8') if count else raw;out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rel=out.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=count)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,previous_ordinary_commit=BASE,annotated_stage_commit='5d5e34f8885bcf89b2fc009458dc1b7dc647447d',no_new_tag_or_record=True,all_saved_success_failure_reader_cost_namespace_raw_index_plan_workorder_monitor_included=True,large_originals_retained=True,credentials_excluded=True,later_results_require_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 git('add','--',*files);git('commit','-m','Append CURB113 frozen regression, WAVE52 actual closure and airborne step-hop review plan');head=git('rev-parse','HEAD');git('push','origin','main');g.g.n.m.cap.g=git;g.g.n.m.cap.a.gitio.g=git;g.g.n.m.cap.a.verify(rows,old,head)
 print(json.dumps(dict(commit=head,ordinary_only=True,actual_remote_main_all1352_original_tag_objects_peels_and_tracked_SHA_verified=True,sources=len(rows),new_files=len(files))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('CURB113_WAVE52_STEP_HOP_ORDINARY_V3_APPEND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),continue_existing_objects_not_duplicate_record_tag_commit=True),indent=2),encoding='utf8');raise
