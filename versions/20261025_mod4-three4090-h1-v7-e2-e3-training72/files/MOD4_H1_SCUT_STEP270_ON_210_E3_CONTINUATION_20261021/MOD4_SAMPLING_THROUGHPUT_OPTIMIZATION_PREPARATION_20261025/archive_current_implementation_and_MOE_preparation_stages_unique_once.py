"""Record two real preparation stages once; retain failed attempts and binaries' indexes."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;G=W/'polar-rl-train';R=S/'reports'
H=lambda b:hashlib.sha256(b).hexdigest()
def git(*args,input=None):
 p=subprocess.run(['git','-C',str(G),*args],input=input,capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').rstrip('\r\n')
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
sys.path.insert(0,str(T/'H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023'))
from capture_index_ordered_parts_v1 import read_capture_index,write_capture_index
sys.path.insert(0,str(G/'archive_tools'))
from capture_history import redact
import record_experiment as rec
prior_entries={};prior_descriptors=[];seen=set()
def prior(path):
 path=Path(path);key=str(path.resolve())
 if key in seen:return
 seen.add(key);raw=path.read_bytes();obj=read_capture_index(path,G);prior_descriptors.append(dict(path=path.relative_to(G).as_posix(),SHA=H(raw),entries=len(obj.get('entries',[]))))
 for x in obj.get('entries',[]):
  if x.get('path') and x.get('SHA') and x.get('archive'):prior_entries[(str(Path(x['path'])),x['SHA'])]=x
 for k,v in obj.items():
  if k.startswith('previous') and isinstance(v,dict) and v.get('path'):
   p=G/v['path']
   if p.is_file() and p.name.endswith('.json'):prior(p)
 del obj
def committed_blob_check(head,files):
 p=subprocess.Popen(['git','-C',str(G),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 for rel,sha in files.items():
  p.stdin.write((head+':'+rel+'\n').encode());p.stdin.flush();header=p.stdout.readline().split();assert len(header)==3 and header[1]==b'blob';left=int(header[2]);digest=hashlib.sha256()
  while left:
   block=p.stdout.read(min(left,8*1024**2));assert block;digest.update(block);left-=len(block)
  assert p.stdout.read(1)==b'\n' and digest.hexdigest()==sha,rel
 p.stdin.close();assert p.wait()==0
def run_stage(kind,roots,extras,note,title):
 ID={'performance':'mod4-post67-v6a-sampling-acceleration-implementation','t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'}[kind]
 TAG='trial-20261025-'+ID;D=G/('versions/20261025_'+ID)
 assert not git('status','--porcelain') and not git('tag','--list',TAG) and not D.exists()
 base=git('rev-parse','HEAD');tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');old_count=len(tags.splitlines())
 nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'
 note_file=nr/'ACTUAL_UNIQUE_STAGE_GIT_NOTE.md'
 with note_file.open('x',encoding='utf8') as f:f.write(note)
 put(nr/'UNIQUE_STAGE_ARCHIVE_STARTED_ACTUAL.json',dict(epoch=time.time(),id=ID,base_HEAD=base,old_tag_count=old_count,pending_remote_push=True))
 paths=sorted({p for root in roots for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.is_symlink()}|set(extras))
 D.mkdir();files={};entries=[];splits=[];binaries=[];producer={}
 def add(path,data):
  path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('xb') as f:f.write(data)
  files[path.relative_to(G).as_posix()]=H(data)
 # Existing small producer receipts provide binary SHA metadata; never hash raw/PT for Git.
 def walk(x):
  if isinstance(x,dict):
   digest=next((x[k] for k in ('SHA','sha256','SHA256') if isinstance(x.get(k),str) and len(x[k])==64),None)
   if digest:
    for k in ('path','local_path','source_path','original_path'):
     if isinstance(x.get(k),str):producer[str(Path(x[k]))]=digest
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 for p in paths:
  if p.suffix=='.json' and p.stat().st_size<8_000_000:
   try:walk(json.loads(p.read_bytes()))
   except (ValueError,UnicodeError):pass
 manifests={}
 for p in paths:
  st=p.stat();suffix=p.suffix.lower()
  if suffix not in {'.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv','.diff','.patch','.ini','.cfg'}:
   digest=producer.get(str(p));origin='existing_producer_receipt' if digest else None
   for parent in p.parents:
    if not parent.is_relative_to(T):break
    mf=parent/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'
    if mf.is_file():
     if mf not in manifests:manifests[mf]={r['relative']:r for r in json.loads(mf.read_bytes())['files']}
     row=manifests[mf].get(p.relative_to(parent).as_posix())
     if row and row['bytes']==st.st_size:digest=row['SHA'];origin='existing_payload_producer_manifest'
     break
   binaries.append(dict(path=str(p),bytes=st.st_size,SHA=digest,SHA_source=origin,unknown_SHA_if_not_previously_recorded=digest is None,no_content_read_for_Git=True,original_retained=True));continue
  raw=p.read_bytes();digest=H(raw);row=dict(path=str(p),bytes=len(raw),SHA=digest,source_mtime_ns=st.st_mtime_ns,original_retained=True)
  prior_row=prior_entries.get((str(p),digest))
  if prior_row:
   row.update(archive=prior_row['archive'],archive_SHA=prior_row.get('archive_SHA',digest),mode='previous_same_SHA_full_capture_reference');entries.append(row);continue
  text=raw.decode('utf8');clean,count=redact(text);data=clean.encode('utf8');dest=D/'files'/p.relative_to(W)
  if len(data)<=49_000_000:
   add(dest,data);row.update(archive=dest.relative_to(G).as_posix(),archive_SHA=H(data),mode='redacted' if count else 'full',redaction_count=count)
  else:
   parts=[];position=0;reassembled=hashlib.sha256()
   while position<len(data):
    end=min(position+24_000_000,len(data))
    if end<len(data):
     while data[end]&0xc0==0x80:end-=1
    block=data[position:end];block.decode('utf8');part=dest.with_name(dest.name+'.utf8part'+str(len(parts)).zfill(4)+'.txt');add(part,block);parts.append(dict(path=part.relative_to(G).as_posix(),bytes=len(block),SHA=H(block)));reassembled.update(block);position=end
   assert reassembled.hexdigest()==H(data)
   desc=dict(original_path=str(p),original_bytes=len(raw),original_SHA=digest,archived_bytes=len(data),archived_SHA=H(data),ordered_UTF8_parts=parts,full_reassembled_SHA_verified=True,redaction_count=count)
   dest=dest.with_name(dest.name+'.ordered_parts.json');add(dest,json.dumps(desc,ensure_ascii=False,indent=2).encode());splits.append(desc);row.update(archive=dest.relative_to(G).as_posix(),archive_SHA=H(data),mode='full_ordered_UTF8_parts',redaction_count=count)
  assert p.stat().st_size==st.st_size and p.stat().st_mtime_ns==st.st_mtime_ns,p
  entries.append(row)
 index=dict(epoch=time.time(),stage=ID,entries=entries,external_binary_index=binaries,previous_full_captures=prior_descriptors,all_saved_failed_reader_source_and_success_reports_retained=True,no_experiment_PT_raw_GPU_host_or_budget_action_for_Git=True)
 write_capture_index(D/'COMPLETE_FILE_CAPTURE_INDEX.json',index,add,splits,G)
 add(D/'EXTERNAL_BINARY_EXISTING_PRODUCER_SHA_INDEX.json',json.dumps(binaries,ensure_ascii=False,indent=2).encode())
 def recgit(*args):
  if args[:2]==('add','--'):return git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(x.encode() for x in args[2:])+b'\0')
  if args[:2]==('tag','-a'):return git('tag','-a',TAG,'-F',str(note_file))
  if args and args[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*args)
 rec.git=recgit;sys.argv=['record_experiment.py','--id',ID,'--title',title,'--kind','diagnostic','--note-file',str(note_file),'--files',*files,'--validation','Actual source/CPU/remote receipts and failures retained in full; binary content indexed using prior producer hashes, original writer/accounting untouched. No unrun deployment or skill/GPU-fit success claimed.','--push'];rec.main()
 head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==git('rev-parse',TAG) and remote['refs/tags/'+TAG+'^{}']==head
 for line in tags.splitlines():
  a=line.split();assert remote[a[0]]==a[1]
  if len(a)>2:assert remote[a[0]+'^{}']==a[2]
 committed_blob_check(head,files);assert len(git('tag','--list').splitlines())==old_count+1 and not git('status','--porcelain')
 for x in entries:prior_entries[(x['path'],x['SHA'])]=x
 prior_descriptors.append(dict(path=(D/'COMPLETE_FILE_CAPTURE_INDEX.json').relative_to(G).as_posix(),SHA=H((D/'COMPLETE_FILE_CAPTURE_INDEX.json').read_bytes()),entries=len(entries)))
 print(json.dumps(dict(stage=ID,remote_main=head,tag=TAG,tag_object=git('rev-parse',TAG),peeled=head,total_tags=old_count+1,all_old_tag_objects_and_peels_unchanged=True,text_entries=len(entries),new_committed_files=len(files),binary_metadata_entries=len(binaries),all_committed_blobs_verified=True,workingtree_clean=True)),flush=True)
def main():
 assert git('rev-parse','HEAD')=='de5ecf4aa8f193877be32cf2da8e75f5875ee7a5' and len(git('tag','--list').splitlines())==1437 and not git('status','--porcelain')
 prior(G/'versions/20261025_t2z_future_training_feasibility_review/COMPLETE_FILE_CAPTURE_INDEX.json')
 roots=[T/n for n in ['MOD4_MIXED_PRECISION_STEP_THROUGHPUT_AFTER67_20261025','MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025','H1_STEP270_POST67_TIMING_REPAIR_PREPARATION_20261025','H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025','H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V1_RESOURCE_V69_20261025','MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025']]
 extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(68,77)]+[T/'read_current_actual_reward_manager_V6A_source_unused_once.py']
 run_stage('performance',roots,extras,'Post67 precision completion, V6A sagittal tuck correction, and lossless sampling implementation.\n\nM4 both half modes actually completed: BF16 observations are trajectory/reset-confounded, FP16 skipped Adam steps and is not an equivalent speed result. Production stays FP32. V6A68 paired installed/GO/PPO is actual, with unchanged physical/control/success standards. The new H1/E3 speed sources and CPU comparisons are prepared in unused69, not installed. The exact normal-save request failed before SSH210 connection; no request reached either slot. New72 evidence shows E3 independently complete-saved11 updates and exited after controller link loss, terminal handoff false. H1 final and original account settlement remain unknown until210 access returns. No benchmark snapshot promoted, ledger copied, refund, second writer or current runtime hotpatch. All originals and errors retained.\n\nThis current subagent round has finished; subsequent work temporarily uses no subagents unless human reauthorizes.\n','Implement lossless sampling acceleration and preserve V6A68 network-boundary evidence')
 Z=T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025';old=T/'MOD4_T2Z_H1_TRANSFER_PAPER_PREPARATION_20261025'
 run_stage('t2z',[old,Z],[], 'Prepare T2-z migration for the complete MoE plus hybrid RL system on the dual4090 host.\n\nThe former H1-only preparation remains historical. Actual72 pinned source, independent Python3.11 environment, torch/requirements/pipcheck, exact71-file method staging, registry and CPU interface/import tests passed. No model was loaded, no T2-z training or new rollout started, and real RGB data and full-model4090 fit remain unproven. Official pinned weight content remains guarded by complete size/hash checks; direct origin download failed with an actual timeout, public-cache transport attempts and their exact actual results are preserved separately. No unaudited model/data success is claimed.\n\nAll original attempts, schema/path/CPU/network errors, source changes, licenses/unknown checkpoint license and no-subagents-after-this-round constraint retained. The original expert training owner/accounting and unknown peer are untouched.\n','Prepare complete MoE RL T2-z interfaces and isolated dual4090 research environment')
if __name__=='__main__':
 try:main()
 except BaseException:
  put(R/('STAGE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_commit_tag_objects_only_do_not_repeat_record=True));raise
