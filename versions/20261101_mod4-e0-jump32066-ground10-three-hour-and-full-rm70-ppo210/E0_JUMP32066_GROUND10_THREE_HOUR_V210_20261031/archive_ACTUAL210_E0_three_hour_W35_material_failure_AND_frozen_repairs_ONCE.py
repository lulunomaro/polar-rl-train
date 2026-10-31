"""Archive the actual210 learning phase once, including all failed startup/repairs.

Run only after the current model-free217 finite returns. Future210 closure is an
ordinary supplement; this recorder never resumes, watches, or stops training.
"""
from pathlib import Path
import base64, hashlib, json, subprocess, sys, time, tomllib

N=Path(__file__).resolve().parent;T=N.parent;G=T.parent/'polar-rl-train';R=N/'reports'
ID='mod4-e0-jump32066-ground10-three-hour-and-full-rm70-ppo210'
TAG='trial-20261101-'+ID;V=G/'versions'/('20261101_'+ID)
names=['W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031',
 'E0_JUMP32066_GROUND_RETENTION_CONTINUATION_V209_20261031',N.name,
 'W35_RM70_ORIGINAL_CAD_SCENE_ADMISSION_V211_20261101',
 'W35_RM70_OWN_MOD4_ROBOT_ADMISSION_V212_20261101',
 'OLD_EXPERTS_NORMALIZATION_NEXT_READY_SOURCE_V213_20261101',
 'W35_FULL_RM70_MATERIAL_LIMIT_REPAIR_SOURCE_V214_20261101',
 'W35_MATERIAL_FAILURE_OWNED_STOP_V215_20261101',
 'W35_USER_AUTHORIZED_EXACT_PROCESS_TERMINATION_V216_20261101',
 'W35_SHARED_MATERIAL_20K_ORIGINAL_PHYSX_ADMISSION_V217_20261101']

def read(p):return json.loads(Path(p).read_bytes())
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return {x.split()[1]:x.split()[0]for x in s.splitlines()if x.strip()}
def put(n,v):
 with (R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False)

