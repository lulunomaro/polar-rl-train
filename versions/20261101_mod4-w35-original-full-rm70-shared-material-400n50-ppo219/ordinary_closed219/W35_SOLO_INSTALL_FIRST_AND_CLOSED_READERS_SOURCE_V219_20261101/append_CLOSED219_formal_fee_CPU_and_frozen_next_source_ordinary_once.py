"""Ordinary supplement of consumed219; no new trial/tag or experiment reads."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;G=T.parent/'polar-rl-train';R=N/'reports'
V=G/'versions/20261101_mod4-w35-original-full-rm70-shared-material-400n50-ppo219'
def read(p):return json.loads(Path(p).read_bytes())
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{x.split()[1]:x.split()[0]for x in s.splitlines()if x.strip()}
assert not git('status','--porcelain')and V.is_dir()
assert git('rev-parse','refs/tags/trial-20261101-mod4-w35-original-full-rm70-shared-material-400n50-ppo219')=='083e0444115d45d1d7616923142c6a370b80522f'
assert read(R/'ROOT219V3_NEW_W35_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')['passed']
req=read(R/'AUTOMATION_CLOSED219_QUALIFIED_AND_PENDING222_UPDATE_REQUEST.json')
app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert app['prompt']==req['prompt'].rstrip('\n')and app['status']=='ACTIVE'and app['rrule']==req['rrule']and app['target_thread_id']==req['targetThreadId']
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert len([x for x in old if not x.endswith('^{}')])==1505 and all(remote.get(k)==v for k,v in old.items())
scope=read(R/'CAPTURE_CLOSED219_ORDINARY_SCOPE.json')
with(R/'CLOSED219_ORDINARY_APPEND_ONCE_CONSUMED.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),no_record_experiment_or_new_tag=True,old_tag_count=1505,no_binary_model_raw_or_GPU_reads_for_Git=True),f,indent=2)
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for p in(G/'versions').rglob('CAPTURE_INDEX*.json'):
 try:x=read(p)
 except(UnicodeDecodeError,json.JSONDecodeError):continue
 for r in x.get('files',[]):
  sha=r.get('SHA')or r.get('sha256');path=r.get('Git_path')or r.get('git_path')
  if sha and path and r.get('capture')=='full_UTF8_byte_exact'and(G/path).is_file():known.setdefault(sha,path)
binary={'.pt','.pth','.onnx','.npz','.npy','.usd','.usda','.usdc','.stl','.obj','.mtl','.zip','.tar','.gz','.7z','.png','.jpg','.jpeg','.mp4','.avi','.mat','.slx','.jsonl','.bin','.pyc','.pyd','.dll','.hf'}
texttypes={'.py','.json','.txt','.md','.log','.xml','.yaml','.yml','.toml','.sh','.ps1','.cfg','.ini','.csv','.tsv','.m','.urdf','.diff','.sha256','.patch'}
def project(v):
 count=0
 if isinstance(v,dict):
  if isinstance(v.get('path'),str)and Path(v['path']).suffix.lower()in(binary-{'.jsonl'})and'UTF8'in v:
   return{k:x for k,x in v.items()if k!='UTF8'}|dict(capture='embedded_binary_metadata_only_local_original_report_preserved'),1
  out={}
  for k,x in v.items():out[k],n=project(x);count+=n
  return out,count
 if isinstance(v,list):
  out=[]
  for x in v:y,n=project(x);out.append(y);count+=n
  return out,count
 return v,0
localmeta={str(Path(x['path']).resolve()).lower():x for x in scope['binary_local_producer_metadata']}
destroot=V/'ordinary_closed219';destroot.mkdir(exist_ok=False);rows=[];selected=[]
for rootstr in scope['frozen_roots']:
 root=Path(rootstr)
 for source in sorted(root.rglob('*')):
  if not source.is_file()or'__pycache__'in source.parts:continue
  rel=source.relative_to(root);size=source.stat().st_size
  if source.suffix.lower()in binary or source.name.startswith('events.out.tfevents'):
   m=localmeta.get(str(source.resolve()).lower(),{});rows.append(dict(path=str(source.resolve()),bytes=size,SHA=m.get('SHA','unknown'),producer=m.get('producer','Existing producer metadata only'),capture='metadata_only_no_content_or_hash_for_Git'));continue
  assert source.suffix.lower()in texttypes or any(x in source.name.lower()for x in('.py.','.py_','.json.','.sh.','.m.','.xml.')),str(source)
  raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in known:
   rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
  projected=0
  try:text=raw.decode('utf8')
  except UnicodeDecodeError:
   safe,count=redact(raw.decode('latin1'));value=raw if count==0 else safe.encode('latin1');dest=destroot/root.name/(rel.as_posix()+'.bytes.b64.txt');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(base64.b64encode(value).decode('ascii')+'\n',encoding='ascii')
   rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=dest.relative_to(G).as_posix(),archive_decoded_SHA=hashlib.sha256(value).hexdigest(),redactions=count,capture='byte_exact_base64_nonUTF8_source'if count==0 else'credential_redacted_base64_nonUTF8_source'));selected.append(dest.relative_to(G).as_posix());continue
  if source.suffix.lower()=='.json':
   try:obj,projected=project(json.loads(text))
   except json.JSONDecodeError:pass
   if projected:text=json.dumps(obj,ensure_ascii=False,indent=2)
  safe,count=redact(text);value=raw if not count and not projected else safe.encode('utf8');dest=destroot/root.name/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(value)
  rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=dest.relative_to(G).as_posix(),archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,binary_embeddings_projected_to_metadata=projected,capture='full_UTF8_except_embedded_binary_metadata_projection'if projected else('full_UTF8_byte_exact'if count==0 else'full_UTF8_credential_pattern_redacted')))
  selected.append(dest.relative_to(G).as_posix())
  if not count and not projected:known[sha]=dest.relative_to(G).as_posix()
index=V/'CAPTURE_INDEX_CLOSED219_ORDINARY.json';index.write_text(json.dumps(dict(epoch=time.time(),same_consumed_phase='mod4-w35-original-full-rm70-shared-material-400n50-ppo219',files=rows,pending_excluded=scope['pending_excluded'],remote_artifacts_metadata_only=scope['remote_artifacts_metadata_only'],no_model_raw_GPU_for_Git=True),indent=2,ensure_ascii=False),encoding='utf8');selected.append(index.relative_to(G).as_posix())
for i in range(0,len(selected),24):git('add','--',*selected[i:i+24])
git('commit','-m','Append closed W35 RM70 PPO219 final, original fee and full-state CPU qualification')
git('push','origin','main')
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert after==old and all(remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag_count=1505,all1505_objects_peels_unchanged=True,indexed_files=len(rows),new_or_updated_text_files=len(selected),clean=True,no_new_trial_tag=True)))
