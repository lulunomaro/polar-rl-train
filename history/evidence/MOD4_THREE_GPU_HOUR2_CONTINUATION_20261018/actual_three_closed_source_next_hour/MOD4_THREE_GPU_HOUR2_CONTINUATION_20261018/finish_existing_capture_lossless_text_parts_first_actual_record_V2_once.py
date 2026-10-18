"""Finish unrecorded capture after the 50MB text limit; never rerun the original stage helper."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,importlib,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;T=W/'MOD4_THREE_GPU_REAL_TRAINING_HOUR_COHORT_20261018';REPO=W/'polar-rl-train'
sp=importlib.util.spec_from_file_location('failed_before_record_capture_pure_functions_only',B/'archive_three_closed_source_next_hour_unique_once.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a);H=a.H
def main():
 assert a.rawgit('rev-parse','HEAD')==a.BASE and not a.rawgit('tag','--list',a.TAG) and not a.rawgit('diff','--cached','--name-only') and not (REPO/'history/experiments'/('20261018-'+a.ID+'.json')).exists()
 tags={}
 for line in a.rawgit('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1379;index=a.DEST/'REPORT_CAPTURE_INDEX.json';initial=index.read_bytes();backup=R/'PRE_RECORD_LARGE_TEXT_INITIAL_CAPTURE_INDEX_ACTUAL.json'
 with backup.open('xb') as f:f.write(initial)
 v=json.loads(initial);entries=v['entries'];split=[]
 for row in entries:
  if row.get('Git_path') and row['Git_path'].startswith(a.DEST.relative_to(REPO).as_posix()+'/'):
   p=REPO/row['Git_path']
   if p.stat().st_size>50_000_000:
    raw=p.read_bytes();whole=hashlib.sha256(raw).hexdigest();assert whole==row['archived_sha256'];partdir=p.with_name(p.name+'.complete_parts');assert not partdir.exists();partdir.mkdir();parts=[];offset=0;joined=hashlib.sha256()
    while offset<len(raw):
     end=min(offset+24_000_000,len(raw))
     if end<len(raw):end=raw.rfind(b'\n',offset,end)+1;assert end>offset
     data=raw[offset:end];data.decode('utf8');q=partdir/('part'+str(len(parts)).zfill(3)+'.txt');q.write_bytes(data);joined.update(data);parts.append(dict(Git_path=q.relative_to(REPO).as_posix(),bytes=len(data),SHA=hashlib.sha256(data).hexdigest()));offset=end
    assert joined.hexdigest()==whole and sum(x['bytes'] for x in parts)==len(raw);descriptor=p.with_name(p.name+'.SPLIT_CAPTURE_INDEX.json');descriptor.write_text(json.dumps(dict(source_path=row['source_path'],source_bytes=row['bytes'],source_SHA=row['sha256'],archived_whole_bytes=len(raw),archived_whole_SHA=whole,ordered_UTF8_parts=parts,reassembly='Concatenate the listed parts in order without inserting bytes',whole_capture_reassembly_SHA_verified=True,redaction_count=row.get('redaction_count',0),original_source_report_unchanged=True,reason='record_experiment per-file50MB limit; complete report retained losslessly in Git parts'),indent=2),'utf8');row.update(capture='complete_UTF8_lossless_ordered_parts',Git_path=descriptor.relative_to(REPO).as_posix(),archived_bytes=descriptor.stat().st_size,archived_sha256=H(descriptor),archived_whole_bytes=len(raw),archived_whole_SHA=whole,ordered_UTF8_parts=parts,whole_capture_reassembly_SHA_verified=True);split.append(dict(source_path=row['source_path'],source_bytes=row['bytes'],source_SHA=row['sha256'],parts=len(parts),whole_SHA=whole))
    assert p.resolve().is_relative_to(a.DEST.resolve()) and p.resolve()!=Path(row['source_path']).resolve();p.unlink()
 assert split
 report=dict(epoch=time.time(),original_helper_failed_before_record_commit_tag=True,actual_HEAD_unchanged=a.BASE,actual_trial_record_absent_before_fix=True,original_large_text_error_preserved=True,complete_texts_split_losslessly=split,no_threshold_model_GPU_or_training_change=True,source_reports_unchanged=True,original_failed_capture_index_backup=str(backup))
 with (R/'LARGE_TEXT_50MB_RECORD_LIMIT_LOSSLESS_FULL_TEXT_PARTS_CPU_FIX_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 existing={row['source_path']:row for row in entries};new=0
 for root in (T,B):
  for p in sorted(x for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix.lower() in a.TEXT):
   raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();key=str(p.resolve())
   if key in existing and existing[key]['sha256']==sha:continue
   try:txt=raw.decode('utf8');enc='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
   safe,n=redact(txt);data=safe.encode(enc) if n else raw;assert len(data)<50_000_000;dest=a.DEST/root.name/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);row=dict(source_path=key,bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=dest.relative_to(REPO).as_posix(),archived_bytes=len(data),archived_sha256=H(dest),redaction_count=n,redaction_reason='Capture-only credential redaction; original retained' if n else None,original_retained=True);entries.append(row);existing[key]=row;new+=1
 v.update(epoch=time.time(),entries=entries,complete_large_text_split_fix=split,first_actual_record_after_pre_record_size_rejection=True,additional_texts_after_initial_rejection=new);index.write_text(json.dumps(v,indent=2),'utf8');files=[p.relative_to(REPO).as_posix() for p in a.DEST.rglob('*') if p.is_file()];assert all((REPO/p).stat().st_size<50_000_000 for p in files);rec=importlib.import_module('record_experiment');rec.git=a.git;sys.argv=['record_experiment.py','--id',a.ID,'--title',a.TITLE,'--kind','training','--note-file',str(a.NOTE),'--files',*files,'--validation','All3closedfullmodelsCPU/cost/out; new3GO/positivePPO/compute; originalPPOphysicalaccountAST;53MBcompleteJSONreportlosslessUTF8partsreassemblySHApassed; originalpre-recordsizeerrorretained.','--push'];rec.main();head=a.rawgit('rev-parse','HEAD');obj=a.rawgit('rev-parse',a.TAG);verify=a.stage.u.u.m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;verify.gitio.g=a.rawgit;verify.verify(entries,tags,head,a.TAG,obj)
 for row in entries:
  if row.get('ordered_UTF8_parts'):
   assembled=hashlib.sha256()
   for part in row['ordered_UTF8_parts']:
    raw=(REPO/part['Git_path']).read_bytes();assert len(raw)==part['bytes'] and hashlib.sha256(raw).hexdigest()==part['SHA'];assembled.update(raw)
   assert assembled.hexdigest()==row['archived_whole_SHA']
 assert len(a.rawgit('tag','--list').splitlines())==1380;print(json.dumps(dict(commit=head,tag=a.TAG,object=obj,total_tags1380=True,remote_main_tag_peel_all1379oldtags_tracked_SHA_and_complete_text_parts_verified=True,entries=len(entries),new_texts=v['new_texts']+new,split_complete_reports=split,deferred=v['deferred'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('NEXT_THREE_HOUR_V2_CAPTURE_RECORD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_record_commit_tag_before_any_finish_only_existingobjects_if_recorded=True),f,indent=2)
  raise
