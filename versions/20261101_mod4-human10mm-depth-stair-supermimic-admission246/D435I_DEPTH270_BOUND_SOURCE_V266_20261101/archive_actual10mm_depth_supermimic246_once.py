"""Archive this new user-directed phase once; never read binary/model/raw for Git."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';G=W/'polar-rl-train'
ID='mod4-human10mm-depth-stair-supermimic-admission246';TAG='trial-20261101-'+ID;V=G/'versions'/('20261101_'+ID)
def read(p):return json.loads(Path(p).read_bytes())
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{x.split()[1]:x.split()[0]for x in s.splitlines()if x.strip()}
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not V.exists()and not git('tag','--list','*'+ID+'*'),'ANY phase tag is consumed; never record/retag'
assert not git('diff','--cached','--name-only')
changes=set(git('diff','--name-only').splitlines());policy={'AGENTS.md','docs/NUMERICAL_AUDIT_AND_TRAINING_GUARDS_20261021.md'};assert changes==policy,changes
x=read(R/'CURRENT_ACTUAL266_D435I_DEPTH_SUPERMIMIC_MAIN_10MM_AND_NEXT_WORK_ORDER.json');assert x['no_current_learning']and x['actual266']['passed']and x['actual266']['depth_frames_with_supported_platform']==12
assert read(R/'ROOT266_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
req=read(R/'AUTOMATION_DEPTH_SUPERMIMIC_10MM_ACTUAL266_UPDATE_REQUEST.json');app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert app['prompt']==req['prompt'].rstrip('\n')and app['status']=='ACTIVE'and app['rrule']==req['rrule']and app['target_thread_id']==req['targetThreadId']
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert len([k for k in old if not k.endswith('^{}')])==1515 and all(remote.get(k)==v for k,v in old.items())
put(R/'RECORD246_ACTUAL_USER10MM_DEPTH_SM_ADMISSION_ONCE_CONSUMED.json',dict(epoch=time.time(),ID=ID,TAG=TAG,protected1515_old_objects_peels=True,old240242_and_all_learning_tags_not_rerecorded=True,models_raw_GPU_experiments_for_Git=0))
put(R/'LOCAL_TEXT_LOOKUP_FALSE_SCOPE_RETAINED.json',dict(epoch=time.time(),lookup='Get-Content MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/jump_literal183.py',actual_error='Path not found',scope='Local source lookup while inspecting reward adapter; actual source is literal_original_methods.py/jump194_boundary.py. No model/physics failure and no model/raw reread. Original tool error retained in conversation.'))
stage_names=[
 'MODEL2050_TRAINED240_USER_MUJOCO_V243_20261101',
 'SCUT_UPSTREAM_JUMP_STAIRS_REWARD_REVIEW_V245_20261101',
 'MODEL2050_HUMAN_CLOSURE10MM_REGRESSION_V246_20261101',
 'DEPTH_STAIR_TARGET_OBSERVATION_SOURCE_V247_20261101',
 'D435I_FRONT_FIXED_SDK_SOURCE_V248_20261101',
 'D435I_SUPERMIMIC50_FIND_ACCEL_JUMP_SOURCE_V249_20261101',
 'D435I_FRONT_DEPTH_ACTUAL_ZERO_PT_SOURCE_V250_20261101',
 'D435I_RAY_DEPTH_BACKEND_SOURCE_V251_20261101',
 'D435I_FORWARD_RAY_DEPTH_ZERO_PT_V254_20261101',
 'D435I_SUPERMIMIC_NATIVE_WM50_CONTEXT40_SOURCE_V255_20261101',
 'D435I_RAY_DEPTH_LINK_BINDING_V256_20261101',
 'D435I_RAY_DEPTH_USD_MESH_BINDING_V257_20261101',
 'D435I_RAY_DEPTH_HASH_NAME_REPAIR_V258_20261101',
 'FUDAN_LITERAL_SUPERMIMIC_REWARD_MEMORY_SOURCE_V259_20261101',
 'D435I_RAY_DEPTH_N1_ORIGINAL_JUMP_V260_20261101',
 'D435I_RAY_DEPTH_ORIGINAL_JUMP_AUDIT_V261_20261101',
 'D435I_NEW261_DEPTH_GEOMETRY_DIAGNOSTIC_V262_20261101',
 'DEPTH_HORIZONTAL_SUPPORT_PIXEL_CENTER_V263_20261101',
 'D435I_REAL_FORWARD_DEPTH_270_LOCALIZATION_V264_20261101',
 'D435I_DEPTH_SOURCE_PATH_REPAIR_V265_20261101',
 'D435I_DEPTH270_BOUND_SOURCE_V266_20261101',
 'W35_LATEST32481_FULL32S_CLOSURE10MM_SOURCE_V1_20261101']
roots=[(n,T/n)for n in stage_names]+[
 ('publisher243249',T/'publish243_249_user_updates_and_compact_reports_once.py'),
 ('publisher266',T/'publish266_current_depth_supermimic_handoff_once.py'),
 ('workspace_policy',W/'AGENTS.md')]
assert all(p.exists()for _,p in roots)
scope=R/'CAPTURE246_FROZEN_ACTUAL_USER10MM_DEPTH_SM_SCOPE.json';put(scope,dict(epoch=time.time(),phase=ID,roots=[dict(archive_label=k,path=str(p))for k,p in roots],modified_repo_policy_files=sorted(policy),includes='Full243 GUI and244 saved-pose CPU; primary245 SCUT; actual24610mm; all247-266 source/CPU/actual/false/reader errors/fullUTF8/automation receipts; new frozen W3510mm source. No new actual SuperMimic learning.',binary_policy='Models/raw/NPZ/USD/media/generatedrenderXML metadata only from existing producer receipts, never hash/read for Git.',pending=x['next_required_work']))
note=R/'ACTUAL246_HUMAN10MM_DEPTH_SUPERMIMIC_EXPERIMENT_NOTE.md'
with note.open('x',encoding='utf8')as f:f.write('''The user changed future MOD4 per-environment closure reset from2mm to10mm, selected a D435i fixed at the chassis front, and directed SuperMimic to find stairs and accelerate onto them. Current policy documents now record that explicit10mm override while preserving historical2mm sources and trials. Physical closed joints, solver, mimic.01rad,400N nominal engineering k2000,50Hz policy/100Hz feedback/400Hz physics,2.5ms TGS32/4 F32, original6-motor actions/PD/delays/D0-D7 remain. Original frozen E0 and retired jump branches are untouched. Latest learned source is the closed2050-adaptation240 formal0f5de75a...552a07, iteration2135/17Adam42940; no new visual SuperMimic GO or policy training has occurred.

The fresh user243 MuJoCo viewer replayed the actual242 cases with true277 meshes/31 bodies and no new physics/NN. The user watched it and it exited normally after69.17s. Saved-pose question244 used one new admitted local JUMP pose pass and the original float32 anchor formula: terminal right_gas_closure2.758587mm, exceeding the old2mm threshold by.758587mm. This is a saved-pose reconstruction, not a newly sampled original GPU scalar. New246 actual actor-only10mm regression consumed one necessary final-model GPU read:1407controls/11256physics/2814feedback. No case hit closure; sampled maxima were below3.132mm. Standing8.26s/reverse4.34s/JUMP5.54s ended on bad_orientation, forward completed10s. Heading drift and stable landing remain unresolved; loosening the reset did not establish270mm success.

Primary SCUT review245 is pinned1a26356d6f591734d4f6f666f5cead1a6925da67. It distinguishes active V14Rough-v1 Airborne/forward-scan StepUp configuration from optional Stair/Takeoff state machines; those special reward definitions are not all active by default. The inspected chain has no corresponding millimetre anchor-distance reset. Its physical constraints are not declared absent. No SCUT reward replacement was selected. The pinned Fudan JUMP19 methods/full config16 weights/per-termclip2.5*dt.02/stateful contact-air/reset memory remain byte-literal in this work.

Depth admission retained all original failures:250 Vulkan ERROR_INCOMPATIBLE_DRIVER followed byCUDA700;252/253 plain-Python backend-source lookup refusals;254 wrong chassis path;256 invalid mesh target;257 hashlib API typo before CIM/network;258 N1 mixed-task10-way assignment refusal;260 inherited directional-audit refusal;261 successful actual depth but incorrect riser-height candidates;264/265 source-date-path refusals before remote. Separate sources preserved every original false.256 fixed the actual /Robot/links/chassis binding;258 generated an explicit valid UsdGeom mesh;261 used the original JUMP sampler and an audit checking that actual class and its original bounds. No reward, command values, physical guard or driver was changed to hide these failures.

New262 necessary one-pass NEW261 depth/K/T inspection and one actual SDK pinhole source read found SDK pixel centers+.5 and the missing horizontal-support filter. New263 analytical flat/riser/stair/stale fixtures passed. Actual266 then returned PASS with12controls/96physics/24feedback and12 supported-plane detections at0.27000019..0.27000064m. It used the current installed SDK forward ray camera and the same physical270mm mesh, no model/PT/ONNX/actor/optimizer/account/GO. All children waited0, ENVclose returned, APPclose requested, locks/SSH/session released/restored. This is ideal geometric depth, not real D435i stereo noise/self occlusion. The84x48/50Hz probe and provisional(.15,0,.15)m/10deg-down mount are not measured hardware calibration. Visible distance/extents do not certify the true front edge or complete landing footprint. The raw generated depth NPZ remains metadata-only; correct localization is not a trained navigation or jump skill.

SuperMimic components249/255/259 are honestly source-only.255 executed one synthetic native H32 WM update on64 synthetic pairs with context40, not real data.259 invoked the actual unchanged Fudan methods through32 synthetic imagined steps, with exact reward/contact-air/action-memory equality to the original reference and finite nonzero scalar gradient2.5211823, no real checkpoint or optimizer. The existing127-state WM cannot provide all31-body contact forces/six applied efforts/own-leg measurements required by the original reward. Those outputs and a real own-state/depth collector must be explicitly added and qualified; missing values cannot be filled with zeros or future PhysX truth. The new actor44/critic47 architecture and three-optimizer native conversion are not yet applied to real weights or called exact PPO resume. Next work is actual fullstate+depth data, WM warmup, actual original-reward H32 gradients and a typed goal-conditioned approach/acceleration task, followed by the original sole72 finite contract. The270mm sensor fixture is not falsely described as the unchanged original Fudan curriculum, whose original highest steps were about.21m.

The same authorized W35 child froze a separate10mm latest32481 full32s source, with the original qualified2d0 checkpoint and fullCAD70mm peak-to-trough geometry. It has not run that full skill case. E2/E3/all old-expert skill acceptance/full SuperMimic conversion/true270 stable landing remain unfinished. This phase includes every saved source, error, report and app receipt; previous annotated trial objects/peels are protected. All binaries/raw/models/media/generatedrenderXML are metadata-only. No experiment, model/raw read, host-GPU query, oldonce replay, budget change or training interruption is performed for Git.
''')
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for p in(G/'versions').rglob('CAPTURE_INDEX*.json'):
 try:i=read(p)
 except(UnicodeDecodeError,json.JSONDecodeError):continue
 for row in i.get('files',[]):
  sha=row.get('SHA')or row.get('sha256');gp=row.get('Git_path')or row.get('git_path')
  if sha and gp and row.get('capture')=='full_UTF8_byte_exact'and(G/gp).is_file():known.setdefault(sha,gp)
binary={'.pt','.pth','.onnx','.data','.npz','.npy','.usd','.usda','.usdc','.stl','.obj','.mtl','.zip','.tar','.gz','.7z','.png','.jpg','.jpeg','.webp','.mp4','.avi','.mat','.slx','.jsonl','.bin','.pyc','.pyd','.dll','.hf'}
texttypes={'.py','.json','.txt','.md','.log','.xml','.yaml','.yml','.toml','.sh','.ps1','.cfg','.ini','.csv','.tsv','.m','.urdf','.diff','.sha256','.patch'}
def is_binary(p):return p.suffix.lower()in binary or p.name.startswith('events.out.tfevents')or p.name=='DISPLAY243_TRUE_MOD4.xml'
def project(value):
 count=0
 if isinstance(value,dict):
  if isinstance(value.get('path'),str)and is_binary(Path(value['path']))and'UTF8'in value:return{k:v for k,v in value.items()if k!='UTF8'}|dict(capture='embedded_binary_metadata_only_original_full_report_retained_locally'),1
  out={}
  for k,v in value.items():out[k],n=project(v);count+=n
  return out,count
 if isinstance(value,list):
  out=[]
  for v in value:y,n=project(v);out.append(y);count+=n
  return out,count
 return value,0
V.mkdir();rows=[];selected=[]
for label,root in roots:
 for p in([root]if root.is_file()else sorted(root.rglob('*'))):
  if not p.is_file()or'__pycache__'in p.parts:continue
  if is_binary(p):rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA='unknown',capture='metadata_only_no_content_or_hash_for_Git'));continue
  assert p.suffix.lower()in texttypes,str(p)
  b=p.read_bytes();sha=hashlib.sha256(b).hexdigest()
  if sha in known:rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
  dest=V/label/(p.name if root.is_file()else p.relative_to(root));dest.parent.mkdir(parents=True,exist_ok=True)
  try:text=b.decode('utf8')
  except UnicodeDecodeError:
   safe,count=redact(b.decode('latin1'));value=b if not count else safe.encode('latin1');dest=dest.with_name(dest.name+'.bytes.b64.txt');dest.write_text(base64.b64encode(value).decode('ascii')+'\n',encoding='ascii');gp=dest.relative_to(G).as_posix();rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=gp,capture='byte_exact_base64_nonUTF8_source'if not count else'credential_redacted_base64_nonUTF8_source',archive_decoded_SHA=hashlib.sha256(value).hexdigest(),redactions=count));selected.append(gp);continue
  projected=0
  if p.suffix.lower()=='.json':
   try:obj,projected=project(json.loads(text))
   except json.JSONDecodeError:pass
   if projected:text=json.dumps(obj,indent=2,ensure_ascii=False)
  safe,count=redact(text);value=b if not count and not projected else safe.encode('utf8');dest.write_bytes(value);gp=dest.relative_to(G).as_posix()
  rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,binary_metadata_projections=projected,capture='full_UTF8_except_embedded_binary_metadata_projection'if projected else('full_UTF8_credential_pattern_redacted'if count else'full_UTF8_byte_exact')));selected.append(gp)
  if not count and not projected:known[sha]=gp
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,actual266=x['actual266'],latest_model_metadata_only=x['latest_qualified_model'],modified_repo_policy_files=sorted(policy),pending=x['next_required_work'],models_raw_GPU_experiment_reads_for_Git=0,protected1515_old_objects_peels=True),indent=2,ensure_ascii=False),encoding='utf8');selected.append(index.relative_to(G).as_posix());selected+=sorted(policy)
import record_experiment as recorder
original_git=recorder.git
def batch(*a):
 if a[:2]==('add','--'):
  for i in range(2,len(a),24):original_git('add','--',*a[i:i+24])
  return''
 return original_git(*a)
recorder.git=batch
note_gp=next(r['Git_path']for r in rows if r['path']==str(note))
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Human10mm closure and real forward-depth270mm localization; literal-reward SuperMimic source admission, no new learner', '--kind','evaluation','--note-file',str(G/note_gp),'--validation','2461407controls10mm/no closure,orientation unresolved;243viewer watched and exited;244original rightgas2.758587mm;245primarySCUT pinned;250/252-265 allfalse retained;26612actualdepthframes96physics24feedback/270mm horizontal support/0model0optimizer0GO/wait0SSHFREE;255syntheticWM and259literal19H32 rewardmemory exact/gradient2.521 sourceonly;W3510mm sourceonly;protect1515oldobjectspeels/no binary model raw GPU reads forGit','--files',*selected,'--push'];recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head and git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,protected1515_old_objects_peels=True,tag_count=1516,indexed_files=len(rows),new_full_files=len(selected),clean=True)))
