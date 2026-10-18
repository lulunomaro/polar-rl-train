"""One unique record after actual deployment; never replay training for archival."""
from pathlib import Path
import json,sys,time,hashlib,subprocess,importlib,traceback
B=Path(__file__).resolve().parent;W=B.parent;G=W/'MOD4_SCUT_FUDAN_THIRD_HOUR_20261019';REPO=W/'polar-rl-train'
BASE='3da5b5769c0ec2d0864364c1ab1eba25fbb55479';ID='scut-fudan-fourth-hour-closed-sources-source-phase-feedback';TAG='trial-20261019-'+ID
DEST=REPO/'history/evidence'/B.name;NOTE=B/'ACTUAL_SCUT_FUDAN_REWARD_TRAINING_NOTE_UTF8.txt';MSG=B/'ACTUAL_SCUT_FUDAN_REWARD_TAG_UTF8.txt'
TITLE='Continue three experts from third reward-hour finals and record local takeoff landing without recovery'
def git(*a):
 p=subprocess.run(['git','-C',str(REPO),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists() and not NOTE.exists()
 d=json.loads((B/'reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());learning=json.loads((B/'reports/THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes());f=json.loads((G/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert learning['three_actual_PPO_learning_verified'] and f['passed_all_three_whole_final_models_CPU']
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
  p=line.split();old[p[0]]=p[1:]
 assert len(old)==1388
 prior={}
 for q in (REPO/'history/evidence/MOD4_SCUT_FUDAN_THIRD_HOUR_20261019/REPORT_CAPTURE_INDEX.json',):
  for r in json.loads(q.read_bytes())['entries']:
   sha=r.get('source_SHA') or r.get('sha256');path=r.get('Git_path');archived=r.get('archived_SHA') or r.get('archived_sha256')
   if sha and path and archived:prior[sha]=dict(Git_path=path,archived_SHA=archived)
 note=(B/'STAGE_SUMMARY.md').read_text('utf8')+'\n\nActual prior closure:\n'+json.dumps(f,indent=2)+'\n\nActual new dispatch and learning metadata:\n'+json.dumps(d,indent=2)+json.dumps(learning,indent=2)
 NOTE.write_text(note,'utf8');MSG.write_text(TITLE+'\n\n'+note,'utf8');DEST.mkdir(parents=True)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 entries=[];files=[];text={'.py','.ps1','.bat','.md','.txt','.json','.toml','.yml','.yaml'}
 for root in (G,B):
  for p in sorted(root.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts or p.suffix.lower() not in text:continue
   raw=p.read_bytes();sha=H(raw);known=prior.get(sha)
   if known:entries.append(dict(source_path=str(p),bytes=len(raw),source_SHA=sha,capture='existing_complete_Git_SHA_reference',**known,original_retained=True));continue
   try:value=raw.decode('utf8');enc='utf8'
   except UnicodeDecodeError:value=raw.decode('latin1');enc='latin1'
   clean,n=redact(value);data=clean.encode(enc) if n else raw;q=DEST/root.name/p.relative_to(root);q.parent.mkdir(parents=True,exist_ok=True)
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
 # PT/source hashes come from actual producer and whole-model proofs, never archival rehash.
 index=dict(epoch=time.time(),entries=entries,large_artifacts=dict(previous_final_models={k:x['final'] for k,x in f['experts'].items()},current_sources=json.loads((B/'reports/THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes())['sources']),deferred=[],local_NPZ_producer_index=[x['raw'] for x in json.loads((B/'reports/THIRD_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes())['episodes']])
 q=DEST/'REPORT_CAPTURE_INDEX.json';q.write_text(json.dumps(index,indent=2),'utf8');files.append(q.relative_to(REPO).as_posix());q=DEST/'PREEXISTING_TAG_OBJECTS_AND_PEELS.json';q.write_text(json.dumps(old,indent=2),'utf8');files.append(q.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment')
 def recordgit(*a):
  if a[:2]==('tag','-a'):assert a[2]==TAG;return git('tag','-a',TAG,'-F',str(MSG))
  if a and a[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*a)
 rec.git=recordgit;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Actual full prior finals/cost/out; upstream formula differential and clipping CPU; public4 normal exact; actual loaded new reward recipe and three GO/positive PPO/GPU compute; original physics/accounting retained.','--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for ref,objects in old.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 # Batch-read the committed text blobs, avoiding thousands of shell invocations.
 request=''.join(head+':'+r['Git_path']+'\n' for r in entries).encode();proc=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True);data=proc.stdout;offset=0
 for r in entries:
  end=data.index(b'\n',offset);header=data[offset:end].split();assert header[1]==b'blob';length=int(header[2]);start=end+1;raw=data[start:start+length];assert H(raw)==r['archived_SHA'];offset=start+length+1
 assert len(git('tag','--list').splitlines())==1389
 print(json.dumps(dict(status='REMOTE_VERIFIED',commit=head,tag=TAG,object=obj,total_tags=1389,all1388old_objects_peels_exact=True,tracked_text_entries=len(entries),new_text_files=len(files),deferred=[])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/'reports/SCUT_FUDAN_UNIQUE_GIT_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),current_HEAD=git('rev-parse','HEAD'),resume_existing_objects_only_if_recorded=True),f,indent=2)
  raise
