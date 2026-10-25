"""Ordinary completed76 supplement; never call record_experiment or create a tag."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;D=N;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports'
U=T/'H1_STEP270_CLOSED76_SAVED_REPLAY_AFTER_V8_20261026'
F=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V77_20261026'
S=G/'versions/20261026_mod4-three4090-same-v8-qualified75-continuation76'
dest=S/'ordinary_closed76_models_cost_saved_motion'
engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py'
ns={'__name__':'ordinary_capture_utilities_only','__file__':str(engine)}
exec(compile(engine.read_text('utf8'),str(engine),'exec'),ns)
git=ns['git'];H=ns['H'];redact=ns['redact']
assert git('rev-parse','HEAD')=='4da472385d8d1d9b302f2bfc97e6b17be426a343' and not git('status','--porcelain')
tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(tags.splitlines())==1448
assert not dest.exists()
assert json.loads((N/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['passed']
for p in (S/'COMPLETE_FILE_CAPTURE_INDEX.json',):ns['prior'](p)
prior=ns['prior_entries'];files={};entries=[];binaries=[];splits=[];producer={}
roots=[N,U,F]
extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v119.py']
paths=sorted({p for root in roots for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.is_symlink()}|set(extras))
def key(p):return str(Path(p)).casefold()
def walk(x):
 if isinstance(x,dict):
  digest=next((x[k] for k in ('SHA','sha256','SHA256') if isinstance(x.get(k),str) and len(x[k])==64),None)
  if digest:
   for k in ('path','local_path','source_path','original_path'):
    if isinstance(x.get(k),str):producer[key(x[k])]=digest
  for v in x.values():walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
for p in paths:
 if p.suffix=='.json' and p.stat().st_size<8_000_000:
  try:walk(json.loads(p.read_bytes()))
  except (ValueError,UnicodeError):pass
def add(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(data)
 files[p.relative_to(G).as_posix()]=H(data)
text_suffixes={'.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv','.diff','.patch','.ini','.cfg'}
dest.mkdir()
for p in paths:
 st=p.stat()
 if p.suffix.lower() not in text_suffixes:
  digest=producer.get(key(p));binaries.append(dict(path=str(p),bytes=st.st_size,SHA=digest,SHA_source='existing_producer_receipt' if digest else None,unknown_SHA_if_not_previously_recorded=digest is None,no_content_read_for_Git=True,original_retained=True));continue
 raw=p.read_bytes();digest=H(raw);row=dict(path=str(p),bytes=len(raw),SHA=digest,source_mtime_ns=st.st_mtime_ns,original_retained=True)
 old=prior.get((str(p),digest))
 if old:
  row.update(archive=old['archive'],archive_SHA=old.get('archive_SHA',digest),mode='previous_same_SHA_full_capture_reference');entries.append(row);continue
 clean,count=redact(raw.decode('utf8'));data=clean.encode('utf8');out=dest/'files'/p.relative_to(W)
 if len(data)<=49_000_000:
  add(out,data);row.update(archive=out.relative_to(G).as_posix(),archive_SHA=H(data),mode='redacted' if count else 'full',redaction_count=count)
 else:
  parts=[];position=0;assembled=hashlib.sha256()
  while position<len(data):
   end=min(position+24_000_000,len(data))
   if end<len(data):
    while data[end]&0xc0==0x80:end-=1
   block=data[position:end];block.decode('utf8');part=out.with_name(out.name+'.utf8part'+str(len(parts)).zfill(4)+'.txt');add(part,block);parts.append(dict(path=part.relative_to(G).as_posix(),bytes=len(block),SHA=H(block)));assembled.update(block);position=end
  assert assembled.hexdigest()==H(data)
  desc=dict(original_path=str(p),original_bytes=len(raw),original_SHA=digest,archived_bytes=len(data),archived_SHA=H(data),ordered_UTF8_parts=parts,full_reassembled_SHA_verified=True,redaction_count=count)
  out=out.with_name(out.name+'.ordered_parts.json');add(out,json.dumps(desc,ensure_ascii=False,indent=2).encode());splits.append(desc);row.update(archive=out.relative_to(G).as_posix(),archive_SHA=H(data),mode='full_ordered_UTF8_parts',redaction_count=count)
 assert p.stat().st_size==st.st_size and p.stat().st_mtime_ns==st.st_mtime_ns,p
 entries.append(row)
index=dict(epoch=time.time(),kind='ordinary_closed76_three_complete_models_original_cost_and_saved_motion',entries=entries,external_binary_index=binaries,previous_full_captures=ns['prior_descriptors'],all_saved_failed_reader_source_and_success_reports_retained=True,no_new_trial_tag_or_remote_training_account_model_raw_action=True)
ns['write_capture_index'](dest/'ORDINARY_CAPTURE_INDEX.json',index,add,splits,G)
add(dest/'EXTERNAL_BINARY_EXISTING_PRODUCER_SHA_INDEX.json',json.dumps(binaries,ensure_ascii=False,indent=2).encode())
proof=json.loads((N/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
summary={k:dict(updates=v['updates'],Adam=v['Adam'],SHA=v['final']['SHA'],original_cost=v['actual_cost']) for k,v in proof['models'].items()}
note='Complete76 H1/E2/E3 fullstate models passed actual twohost fullSHA and CPU finite/17Adam x20/actor9 including STD/critic8/clock checks. Original single writer settled each actual interval and original children, canonical and locks were actually closed. H1 V8 is a training-only sampled-leg-excess regularizer with the prior near-edge gate unchanged, not automatic skill graduation. Saved-only motion and production speed descriptive reports retain their exact sampling limitations; no frozen/whole-window success or causal speedup is inferred. All errors, CPU/source reports and actual receipts retained. Binary only prior producer path/bytes/SHA, no model/raw/GPU read for Git. Ordinary supplement to already-consumed76 trial; no new tag or record.\n'+json.dumps(dict(models=summary,actual_cost_sumonce=proof['actual_cost_sumonce'],remaining_closed_snapshot=proof['remaining_actual_snapshot']),ensure_ascii=False,indent=2)+'\n'
add(dest/'ACTUAL_RESULT_NOTE.md',note.encode('utf8'))
git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(x.encode() for x in files)+b'\0')
git('commit','-m','Record closed76 full models, original cost and saved motion before V8')
git('push','origin','HEAD:main')
head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
assert remote['refs/heads/main']==head
for line in tags.splitlines():
 x=line.split();assert remote[x[0]]==x[1]
 if len(x)>2:assert remote[x[0]+'^{}']==x[2]
ns['committed_blob_check'](head,files)
assert len(git('tag','--list').splitlines())==1448 and not git('status','--porcelain')
print(json.dumps(dict(remote_main=head,ordinary_text_entries=len(entries),new_files=len(files),binary_metadata_entries=len(binaries),all1448_old_tag_objects_peels_unchanged=True,no_new_trial_or_tag=True,all_committed_blobs_verified=True,workingtree_clean=True)))
