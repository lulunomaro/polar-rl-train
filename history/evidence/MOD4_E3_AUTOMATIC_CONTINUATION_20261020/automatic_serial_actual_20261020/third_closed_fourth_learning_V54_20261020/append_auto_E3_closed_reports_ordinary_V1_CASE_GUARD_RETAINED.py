"""Copy to a fresh *_once.py with one local JSON args file; ordinary append, never record/tag/train."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';REPO=W/'polar-rl-train';ROOT=REPO/'history/evidence'/B.name/'automatic_serial_actual_20261020';NAME=Path(__file__).stem;H=lambda x:hashlib.sha256(x).hexdigest()
def git(*args,input=None):
 p=subprocess.run(['git','-C',str(REPO),*args],input=input,capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').strip()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert NAME.endswith('_once') and 'TEMPLATE' not in NAME;argsfile=R/sys.argv[1];assert argsfile.resolve().is_relative_to(R.resolve());cfg=json.loads(argsfile.read_bytes());assert re.fullmatch('[a-z0-9_]{3,90}',cfg['destination']) and re.fullmatch('[a-f0-9]{40}',cfg['base_HEAD']);DEST=ROOT/cfg['destination'];assert git('rev-parse','HEAD')==cfg['base_HEAD'] and not git('status','--porcelain') and not DEST.exists();review_path=R/cfg['review_report'];receipt_path=R/cfg['reader_receipt'];assert review_path.resolve().is_relative_to(R.resolve()) and receipt_path.resolve().is_relative_to(R.resolve());cpu=json.loads(review_path.read_bytes());receipt=json.loads(receipt_path.read_bytes());assert cpu['passed'] and receipt['actual_finite_transport_returned'];put(NAME+'_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,configuration=cfg,no_new_record_tag_training_or_ledger=True));old=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');count=len(old.splitlines());assert count>=1412 and git('rev-parse','trial-20261020-automatic-serial-linux-e3-existing-budget-pending-cost')=='df0f2a6ec4a785ecb4b129e2deabbfd517653e4a';prior={};prior_paths={};indexes=[]
 for p in ROOT.rglob('*CAPTURE_INDEX.json'):
  v=json.loads(p.read_bytes())
  if v.get('entries') and v.get('epoch'):indexes.append((v['epoch'],v))
 for capture_epoch,v in sorted(indexes,key=lambda x:x[0]):
  for row in v['entries']:
   if row.get('source_SHA') and row.get('Git_path') and row.get('archived_SHA'):prior[row['source_SHA']]=row;prior_paths[row['source_path'].casefold()]=dict(row,prior_capture_index_epoch=capture_epoch)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir();files=[];entries=[];split=[];extensions={'.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv','.bat','.ps1','.xml','.mjcf','.cfg','.h','.cpp','.c','.ini'}
 for f in sorted(B.rglob('*')):
  if not f.is_file() or '__pycache__' in f.parts or f.suffix.lower() not in extensions:continue
  stat=f.stat();saved=prior_paths.get(str(f).casefold());same_stat=bool(saved and saved['bytes']==stat.st_size and (saved['source_mtime_ns']==stat.st_mtime_ns if 'source_mtime_ns' in saved else stat.st_mtime<=saved['prior_capture_index_epoch']))
  if same_stat:entries.append(dict(source_path=str(f),source_SHA=saved['source_SHA'],bytes=stat.st_size,source_mtime_ns=stat.st_mtime_ns,capture='existing_complete_Git_immutable_source_path_size_mtime_reference',Git_path=saved['Git_path'],archived_SHA=saved['archived_SHA'],original_retained=True,not_rehashed_for_archival=True));continue
  raw=f.read_bytes();sha=H(raw);known=prior.get(sha)
  if known:entries.append(dict(source_path=str(f),source_SHA=sha,bytes=len(raw),source_mtime_ns=stat.st_mtime_ns,capture='existing_complete_Git_SHA_reference',Git_path=known['Git_path'],archived_SHA=known['archived_SHA'],original_retained=True));continue
  try:text=raw.decode('utf8');encoding='utf8'
  except UnicodeDecodeError:text=raw.decode('latin1');encoding='latin1'
  clean,redactions=redact(text);data=clean.encode('utf8');q=DEST/f.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);row=dict(source_path=str(f),source_SHA=sha,bytes=len(raw),source_mtime_ns=stat.st_mtime_ns,source_encoding=encoding,archive_encoding='utf8',redactions=redactions,redaction_reason='capture-only credential redaction' if redactions else None,original_retained=True)
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
   assert joined.hexdigest()==H(data);row.update(capture='complete_lossless_ordered_UTF8_parts',parts=parts,reassembled_SHA=H(data),reassembled_bytes=len(data));q=q.with_name(q.name+'.SPLIT_CAPTURE_INDEX.json');q.write_text(json.dumps(row,indent=2),encoding='utf8');split.append(dict(source_path=str(f),source_SHA=sha,parts=len(parts),reassembled_SHA=H(data),bytes=len(data)))
  else:q.write_bytes(data);row['capture']='complete_credential_redacted' if redactions else 'complete_exact_bytes' if encoding=='utf8' else 'complete_latin1_to_UTF8_encoding_conversion'
  rel=q.relative_to(REPO).as_posix();row.update(Git_path=rel,archived_SHA=H(q.read_bytes()));entries.append(row);files.append(rel);prior[sha]=row
 index=dict(epoch=time.time(),kind='ordinary_append_same_auto_E3_series',entries=entries,complete_split_texts=split,new_models_producer_indexes=cpu['new_closed_models'],series_completed_pending_seconds=cpu['series_completed_actual_pending_seconds'],original_canonical_settled=False,current_window_actual_learning_verified=cpu['current_window_actual_learning_verified'],all_existing_tags_preserved=True,no_new_record_or_training_or_ledger_or_SSH=True,deferred=[]);q=DEST/'COMPLETE_REPORT_CAPTURE_INDEX.json';q.write_text(json.dumps(index,indent=2),encoding='utf8');files.append(q.relative_to(REPO).as_posix());git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(x.encode('utf8') for x in files)+b'\0');git('commit','-m',cfg['title']);git('push','origin','HEAD:main');head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags')==old
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
 assert not git('status','--porcelain');print(json.dumps(dict(status='ORDINARY_REMOTE_VERIFIED',commit=head,total_tags=count,all_old_tag_objects_and_peels_unchanged=True,text_entries=len(entries),new_Git_files=len(files),complete_large_logs_split=len(split),all_Git_blobs_and_full_text_reassembly_verified=True,new_models=[x['final']['SHA'] for x in cpu['new_closed_models']],current_window_learning=cpu['current_window_actual_learning_verified'],canonical_cost_still_pending=True,deferred=[])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put(NAME+'_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_existing_objects_only=True));raise
