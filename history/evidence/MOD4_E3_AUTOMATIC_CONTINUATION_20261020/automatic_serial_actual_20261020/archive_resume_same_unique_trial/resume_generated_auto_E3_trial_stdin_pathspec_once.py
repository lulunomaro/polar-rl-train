"""Finish the already generated unique trial after git-add CreateProcess206; never rerecord/retrain."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;REPO=W/'polar-rl-train';R=B/'reports';DEST=REPO/'history/evidence'/B.name/'automatic_serial_actual_20261020';ID='20261020-automatic-serial-linux-e3-existing-budget-pending-cost';TAG='trial-'+ID;EXP=REPO/'history/experiments'/(ID+'.json');BASE='4513efec0622757e0aca1585140641ba4b4f7848';H=lambda x:hashlib.sha256(x).hexdigest()
def git(*args,input=None):
 p=subprocess.run(['git','-C',str(REPO),*args],input=input,capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').strip()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('diff','--cached','--name-only') and not git('tag','--list',TAG);original=EXP.read_bytes();record=json.loads(original);index=json.loads((DEST/'REPORT_CAPTURE_INDEX.json').read_bytes());old=json.loads((DEST/'PREEXISTING_TAG_OBJECTS_AND_PEELS.json').read_bytes());assert len(old)==1411 and len(record['source_and_evidence_sha256'])>0;longargs=['git','-C',str(REPO),'add','--',EXP.relative_to(REPO).as_posix(),*record['source_and_evidence_sha256']];length=len(subprocess.list2cmdline(longargs));assert length>32767
 (R/'ORIGINAL_GENERATED_TRIAL_RECORD_BEFORE_GIT_ADD_ERROR.json').write_bytes(original)
 plan=dict(epoch=time.time(),kind='local_git_archive_CreateProcess_error_and_stdin_pathspec_resume',original_failure='FileNotFoundError [WinError 206] at subprocess CreateProcess git add',reconstructed_git_add_command_characters=length,HEAD_unchanged_before_resume=BASE,no_commit_or_tag_created_at_failure=True,unique_record_already_generated_not_rerun=True,fix='same explicit path list supplied via git add --pathspec-from-file=- --pathspec-file-nul stdin',no_GPU_or_training_or_budget_or_host_change=True)
 (R/'GIT_ADD_ORIGINAL_COMMAND_LENGTH_AND_STDIN_RESUME_CPU_ACTUAL.json').write_text(json.dumps(plan,indent=2),encoding='utf8');sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 known={(x['source_path'],x.get('source_SHA')) for x in index['entries'] if 'source_SHA' in x};new=[];extra=[];extensions={'.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv','.bat','.ps1','.xml','.mjcf','.cfg','.h','.cpp','.c','.ini'};resume=DEST/'archive_resume_same_unique_trial';resume.mkdir()
 for f in sorted(B.rglob('*')):
  if not f.is_file() or '__pycache__' in f.parts or f.suffix.lower() not in extensions:continue
  raw=f.read_bytes();sha=H(raw)
  if (str(f),sha) in known:continue
  try:txt=raw.decode('utf8');enc='utf8'
  except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
  clean,count=redact(txt);data=clean.encode(enc) if count else raw;assert len(data)<50_000_000;q=resume/f.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data);rel=q.relative_to(REPO).as_posix();extra.append(rel);new.append(dict(source_path=str(f),source_SHA=sha,bytes=len(raw),Git_path=rel,archived_SHA=H(data),capture='complete_credential_redacted' if count else 'complete_exact_bytes',redactions=count,original_retained=True))
 supplement=resume/'RESUME_REPORT_CAPTURE_INDEX.json';supplement.write_text(json.dumps(dict(epoch=time.time(),original_full_index=str(DEST/'REPORT_CAPTURE_INDEX.json'),entries=new,original_record_retained=True,same_unique_record_finished_not_repeated=True),indent=2),encoding='utf8');extra.append(supplement.relative_to(REPO).as_posix());record['repair_or_experiment_note']+='\n\nArchive-only failure and repair: initial git add process creation raised WinError206 with '+str(length)+' command characters before any commit/tag. The original generated record/helper/trace are retained. Resume supplies the same explicit paths through stdin, finishes this existing unique record once, and does not rerun record_experiment or training.'
 for rel in extra:record['source_and_evidence_sha256'][rel]=H((REPO/rel).read_bytes())
 EXP.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');selected=[EXP.relative_to(REPO).as_posix(),*record['source_and_evidence_sha256']];git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(x.encode('utf8') for x in selected)+b'\0');git('commit','-m',record['title']+'\n\nExperiment: '+TAG+'\nValidation: '+record['validation']);msg=R/'GENERATED_UNIQUE_TRIAL_FINAL_TAG_MESSAGE.txt';msg.write_text(record['title']+'\n\n'+record['repair_or_experiment_note'],encoding='utf8');git('tag','-a',TAG,'-F',str(msg));git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG);head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for ref,objects in old.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 for rel,sha in record['source_and_evidence_sha256'].items():
  p=subprocess.run(['git','-C',str(REPO),'show',head+':'+rel],capture_output=True,check=True);assert H(p.stdout)==sha
 assert len(git('tag','--list').splitlines())==1412;print(json.dumps(dict(status='REMOTE_VERIFIED',commit=head,tag=TAG,tag_object=obj,total_tags=1412,all1411_old_objects_and_peels_exact=True,all_committed_text_blobs_verified=True,files=len(selected),original_record_resumed_not_repeated=True,no_new_training_or_cost_change=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('AUTO_E3_GIT_STDIN_RESUME_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_existing_objects_only=True),f,indent=2)
  raise
