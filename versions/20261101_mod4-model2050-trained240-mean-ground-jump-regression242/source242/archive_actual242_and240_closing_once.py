"""New actual evaluation242 plus closed240 supplement. Never rerun experiments."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;R=N/'reports';T=N.parent;C=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';G=T.parent/'polar-rl-train'
ID='mod4-model2050-trained240-mean-ground-jump-regression242';TAG='trial-20261101-'+ID;V=G/'versions'/('20261101_'+ID)
def read(p):return json.loads(Path(p).read_bytes())
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{x.split()[1]:x.split()[0]for x in s.splitlines()if x.strip()}
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not git('status','--porcelain')and not V.exists()
assert not git('tag','--list','*'+ID+'*'),'ANY242 tag is consumed, never record/retag again'
x=read(R/'CURRENT_ACTUAL242_WHEEL_AIR_EARLY_CLOSURE_AND_CLOSED240_WORK_ORDER.json');assert x['execution_passed']and not x['physical_skill_passed']and x['no_current_learning']
assert read(R/'ROOT242_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
assert read(C/'reports/ROOT240V2_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')['passed_collection']and read(C/'reports/ROOT240V2_NEW_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')['passed']
request=read(R/'AUTOMATION_CLOSED240_ACTUAL242_W35_NO_ADAPTER_CLARIFIED_UPDATE_REQUEST.json')
app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert app['prompt']==request['prompt'].rstrip('\n')and app['status']=='ACTIVE'and app['rrule']==request['rrule']and app['target_thread_id']==request['targetThreadId']
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert len([k for k in old if not k.endswith('^{}')])==1514 and all(remote.get(k)==v for k,v in old.items())
put(R/'RECORD242_ACTUAL_EVAL_AND240_CLOSING_ONCE_CONSUMED.json',dict(epoch=time.time(),ID=ID,TAG=TAG,protected1514_old_objects_peels=True,training240_tag_never_rerecorded=True,model_raw_GPU_or_experiment_reads_for_Git=0))
roots=[('source242',N),('closed240/reports',C/'reports'),('closed240/normal240_V2_path_reader',C/'normal240_V2_path_reader'),('closed240/normal_V2_INDEX',C/'INDEX240_NORMAL_READERS_V2_PATH_FROZEN.json'),('closed240/consolidation_source',T/'consolidate_closed240_actual85_from_saved_JSON_once.py')]
scope=R/'CAPTURE242_FROZEN_ACTUAL_SCOPE.json'
put(scope,dict(epoch=time.time(),phase=ID,roots=[dict(archive_label=k,path=str(p))for k,p in roots],includes='All242 frozen source/newCPU/actual admission/fourcase/fullUTF8/SSH receipts and both app automation updates; all240 reports including original normal pathfalse/V2actualfee/formalCPU and historical references.',binary_policy='Metadata only from existing producer SHA; no model/raw/GPU reads for Git.',pending=['W35 latest2d0 full32s actual skill stillpending; same208 confirmed existing AUTH240V2 closed branch compatible, no sourcechange.', 'No new learning chosen after240; original2mm closure failed all4 cases, cause not yet isolated. New diagnosis requires independently frozen purpose/count admission.', 'E2/E3/all oldexpertfullskills/fullSuperMimic/true270 unfinished.']))
note=R/'ACTUAL242_EXPERIMENT_NOTE.md'
with note.open('x',encoding='utf8')as f:f.write('''The ONNX-matched model2050 adaptation240 completed its original one-hour save window with85 PPO updates/40.8M own transitions, iteration2135/17Adam42940. Its new formal0f5de75a...552a07 is22,099,209B and passed the one admitted wholeCPU decode:259finite tensors/full actor35critic38STD6/hidden12864/32/DR/mixed mask/original JUMP memory. Final adaptive optimizer LR is0.0019461950683593758. All original processes exited and locks/account settled; original rawfee3647.559406042099 was summed once. The original collector refused a wrong saved-receipt filename before CIM/marker/network. An independent V2 repaired only that path and report/index prefixes, preserving the signed local+remote900 timing, original owner/node waits and budget code. Both the original false and the actual V2 success are retained.

New evaluation242 used that exact final model once on GPU168 with fresh ten ownMOD4 environments, fresh current CNone/resource/private/shared lock admission, actor-only deterministic mean and the original400N50Hz/fullD0-D7/2.5msTGS32/4/clip6/PD/delay/2mm closure/.01 mimic recipe. Source tests were new saved-JSON/schema/AST checks, not old fixture replays. The original disjointE0 ground and byte-literal19-method/16-weight FudanJUMP rewards and physics were unchanged. The four controlled first episodes requested up to10s each; standing ended at5.42s, forward.28s, reverse.32s, JUMP.34s, all on original closure only. Total318controls/2544physics/636feedback, no learning/GO/account write or Critic/WM forward. All children waited0, ENVclose returned, APPclose requested; a post-Appclose-return marker was absent and is not invented. ROOT SSH and sessions closed/restored/FREE.

Each case exhibited sampled bilateral wheel-air (both already-read force norms<=1N and both original authored collision bottoms>5mm for>=2 consecutive50Hz endpoints). Standing had15runs/177candidate endpoints; forward1/8, reverse1/11, JUMP1/12. The JUMP endpoint span was.22s; .34s is episode duration until reset. Standing also bounced. Penalized nonwheel forces did not exceed1N at candidate endpoints, but this does not certify continuous400Hz/full-body flight or stable landing. All four requested windows were incomplete; physical skill did not pass, and270mm success remains unachieved. The leftcrank is not locked atclip6 in these cases; the rightwheel channel sometimes clips. No unique DR/reward/action/solver cause is established and no guard or reward change or blind continuation is selected.

Four generated NPZs are retained remotely with existing producer path/bytes/SHA only, with no download/read. Models/ONNX/NPZ/USD/raw/media are never reopened for Git. This new evaluation phase also appends all closed240 reports, normal-reader failures/repair and the two automation update receipts. The same authorized W35 child confirmed the already-frozen AUTH240V2 caller supports the actual same240 closed+freshCNone branch; its --closing/--new-cpu remain W35 D227 qualification inputs, not model240. No W35 source/fixture/model/SDK/remote action was repeated. Existing1514 tag objects and peels are protected, and240 is not re-tagged. Future diagnostics must freeze a new necessary purpose and counts; there is no current ownH1 learning.
''')
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for p in (G/'versions').rglob('CAPTURE_INDEX*.json'):
 try:i=read(p)
 except(UnicodeDecodeError,json.JSONDecodeError):continue
 for row in i.get('files',[]):
  sha=row.get('SHA')or row.get('sha256');gp=row.get('Git_path')or row.get('git_path')
  if sha and gp and row.get('capture')=='full_UTF8_byte_exact'and(G/gp).is_file():known.setdefault(sha,gp)
binary={'.pt','.pth','.onnx','.data','.npz','.npy','.usd','.usda','.usdc','.stl','.obj','.mtl','.zip','.tar','.gz','.7z','.png','.jpg','.jpeg','.mp4','.avi','.mat','.slx','.jsonl','.bin','.pyc','.pyd','.dll','.hf'}
texttypes={'.py','.json','.txt','.md','.log','.xml','.yaml','.yml','.toml','.sh','.ps1','.cfg','.ini','.csv','.tsv','.m','.urdf','.diff','.sha256','.patch'}
def project(value):
 count=0
 if isinstance(value,dict):
  if isinstance(value.get('path'),str)and Path(value['path']).suffix.lower()in binary and 'UTF8'in value:return{k:v for k,v in value.items()if k!='UTF8'}|dict(capture='embedded_binary_metadata_only_original_full_report_retained_locally'),1
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
 for p in ([root]if root.is_file()else sorted(root.rglob('*'))):
  if not p.is_file()or'__pycache__'in p.parts:continue
  if p.suffix.lower()in binary or p.name.startswith('events.out.tfevents'):
   rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA='unknown',capture='metadata_only_no_content_or_hash_for_Git'));continue
  assert p.suffix.lower()in texttypes,str(p)
  b=p.read_bytes();sha=hashlib.sha256(b).hexdigest()
  if sha in known:rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
  dest=V/label/(p.name if root.is_file()else p.relative_to(root));dest.parent.mkdir(parents=True,exist_ok=True)
  try:text=b.decode('utf8')
  except UnicodeDecodeError:
   safe,count=redact(b.decode('latin1'));value=b if not count else safe.encode('latin1');dest=dest.with_name(dest.name+'.bytes.b64.txt');dest.write_text(base64.b64encode(value).decode('ascii')+'\n',encoding='ascii')
   gp=dest.relative_to(G).as_posix();rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=gp,capture='byte_exact_base64_nonUTF8_source'if not count else'credential_redacted_base64_nonUTF8_source',archive_decoded_SHA=hashlib.sha256(value).hexdigest(),redactions=count));selected.append(gp);continue
  projected=0
  if p.suffix.lower()=='.json':
   try:obj,projected=project(json.loads(text))
   except json.JSONDecodeError:pass
   if projected:text=json.dumps(obj,indent=2,ensure_ascii=False)
  safe,count=redact(text);value=b if not count and not projected else safe.encode('utf8');dest.write_bytes(value);gp=dest.relative_to(G).as_posix()
  rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,binary_metadata_projections=projected,capture='full_UTF8_except_embedded_binary_metadata_projection'if projected else('full_UTF8_credential_pattern_redacted'if count else'full_UTF8_byte_exact')));selected.append(gp)
  if not count and not projected:known[sha]=gp
formal=read(C/'reports/ROOT240V2_NEW_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')['roles']['jump_72']
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,remote_artifacts_metadata_only=[c['producer']for c in x['cases']],new_formal_metadata_only={k:formal[k]for k in('path','bytes','SHA','saved_iteration','Adam17_step','new_PPO_updates')},model_raw_GPU_or_experiment_reads_for_Git=0,pending=read(scope)['pending'],protected1514_old_objects_peels=True),indent=2,ensure_ascii=False),encoding='utf8');selected.append(index.relative_to(G).as_posix())
import record_experiment as recorder
original_git=recorder.git
def batch(*a):
 if a[:2]==('add','--'):
  for i in range(2,len(a),24):original_git('add','--',*a[i:i+24])
  return''
 return original_git(*a)
recorder.git=batch
note_gp=next(r['Git_path']for r in rows if r['path']==str(note));note_repo=G/note_gp
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Evaluate trained2050 adaptation240: wheel-air observed but all short ground and jump cases hit original closure', '--kind','evaluation','--note-file',str(note_repo),'--validation','240 complete85PPO/40.8M/2135/42940/259finite and finalsave>=deadline/rawfeeSUMONCE; V1 pathfalse+V2 actual retained; new242 source3groups7AST13reject/freshCNone/private-shared/resource/oneGPUread; fourmeanfirstepisodes271/14/16/17controls allclosure,318controls2544physics636feedback; bilateralwheelair50Hz evidence18runs not stablelanding/270; wait0/ENVcloseRETURNED/APPcloseREQUESTED/SSHFREE; no rewardguardchange,oldmodel/rawreplay or newlearning; protect1514oldobjectspeels','--files',*selected,'--push'];recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head and git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,protected1514_old_objects_peels=True,tag_count=1515,indexed_files=len(rows),new_full_files=len(selected),clean=True)))
