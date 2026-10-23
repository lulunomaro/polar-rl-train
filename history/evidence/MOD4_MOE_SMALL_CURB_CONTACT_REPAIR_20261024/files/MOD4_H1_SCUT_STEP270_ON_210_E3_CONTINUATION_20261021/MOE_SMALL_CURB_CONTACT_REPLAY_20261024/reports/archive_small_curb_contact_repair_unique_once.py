from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent.parent;R=D/'reports';T=D.parent;W=T.parent;PLAYER=W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023';G=W/'polar-rl-train';DEST=G/'history/evidence/MOD4_MOE_SMALL_CURB_CONTACT_REPAIR_20261024';ID='moe-small-curb-native-multiccd-contact-repair';TAG='trial-20261024-'+ID;BASE='f3f7098691bb3d4169889374a6df65b46709c6b6'
H=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):
 p=subprocess.run(['git','-C',str(G),*args],capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').strip()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists() and not (R/'CONTACT_REPAIR_UNIQUE_RECORD_STARTED_ACTUAL.json').exists()
 proof=json.loads((R/'CONTROLLED_COLLISION_PIPELINE_REPAIR_AND_COMPLETE_PREFIX_SCOPE_ACTUAL.json').read_bytes());assert proof['all8_ablation_cases_no_UI_fall'] and proof['original_V4_whole_returncode']==1 and proof['V5_only_missing_multi_off_four_complete_and_FINAL']
 source=json.loads((R/'VERSIONED_PLAYER_CONTACT_REPAIR_SOURCE_AST_AND_LIMITS_ACTUAL.json').read_bytes());assert source['original_XML_and_mesh_unchanged'] and source['all_actor_and_gate_ONNX_unchanged']
 tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(tags.splitlines())==1429
 put(R/'CONTACT_REPAIR_UNIQUE_RECORD_STARTED_ACTUAL.json',dict(epoch=time.time(),base_HEAD=BASE,tag=TAG,original_tag_count=1429,not_training_or_budget_write=True))
 note='Human reported ordinary driving over small features makes the robot fly and lose stability. Retained started metadata and last coarse player snapshot: normal mode, about0.636m/s command,53.7degree tilt; no original command or contact trajectory exists. New remote4090 frozen diagnostic used task-isolated MuJoCo3.14 and ORT1.30 matching local versions; CPU physics and primary ONNX CPU inference on Linux4090 host, frozen TorchCUDA actor/gate references on the shared4090, not PhysX/GPU physics. V1 isolated pip install succeeded but import path failed before rollout; V2 explicit sys.path reused exact installed dependencies, six complete cases; V3 nine new command cases reproduced fixedE0 launch/fall at0.65 and1.0m/s. Actual0.5ms contact-force vectors sum to recorded root generalized constraint forces. Guide roller deeply contacts opposing40micrometre-thick quad/triangle prism surfaces; one step changes upward velocity by6.944m/s, not an MoE switching event. V4 nativeCCD-off completed four prefixes without the prior falls, then failed on an obsolete multiCCD enable enum; rc1/no wholeFINAL is preserved. V5 only missing four multiCCD-off cases used current disablebit524288 and completed FINAL; no old baseline/native-off replay. Both isolation branches remove the reproduced falls in their finite tests, at unchanged initial-stateSHA, geometry, gains, actuator limits, observations, frozen policies and commands. Candidate separate player entry disables multiCCD only and keeps nativeCCD, all original source/entry/terrain and experts intact; no original player or Isaac training hotpatch. Source-only local preparation and saved-array analysis, no local agent policy/physics test after4090 instruction. Preserve all local blank-line-anchor,6vertex-assumption, generated-label-newline errors and V2 corrections, original source, package install log, actual complete/prefix/error receipts, all producer artifactSHA, detailed forces and saved-result plot. Not exact original human replay, unique upstream bug proof, exact energy balance, all-terrain/jump/recovery qualification, or MoE training. Similar public upstream issue3691 is a hypothesis only. Record all outcomes, not only success.'
 (D/'STAGE_NOTE.md').write_text(note+'\n',encoding='utf8');(D/'TAG_NOTE.txt').write_text(note+'\n',encoding='utf8');DEST.mkdir(parents=True)
 known={};external=[]
 for version,folder in (('', 'actual_contact_4090'),('_V2','actual_contact_V2_4090'),('_V3','actual_contact_V3_4090'),('_V4','actual_contact_V4_4090'),('_V5','actual_contact_V5_4090')):
  result=json.loads((R/('4090_SMALL_CURB'+version+'_FROZEN_FINITE_RETURNED_ACTUAL.json')).read_bytes())
  for row in result['artifacts']:known[str((D/folder/row['relative']).resolve())]=row['SHA']
  pack=json.loads((R/('4090_SMALL_CURB'+version+'_DEPLOY_STARTED_ACTUAL.json')).read_bytes())['payload'];known[str(Path(pack['path']).resolve())]=pack['SHA']
 for report in (R/'SAVED_CONTACT_COMPARISON_PLOT_PRODUCER_ACTUAL.json',):
  row=json.loads(report.read_bytes());known[str(Path(row['path']).resolve())]=row['SHA']
 manifest=json.loads((PLAYER/'policy/manifest.json').read_bytes());known[str((PLAYER/'policy/hybrid_moe.onnx').resolve())]=manifest['onnx_SHA']
 extras=[T/'MOE_ROUTING_MATCHED_4090_DIAGNOSTIC_20261024/prepare_human_small_curb_contact_stage_once.py',PLAYER/'policy/manifest.json',PLAYER/'试玩小坎碰撞修正版.bat',PLAYER/'小坎碰撞修正版说明.md',PLAYER/'player/rm7v7_contact_stable_candidate_v1.py',PLAYER/'player/drive_rm7v7_contact_stable_candidate_v1.py']
 extras += [T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(n)+'.py') for n in range(17,22)]
 files=[];entries=[];bySHA={};sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
 selected=sorted({p for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts}|set(extras))
 for p in selected:
  st=p.stat();name=str(p)
  if p.suffix.lower() in ('.pt','.onnx','.npz','.zip','.png','.jpg','.stl','.mjb','.pyc','.so','.dll','.pyd'):
   external.append(dict(path=name,bytes=st.st_size,SHA=known.get(str(p.resolve())),SHA_kind='existing producer receipt' if str(p.resolve()) in known else 'unknown; no archive binary rehash',original_retained=True));continue
  raw=p.read_bytes();sha=H(raw)
  if sha in bySHA:entries.append(dict(path=name,bytes=len(raw),SHA=sha,**bySHA[sha]));continue
  try:text=raw.decode('utf8')
  except UnicodeDecodeError:external.append(dict(path=name,bytes=st.st_size,SHA=known.get(str(p.resolve())),original_retained=True));continue
  clean,n=redact(text);data=clean.encode('utf8');q=DEST/'files'/p.relative_to(W);q.parent.mkdir(parents=True,exist_ok=True);assert len(data)<49_000_000;q.write_bytes(data);target=q.relative_to(G).as_posix();row=dict(path=name,bytes=len(raw),SHA=sha,archive=target,archive_SHA=H(data),source_mtime_ns=st.st_mtime_ns,mode='redacted' if n else 'full',redactions=n,original_retained=True);entries.append(row);files.append(target);bySHA[sha]={k:row[k] for k in ('archive','archive_SHA','mode')}
 index=dict(epoch=time.time(),kind='human_small_curb_contact_launch_and_versioned_player_repair',entries=entries,artifacts=external,reference_original_player_complete_capture_commit=BASE,reference_original_player_source_archive='versions/20261020_two_linux_policy50_series/current_clearance_v4_closed48_pair49_and_MoE4090_20261024/COMPLETE_FILE_CAPTURE_INDEX.json',models=manifest['sources'],original_combined_ONNX_SHA=manifest['onnx_SHA'],all_original_errors_and_partial_classifications_preserved=True,old_tag_objects_peels=tags,no_archival_model_raw_rehash_or_training_host_query=True)
 q=DEST/'REPORT_CAPTURE_INDEX.json';q.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf8');files.append(q.relative_to(G).as_posix())
 rec=importlib.import_module('record_experiment')
 def rg(*args):
  if args[:2]==('tag','-a'):assert args[2]==TAG;return git('tag','-a',TAG,'-F',str(D/'TAG_NOTE.txt'))
  if args and args[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*args)
 rec.git=rg;sys.argv=['record_experiment.py','--id',ID,'--title','Isolate small-curb launch contacts and deliver separate collision-repaired player','--kind','repair','--note-file',str(D/'STAGE_NOTE.md'),'--files',*files,'--validation',note,'--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for line in tags.splitlines():
  a=line.split();assert remote[a[0]]==a[1]
  if len(a)>2:assert remote[a[0]+'^{}']==a[2]
 for row in entries:assert H(subprocess.run(['git','-C',str(G),'show',head+':'+row['archive']],capture_output=True,check=True).stdout)==row['archive_SHA']
 assert not git('status','--porcelain') and len(git('tag','--list').splitlines())==1430
 print(json.dumps(dict(remote_main=head,tag=TAG,tag_object=obj,peeled=head,total_tags=1430,all1429_old_objects_peels_unchanged=True,fulltext_references=len(entries),new_Git_files=len(files),binary_producer_indexes_only=True,all_new_text_blobs_verified=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('CONTACT_REPAIR_UNIQUE_RECORD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_existing_objects_only=True));raise