assert not git('status','--porcelain') and not V.exists()
assert not git('tag','--list','*'+ID+'*') and not git('tag','--list','*ppo210*'),'Existing actual210 tag is consumed; do not record or retag'
first=read(R/'ROOT210_E0_72_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json')
assert first['passed'] and first['first']['actual_new_PPO_updates']>0
assert not read(R/'ROOT210_W35_72_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json')['passed']
ex=read(T/names[8]/'reports/ROOT216_ORIGINAL_POST_SIGNAL_EXIT_AND_NODE_RECEIPTS_ACTUAL.json')
assert ex['original_worker_status']['original_out'] and ex['private_EX_free']
probe=read(T/names[9]/'reports/ROOT217_ORIGINAL_20K_SHARED_MATERIAL_NATIVE_OR_ERROR_RETURNED_ACTUAL.json')
assert probe['all_own_children_waited'] and probe['private_EX_released']
assert read(T/names[9]/'reports/ROOT217_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
scope=read(R/'CAPTURE210_ACTUAL217_COMPLETE_FROZEN_SCOPE_V3.json')
request=read(R/scope['automation_request_file'])
app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert app['prompt']==request['prompt'].rstrip('\n') and app['status']=='ACTIVE'
assert app['rrule']=='FREQ=HOURLY;INTERVAL=1' and app['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
roots=[T/name for name in names]
for extra in scope.get('additional_frozen_roots',[]):
 root=Path(extra['path']);assert (root/extra['index']).is_file();roots.append(root)
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert len([k for k in old if not k.endswith('^{}')])==1503
assert all(remote.get(k)==v for k,v in old.items())
put('ARCHIVE210_ACTUAL_NEW_E0_PPO_AND_FAILED_W35_ONCE_CONSUMED.json',dict(
 epoch=time.time(),ID=ID,TAG=TAG,protected1503_old_objects_peels=True,
 E0_window_continues_not_stopped_for_Git=True,W35_no_PPO=True,
 model_raw_binary_GPU_reads_for_Git=0,all_false_and_errors_preserved=True))
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for index in (G/'versions').rglob('CAPTURE_INDEX.json'):
 try:previous=read(index)
 except (UnicodeDecodeError,json.JSONDecodeError):continue
 for row in previous.get('files',[]):
  sha=row.get('SHA')or row.get('sha256');path=row.get('Git_path')or row.get('git_path')
  if sha and path and row.get('capture')=='full_UTF8_byte_exact'and(G/path).is_file():known.setdefault(sha,path)
binary={'.pt','.pth','.onnx','.npz','.npy','.usd','.usda','.usdc','.stl','.obj','.mtl','.zip','.tar','.gz','.7z','.png','.jpg','.jpeg','.mp4','.avi','.mat','.slx','.jsonl','.bin','.pyc','.pyd','.dll','.hf'}
text_types={'.py','.json','.txt','.md','.log','.xml','.yaml','.yml','.toml','.sh','.ps1','.cfg','.ini','.csv','.tsv','.m','.urdf','.diff','.sha256','.patch'}
def project_binary_embeddings(value):
 count=0
 if isinstance(value,dict):
  if isinstance(value.get('path'),str)and Path(value['path']).suffix.lower()in(binary-{'.jsonl'})and'UTF8'in value:
   return {k:v for k,v in value.items()if k!='UTF8'}|dict(capture='embedded_binary_metadata_only_original_full_UTF8_retained_locally'),1
  out={}
  for k,v in value.items():
   out[k],n=project_binary_embeddings(v);count+=n
  return out,count
 if isinstance(value,list):
  out=[]
  for item in value:
   x,n=project_binary_embeddings(item);out.append(x);count+=n
  return out,count
 return value,0
known_binary={}
for manifest in (N/'PACKAGE210_MANIFEST.json',N/'PACKAGE210_W35_MANIFEST.json'):
 for row in read(manifest)['files']:
  p=row.get('local_path')
  if p and Path(p).suffix.lower()in binary:known_binary[str(Path(p).resolve()).lower()]=(row['SHA'],'Existing selected input installation manifest')
V.mkdir();rows=[];selected=[]
for root in roots:
 for source in sorted(root.rglob('*')):
  if not source.is_file()or'__pycache__'in source.parts:continue
  rel=source.relative_to(root);size=source.stat().st_size
  if source.suffix.lower()in binary or source.name.startswith('events.out.tfevents'):
   sha,producer=known_binary.get(str(source.resolve()).lower(),('unknown','Existing producer metadata only; no content/hash read for Git'))
   rows.append(dict(path=str(source.resolve()),bytes=size,SHA=sha,producer=producer,capture='metadata_only_no_content_read_for_Git'));continue
  assert source.suffix.lower()in text_types or any(x in source.name.lower()for x in('.py.','.py_','.json.','.sh.','.m.','.xml.')),str(source)
  raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in known:
   rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
  try:text=raw.decode('utf8')
  except UnicodeDecodeError:
   safe,count=redact(raw.decode('latin1'));encoded=raw if count==0 else safe.encode('latin1')
   dest=V/root.name/(rel.as_posix()+'.bytes.b64.txt');dest.parent.mkdir(parents=True,exist_ok=True)
   dest.write_text(base64.b64encode(encoded).decode('ascii')+'\n',encoding='ascii')
   rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=dest.relative_to(G).as_posix(),
    archive_decoded_SHA=hashlib.sha256(encoded).hexdigest(),redactions=count,
    capture='byte_exact_base64_nonUTF8_source'if count==0 else'credential_redacted_base64_nonUTF8_source',decode='Base64 decode excluding final newline'))
   selected.append(dest.relative_to(G).as_posix());continue
  binary_embeddings=0
  if source.suffix.lower()=='.json':
   try:obj,binary_embeddings=project_binary_embeddings(json.loads(text))
   except json.JSONDecodeError:binary_embeddings=0
   if binary_embeddings:text=json.dumps(obj,ensure_ascii=False,indent=2)
  safe,count=redact(text);dest=V/root.name/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  out=raw if count==0 and binary_embeddings==0 else safe.encode('utf8');dest.write_bytes(out)
  rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=dest.relative_to(G).as_posix(),archive_SHA=hashlib.sha256(out).hexdigest(),redactions=count,
   binary_embeddings_projected_to_metadata=binary_embeddings,
   capture='full_UTF8_except_embedded_binary_metadata_projection'if binary_embeddings else('full_UTF8_byte_exact'if count==0 else'full_UTF8_credential_pattern_redacted')))
  selected.append(dest.relative_to(G).as_posix())
  if count==0 and binary_embeddings==0:known[sha]=dest.relative_to(G).as_posix()
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,
 trials=scope['trials'],pending_excluded=scope['pending_excluded'],
 original_checkpoint_and_remote_artifacts_metadata_only=scope['remote_artifacts_metadata_only'],
 model_raw_NPZ_binary_or_host_GPU_reads_for_Git=0),indent=2,ensure_ascii=False),encoding='utf8')
selected.append(index.relative_to(G).as_posix())
note=V/'EXPERIMENT_NOTE.md';note.write_text((R/'ACTUAL210_ARCHIVE_NOTE_WITH217.md').read_text('utf8'),encoding='utf8');selected.append(note.relative_to(G).as_posix())
import record_experiment as recorder
original_git=recorder.git
def batched(*args):
 if args[:2]==('add','--'):
  for i in range(2,len(args),24):original_git('add','--',*args[i:i+24])
  return''
 return original_git(*args)
recorder.git=batched
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title',
 'Continue frozen-E0 copy with ground10 and literal JUMP for three hours; retain W35 material startup failure and repairs',
 '--kind','training','--note-file',str(note),'--validation',
 'E0 actual new PPO/fullstate FIRST; W35 original 64K failure and exact authorized owned exit; actual217 model-free material result preserved; all1503 older tags protected',
 '--files',*selected,'--push']
recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,protected1503_objects_peels=True,
 tag_count=1504,indexed_files=len(rows),clean=True,no_postGit_report_chasing=True)))
