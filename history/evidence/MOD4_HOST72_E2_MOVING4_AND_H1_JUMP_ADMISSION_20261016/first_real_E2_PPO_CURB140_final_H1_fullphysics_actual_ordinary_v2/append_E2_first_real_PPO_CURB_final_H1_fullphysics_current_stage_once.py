"""Ordinary supplement to the existing E2/H1 annotated stage; no new trial/tag."""
from pathlib import Path
import hashlib,json,time,traceback,importlib.util,sys
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train';BASE='bc9dbb396978904b820d2e714ac33e6b5edf7556'
OLD=REPO/'history/evidence'/D.name/'E2_signed4_new_expert_H1_jump_admission_actual_v1/REPORT_CAPTURE_INDEX.json'
DEST=REPO/'history/evidence'/D.name/'first_real_E2_PPO_CURB140_final_H1_fullphysics_actual_ordinary_v2'
s=importlib.util.spec_from_file_location('actual_git_helpers',W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/archive_three_gpu_single_PPO_seven_hour_stage_once.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);git=g.git;H=g.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists()
 assert json.loads((R/'E2_FIRST_REAL_MOVING4_PRODUCTION_COMPLETE_MODELS_LOCAL_CPU_VERIFIED.json').read_bytes())
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();old[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(old)==1354,len(old)
 bysha={x['sha256']:x for x in json.loads(OLD.read_bytes())['entries']}
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[];new=0
 for p in sorted(x for x in D.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.name.endswith('.partial'):
   deferred.append(dict(path=str(p.resolve()),bytes=p.stat().st_size,reason='Incomplete transport file; not CPU admitted; preserve actual original and append only after complete.'));continue
  size=p.stat().st_size;h=H(p);row=dict(source_path=str(p.resolve()),bytes=size,sha256=h);prior=bysha.get(h)
  if prior:
   row.update(capture='same_SHA_prior_stage_reference',prior_index=OLD.relative_to(REPO).as_posix())
   if prior.get('Git_path'):
    assert H(REPO/prior['Git_path'])==prior['archived_sha256'];row.update(Git_path=prior['Git_path'],archived_sha256=prior['archived_sha256'])
   else:row.update(original_retained=True)
  elif size>8*1024*1024 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip','.gz','.mp4','.dmp'):
   row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True);new+=1
  else:
   raw=p.read_bytes()
   try:clean,count=redact(raw.decode('utf8'))
   except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   data=clean.encode('utf8') if count else raw;out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rel=out.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=count);new+=1
  rows.append(row)
 idx=DEST/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,ordinary_supplement_to_existing_annotated_stage=True,all_errors_and_failed_prefixes_retained=True,later_results_require_append=True),indent=2),encoding='utf8');files.append(idx.relative_to(REPO).as_posix());assert new>0
 git('add','--',*files);git('commit','-m','Record first real E2 PPO, closed CURB35 final and H1 jump admission measurements with preserved errors');head=git('rev-parse','HEAD');git('push','origin','main');g.n.m.cap.a.gitio.g=git;g.n.m.cap.a.verify(rows,old,head)
 print(json.dumps(dict(commit=head,ordinary_existing_stage_no_new_tag=True,actual_remote_main_all1354_original_tag_objects_peels_and_tracked_SHA_verified=True,captured_sources=len(rows),new_sources=new,deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E2_H1_FIRST_REAL_PPO_H1_CALIBRATION_ORDINARY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),inspect_actual_HEAD_index_before_resume_existing_objects_never_repeat_commit_or_tag=True),f,indent=2)
  raise
