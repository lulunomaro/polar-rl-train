"""Ordinary240 supplement only: do not create,record or move any trial tag."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
T=Path(__file__).resolve().parent;G=T.parent/'polar-rl-train';N=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';R=N/'reports'
V=G/'versions/20261101_mod4-model2050-onnx-matched-literal-fudan-jump400n50-ground10-ppo240/SUPPLEMENT241_HEALTH_W35_AUTH240'
def read(p):return json.loads(Path(p).read_bytes())
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{x.split()[1]:x.split()[0]for x in s.splitlines()if x.strip()}
assert not git('status','--porcelain')and not V.exists()
tag='refs/tags/trial-20261101-mod4-model2050-onnx-matched-literal-fudan-jump400n50-ground10-ppo240'
assert git('rev-parse',tag)=='eb71fbfefa78be0572704cb2b812cee0e46154dd'
scope=read(R/'CAPTURE241_ORDINARY240_FROZEN_SCOPE.json');request=read(scope['automation_request_path'])
app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert app['prompt']==request['prompt'].rstrip('\n')and app['status']=='ACTIVE'and app['rrule']==request['rrule']and app['target_thread_id']==request['targetThreadId']
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert len([k for k in old if not k.endswith('^{}')])==1514 and all(remote.get(k)==v for k,v in old.items())
marker=R/'ARCHIVE241_ORDINARY240_ONCE_CONSUMED_NO_NEW_TAG.json'
with marker.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),scope='Ordinary240append',new_trial_tag=False,protected1514objects_peels=True,no_model_raw_SDK_GPU_or_experiment_replays_for_Git=True),f,indent=2)
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for p in(G/'versions').rglob('CAPTURE_INDEX*.json'):
 try:x=read(p)
 except(UnicodeDecodeError,json.JSONDecodeError):continue
 for row in x.get('files',[]):
  sha=row.get('SHA')or row.get('sha256');gp=row.get('Git_path')or row.get('git_path')
  if sha and gp and row.get('capture')=='full_UTF8_byte_exact'and(G/gp).is_file():known.setdefault(sha,gp)
paths=[Path(p)for p in scope['files']]+[marker,R/'CAPTURE241_ORDINARY240_FROZEN_SCOPE.json',Path(__file__).resolve()]
for p in map(Path,scope['roots']):paths += [q for q in p.rglob('*')if q.is_file()and'__pycache__'not in q.parts]
V.mkdir();rows=[];selected=[]
for p in dict.fromkeys(paths):
 assert p.suffix.lower()in('.py','.json','.txt','.md','.log'),str(p)
 b=p.read_bytes();sha=hashlib.sha256(b).hexdigest()
 if sha in known:
  rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
 text=b.decode('utf8');safe,count=redact(text);value=b if not count else safe.encode('utf8')
 rel=p.relative_to(T);dest=V/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(value)
 gp=dest.relative_to(G).as_posix();rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,
  capture='full_UTF8_byte_exact'if not count else'full_UTF8_credential_pattern_redacted'));selected.append(gp)
 if not count:known[sha]=gp
index=V/'CAPTURE_INDEX_SUPPLEMENT241.json';index.write_text(json.dumps(dict(epoch=time.time(),ordinary_parent_phase='mod4-model2050-onnx-matched-literal-fudan-jump400n50-ground10-ppo240',files=rows,
 new_trial_tag=False,all_old1514_objects_peels_preserved=True,model_raw_GPU_or_experiment_reads_for_Git=0,pending=scope['pending']),indent=2),encoding='utf8');selected.append(index.relative_to(G).as_posix())
for i in range(0,len(selected),24):git('add','--',*selected[i:i+24])
git('commit','-m','Append one human240 health snapshot and frozen W35 authority240 V1/V2 sources')
git('push','origin','main')
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert after==old and all(remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,indexed_files=len(rows),new_tag=False,tag_count=1514,protected_all_old_objects_peels=True,clean=True)))
