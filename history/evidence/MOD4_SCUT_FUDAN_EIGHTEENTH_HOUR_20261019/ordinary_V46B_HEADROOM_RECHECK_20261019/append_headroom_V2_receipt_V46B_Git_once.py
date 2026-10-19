"""Ordinary append of new saved reports only; no new record/tag, GPU or transport."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib,traceback
B=Path(__file__).resolve().parent;REPO=B.parent/'polar-rl-train';BASE='61d55f1bff0957dbf0caf46fd97ac7e65d3739ee'
DEST=REPO/'history/evidence'/B.name/'ordinary_V46B_HEADROOM_RECHECK_20261019';H=lambda raw:hashlib.sha256(raw).hexdigest()
def git(*a):
 p=subprocess.run(['git','-C',str(REPO),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout.strip()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists()
 args=json.loads((B/'AUTOMATION_HEADROOM_V2_RETURN_NEXT_V3_V46B_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 for k in ('name','kind','prompt','status','rrule'):assert actual[k]==args[k],k
 assert actual['target_thread_id']==args['targetThreadId'] and actual['status']=='ACTIVE'
 with (B/'reports/AUTOMATION_V46B_EXACT_APP_READBACK_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),exact_name_kind_prompt_status_rrule_target_readback=True,original_monitor_retained=True,V2_consumed_pending_and_next_V3_unused=True,no_second_monitor_or_GPU_action=True),f,indent=2)
 old={x.split()[0]:x.split()[1:] for x in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines()};assert len(old)==1408
 prior={}
 for index in sorted((REPO/'history/evidence'/B.name).rglob('REPORT_CAPTURE_INDEX.json')):
  for row in json.loads(index.read_bytes())['entries']:
   sha=row.get('source_SHA');path=row.get('Git_path');archived=row.get('archived_SHA')
   if sha and path and archived:prior[sha]=dict(Git_path=path,archived_SHA=archived)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 entries=[];files=[];DEST.mkdir(parents=True);extensions={'.py','.ps1','.bat','.md','.txt','.json','.jsonl','.toml','.yml','.yaml'}
 for p in sorted(B.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or not any(p.name.lower().endswith(e) or e+'.' in p.name.lower() for e in extensions):continue
  raw=p.read_bytes();sha=H(raw);known=prior.get(sha)
  if known:entries.append(dict(source_path=str(p),bytes=len(raw),source_SHA=sha,capture='existing_complete_Git_SHA_reference',**known));continue
  clean,n=redact(raw.decode('utf8'));data=clean.encode('utf8') if n else raw;assert len(data)<49_000_000
  q=DEST/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data);rel=q.relative_to(REPO).as_posix();entries.append(dict(source_path=str(p),bytes=len(raw),source_SHA=sha,Git_path=rel,archived_SHA=H(data),capture='complete_credential_redacted' if n else 'complete_exact_bytes',redactions=n,original_retained=True));files.append(rel)
 assert files
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),base_commit=BASE,entries=entries,same_pending_stage_ordinary_append=True,V2_actual_returned_pending=True,no_new_trial_tag_or_GPU_or_budget_action=True,deferred=[]),indent=2),'utf8');files.append(index.relative_to(REPO).as_posix())
 q=DEST/'PREEXISTING_TAG_OBJECTS_AND_PEELS.json';q.write_text(json.dumps(old,indent=2),'utf8');files.append(q.relative_to(REPO).as_posix());git('add','--',*files);git('commit','-m','Append eighteenth headroom resource receipt and next bounded reader');git('push','origin','HEAD:main')
 head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head
 for ref,objects in old.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 request=''.join(head+':'+r['Git_path']+'\n' for r in entries).encode();result=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True);data=result.stdout;offset=0
 for r in entries:
  end=data.index(b'\n',offset);header=data[offset:end].split();assert header[1]==b'blob';length=int(header[2]);start=end+1;assert H(data[start:start+length])==r['archived_SHA'];offset=start+length+1
 assert len(git('tag','--list').splitlines())==1408 and not git('status','--porcelain')
 print(json.dumps(dict(status='ORDINARY_REMOTE_VERIFIED',commit=head,new_text_files=len(files),all_text_entries=len(entries),total_tags_unchanged=1408,all_old_tag_objects_and_peels_exact=True,no_deferred_saved_reports=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/'reports/HEADROOM_V46B_ORDINARY_GIT_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),do_not_rerun_record_or_tag_resume_existing_objects=True),f,indent=2)
  raise
