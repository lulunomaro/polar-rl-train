"""Archive all actual attempts and saved reports once; never rerun training for Git."""
from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,tomllib,traceback
B=Path(__file__).resolve().parent;W=B.parent;REPO=W/'polar-rl-train';R=B/'reports'
BASE='d784f3d577e57ba68c93100bcde02ac80f8d9ac7';ID='single-linux-e3-offline-cost-available-gpu-continuation';TAG='trial-20261020-'+ID
DEST=REPO/'history/evidence'/B.name/'single_E3_actual_20261020';NOTE=B/'ACTUAL_SINGLE_E3_ARCHIVE_NOTE_UTF8.txt';MSG=B/'ACTUAL_SINGLE_E3_ARCHIVE_TAG_UTF8.txt';TITLE='Continue available Linux E3 alone with approved bounded pending cost; retain Windows and scheduling refusals'
H=lambda x:hashlib.sha256(x).hexdigest()
def git(*args):
 p=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists()
 learning=json.loads((R/'SINGLE_E3_ACTUAL_GO_PPO_GPU_VERIFIED_OR_PENDING.json').read_bytes());approval=json.loads((R/'SINGLE_E3_EXPLICIT_OFFLINE_COST_APPROVAL_ACTUAL.json').read_bytes());p=json.loads((R/'APPROVED_SINGLE_E3_PAYLOAD_CPU_PREPARED_ACTUAL.json').read_bytes());assert learning['single_E3_actual_learning_verified'] and approval['explicit_offline_cost_approval'] and p['passed'];assert learning['original_canonical_settled'] is False
 args=json.loads((B/'AUTOMATION_SINGLE_E3_ACTUAL_V49_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert all(actual[k]==args[k] for k in ('name','kind','prompt','status','rrule')) and actual['target_thread_id']==args['targetThreadId']
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
  a=line.split();old[a[0]]=a[1:]
 assert len(old)==1408
 prior={}
 for name in ('MOD4_SCUT_FUDAN_EIGHTEENTH_HOUR_20261019','MOD4_SCUT_FUDAN_SEVENTEENTH_HOUR_20261019'):
  for q in (REPO/'history/evidence'/name).rglob('REPORT_CAPTURE_INDEX.json'):
   for row in json.loads(q.read_bytes())['entries']:
    sha=row.get('source_SHA') or row.get('sha256');path=row.get('Git_path');arch=row.get('archived_SHA') or row.get('archived_sha256')
    if sha and path and arch:prior[sha]=dict(Git_path=path,archived_SHA=arch)
 note=(B/'STAGE_SUMMARY.md').read_text('utf8')+'\n\nActual single E3 learning:\n'+json.dumps(learning,indent=2)+'\n\nSpecific approval:\n'+json.dumps(approval,ensure_ascii=False,indent=2);NOTE.write_text(note,encoding='utf8');MSG.write_text(TITLE+'\n\n'+note,encoding='utf8');DEST.mkdir(parents=True)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 entries=[];files=[];extensions={'.py','.ps1','.bat','.md','.txt','.json','.jsonl','.toml','.yaml','.yml'}
 for f in sorted(B.rglob('*')):
  if not f.is_file() or '__pycache__' in f.parts or not any(f.name.lower().endswith(e) or e+'.' in f.name.lower() for e in extensions):continue
  raw=f.read_bytes();sha=H(raw);known=prior.get(sha)
  if known:entries.append(dict(source_path=str(f),bytes=len(raw),source_SHA=sha,capture='existing_complete_Git_SHA_reference',original_retained=True,**known));continue
  try:txt=raw.decode('utf8');enc='utf8'
  except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
  clean,count=redact(txt);data=clean.encode(enc) if count else raw;q=DEST/f.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);row=dict(source_path=str(f),bytes=len(raw),source_SHA=sha,redactions=count,redaction_reason='capture-only credential redaction' if count else None,original_retained=True)
  if len(data)>49_000_000:
   folder=q.with_name(q.name+'.complete_parts');folder.mkdir();parts=[];offset=0;joined=hashlib.sha256()
   while offset<len(data):
    end=min(offset+24_000_000,len(data))
    if end<len(data):end=data.rfind(b'\n',offset,end)+1;assert end>offset
    block=data[offset:end];block.decode(enc);part=folder/('part'+str(len(parts)).zfill(3)+'.txt');part.write_bytes(block);joined.update(block);rel=part.relative_to(REPO).as_posix();parts.append(dict(Git_path=rel,bytes=len(block),SHA=H(block)));entries.append(dict(source_path=str(f),source_whole_SHA=sha,source_part_offset=offset,bytes=len(block),capture='ordered_complete_text_part',Git_path=rel,archived_SHA=H(block)));files.append(rel);offset=end
   assert joined.hexdigest()==H(data);row.update(capture='complete_lossless_ordered_UTF8_parts',parts=parts,reassembled_SHA=H(data),reassembled_bytes=len(data));q=q.with_name(q.name+'.SPLIT_CAPTURE_INDEX.json');q.write_text(json.dumps(row,indent=2),encoding='utf8')
  else:q.write_bytes(data);row['capture']='complete_credential_redacted' if count else 'complete_exact_bytes'
  rel=q.relative_to(REPO).as_posix();row.update(Git_path=rel,archived_SHA=H(q.read_bytes()));entries.append(row);files.append(rel);prior[sha]=dict(Git_path=rel,archived_SHA=row['archived_SHA'])
 prepared=json.loads((R/'TWO_AVAILABLE_SOURCE_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());index=dict(epoch=time.time(),entries=entries,deferred=[],large_artifacts=dict(prepared_original_sources=prepared['sources'],single_E3_prepared_source=dict(path=str(Path(p['payloads']['recovery'])/'job0/source'/p['specs']['recovery']['source_filename']),SHA=p['source_SHA'],bytes=14715349),no_mid_hour_final_or_raw_download_or_archival_rehash=True,no_new_raw_deletion=True,old782_raw_deletion_already_recorded=True),single_E3_source_SHA=p['source_SHA'],original_canonical_settled=False)
 for name,value in [('REPORT_CAPTURE_INDEX.json',index),('PREEXISTING_TAG_OBJECTS_AND_PEELS.json',old)]:
  q=DEST/name;q.write_text(json.dumps(value,indent=2),encoding='utf8');files.append(q.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment')
 def rg(*a):
  if a[:2]==('tag','-a'):assert a[2]==TAG;return git('tag','-a',TAG,'-F',str(MSG))
  if a and a[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*a)
 rec.git=rg;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Actual explicit one-window offline-cost approval; Linux72 E3 GO, positive PPO and exact worker creation argv matching GPU UUID verified. Original production source f4837513 Adam699640 and full recipe retained; node endpoint only changed. CPU actual pending owner tested success/failure/approval/auth/interval cases, original fixture errors retained. No original canonical copy/write/settlement or two-lock claim; durable one-window reservation retained, no auto second hour. Linux210 strict host-key mismatch retained; observed key matches existing separate Windows pin, Windows11 identity and known-path volume readbacks preserved, no host-key overwrite/system/peer/player changes. Earlier two-participant CPU scheduling tests and failed fixture, unused proposals/deployers, all saved source reports handoffs app receipts captured complete or prior exact Git references; large PT source producer indexes only. All1408 old tag objects and peels preserved.','--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for ref,objects in old.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 request=''.join(head+':'+r['Git_path']+'\n' for r in entries).encode();z=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True);offset=0
 for r in entries:
  end=z.stdout.index(b'\n',offset);header=z.stdout[offset:end].split();assert header[1]==b'blob';size=int(header[2]);offset=end+1;assert H(z.stdout[offset:offset+size])==r['archived_SHA'];offset+=size+1
 assert len(git('tag','--list').splitlines())==1409
 print(json.dumps(dict(status='REMOTE_VERIFIED',commit=head,tag=TAG,tag_object=obj,total_tags=1409,all1408_old_objects_and_peels_exact=True,all_committed_text_blobs_verified=True,text_entries=len(entries),new_files=len(files),deferred=[])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SINGLE_E3_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),current_HEAD=git('rev-parse','HEAD'),resume_existing_objects_only_if_recorded=True),f,indent=2)
  raise
