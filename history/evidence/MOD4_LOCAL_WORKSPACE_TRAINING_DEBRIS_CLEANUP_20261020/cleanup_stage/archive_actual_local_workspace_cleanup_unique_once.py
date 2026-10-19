"""Record the explicitly authorized exact local deletion and all retained evidence once."""
from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,traceback,tomllib
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';REPO=W/'polar-rl-train';BASE='d90da2e2039656f51397b12c57e7381380348318'
ID='workspace-obsolete-replay-data-cleanup';TAG='trial-20261020-'+ID;DEST=REPO/'history/evidence'/B.name;TITLE='Free workspace space by exact deletion of obsolete replay arrays and one redundant ZIP'
H=lambda raw:hashlib.sha256(raw).hexdigest()
def git(*a):
 p=subprocess.run(['git','-C',str(REPO),*a],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists()
 plan=json.loads((R/'EXACT_WORKSPACE_OBSOLETE_REPLAY_AND_REDUNDANT_ZIP_CLEANUP_PLAN_ACTUAL.json').read_bytes());actual=json.loads((R/'EXPLICIT_LOCAL_WORKSPACE_CLEANUP_COMPLETE_ACTUAL.json').read_bytes());assert actual['completed_all'] and actual['deleted_files']==173 and actual['deleted_logical_bytes']==34018495442 and actual['all_producer_reports_and_summaries_retained'];assert all(not Path(x['path']).exists() for x in actual['deleted']);assert all(Path(x['path']).is_file() and H(Path(x['path']).read_bytes())==x['SHA'] for x in plan['producer_reports_and_summaries_retained'])
 a=json.loads((B/'AUTOMATION_WORKSPACE_CLEANUP_V49C_ARGS.json').read_bytes());v=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert all(a[k]==v[k] for k in ('name','kind','prompt','status','rrule')) and v['target_thread_id']==a['targetThreadId']
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
  fields=line.split();old[fields[0]]=fields[1:]
 assert len(old)==1409
 tops={Path(x['path']).relative_to(W).parts[0] for x in plan['producer_reports_and_summaries_retained']};prior={}
 for top in tops:
  for idx in (REPO/'history/evidence'/top).rglob('REPORT_CAPTURE_INDEX.json'):
   for row in json.loads(idx.read_bytes()).get('entries',[]):
    sha=row.get('source_SHA') or row.get('sha256');path=row.get('Git_path');arch=row.get('archived_SHA') or row.get('archived_sha256')
    if sha and path and arch:prior[sha]=dict(Git_path=path,archived_SHA=arch)
 summary='''# User-authorized local workspace cleanup, actual2026-10-20

Human requested: “本机存储了大量无用训练残废数据你清理一下，注意只清理工作区的”. Authorization covers this concrete local cleanup only; it does not authorize future automatic deletion or remote changes.

Inventory covered316075 files /102.18333141785115GiB logical within C:/Users/lulu/Desktop/claude/mjcf, without following reparse points. PermissionDenied at rmuc2026_work/unpack_verify_4zomhj13 was retained without permission changes. No remote transport or GPU/training/account/system action occurred.

Deleted exactly172 old frozen replay NPZ files under MOD4 stages dated<=20261018, bound to adjacent COMPLETE_ACTUAL/probe text reports and original producer path/size/SHA. They include historical false and failed skill outcomes; no result was reclassified. All344 complete producer reports/numerical summaries are retained unchanged and captured or referenced in Git. The deleted local arrays cannot be reconstructed from their SHA, and no remote-original survival claim is made.54 candidates without the complete unique binding or protected scope remain.

Deleted exactly one redundant4.22GiB TESTED_MINIMAL_NATIVE311_WHEELHOUSE_20261013.zip after matching177 retained extracted members by path, uncompressed size and ZIP CRC32. The extracted wheelhouse remains. The outer ZIP SHA is explicitly unknown (not rehashed for cleanup); exact member verification is recorded. No partial or complete checkpoint was deleted.

Total173 files /34018495442 bytes=31.68219275958836GiB logical removed. Actual free-space delta and before/after disk values are recorded separately because other filesystem activity can affect the delta. Every absolute target was resolved inside the workspace, all ancestors checked for reparse points, and size/mtime revalidated immediately before exact file unlink. No recursive directory deletion, blanket wildcard deletion, cross-shell deletion composition or workspace-external deletion occurred.

All PT models/source/preupdate,20261019-20 current source/closing helpers, reset-collision banks, runtime/SDK/environments/CAD/terrain, user player, code/text/errors/indexes and entire polar-rl-train Git history were protected.172-array producer SHA indexes and append-only deletion journal record deleted=true. Original raw-retained statements in older reports remain historical and are not overwritten. New automation prefix marks only these exact local artifacts deleted and preserves the singleE3 pending-cost one-window training boundary.

This is a local cleanup stage, not a new training trial or skill qualification. Current E3 is untouched. All new helpers, inventory errors, plan, deletion receipts, reports, exact monitor args/appreceipt/readback and retained producer evidence enter the new unique trial. Earlier1409 annotated objects/peels remain unchanged. No archival model/raw rehash or GPU/Task replay.
'''
 with (B/'STAGE_SUMMARY.md').open('x',encoding='utf8') as f:f.write(summary)
 note=B/'ACTUAL_CLEANUP_NOTE_UTF8.txt';msg=B/'ACTUAL_CLEANUP_TAG_UTF8.txt';note.write_text(summary,encoding='utf8');msg.write_text(TITLE+'\n\n'+summary,encoding='utf8');DEST.mkdir(parents=True);sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 entries=[];files=[];paths=[p for p in sorted(B.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix.lower() in ('.py','.json','.jsonl','.txt','.md','.toml','.ps1')];paths+=sorted(Path(x['path']) for x in plan['producer_reports_and_summaries_retained'])
 for src in paths:
  raw=src.read_bytes();sha=H(raw)
  if sha in prior:entries.append(dict(source_path=str(src),bytes=len(raw),source_SHA=sha,capture='existing_complete_Git_SHA_reference',original_retained=True,**prior[sha]));continue
  value=raw.decode('utf8');clean,n=redact(value);data=clean.encode('utf8') if n else raw;rel=Path('cleanup_stage')/src.relative_to(B) if src.is_relative_to(B) else Path('retained_producer_reports')/src.relative_to(W);q=DEST/rel;q.parent.mkdir(parents=True,exist_ok=True);row=dict(source_path=str(src),bytes=len(raw),source_SHA=sha,redactions=n,original_retained=True)
  if len(data)>49_000_000:
   folder=q.with_name(q.name+'.complete_parts');folder.mkdir();parts=[];offset=0;joined=hashlib.sha256()
   while offset<len(data):
    end=min(offset+24_000_000,len(data))
    if end<len(data):end=data.rfind(b'\n',offset,end)+1;assert end>offset
    block=data[offset:end];block.decode('utf8');part=folder/('part'+str(len(parts)).zfill(3)+'.txt');part.write_bytes(block);joined.update(block);partrel=part.relative_to(REPO).as_posix();parts.append(dict(Git_path=partrel,bytes=len(block),SHA=H(block)));entries.append(dict(source_path=str(src),capture='complete_ordered_UTF8_part',Git_path=partrel,archived_SHA=H(block),source_whole_SHA=sha,source_offset=offset));files.append(partrel);offset=end
   assert joined.hexdigest()==H(data);row.update(capture='complete_lossless_ordered_UTF8_parts',parts=parts,reassembled_SHA=H(data));q=q.with_name(q.name+'.SPLIT_CAPTURE_INDEX.json');q.write_text(json.dumps(row,indent=2),encoding='utf8')
  else:q.write_bytes(data);row['capture']='complete_redacted' if n else 'complete_exact_bytes'
  gitpath=q.relative_to(REPO).as_posix();row.update(Git_path=gitpath,archived_SHA=H(q.read_bytes()));entries.append(row);files.append(gitpath);prior[sha]=dict(Git_path=gitpath,archived_SHA=row['archived_SHA'])
 for name,value in [('REPORT_CAPTURE_INDEX.json',dict(epoch=time.time(),entries=entries,deferred=[],large_artifacts=dict(deleted=plan['selected'],state='explicit_user_authorized_deleted_local_only',no_raw_binary_committed=True,remote_original_state_unknown=True),original_reports_and_false_classification_unchanged=True)),('PREEXISTING_TAG_OBJECTS_AND_PEELS.json',old)]:
  q=DEST/name;q.write_text(json.dumps(value,indent=2),encoding='utf8');files.append(q.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment')
 def rg(*a):
  if a[:2]==('tag','-a'):assert a[2]==TAG;return git('tag','-a',TAG,'-F',str(msg))
  if a and a[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*a)
 rec.git=rg;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','repair','--note-file',str(note),'--files',*files,'--validation','Actual explicit workspace-only cleanup:173 exact files deleted,34018495442 logical bytes,172 old closed replay arrays with producer path size SHA and344 unchanged COMPLETE/probe reports, plus1 duplicate ZIP whose177 extracted files verified by size CRC and retained. Absolute resolved workspace scope and no reparse checks; exact file unlink only; append-only journal and separate actual free delta; no models checkpoint resetbank runtime player Git history current stages or outside workspace deleted.54 unbound candidates retained; PermissionDenied retained/no permission changes. No remote GPU training task budget system or peer action. All saved inventory plan source original errors deletion reports monitor appreceipt exact readback and producer text evidence captured; binary indexes explicitly deleted, older false classifications not changed, no remote retention or SHA-based recovery claim. All1409 old tag objects and peels preserved.','--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for ref,objects in old.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 request=''.join(head+':'+x['Git_path']+'\n' for x in entries).encode();z=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True);offset=0
 for row in entries:
  end=z.stdout.index(b'\n',offset);header=z.stdout[offset:end].split();assert header[1]==b'blob';size=int(header[2]);offset=end+1;assert H(z.stdout[offset:offset+size])==row['archived_SHA'];offset+=size+1
 assert len(git('tag','--list').splitlines())==1410
 print(json.dumps(dict(status='REMOTE_VERIFIED',commit=head,tag=TAG,tag_object=obj,total_tags=1410,all1409_old_objects_and_peels_exact=True,all_committed_text_entries_verified=len(entries),new_files=len(files),deferred=[])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('LOCAL_CLEANUP_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),current_HEAD=git('rev-parse','HEAD'),resume_existing_objects_if_recorded=True),f,indent=2)
  raise
