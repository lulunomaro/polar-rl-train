"""One unique record after actual deployment; never replay training for archival."""
from pathlib import Path
import json,sys,time,hashlib,subprocess,importlib,traceback
B=Path(__file__).resolve().parent;W=B.parent;G=W/'MOD4_SEVENTEENTH_USER_DISK_CLEANUP_20261019';REPO=W/'polar-rl-train'
BASE='c3d09b61821a2a3c7e742d0e3b2eea8a8a38feda';ID='scut-fudan-seventeenth-hour-post-go-h1-oom-two-healthy-learning';TAG='trial-20261019-'+ID
DEST=REPO/'history/evidence'/B.name/'actual_partial_post_go_H1_oom_20261019';NOTE=B/'ACTUAL_SEVENTEENTH_PARTIAL_NOTE_UTF8.txt';MSG=B/'ACTUAL_SEVENTEENTH_PARTIAL_TAG_UTF8.txt'
TITLE='Resume E2 and E3; retain H1 post-GO initialization OOM and safer future admission'
def git(*a):
 p=subprocess.run(['git','-C',str(REPO),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists() and not NOTE.exists()
 d=json.loads((B/'reports/THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes());learning=json.loads((B/'reports/PARTIAL_THREE_GO_CLOSING_RETAINED_H1_AND_EMPIRICAL_MEMORY_GUARD_CPU_ACTUAL.json').read_bytes());f=json.loads((W/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());a=json.loads((B/'reports/TWO_HEALTHY_PPO_AND_H1_POST_GO_ALLOCATION_FAILURE_V2_ACTUAL.json').read_bytes());h=json.loads((B/'reports/H1_POST_GO_ENV_INITIALIZATION_FAILURE_TERMINAL_AND_LOG_ACTUAL.json').read_bytes());assert d['passed'] and f['passed_all_three_whole_final_models_CPU'] and learning['current_owner']==413504 and learning['two_healthy_actual_PPO_verified'] and learning['H1_actual_GO_true_not_old_preGO_failure'] and a['two_actual_PPO_learning_verified'] and a['actual_finite_transport_returned'] and h['terminal']['row']['original_error'] and not h['actual_own_processes'] and len(learning['future_templates'])==5 and len(learning['closing_helpers'])==2
 import tomllib
 args=json.loads((B/'AUTOMATION_ACTUAL_SEVENTEENTH_POST_GO_OOM_TWO_HEALTHY_V45_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 for key in ('name','kind','prompt','status','rrule'):assert actual[key]==args[key]
 assert actual['target_thread_id']==args['targetThreadId'] and actual['status']=='ACTIVE'
 with (B/'reports/AUTOMATION_V45_PARTIAL_SEVENTEENTH_EXACT_READBACK_CPU.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),actual_name_prompt_kind_status_rrule_target_exact=True,original_ACTIVE_hourly_target_preserved=True,actual_three_GO_two_positive_PPO_H1_post_GO_initialization_OOM=True,current_owner413504_three_real_GO_cost_and_two_final_closing_bound=True,no_second_monitor_or_mid_hour_heavy_audit=True,no_second_monitor_or_live_training_change=True),stream,indent=2)
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
  p=line.split();old[p[0]]=p[1:]
 assert len(old)==1406
 prior={}
 for q in sorted([*(REPO/'history/evidence'/G.name).rglob('REPORT_CAPTURE_INDEX.json'),*(REPO/'history/evidence'/B.name).rglob('REPORT_CAPTURE_INDEX.json')]):
  for r in json.loads(q.read_bytes())['entries']:
   sha=r.get('source_SHA') or r.get('sha256');path=r.get('Git_path');archived=r.get('archived_SHA') or r.get('archived_sha256')
   if sha and path and archived:prior[sha]=dict(Git_path=path,archived_SHA=archived)
 note=(B/'ACTUAL_SEVENTEENTH_PARTIAL_POST_GO_STAGE_SUMMARY.md').read_text('utf8')+'\n\nActual prior closure:\n'+json.dumps(f,indent=2)+'\n\nPrepared next sources and actual capacity pending facts:\n'+json.dumps(d,indent=2)+json.dumps(learning,indent=2)
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
 index=dict(epoch=time.time(),entries=entries,large_artifacts=dict(previous_final_models={k:x['final'] for k,x in f['experts'].items()},current_sources=d['sources'],current_intermediate_PPO_metadata_only={k:x['latest_complete'] for k,x in a['experts'].items()},current_PPO_weights_not_downloaded_or_whole_model_CPU_qualified=True,old_raw_deleted_by_explicit_human_authority=dict(actual_count=782,actual_logical_bytes=259494886175,complete_deletion_rows_report=str(G/'reports/EXPLICIT_OLD_TRAJECTORY_DELETION_COMPLETE_ACTUAL.json'),producer_SHA_not_rehashed=True,not_retained_after_this_authorized_deletion=True),installer_copy=dict(local_partial_path='D:/MOD4_RETAINED_INSTALLERS_20261019/source4090_environment_and_lab_v2_linuxpaths.tar.gz.partial',partial_bytes=272629760,SHA=None,complete=False,partial_preserved=True,remote_original_path='/home/lc01/Zonglin Li/zonglin2/downloads/source4090_environment_and_lab_v2_linuxpaths.tar.gz',remote_producer_bytes=20988865638,remote_existing_producer_SHA='77b823a63570fd5f0acfa7b1ce935cd61b914e9a5727e1e3333b39a95be7e184',remote_installer_not_deleted_by_this_action=True)),deferred=[],local_NPZ_producer_index=[x['raw'] for x in json.loads((B/'reports/SIXTEENTH_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').read_bytes())['episodes']])
 q=DEST/'REPORT_CAPTURE_INDEX.json';q.write_text(json.dumps(index,indent=2),'utf8');files.append(q.relative_to(REPO).as_posix());q=DEST/'PREEXISTING_TAG_OBJECTS_AND_PEELS.json';q.write_text(json.dumps(old,indent=2),'utf8');files.append(q.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment')
 def recordgit(*a):
  if a[:2]==('tag','-a'):assert a[2]==TAG;return git('tag','-a',TAG,'-F',str(MSG))
  if a and a[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*a)
 rec.git=recordgit;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Actual new originalowner413504 threeGO from source16 fullcb11/c51a/d17a afterV5 snapshotH1free9683/E3free24203/disk284497711104bytes; target source/SDKmath/RSL/runtimeassets CPU and old376288 actualclosure/canonicalNone/twofcntl/settledcost rechecked. H1 then FAILED after actualGO during environment initialization: exact9375byte workerlogSHA7db3207bbb0cd96e179380a3b1a55df4c0103a11dea3f2e4278d0377f0744e7f showsPhysX/WarpCUDAoutofmemory, exceptionfailed560000byteallocation, noPPO/newFINAL/PT; workerwrapperreturncode0 is notsuccess, originalnodeassert/errors/terminalallchildrenwait/lockrelease preserved. Firstactualmetadataall3False preserved; secondmissingonlyreaderactualreturned confirms E2E3actualGOpositivePPOmatchingUUIDcompute while preservingH1terminalandfulllog; noGPU/Task/native/workerretry/stophealthy/hotpatch/peeridentityqueryinterference. OriginalH1GOcost is a realinterval to originalterminal receipt, neverzero/refund/preGOclassification; currentaccount stays originalowner, settlementlater. Preparedcollector gets onlytwoactualnewfinals plus H1terminal/allthreeGOoriginalcost/canonicaloutlocks, reviewerwholeCPUtwofinals and retainedH1source16cb11 withsourceowned42 distinguishedfromcurrent0. Futurepartialfivefiles useactualhealthyP16runtime forH1, currentQ17healthyE2E3; postGOfailedrootchecks and originalthreechargedexpertownerhandoff retained. Future-only H1resourceINSTALLandnodeadditionalstartfree>=15669MiB matches existing successful same20k recipe hour16 snapshot; original>7000/sharing/RAM/disk/locks/saveguards and E2E3exclusive unchanged, nineCPU actualresourceassertionboundarycases passed. EmpiricalconservativeheadroomnotprovedminimumorOOMguarantee; resourcecontrollerbytesexplicitlychanged onlyinunusedfuture, no currentPPO/rewardphysics/20k/LR/STD/SDK/system/account/playerchange. Unusedallthreesuccesshandoff/archive drafts notexecuted andpreserved; no currentthreePPOclaim/midheavyPT/oldbehaviorreplay/skillPASS. SamehourlymonitorV45actualreadback; completeerrors/falsemetadata/log/source/partialclosing/future/monitor/appreceiptscaptured; largebinariesproducerindexonly, prior782authorizedrawdeletionandinstallerpartialremainhistorical, all1406oldtagobjectspeelskept.','--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for ref,objects in old.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 # Batch-read the committed text blobs, avoiding thousands of shell invocations.
 request=''.join(head+':'+r['Git_path']+'\n' for r in entries).encode();proc=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True);data=proc.stdout;offset=0
 for r in entries:
  end=data.index(b'\n',offset);header=data[offset:end].split();assert header[1]==b'blob';length=int(header[2]);start=end+1;raw=data[start:start+length];assert H(raw)==r['archived_SHA'];offset=start+length+1
 assert len(git('tag','--list').splitlines())==1407
 print(json.dumps(dict(status='REMOTE_VERIFIED',commit=head,tag=TAG,object=obj,total_tags=1407,all1406old_objects_peels_exact=True,tracked_text_entries=len(entries),new_text_files=len(files),deferred=[])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/'reports/SCUT_FUDAN_UNIQUE_GIT_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),current_HEAD=git('rev-parse','HEAD'),resume_existing_objects_only_if_recorded=True),f,indent=2)
  raise
