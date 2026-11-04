"""NEW bounded CPU volume purpose. Reuse full frozen inputs, never replay native/qualification."""
from pathlib import Path,PurePosixPath
import ast,sys,json,hashlib,shlex,time
R=Path(__file__).resolve().parent;H=lambda b:hashlib.sha256(b).hexdigest();out=R/'reports/PHASE1_TYPED_CAPTURE_ACTUAL_SIZE_CPU_V1.json';mark=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_TYPED_CAPTURE_SIZE_CPU_STARTED_ONCE_V1.json';assert not out.exists()and not mark.exists();payload={};checked={}
for name in('PHASE1_B4_ACTUAL_REAL_SENSOR_CPU_V2.json','PHASE1_TYPED_C2_ACTUAL_REAL_CPU_V2.json'):
 q=json.loads((R/'reports'/name).read_bytes());assert q['returncode']==0 and q['receipt']['status']=='PASS'
def source(path,pin=None):
 path=Path(path).resolve();assert path.is_relative_to(R)and path.suffix.lower()in('.py','.json','.md','.txt','.patch');b=path.read_bytes()
 if pin is not None:assert(len(b),H(b))==pin,str(path)
 checked[str(path)]=dict(bytes=len(b),SHA256=H(b));return b
def pack(label,d,n,sha,count):
 raw=source(d/'SOURCE_SEAL.json',(n,sha));s=json.loads(raw);members=s.get('members',s.get('files'));assert type(members)in(dict,list)
 rows=[dict(name=name,**row)for name,row in members.items()]if type(members)is dict else members;assert len(rows)==count
 payload[label+'/SOURCE_SEAL.json']=raw
 for row in rows:
  name=row.get('relative')or row.get('name');assert type(name)is str and Path(name).name==name
  payload[label+'/'+name]=source(d/name,(row['bytes'],row.get('SHA256')or row.get('sha256')))
for args in[
 ('b4',R/'source_phase1_passive_sensor_capture_v4',3824,'81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3',21),
 ('codec',R/'source_phase1_typed_capture_codec_v1',1427,'2cc26eaee058d30c9ac5b17ca8fb37541beb7c1e5ddbb738963ddef08c199219',7),
 ('b4_fixture',R/'source_phase1_b4_real_sensor_cpu_fixture_v2',1295,'89c85204dc27025737995090063676dd1aca56b104c0a1c68de1ac4af371577d',7),
 ('c2_fixture',R/'source_phase1_typed_c2_real_cpu_fixture_v1',1454,'0c1f4b30929c8dd6635e93eefdecb42318a03aebcd1896df4b7af93251dcb4a4',7),
 ('size',R/'source_phase1_typed_capture_size_cpu_fixture_v1',1529,'ff2ccc48aaf40e78aa709e09ad771c6571956f342cc5ae508a8c7d558bb35af4',5),
 ('actuation',R/'source_phase1_actuation_clock_scope_v2',5938,'105df1f6e47b82061aae729878a12874f731dd34b7cb0feeb75724028298469b',5),
 ('producer',R/'source_phase1_typed_native_capture_v1',3503,'f92384f7943d27a4d588316cfba129011ca47851571ff252040df4c740424966',15),
]:pack(*args)
math=json.loads(payload['b4_fixture/SOURCE_PINS.json'])['original_complete_cpu_sources'];assert set(math)=={'sensor_mild_math.py','feedback_delay_mild.py'}
for name,row in math.items():
 p=Path(row['path']);assert p.is_relative_to(R/'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4')and p.name==name;payload['original/'+name]=source(p,(row['bytes'],row['sha256']))
c2pins=json.loads(payload['c2_fixture/SOURCE_PINS.json'])['runtime_sources'];row=c2pins['queue'];p=Path(row['path']);assert p.name=='action_delay_physics_queue.py';payload['original/action_delay_physics_queue.py']=source(p,(row['bytes'],row['sha256']))
program=R/'phase1_typed_capture_size_cpu_program_v1.py';payload[program.name]=source(program)
for name,b in payload.items():
 if name.endswith('.py'):ast.parse(b)
paths=dict(b4_fixture='b4_fixture/cpu_fixture.py',c2_fixture='c2_fixture/typed_c2_cpu_fixture.py',worker='producer/worker_passive_interface_v1.py',parent='producer/single_gpu_passive_capture_parent_v1.py',contract='producer/phase1_capture_contract.py',observer='producer/phase1_capture_observer.py',runtime='producer/phase1_capture_runtime.py',codec='codec/typed_capture_codec.py',passive='b4/passive_capture.py')
sizepins=json.loads(payload['size/SOURCE_PINS.json']);assert set(paths)=={x['label']for x in sizepins['inputs']}
for row in sizepins['inputs']:
 b=payload[paths[row['label']]];assert(len(b),H(b))==(row['bytes'],row['SHA256'])
config=dict(kind='NEW_PARENT_TYPED_CAPTURE_FUNCTIONAL_SYNTHETIC_VOLUME_CPU_V1',epoch=time.time(),purpose='NEW_TYPED_CAPTURE_SYNTHETIC_MATERIALIZED_VOLUME_NOT_QUALIFICATION',files=[dict(relative=n,bytes=len(b),SHA256=H(b))for n,b in sorted(payload.items())],size_input_paths=paths,verified_local_source=checked,actual_native_model_raw_C_lock_or_resource_operations=0,native_size_guarantee=False)
with mark.open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();B='/home/lc01/Zonglin Li/zonglin2';job=B+'/tasks/PHASE1_TYPED_CAPTURE_SIZE_CPU_V1_'+str(time.time_ns());config['remote_root']=job
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('Fresh volume CPU purpose already exists')
 s.mkdir(job);made={job}
 for rel,b in payload.items():
  target=PurePosixPath(job)/rel
  for parent in list(target.parents)[::-1]:
   parent=str(parent)
   if parent.startswith(job+'/')and parent not in made:s.mkdir(parent);made.add(parent)
  with s.open(str(target),'wx')as f:f.write(b)
 with s.open(job+'/INPUT.json','wx')as f:f.write(json.dumps(config,indent=2).encode())
 output=job+'/RESULT.json';argv=[job+'/'+program.name,'--root',job,'--output',output];code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(job,argv,argv[0]);i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=1800);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();v=dict(config,returncode=rc,stdout=stdout,stderr=stderr)
 try:
  with s.open(output,'rb')as f:raw=f.read(2*1024*1024+1)
  assert len(raw)<=2*1024*1024;v.update(receipt=json.loads(raw),receipt_bytes=len(raw),receipt_SHA256=H(raw))
 except FileNotFoundError:v['receipt_missing']=True
 v['local_pinned_source_unchanged']=all((Path(p).read_bytes().__len__(),H(Path(p).read_bytes()))==(z['bytes'],z['SHA256'])for p,z in checked.items())
 with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
 print(json.dumps(dict(remote_root=job,returncode=rc,receipt=v.get('receipt'),local_pinned_source_unchanged=v['local_pinned_source_unchanged']),indent=2));assert rc==0 and v['receipt']['status']=='PASS'and v['local_pinned_source_unchanged'],stderr or stdout
finally:s.close();c.close()
