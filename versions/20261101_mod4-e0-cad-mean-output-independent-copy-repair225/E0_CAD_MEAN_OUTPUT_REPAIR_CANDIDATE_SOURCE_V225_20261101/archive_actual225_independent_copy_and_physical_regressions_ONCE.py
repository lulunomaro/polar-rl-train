"""Archive actual new219 PPO once, preserving pre-GO failures and prior210 closure.
No experiments/model/raw/GPU actions are performed for Git.
"""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;G=T.parent/'polar-rl-train';R=N/'reports'
ID='mod4-e0-cad-mean-output-independent-copy-repair225'
TAG='trial-20261101-'+ID;V=G/'versions'/('20261101_'+ID)
def read(p):return json.loads(Path(p).read_bytes())
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{x.split()[1]:x.split()[0]for x in s.splitlines()if x.strip()}
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False)
assert not git('status','--porcelain')and not V.exists()
assert not git('tag','--list','*'+ID+'*'),'Existing actual225 repair phase is consumed; do not record/retag'
scope=read(R/'CAPTURE225_ACTUAL_FROZEN_SCOPE.json')
assert read(R/'ROOT225_ACTUAL_BOUND_COPY_AND_OWN_READBACK_CPU_RETURNED_ACTUAL.json')['passed']
assert read(T/'E0_CANDIDATE225_CONTROLLED_PHYSICAL_REGRESSION_V230_20261101/reports/ROOT230_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
request=read(R/scope['automation_request_file'])
app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert app['prompt']==request['prompt'].rstrip('\n')and app['status']=='ACTIVE'and app['rrule']==request['rrule']and app['target_thread_id']==request['targetThreadId']
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert len([k for k in old if not k.endswith('^{}')])==1506 and all(remote.get(k)==v for k,v in old.items())
put('ARCHIVE225_ACTUAL_REPAIR_ONCE_CONSUMED_BEFORE_RECORD.json',dict(epoch=time.time(),ID=ID,TAG=TAG,protected1506_old_objects_peels=True,
 no_model_binary_raw_or_hostGPU_reads_for_Git=True,all_original_source_reader_errors_and_before_use_repairs_preserved=True))
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for index in(G/'versions').rglob('CAPTURE_INDEX.json'):
 try:x=read(index)
 except(UnicodeDecodeError,json.JSONDecodeError):continue
 for row in x.get('files',[]):
  sha=row.get('SHA')or row.get('sha256');p=row.get('Git_path')or row.get('git_path')
  if sha and p and row.get('capture')=='full_UTF8_byte_exact'and(G/p).is_file():known.setdefault(sha,p)
binary={'.pt','.pth','.onnx','.npz','.npy','.usd','.usda','.usdc','.stl','.obj','.mtl','.zip','.tar','.gz','.7z','.png','.jpg','.jpeg','.mp4','.avi','.mat','.slx','.jsonl','.bin','.pyc','.pyd','.dll','.hf'}
texttypes={'.py','.json','.txt','.md','.log','.xml','.yaml','.yml','.toml','.sh','.ps1','.cfg','.ini','.csv','.tsv','.m','.urdf','.diff','.sha256','.patch'}
def project(value):
 count=0
 if isinstance(value,dict):
  if isinstance(value.get('path'),str)and Path(value['path']).suffix.lower()in(binary-{'.jsonl'})and'UTF8'in value:
   return{k:v for k,v in value.items()if k!='UTF8'}|dict(capture='embedded_binary_metadata_only_original_full_report_retained_locally'),1
  out={}
  for k,v in value.items():out[k],n=project(v);count+=n
  return out,count
 if isinstance(value,list):
  out=[]
  for x in value:y,n=project(x);out.append(y);count+=n
  return out,count
 return value,0
known_binary={str(Path(x['path']).resolve()).lower():x for x in scope.get('binary_local_producer_metadata',[])}
V.mkdir();rows=[];selected=[]
for root_text in scope['roots']:
 root=Path(root_text)
 for source in ([root] if root.is_file() else sorted(root.rglob('*'))):
  if not source.is_file()or'__pycache__'in source.parts:continue
  rel=Path(source.name) if root.is_file() else source.relative_to(root);size=source.stat().st_size
  if source.suffix.lower()in binary or source.name.startswith('events.out.tfevents'):
   meta=known_binary.get(str(source.resolve()).lower(),{})
   rows.append(dict(path=str(source.resolve()),bytes=size,SHA=meta.get('SHA','unknown'),producer=meta.get('producer','Existing producer metadata only'),capture='metadata_only_no_content_or_hash_for_Git'));continue
  assert source.suffix.lower()in texttypes or any(x in source.name.lower()for x in('.py.','.py_','.json.','.sh.','.m.','.xml.')),str(source)
  raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in known:
   rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
  try:text=raw.decode('utf8')
  except UnicodeDecodeError:
   safe,count=redact(raw.decode('latin1'));value=raw if count==0 else safe.encode('latin1')
   dest=V/(root.parent.name if root.is_file() else root.name)/(rel.as_posix()+'.bytes.b64.txt');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(base64.b64encode(value).decode('ascii')+'\n',encoding='ascii')
   rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=dest.relative_to(G).as_posix(),archive_decoded_SHA=hashlib.sha256(value).hexdigest(),redactions=count,capture='byte_exact_base64_nonUTF8_source'if count==0 else'credential_redacted_base64_nonUTF8_source'));selected.append(dest.relative_to(G).as_posix());continue
  projected=0
  if source.suffix.lower()=='.json':
   try:obj,projected=project(json.loads(text))
   except json.JSONDecodeError:pass
   if projected:text=json.dumps(obj,ensure_ascii=False,indent=2)
  safe,count=redact(text);dest=V/(root.parent.name if root.is_file() else root.name)/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  value=raw if not count and not projected else safe.encode('utf8');dest.write_bytes(value)
  rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=dest.relative_to(G).as_posix(),archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,binary_embeddings_projected_to_metadata=projected,
   capture='full_UTF8_except_embedded_binary_metadata_projection'if projected else('full_UTF8_byte_exact'if count==0 else'full_UTF8_credential_pattern_redacted')))
  selected.append(dest.relative_to(G).as_posix())
  if not count and not projected:known[sha]=dest.relative_to(G).as_posix()
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,trials=scope['trials'],pending_excluded=scope['pending_excluded'],remote_artifacts_metadata_only=scope['remote_artifacts_metadata_only'],model_raw_binary_or_GPU_for_Git=0),indent=2,ensure_ascii=False),encoding='utf8');selected.append(index.relative_to(G).as_posix())
note=V/'EXPERIMENT_NOTE.md';note.write_text((R/'ACTUAL225_REPAIR_EXPERIMENT_NOTE.md').read_text('utf8'),encoding='utf8');selected.append(note.relative_to(G).as_posix())
import record_experiment as recorder
original_git=recorder.git
def batch(*a):
 if a[:2]==('add','--'):
  for i in range(2,len(a),24):original_git('add','--',*a[i:i+24])
  return''
 return original_git(*a)
recorder.git=batch
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title',
 'Create an independently bound E0 action-head repair copy and test original-guard physical regressions',
 '--kind','repair','--note-file',str(note),'--validation',
 'Actual SDK action closure and optimizer identity; 259-finite-tensor independent copy with same-input mean target equivalence; four bounded physical regression purposes and all original failures; W35 continuation source only unless separately admitted; preserve 1506 old tag objects and peels',
 '--files',*selected,'--push'];recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head and git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,protected1506_objects_peels=True,tag_count=1507,indexed_files=len(rows),clean=True)))
