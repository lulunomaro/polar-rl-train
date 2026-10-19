"""Record this actual authorized serial training stage once; every saved source/report/error included."""
from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,tomllib,traceback
B=Path(__file__).resolve().parent;W=B.parent;REPO=W/'polar-rl-train';R=B/'reports';BASE='4513efec0622757e0aca1585140641ba4b4f7848';ID='automatic-serial-linux-e3-existing-budget-pending-cost';TAG='trial-20261020-'+ID;DEST=REPO/'history/evidence'/B.name/'automatic_serial_actual_20261020';TITLE='Enable explicitly authorized serial E3 continuation within existing budget with full-save and pending-cost gates';NOTE=B/'AUTOMATIC_SERIAL_ACTUAL_ARCHIVE_NOTE_UTF8.txt';MSG=B/'AUTOMATIC_SERIAL_ACTUAL_TAG_UTF8.txt';H=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):
 p=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists();v=json.loads((R/'AUTO_E3_FIRST_WINDOW_GO_PPO_GPU_VERIFIED_OR_PENDING_ACTUAL.json').read_bytes());assert v['automatic_E3_first_actual_learning_verified'];review=json.loads((R/'AUTO_E3_SERIAL_CONTROLLER_AND_DYNAMIC_SOURCE_CPU_ACTUAL.json').read_bytes());deploy=json.loads((R/'AUTO_E3_SERIAL_SUPERVISOR_DEPLOYED_ACTUAL.json').read_bytes());assert review['passed'] and deploy['reviewed_files']==review['reviewed_files'];assert all(H((B/n).read_bytes())==sha for n,sha in review['reviewed_files'].items());args=json.loads((R/'AUTO_E3_FINAL_AUTOMATION_UPDATE_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert all(actual[k]==args[k] for k in ('name','kind','prompt','status','rrule')) and actual['target_thread_id']==args['targetThreadId'];old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
  z=line.split();old[z[0]]=z[1:]
 assert len(old)==1411;note=(B/'STAGE_SUMMARY.md').read_text('utf8')+'\n\nActual first-window learning evidence:\n'+json.dumps(v,indent=2);NOTE.write_text(note,encoding='utf8');MSG.write_text(TITLE+'\n\n'+note,encoding='utf8');DEST.mkdir(parents=True);sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 entries=[];files=[];skipped=[];extensions={'.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv','.bat','.ps1','.xml','.mjcf','.cfg','.h','.cpp','.c','.ini'}
 fixture=json.loads((B/'cpu_factory_probe/windows/hour0001/recovery/THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());producer={str(B/'cpu_factory_probe/windows/hour0001/recovery'/x['relative']):x for x in fixture['files']}
 for f in sorted(B.rglob('*')):
  if not f.is_file() or '__pycache__' in f.parts:continue
  if f.suffix.lower() not in extensions:
   p=producer.get(str(f));skipped.append(dict(path=str(f),bytes=f.stat().st_size,SHA=p['SHA'] if p else None,kind='producer_artifact_index_only' if p else 'unknown_nontext_not_committed',original_retained=True));continue
  raw=f.read_bytes();sha=H(raw)
  try:txt=raw.decode('utf8');enc='utf8'
  except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
  clean,count=redact(txt);data=clean.encode(enc) if count else raw;q=DEST/f.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);row=dict(source_path=str(f),bytes=len(raw),source_SHA=sha,redactions=count,redaction_reason='capture-only credential redaction' if count else None,original_retained=True)
  if len(data)>49_000_000:
   folder=q.with_name(q.name+'.complete_parts');folder.mkdir();parts=[];offset=0;joined=hashlib.sha256()
   while offset<len(data):
    end=min(offset+24_000_000,len(data))
    if end<len(data):end=data.rfind(b'\n',offset,end)+1;assert end>offset
    block=data[offset:end];block.decode(enc);part=folder/('part'+str(len(parts)).zfill(3)+'.txt');part.write_bytes(block);joined.update(block);rel=part.relative_to(REPO).as_posix();parts.append(dict(Git_path=rel,bytes=len(block),SHA=H(block)));entries.append(dict(source_path=str(f),source_whole_SHA=sha,source_part_offset=offset,bytes=len(block),capture='ordered_complete_text_part',Git_path=rel,archived_SHA=H(block)));files.append(rel);offset=end
   assert joined.hexdigest()==H(data);row.update(capture='complete_ordered_UTF8_parts',parts=parts,reassembled_SHA=H(data),reassembled_bytes=len(data));q=q.with_name(q.name+'.SPLIT_CAPTURE_INDEX.json');q.write_text(json.dumps(row,indent=2),encoding='utf8')
  else:q.write_bytes(data);row['capture']='complete_credential_redacted' if count else 'complete_exact_bytes'
  rel=q.relative_to(REPO).as_posix();row.update(Git_path=rel,archived_SHA=H(q.read_bytes()));entries.append(row);files.append(rel)
 index=dict(epoch=time.time(),entries=entries,nontext_producer_indexes=skipped,initial_source=deploy['source'],original_canonical_settled=False,current_first_window_no_future_FINAL_inferred=True,no_training_or_budget_or_cleanup_for_archival=True,deferred=[])
 for name,value in [('REPORT_CAPTURE_INDEX.json',index),('PREEXISTING_TAG_OBJECTS_AND_PEELS.json',old)]:
  q=DEST/name;q.write_text(json.dumps(value,indent=2),encoding='utf8');files.append(q.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment')
 def rg(*a):
  if a[:2]==('tag','-a'):assert a[2]==TAG;return git('tag','-a',TAG,'-F',str(MSG))
  if a and a[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*a)
 rec.git=rg;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Explicit user automatic continuation authority supersedes one-window restriction, no budget increase. Actual first E3 GO and positive PPO, matching UUID compute and worker+serial-parent creation/argv verified. Full original source 2275dbb4 Adam701620, target installed SDK/RSL CPU and original recipe preserved. Actual synthetic owner success/failure/once/auth costs, budget reserve boundary/duplicate runid and pending receipt rejection tests passed; latest-source factory and runtime asset bytes exact, source-directory predeployment fix and original code retained. Only one serial parent/per-window owner, durable O_EXCL reservations, full final wholeCPU/actual exit/cost gates before next window, resource/identity/budget stop. Costs remain pending, original canonical never opened/copied/written; old Windows/unknown reserves separate. All source/reports/original lookup error/app receipts retained, large artifacts producer pathsizeSHA only. All1411 old tag objects and peels preserved. Future handoff success not inferred from first PPO.','--push'];rec.main();head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for ref,objects in old.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 request=''.join(head+':'+x['Git_path']+'\n' for x in entries).encode();z=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True);offset=0
 for row in entries:
  end=z.stdout.index(b'\n',offset);header=z.stdout[offset:end].split();assert header[1]==b'blob';size=int(header[2]);offset=end+1;assert H(z.stdout[offset:offset+size])==row['archived_SHA'];offset+=size+1
 assert len(git('tag','--list').splitlines())==1412;print(json.dumps(dict(status='REMOTE_VERIFIED',commit=head,tag=TAG,tag_object=obj,total_tags=1412,all1411_old_objects_and_peels_exact=True,all_committed_text_blobs_verified=True,text_entries=len(entries),new_files=len(files),deferred=[])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('AUTO_E3_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),current_HEAD=git('rev-parse','HEAD'),resume_existing_objects_only_if_recorded=True),f,indent=2)
  raise
