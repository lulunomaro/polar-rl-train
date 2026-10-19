"""One unique record after actual deployment; never replay training for archival."""
from pathlib import Path
import json,sys,time,hashlib,subprocess,importlib,traceback
B=Path(__file__).resolve().parent;W=B.parent;G=W/'MOD4_SCUT_FUDAN_ELEVENTH_HOUR_20261019';REPO=W/'polar-rl-train'
BASE='aa025a05643cae509023c1d9824cbf29b0bee944';ID='scut-fudan-twelfth-hour-h1-shared-gpu-repaired-three-expert-continuation';TAG='trial-20261019-'+ID
DEST=REPO/'history/evidence'/B.name;NOTE=B/'ACTUAL_SCUT_FUDAN_REWARD_TRAINING_NOTE_UTF8.txt';MSG=B/'ACTUAL_SCUT_FUDAN_REWARD_TAG_UTF8.txt'
TITLE='Restore H1 shared-GPU admission and verified three-expert learning after actual partial-hour closure'
def git(*a):
 p=subprocess.run(['git','-C',str(REPO),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists() and not NOTE.exists()
 d=json.loads((B/'reports/THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());learning=json.loads((B/'reports/THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes());f=json.loads((G/'reports/PARTIAL_HOUR_ACTUAL_GO_FINALS_AND_NEXT_SOURCES_CPU_ACTUAL.json').read_bytes());proof=json.loads((B/'reports/H1_ACTUAL_PPO_REPAIR_AND_FULL_THREE_FUTURE_BINDING_CPU_ACTUAL.json').read_bytes());assert learning['three_actual_PPO_learning_verified'] and f['passed_all_actual_GO_final_models_CPU'] and f['passed_next_three_sources_whole_model_CPU'] and set(f['actual_owned_new_final_experts'])=={'e2','recovery'} and f['H1_failed_admission_zero_GO_retains_hour10_source'] and d['owner']['detached_pid']==329132;assert all(proof[k] for k in ('three_actual_GO_positive_PPO_matching_UUID_compute','H1_admission_repair_verified_on_actual_target_and_by_positive_PPO','resource_override_after_controller_copy_exact_bytes_verified','healthy_runtime_worker_AST_binding_verified','future_preparer_uses_each_actual_current_healthy_runtime_binding','future_preparer_retains_H1_override_after_controller_copy','future_owner_expects_full_three_completed_GO_experts','current_closing_collectors_bound329132'))
 import tomllib
 args=json.loads((B/'AUTOMATION_ACTUAL_REPAIRED_THREE_EXPERTS_V35_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 for key in ('name','kind','prompt','status','rrule'):assert actual[key]==args[key]
 assert actual['target_thread_id']==args['targetThreadId'] and actual['status']=='ACTIVE'
 with (B/'reports/AUTOMATION_V35_REPAIRED_THREE_EXPERTS_ACTUAL_READBACK_CPU.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),actual_name_prompt_kind_status_rrule_target_exact=True,original_ACTIVE_hourly_target_preserved=True,actual_three_GO_repaired_H1_and329132_binding=True,previous_partial_two_new_finals_retained_hour10_H1_and_zero_charge_exact=True,no_second_monitor_or_live_training_change=True),stream,indent=2)
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
  p=line.split();old[p[0]]=p[1:]
 assert len(old)==1399
 prior={}
 for q in (REPO/'history/evidence/MOD4_SCUT_FUDAN_ELEVENTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json',REPO/'history/evidence/MOD4_SCUT_FUDAN_ELEVENTH_HOUR_20261019/PREPARED_HEALTHY_BINDING_V34B_SUPPLEMENT/REPORT_CAPTURE_INDEX.json'):
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
 index=dict(epoch=time.time(),entries=entries,large_artifacts=dict(previous_actual_new_final_models={k:f['experts'][k]['final'] for k in f['actual_owned_new_final_experts']},retained_H1_previous_healthy_hour10_source=f['experts']['h1'],current_sources=json.loads((B/'reports/THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes())['sources']),deferred=[],local_behavior_this_stage_not_replayed=True,retained_source10_behavior_original_report=str(G/'reports/TENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json'))
 q=DEST/'REPORT_CAPTURE_INDEX.json';q.write_text(json.dumps(index,indent=2),'utf8');files.append(q.relative_to(REPO).as_posix());q=DEST/'PREEXISTING_TAG_OBJECTS_AND_PEELS.json';q.write_text(json.dumps(old,indent=2),'utf8');files.append(q.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment')
 def recordgit(*a):
  if a[:2]==('tag','-a'):assert a[2]==TAG;return git('tag','-a',TAG,'-F',str(MSG))
  if a and a[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*a)
 rec.git=recordgit;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Actual eleventh-hour E2/E3 complete finals240/99, whole-model CPU/all17Adam/17parameter changes and original7256.350798845291s independent cost once settled; sole old owner318576 and children out, canonicalNone/two original fcntl/private/shared locks free. H1 eleventh admission failure0GO0charge retained, latest healthy tenth3223 source with Adam670480 qualified without inventing an eleventh final. Unused repair-template healthy-runtime binding mismatch corrected on CPU before any remote attempt. New unused twelfth namespace owner329132: actual H1/E2/E3 GO, positive PPO and matching UUID worker compute verified. H1 sharing resource override after controller copy, predeploy exactbytes, healthy J worker sourcefilename/Adam normalization, current installed SDKmath/RSL/assets and all33 negative cases passed. Generic full-three closing and thirteenth future helpers bound to actual current owner/runtime, explicit H1 sharing retained with original memory/locks/save guards. No behavior case replay, intermediate PT audit, extra native/Task replay, live patch/stop, peer interference, recipe/PPO/reward/physics/STD/LR/budget/account/player change.','--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for ref,objects in old.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 # Batch-read the committed text blobs, avoiding thousands of shell invocations.
 request=''.join(head+':'+r['Git_path']+'\n' for r in entries).encode();proc=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True);data=proc.stdout;offset=0
 for r in entries:
  end=data.index(b'\n',offset);header=data[offset:end].split();assert header[1]==b'blob';length=int(header[2]);start=end+1;raw=data[start:start+length];assert H(raw)==r['archived_SHA'];offset=start+length+1
 assert len(git('tag','--list').splitlines())==1400
 print(json.dumps(dict(status='REMOTE_VERIFIED',commit=head,tag=TAG,object=obj,total_tags=1400,all1399old_objects_peels_exact=True,tracked_text_entries=len(entries),new_text_files=len(files),deferred=[])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/'reports/SCUT_FUDAN_UNIQUE_GIT_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),current_HEAD=git('rev-parse','HEAD'),resume_existing_objects_only_if_recorded=True),f,indent=2)
  raise
