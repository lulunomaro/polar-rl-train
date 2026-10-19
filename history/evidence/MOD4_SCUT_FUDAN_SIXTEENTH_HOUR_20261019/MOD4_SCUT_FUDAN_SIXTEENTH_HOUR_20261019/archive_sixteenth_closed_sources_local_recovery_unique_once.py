"""One unique record after actual deployment; never replay training for archival."""
from pathlib import Path
import json,sys,time,hashlib,subprocess,importlib,traceback
B=Path(__file__).resolve().parent;W=B.parent;G=W/'MOD4_SCUT_FUDAN_FIFTEENTH_HOUR_20261019';REPO=W/'polar-rl-train'
BASE='69bc89eb3fa71d0d5c09e86b69d72aacb14c5227';ID='scut-fudan-sixteenth-hour-closed-sources-local-recovery-review';TAG='trial-20261019-'+ID
DEST=REPO/'history/evidence'/B.name;NOTE=B/'ACTUAL_SCUT_FUDAN_REWARD_TRAINING_NOTE_UTF8.txt';MSG=B/'ACTUAL_SCUT_FUDAN_REWARD_TAG_UTF8.txt'
TITLE='Continue three experts from fifteenth-hour full finals and retain further delayed local recovery and normal drift'
def git(*a):
 p=subprocess.run(['git','-C',str(REPO),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists() and not NOTE.exists()
 d=json.loads((B/'reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());learning=json.loads((B/'reports/THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes());f=json.loads((G/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert learning['three_actual_PPO_learning_verified'] and f['passed_all_three_whole_final_models_CPU'] and d['owner']['detached_pid']==376288
 import tomllib
 args=json.loads((B/'AUTOMATION_ACTUAL_SIXTEENTH_LOCAL_RECOVERY_V39_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 for key in ('name','kind','prompt','status','rrule'):assert actual[key]==args[key]
 assert actual['target_thread_id']==args['targetThreadId'] and actual['status']=='ACTIVE'
 with (B/'reports/AUTOMATION_V39_SIXTEENTH_ACTUAL_READBACK_CPU.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),actual_name_prompt_kind_status_rrule_target_exact=True,original_ACTIVE_hourly_target_preserved=True,actual_three_learning_and376288_binding=True,current_full_three_closing_and_next_generic_healthy_runtime_H1_sharing_preserved=True,no_second_monitor_or_live_training_change=True),stream,indent=2)
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
  p=line.split();old[p[0]]=p[1:]
 assert len(old)==1403
 prior={}
 for q in (REPO/'history/evidence/MOD4_SCUT_FUDAN_FIFTEENTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json',):
  for r in json.loads(q.read_bytes())['entries']:
   sha=r.get('source_SHA') or r.get('sha256');path=r.get('Git_path');archived=r.get('archived_SHA') or r.get('archived_sha256')
   if sha and path and archived:prior[sha]=dict(Git_path=path,archived_SHA=archived)
 note=(B/'STAGE_SUMMARY.md').read_text('utf8')+'\n\nActual prior closure:\n'+json.dumps(f,indent=2)+'\n\nActual new dispatch and learning metadata:\n'+json.dumps(d,indent=2)+json.dumps(learning,indent=2)
 NOTE.write_text(note,'utf8');MSG.write_text(TITLE+'\n\n'+note,'utf8');DEST.mkdir(parents=True)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 entries=[];files=[];text={'.py','.ps1','.bat','.md','.txt','.json','.jsonl','.toml','.yml','.yaml'}
 for root in (G,B):
  for p in sorted(root.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts or not any(p.name.lower().endswith(ext) or ext+'.' in p.name.lower() for ext in text):continue
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
 index=dict(epoch=time.time(),entries=entries,large_artifacts=dict(previous_final_models={k:x['final'] for k,x in f['experts'].items()},current_sources=json.loads((B/'reports/THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes())['sources']),deferred=[],local_NPZ_producer_index=[x['raw'] for x in json.loads((B/'reports/FIFTEENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes())['episodes']])
 q=DEST/'REPORT_CAPTURE_INDEX.json';q.write_text(json.dumps(index,indent=2),'utf8');files.append(q.relative_to(REPO).as_posix());q=DEST/'PREEXISTING_TAG_OBJECTS_AND_PEELS.json';q.write_text(json.dumps(old,indent=2),'utf8');files.append(q.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment')
 def recordgit(*a):
  if a[:2]==('tag','-a'):assert a[2]==TAG;return git('tag','-a',TAG,'-F',str(MSG))
  if a and a[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*a)
 rec.git=recordgit;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Actual fifteenth-hour complete H1/E2/E3 finals42/224/96, two-host full SHA, whole model/runtime finite CPU, all17Adam20 per update and actor9STD/critic8 changes; original10923.77741265297s independent cost once settled, originalowner364556/all own children out/canonicalNone/two original fcntl/private/shared free. Sixteenth actualowner376288 three GO/positive PPO/matching UUID compute from each latest full source3428/bbd5/dd5c; source filenames do not identify models. H1 explicit human-authorized sharing and exact CRLF helper after controller copy/before manifest retained; installed SDKmath/RSL/assets and33 negative cases pass, normal full-three future runtime/account bindings retained. Four genuinely new3428 local MuJoCo trajectories only, strict jump1/1/1 and15s survival but recovery9.795s versus8.175, clearance.0943004m versus.0948115, and normal speed.016753/displacement.254691/yaw-.377346 greater than prior.000536858/.0219208/-.229745. Original recovery200-callback window9.2975 through9.795, nonyaw last fail2.2925 and yaw last fail9.295; aggregate2859 yaw-only failing callbacks7.1475s is not a single continuous window, temporal readout not unique reward causation. Prior local generator parse failure and all source/error/unused drafts retained through prior stage and new capture. Different backend/no20kDR/two deterministic yaws, not PhysX qualification/statistical significance/full normal nonregression/graduation. No old case replay, extra GPU/native/Task, live patch/stop, peer interference, duplicate charge/refund/clearactive, reward/LR/STD/physics/CAD/threshold/budget/player change.','--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for ref,objects in old.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 # Batch-read the committed text blobs, avoiding thousands of shell invocations.
 request=''.join(head+':'+r['Git_path']+'\n' for r in entries).encode();proc=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True);data=proc.stdout;offset=0
 for r in entries:
  end=data.index(b'\n',offset);header=data[offset:end].split();assert header[1]==b'blob';length=int(header[2]);start=end+1;raw=data[start:start+length];assert H(raw)==r['archived_SHA'];offset=start+length+1
 assert len(git('tag','--list').splitlines())==1404
 print(json.dumps(dict(status='REMOTE_VERIFIED',commit=head,tag=TAG,object=obj,total_tags=1404,all1403old_objects_peels_exact=True,tracked_text_entries=len(entries),new_text_files=len(files),deferred=[])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/'reports/SCUT_FUDAN_UNIQUE_GIT_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),current_HEAD=git('rev-parse','HEAD'),resume_existing_objects_only_if_recorded=True),f,indent=2)
  raise
