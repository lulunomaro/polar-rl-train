"""Parent NEW actual typed-C2 CPU purpose; no old CPU suite or native replay."""
from pathlib import Path
import ast,hashlib,json,shlex,sys,time
R=Path(__file__).resolve().parent;D=R/'source_phase1_typed_c2_real_cpu_fixture_v1';out=R/'reports/PHASE1_TYPED_C2_ACTUAL_REAL_CPU_V2.json';mark=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_TYPED_C2_REAL_CPU_STARTED_ONCE_V2.json';assert not out.exists()and not mark.exists();H=lambda b:hashlib.sha256(b).hexdigest();checked={}
def checked_source(path,pin=None):
 path=Path(path).resolve();assert path.is_relative_to(R)and path.suffix.lower()in('.py','.json','.txt','.md','.patch');b=path.read_bytes()
 if pin is not None:assert(len(b),H(b))==pin
 checked[str(path)]=dict(bytes=len(b),SHA256=H(b));return b
sraw=checked_source(D/'SOURCE_SEAL.json',(1454,'0c1f4b30929c8dd6635e93eefdecb42318a03aebcd1896df4b7af93251dcb4a4'));seal=json.loads(sraw);assert seal['content_root_sha256']=='91738b873aeeb50a1a203f454b2ce2b19c48ae7eebfa60165925148e188a505b'and len(seal['files'])==7
for x in seal['files']:checked_source(D/x['relative'],(x['bytes'],x['sha256']))
sourcepins=json.loads(checked_source(D/'SOURCE_PINS.json'));payload={}
for name,x in sourcepins['runtime_sources'].items():
 b=checked_source(x['path'],(x['bytes'],x['sha256']));payload[Path(x['path']).name]=b
for x in sourcepins['readonly_upstream_seals'].values():
 p=Path(x['path']);s=json.loads(checked_source(p,(x['bytes'],x['sha256'])));members=s.get('members',s.get('files'));assert type(members)in(list,dict);members=([dict(name=name,**pin)for name,pin in members.items()]if type(members)is dict else members);assert len(members)=={'source_phase1_actuation_clock_scope_v2':5,'source_phase1_passive_sensor_capture_v4':21,'source_phase1_typed_capture_codec_v1':7,'source_phase1_typed_native_capture_v1':15}[p.parent.name]
 for m in members:checked_source(p.parent/(m.get('relative')or m.get('name')),(m['bytes'],m.get('SHA256')or m.get('sha256')))
for x in sourcepins['design_references']:checked_source(x['path'],(x['bytes'],x['sha256']))
payload['typed_c2_cpu_fixture.py']=checked_source(D/'typed_c2_cpu_fixture.py',(14088,'b43c4bc2b8790b4bafc05eefb33063047ba6c17173a8c12b9944e16de417f3cc'));payload['SOURCE_PINS.json']=checked_source(D/'SOURCE_PINS.json');program=checked_source(R/'phase1_typed_c2_real_cpu_program_v2.py')
for name,b in payload.items():
 if name.endswith('.py'):ast.parse(b)
ast.parse(program);pins={n:dict(bytes=len(b),SHA256=H(b))for n,b in payload.items()};payload['TYPED_C2_CPU_DRIVER.py']=program;payload['PINS.json']=json.dumps(pins).encode();B='/home/lc01/Zonglin Li/zonglin2';job=B+'/tasks/PHASE1_TYPED_C2_REAL_CPU_V2_'+str(time.time_ns());config=dict(kind='NEW_TYPED_C2_REAL_CPU_COUPLING_FUNCTIONAL_PURPOSE_NOT_NATIVE_V2',epoch=time.time(),root=job,verified_local_SOURCE=checked,uploaded_source={n:dict(bytes=len(b),SHA256=H(b))for n,b in payload.items()},expected_N=80,expected_controls=64,fixture_is_not_SDK_clock_or_natural_reset=True,actual_GPU_model_raw_SDK_C_lock_or_parent_operations=0)
with mark.open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('CPU purpose root exists')
 s.mkdir(job)
 for name,b in payload.items():
  with s.open(job+'/'+name,'wx')as f:f.write(b)
 script=job+'/TYPED_C2_CPU_DRIVER.py';invoke="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';sys.path.insert(0,%r);runpy.run_path(%r,run_name='__main__')"%(job,script);i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(invoke),timeout=300);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();v=dict(config,returncode=rc,stdout=stdout,stderr=stderr,local_pinned_Source_unchanged=all((Path(p).read_bytes().__len__(),H(Path(p).read_bytes()))==(z['bytes'],z['SHA256'])for p,z in checked.items()))
 if stdout.strip():
  try:v['receipt']=json.loads(stdout)
  except json.JSONDecodeError:v['receipt_parse_error']='NO_SINGLE_JSON_RECEIPT'
 with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
 assert rc==0,stderr or stdout
 assert v['local_pinned_Source_unchanged']and v['receipt']['status']=='PASS',v.get('receipt')
 print(json.dumps(dict(report=str(out),returncode=rc,status=v['receipt']['status'],result=v['receipt']['fixture_result'],stage2_GO=False),indent=2))
finally:s.close();c.close()
