"""Ordinary append of this new actual closed-window audit, complete logs and all saved trials/errors."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';REPO=W/'polar-rl-train';ROOT=REPO/'history/evidence'/B.name/'automatic_serial_actual_20261020';DEST=ROOT/'first_closed_second_learning_V52_20261020';BASE='c8aa60c314fba6a24037adc95239a245d1c0ee38';H=lambda b:hashlib.sha256(b).hexdigest()
def git(*args,input=None):
 p=subprocess.run(['git','-C',str(REPO),*args],input=input,capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').strip()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();cpu=json.loads((R/'AUTO_E3_FIRST_CLOSED_FINAL_WHOLE_MODEL_AND_SECOND_AUTONOMOUS_LEARNING_CPU_ACTUAL.json').read_bytes());assert cpu['passed'] and cpu['second_window_actual_GO_positive_PPO_compute_and_worker_createargv'];receipt=json.loads((R/'collect_auto_E3_new_closed_windows_hourly_V1_once_RETURNED_ACTUAL.json').read_bytes());assert receipt['actual_finite_transport_returned'];old=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(old.splitlines())==1412;prior={}
 for p in [ROOT/'REPORT_CAPTURE_INDEX.json',ROOT/'archive_resume_same_unique_trial/RESUME_REPORT_CAPTURE_INDEX.json',ROOT/'ordinary_git_receipts_20261020/ORDINARY_SUPPLEMENT_CAPTURE_INDEX.json']:
  for row in json.loads(p.read_bytes())['entries']:
   if row.get('source_SHA') and row.get('Git_path') and row.get('archived_SHA'):prior[row['source_SHA']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir();files=[];entries=[];largeparts=[];extensions={'.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv','.bat','.ps1','.xml','.mjcf','.cfg','.h','.cpp','.c','.ini'}
 for f in sorted(B.rglob('*')):
  if not f.is_file() or '__pycache__' in f.parts or f.suffix.lower() not in extensions:continue
  raw=f.read_bytes();sha=H(raw);known=prior.get(sha)
  if known:entries.append(dict(source_path=str(f),source_SHA=sha,bytes=len(raw),capture='existing_complete_Git_SHA_reference',Git_path=known['Git_path'],archived_SHA=known['archived_SHA'],original_retained=True));continue
  try:text=raw.decode('utf8');source_encoding='utf8'
  except UnicodeDecodeError:text=raw.decode('latin1');source_encoding='latin1'
  clean,count=redact(text);data=clean.encode('utf8');q=DEST/f.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);row=dict(source_path=str(f),source_SHA=sha,bytes=len(raw),source_encoding=source_encoding,archive_encoding='utf8',redactions=count,redaction_reason='capture-only credential redaction' if count else None,original_retained=True)
  if len(data)>49_000_000:
   folder=q.with_name(q.name+'.complete_parts');folder.mkdir();parts=[];offset=0;joined=hashlib.sha256()
   while offset<len(data):
    end=min(offset+20_000_000,len(data))
    if end<len(data):
     newline=data.rfind(b'\n',offset,end)
     if newline>=offset:end=newline+1
     else:
      while end>offset and data[end]&0xc0==0x80:end-=1
    assert end>offset;block=data[offset:end];block.decode('utf8');part=folder/('part'+str(len(parts)).zfill(3)+'.txt');part.write_bytes(block);joined.update(block);rel=part.relative_to(REPO).as_posix();parts.append(dict(Git_path=rel,bytes=len(block),SHA=H(block)));entries.append(dict(source_path=str(f),source_whole_SHA=sha,source_part_offset=offset,bytes=len(block),capture='ordered_complete_UTF8_text_part',Git_path=rel,archived_SHA=H(block)));files.append(rel);offset=end
   assert joined.hexdigest()==H(data);row.update(capture='complete_lossless_ordered_UTF8_parts',parts=parts,reassembled_SHA=H(data),reassembled_bytes=len(data));q=q.with_name(q.name+'.SPLIT_CAPTURE_INDEX.json');q.write_text(json.dumps(row,indent=2),encoding='utf8');largeparts.append(dict(source_path=str(f),source_SHA=sha,parts=len(parts),reassembled_SHA=H(data),bytes=len(data)))
  else:q.write_bytes(data);row['capture']='complete_credential_redacted' if count else 'complete_exact_bytes' if source_encoding=='utf8' else 'complete_latin1_to_UTF8_encoding_conversion'
  rel=q.relative_to(REPO).as_posix();row.update(Git_path=rel,archived_SHA=H(q.read_bytes()));entries.append(row);files.append(rel);prior[sha]=row
 index=dict(epoch=time.time(),kind='ordinary_append_same_auto_E3_series_first_closure',entries=entries,complete_split_texts=largeparts,new_model_producer_index=cpu['new_complete_final'],first_closed_pending_cost_seconds=3638.964695453644,original_canonical_settled=False,all_tags_preserved=True,no_new_record_or_training_or_ledger_or_SSH=True,deferred=[]);q=DEST/'V52_COMPLETE_REPORT_CAPTURE_INDEX.json';q.write_text(json.dumps(index,indent=2),encoding='utf8');files.append(q.relative_to(REPO).as_posix());git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(x.encode('utf8') for x in files)+b'\0');git('commit','-m','Audit first automatic E3 full closure and second actual learning; preserve complete logs and pending cost');git('push','origin','HEAD:main');head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags')==old
 for line in old.splitlines():
  a=line.split();assert remote[a[0]]==a[1]
  if len(a)>2:assert remote[a[0]+'^{}']==a[2]
 unique={x['Git_path']:x['archived_SHA'] for x in entries};request=''.join(head+':'+p+'\n' for p in unique).encode();z=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True);offset=0
 for rel,sha in unique.items():
  end=z.stdout.index(b'\n',offset);header=z.stdout[offset:end].split();assert header[1]==b'blob';size=int(header[2]);offset=end+1;assert H(z.stdout[offset:offset+size])==sha;offset+=size+1
 for row in entries:
  if row.get('capture')=='complete_lossless_ordered_UTF8_parts':
   joined=hashlib.sha256();size=0
   for part in row['parts']:
    data=(REPO/part['Git_path']).read_bytes();assert H(data)==part['SHA'];joined.update(data);size+=len(data)
   assert joined.hexdigest()==row['reassembled_SHA'] and size==row['reassembled_bytes']
 assert not git('status','--porcelain');print(json.dumps(dict(status='V52_ORDINARY_REMOTE_VERIFIED',commit=head,total_tags=1412,all1412_tag_objects_and_peels_unchanged=True,text_entries=len(entries),new_Git_files=len(files),complete_large_logs_split=len(largeparts),all_Git_blobs_and_full_text_reassembly_verified=True,new_source_SHA=cpu['new_complete_final']['SHA'],new_model_twohost_CPU_verified=True,actual_second_window_learning=True,canonical_cost_still_pending=True,deferred=[])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('AUTO_E3_V52_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_existing_objects_only=True),f,indent=2)
  raise
