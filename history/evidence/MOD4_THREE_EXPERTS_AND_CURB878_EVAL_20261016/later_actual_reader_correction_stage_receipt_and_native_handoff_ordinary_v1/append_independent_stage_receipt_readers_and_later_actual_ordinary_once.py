"""Append later actual own reports to the existing trial; no new trial or tag."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train';BASE='5d5e34f8885bcf89b2fc009458dc1b7dc647447d'
DEST=REPO/'history/evidence'/D.name/'later_actual_reader_correction_stage_receipt_and_native_handoff_ordinary_v1'
s=importlib.util.spec_from_file_location('independent_stage_pure_helpers',D/'archive_three_experts_CURB878_eval_and_wave_reader_repair_stage_once.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);git=g.git;H=g.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();prior={x['source_path']:x for x in json.loads((g.DEST/'REPORT_CAPTURE_INDEX.json').read_bytes())['entries']};old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  v=line.split();old[v[0]]=(v[1],v[2] if len(v)>2 else v[1])
 assert len(old)==1352;sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[]
 for p in sorted(x for x in D.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':raise AssertionError('Incomplete actual collection must be explicitly deferred')
  h=H(p);size=p.stat().st_size;row=dict(source_path=str(p.resolve()),bytes=size,sha256=h);pr=prior.get(str(p.resolve()))
  if pr and pr['sha256']==h and pr.get('Git_path'):
   assert H(REPO/pr['Git_path'])==pr['archived_sha256'];row.update(capture='same_SHA_existing_stage_Git_reference',Git_path=pr['Git_path'],archived_sha256=pr['archived_sha256'])
  elif size>8*1024*1024 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip','.gz','.mp4','.dmp'):row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   raw=p.read_bytes()
   try:clean,count=redact(raw.decode('utf8'))
   except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   data=clean.encode('utf8') if count else raw;out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rel=out.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=count)
  rows.append(row)
 p=DEST/'REPORT_CAPTURE_INDEX.json';p.write_text(json.dumps(dict(epoch=time.time(),entries=rows,ordinary_supplement_of_existing_trial=BASE,no_new_tag_or_record=True,all_saved_postcapture_reader_false_repairs_actual_results_monitor_and_receipt_included=True,credentials_excluded=True,large_originals_retained=True,later_results_require_ordinary_supplement=True),indent=2),encoding='utf8');files.append(p.relative_to(REPO).as_posix());git('add','--',*files);git('commit','-m','Append three distinct saved PPO models, two expert finals, exact cost overrun and WAVE handoff');head=git('rev-parse','HEAD');git('push','origin','main');g.g.n.m.cap.g=git;g.g.n.m.cap.a.gitio.g=git;g.g.n.m.cap.a.verify(rows,old,head);print(json.dumps(dict(commit=head,ordinary_supplement=True,actual_remote_main_all1352_originaltags_and_tracked_SHA_verified=True,sources=len(rows),new_files=len(files))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('INDEPENDENT_ORDINARY_APPEND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),continue_existing_objects_not_duplicate_record_tag_commit=True),indent=2),encoding='utf8');raise
