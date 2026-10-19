"""Append saved same-stage capacity reports, preserving the existing unique trial tags."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib,traceback
B=Path(__file__).resolve().parent;REPO=B.parent/'polar-rl-train';R=B/'reports'
BASE='5dc566764b027eb886ee7fc97de7467eb25a903e'
DEST=REPO/'history/evidence'/B.name/'capacity_recheck_V40B_20261019'
MSG=B/'CAPACITY_RECHECK_V40B_ORDINARY_APPEND_NOTE_UTF8.txt'
H=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):
 p=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8')
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout.strip()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists() and not MSG.exists()
 v=json.loads((R/'collect_pending_seventeenth_capacity_finite_once_RETURNED_ACTUAL.json').read_bytes());assert v['actual_finite_transport_returned'] and not v['ready_for_prepared_deployer_resource_checks'] and v['durable']['free']==25709084672
 assert not (R/'THREE_NEXT_HOUR_DEPLOY_STARTED_ACTUAL.json').exists()
 args=json.loads((B/'AUTOMATION_ACTUAL_SEVENTEENTH_CAPACITY_RECHECK_V40B_V2_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 for k in ('name','kind','prompt','status','rrule'):assert args[k]==actual[k]
 assert actual['status']=='ACTIVE' and actual['target_thread_id']==args['targetThreadId']
 with (R/'AUTOMATION_V40B_V2_CAPACITY_RECHECK_ACTUAL_READBACK_CPU.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),actual_name_prompt_kind_status_rrule_target_exact=True,original_ACTIVE_hourly_target_preserved=True,capacity_reader_actual_return_consumed_and_next_unused_V2_bound=True,seventeenth_no_new_owner_GO_or_charge=True,no_second_monitor_new_GPU_or_account_change=True),f,indent=2)
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
  p=line.split();tags[p[0]]=p[1:]
 assert len(tags)==1405
 prior={}
 for x in json.loads((REPO/'history/evidence'/B.name/'REPORT_CAPTURE_INDEX.json').read_bytes())['entries']:
  if x.get('source_SHA') and x.get('Git_path') and x.get('archived_SHA'):prior[x['source_SHA']]=dict(Git_path=x['Git_path'],archived_SHA=x['archived_SHA'])
 MSG.write_text('Append returned capacity snapshot and V40B same-stage monitor handoff\n\nOne bounded72 capacity reader actually returned: free remains25709084672bytes=23.943450927734375GiB, below the original strict25GiB start guard. No seventeenth owner/GO/PPO/charge, cleanup, model/raw hashing, behavior replay, budget change or new trial tag. Preserve original reader receipt, CPU handoff, app receipt/readback, and one unused next-hour finite reader; existing1405 trial objects/peels unchanged.\n','utf8')
 DEST.mkdir(parents=True);sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 entries=[];files=[];exts={'.py','.ps1','.bat','.md','.txt','.json','.jsonl','.toml','.yml','.yaml'}
 for p in sorted(B.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or not any(p.name.lower().endswith(e) or e+'.' in p.name.lower() for e in exts):continue
  raw=p.read_bytes();sha=H(raw)
  if sha in prior:entries.append(dict(source_path=str(p),bytes=len(raw),source_SHA=sha,capture='existing_complete_Git_SHA_reference',**prior[sha],original_retained=True));continue
  try:value=raw.decode('utf8');enc='utf8'
  except UnicodeDecodeError:value=raw.decode('latin1');enc='latin1'
  clean,n=redact(value);data=clean.encode(enc) if n else raw;q=DEST/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True)
  row=dict(source_path=str(p),bytes=len(raw),source_SHA=sha,redactions=n,reason='Capture-only credential redaction' if n else None,original_retained=True)
  if len(data)>49_000_000:
   parts=[];offset=0;partsdir=q.with_name(q.name+'.complete_parts');partsdir.mkdir();joined=hashlib.sha256()
   while offset<len(data):
    end=min(offset+24_000_000,len(data))
    if end<len(data):end=data.rfind(b'\n',offset,end)+1;assert end>offset
    block=data[offset:end];block.decode(enc);part=partsdir/('part'+str(len(parts)).zfill(3)+'.txt');part.write_bytes(block);joined.update(block);rel=part.relative_to(REPO).as_posix();parts.append(dict(Git_path=rel,bytes=len(block),SHA=H(block)));entries.append(dict(source_path=str(p),capture='ordered_complete_text_part',source_part_offset=offset,bytes=len(block),Git_path=rel,archived_SHA=H(block),source_whole_SHA=sha,original_retained=True));files.append(rel);offset=end
   assert joined.hexdigest()==H(data);q=q.with_name(q.name+'.SPLIT_CAPTURE_INDEX.json');row.update(capture='complete_lossless_ordered_UTF8_parts',ordered_UTF8_parts=parts,archived_whole_SHA=H(data),archived_whole_bytes=len(data));q.write_text(json.dumps(row,indent=2),'utf8')
  else:q.write_bytes(data);row['capture']='complete_credential_redacted' if n else 'complete_exact_bytes'
  rel=q.relative_to(REPO).as_posix();row.update(Git_path=rel,archived_SHA=H(q.read_bytes()));entries.append(row);prior[sha]=dict(Git_path=rel,archived_SHA=row['archived_SHA']);files.append(rel)
 q=DEST/'REPORT_CAPTURE_INDEX.json';q.write_text(json.dumps(dict(epoch=time.time(),entries=entries,deferred=[],ordinary_same_pending_stage_supplement=True,no_new_trial_tag=True,no_binary_artifact_rehash_or_download=True),indent=2),'utf8');files.append(q.relative_to(REPO).as_posix())
 git('add','--',*files);git('commit','-F',str(MSG));git('push','--atomic','origin','HEAD:main')
 head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head
 for ref,objects in tags.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 request=''.join(head+':'+r['Git_path']+'\n' for r in entries).encode();proc=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True);data=proc.stdout;offset=0
 for r in entries:
  end=data.index(b'\n',offset);header=data[offset:end].split();assert header[1]==b'blob';length=int(header[2]);start=end+1;raw=data[start:start+length];assert H(raw)==r['archived_SHA'];offset=start+length+1
 assert len(git('tag','--list').splitlines())==1405
 print(json.dumps(dict(status='REMOTE_VERIFIED',ordinary_supplement_commit=head,total_tags=1405,all1405_existing_objects_peels_exact=True,tracked_text_entries=len(entries),new_text_files=len(files),deferred=[],no_new_GO_or_charge=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/'CAPACITY_RECHECK_V40B_V2_GIT_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),current_HEAD=git('rev-parse','HEAD'),resume_existing_objects_only_if_committed=True),f,indent=2)
  raise
