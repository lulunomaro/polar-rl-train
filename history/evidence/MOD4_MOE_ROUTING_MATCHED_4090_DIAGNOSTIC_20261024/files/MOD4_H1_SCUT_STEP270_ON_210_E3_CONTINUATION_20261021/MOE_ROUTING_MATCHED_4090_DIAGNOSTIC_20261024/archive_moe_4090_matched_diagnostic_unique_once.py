from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports';PLAYER=W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023';G=W/'polar-rl-train';DEST=G/'history/evidence/MOD4_MOE_ROUTING_MATCHED_4090_DIAGNOSTIC_20261024';ID='moe-routing-player-frozen-4090-comparison';TAG='trial-20261024-'+ID;BASE='e3c2d6c2361af38063264917a7a513f0fe5fe1f0'
H=lambda raw:hashlib.sha256(raw).hexdigest()
def git(*a):
 p=subprocess.run(['git','-C',str(G),*a],capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').strip()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists() and not (R/'GPU_UNIQUE_RECORD_STARTED_ACTUAL.json').exists()
 result=json.loads((R/'4090_MATCHED_FROZEN_FINITE_RETURNED_ACTUAL.json').read_bytes());proof=json.loads((R/'4090_MATCHED_CORRECT_BODY_SPEED_ROUTING_AND_LIMITS_CPU_ANALYSIS_ACTUAL.json').read_bytes());fix=json.loads((PLAYER/'reports/HUD_REGULAR_BODY_FRAME_FIX_AFTER_4090_SAVED_POSE_ACTUAL.json').read_bytes());assert result['actual_returncode']==0 and result['final']['passed_frozen_execution'] and len(result['final']['cases'])==12 and fix['no_claim_fixed_locomotion_or_stability']
 old=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(old.splitlines())==1428
 put(R/'GPU_UNIQUE_RECORD_STARTED_ACTUAL.json',dict(epoch=time.time(),base_HEAD=BASE,tag=TAG,original_all_tags_count=1428))
 note='Human observed poor MoE flat driving while standalone experts had worked and requested4090 testing rather than local testing. Frozen matched12cases ran on the shared thirdRTX4090: exact copied player MuJoCo3.12 CPU physics on remote72, torch2.10 CUDA actor/gate inference, not PhysX GPU physics. Auto/E0/W35 x(.3,.6,1.2,-.6m/s),500controls each, all initial physical-state SHA equal, actor9 includingSTD unchanged, no optimizer, no training or canonical mutation. Every forward auto trace was byte-identical to fixedW35 with zero switches; reverse switched5times. These cases do not support forward switching chatter as the cause. Found HUD/summary BODY inertial-axis speed error: corrected display to XBODY regular chassis frame, independently verified on remote saved poses against qvel rotation/world finite differences. Preserve original incorrect metrics and source,90s readback timeout, subsequent missing-only retrieval of the original full readback after its exact-RPC/time-window candidate exited, old BODY bitexact reader assertion and V2 correction, inline builder syntax error, all constraints and source. No local simulation after the4090 instruction. Earlier local3.14/ONNX pause is not isolated against remote3.12/CUDA. Fixed experts also show yaw/lateral drift;1.2cases leave the declared flat route and saved-pose geometry shows rear chassis contact, not original force evidence or unique cause. HUD fix changes no policy/physics/actions and is not a stability or270mm graduation claim. All new reports/fulltext/errors/code retained; model/raw/mesh/zip binary producer indexes only; no archive-driven rehash.'
 (D/'STAGE_NOTE.md').write_text(note+'\n',encoding='utf8');(D/'TAG_NOTE.txt').write_text(note+'\n',encoding='utf8');DEST.mkdir(parents=True)
 known={str((D/'actual_4090'/row['relative']).resolve()):row['SHA'] for row in result['artifacts']}
 pack=json.loads((R/'4090_MATCHED_DEPLOY_STARTED_ACTUAL.json').read_bytes())['payload'];known[str(Path(pack['path']).resolve())]=pack['SHA'];local=json.loads((PLAYER/'reports/REQUESTED_LOCAL_RUN_JUMP_PLAYTEST_CPU_ACTUAL.json').read_bytes())['artifact'];known[str(Path(local['path']).resolve())]=local['SHA'];known[str((PLAYER/'policy/hybrid_moe.onnx').resolve())]=json.loads((PLAYER/'policy/manifest.json').read_bytes())['onnx_SHA']
 portable=json.loads((W/'MOD4_LATEST_HYBRID_MOE_PACKAGE_20261020/delivery/MOD4_HybridMoE_20261020/PACKAGE_MANIFEST.json').read_bytes())
 for row in portable['files']:
  if row['path'].startswith('player/assets/'):known[str((PLAYER/row['path']).resolve())]=row['SHA']
 extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in (13,14,15)]
 files=[];entries=[];artifacts=[];bySHA={};sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
 selected=sorted({p for base in (D,PLAYER) for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}|set(extras))
 for p in selected:
  st=p.stat();s=str(p)
  if p.suffix.lower() in ('.pt','.pth','.onnx','.npz','.npy','.stl','.mesh','.bin','.png','.jpg','.mp4','.mjb','.usd','.zip','.lock','.pyc'):
   sha=known.get(str(p.resolve()));artifacts.append(dict(path=s,bytes=st.st_size,SHA=sha,SHA_kind='known producer manifest or actual receipt' if sha else 'unknown; no archival binary rehash',original_retained=True));continue
  raw=p.read_bytes();sha=H(raw)
  if sha in bySHA:entries.append(dict(path=s,bytes=len(raw),SHA=sha,**bySHA[sha]));continue
  try:text=raw.decode('utf8-sig') if raw.startswith(b'\xef\xbb\xbf') else raw.decode('utf8')
  except UnicodeDecodeError:artifacts.append(dict(path=s,bytes=st.st_size,SHA=known.get(str(p.resolve())),original_retained=True));continue
  clean,n=redact(text);data=clean.encode('utf8') if n else raw;q=DEST/'files'/p.relative_to(W);q.parent.mkdir(parents=True,exist_ok=True);assert len(data)<49_000_000;q.write_bytes(data);target=q.relative_to(G).as_posix();row=dict(path=s,bytes=len(raw),SHA=sha,archive=target,archive_SHA=H(data),source_mtime_ns=st.st_mtime_ns,capture_epoch=time.time(),mode='redacted' if n else 'full',redactions=n,original_retained=True);entries.append(row);files.append(target);bySHA[sha]={k:row[k] for k in ('archive','archive_SHA','mode')}
 index=dict(epoch=time.time(),kind='human_requested_matched4090_MoE_routing_diagnostic_and_HUD_fix',entries=entries,artifacts=artifacts,source_models=json.loads((D/'CONFIG.json').read_bytes())['checkpoints'],all_old_metrics_reader_errors_and_scope_corrections_retained=True,no_local_rollout_after_human4090_instruction=True,no_archive_driven_model_or_raw_or_GPU_or_training_host_or_budget_read=True,old_tag_objects_and_peels=old)
 q=DEST/'REPORT_CAPTURE_INDEX.json';q.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf8');files.append(q.relative_to(G).as_posix())
 rec=importlib.import_module('record_experiment')
 def rg(*a):
  if a[:2]==('tag','-a'):assert a[2]==TAG;return git('tag','-a',TAG,'-F',str(D/'TAG_NOTE.txt'))
  if a and a[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*a)
 rec.git=rg;sys.argv=['record_experiment.py','--id',ID,'--title','Diagnose frozen MoE on4090 and correct player body-frame speed HUD','--kind','diagnostic','--note-file',str(D/'STAGE_NOTE.md'),'--files',*files,'--validation',note,'--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for line in old.splitlines():
  a=line.split();assert remote[a[0]]==a[1]
  if len(a)>2:assert remote[a[0]+'^{}']==a[2]
 for row in entries:assert H(subprocess.run(['git','-C',str(G),'show',head+':'+row['archive']],capture_output=True,check=True).stdout)==row['archive_SHA']
 assert not git('status','--porcelain') and len(git('tag','--list').splitlines())==1429
 print(json.dumps(dict(remote_main=head,tag=TAG,tag_object=obj,peeled=head,total_tags=1429,all1428_old_objects_peels_unchanged=True,fulltext_references=len(entries),new_Git_files=len(files),all_new_text_blobs_verified=True,binary_producer_indexes_only=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('GPU_UNIQUE_RECORD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_existing_objects_only=True));raise
