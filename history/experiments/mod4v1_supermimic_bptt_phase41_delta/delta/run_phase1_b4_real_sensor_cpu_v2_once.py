"""One new real B4/Sensor/Delay CPU software-contract purpose, not native."""
from pathlib import Path,PurePosixPath
import sys,json,hashlib,shlex,time
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_B4_ACTUAL_REAL_SENSOR_CPU_V2.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_B4_REAL_SENSOR_CPU_V2_STARTED_ONCE.json';assert not out.exists()and not marker.exists();H=lambda b:hashlib.sha256(b).hexdigest();payload={};fdir=R/'source_phase1_b4_real_sensor_cpu_fixture_v2'
prior=json.loads((R/'reports/PHASE1_B4_ACTUAL_REAL_SENSOR_CPU_V1.json').read_bytes());assert prior['returncode']==1 and prior['receipt']['fixture_result']is None and prior['receipt']['all_uploaded_source_bytes_unchanged']and 'Index put requires'in prior['receipt']['error']['message']
for label,d,n,sha,count in [('b4',R/'source_phase1_passive_sensor_capture_v4',3824,'81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3',21),('codec',R/'source_phase1_typed_capture_codec_v1',1427,'2cc26eaee058d30c9ac5b17ca8fb37541beb7c1e5ddbb738963ddef08c199219',7),('fixture',fdir,1295,'89c85204dc27025737995090063676dd1aca56b104c0a1c68de1ac4af371577d',7)]:
 raw=(d/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(n,sha);s=json.loads(raw);assert len(s['files'])==count;payload[label+'/SOURCE_SEAL.json']=raw
 for name,row in s['files'].items():
  assert Path(name).name==name and Path(name).suffix.lower()in('.py','.json','.txt','.md','.patch');b=(d/name).read_bytes();assert(len(b),H(b))==(row['bytes'],row['sha256']);payload[label+'/'+name]=b
pins=json.loads(payload['fixture/SOURCE_PINS.json'])['original_complete_cpu_sources']
for name,row in pins.items():
 p=Path(row['path']);assert p.is_relative_to(R/'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4')and p.name==name and p.suffix=='.py';raw=p.read_bytes();assert(len(raw),H(raw))==(row['bytes'],row['sha256']);payload['original/'+name]=raw
assert set(pins)=={'sensor_mild_math.py','feedback_delay_mild.py'};program=R/'phase1_b4_real_sensor_cpu_program_v2.py';payload[program.name]=program.read_bytes();assert len(payload)==41
config=dict(kind='NEW_PARENT_B4_REAL_SENSOR_DELAY_SOFTWARE_CPU_ONLY_V2',epoch=time.time(),purpose='NEW_B4_REAL_SENSOR_DELAY_SOFTWARE_CPU_V2_NOT_NATIVE',files=[dict(relative=n,bytes=len(b),SHA256=H(b))for n,b in sorted(payload.items())],actual_native_preflight_parent_SDK_model_raw_C_or_resource_operations=0)
with marker.open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();B='/home/lc01/Zonglin Li/zonglin2';job=B+'/tasks/PHASE1_B4_REAL_SENSOR_CPU_V2_'+str(time.time_ns());config['remote_root']=job
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('Fresh CPU purpose root exists')
 s.mkdir(job);made={job}
 for rel,b in payload.items():
  target=PurePosixPath(job)/rel
  for parent in list(target.parents)[::-1]:
   parent=str(parent)
   if parent.startswith(job+'/')and parent not in made:s.mkdir(parent);made.add(parent)
  with s.open(str(target),'wx')as f:f.write(b)
 with s.open(job+'/INPUT.json','wx')as f:f.write(json.dumps(config,indent=2).encode())
 output=job+'/RESULT.json';argv=[job+'/'+program.name,'--root',job,'--output',output];code="import sys,runpy;sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(job,argv,argv[0]);i,o,e=c.exec_command('PYTHONDONTWRITEBYTECODE=1 '+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=1200);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();v=dict(config,returncode=rc,stdout=stdout,stderr=stderr)
 try:
  with s.open(output,'rb')as f:raw=f.read(2*1024*1024+1)
  assert len(raw)<=2*1024*1024;v.update(receipt=json.loads(raw),receipt_bytes=len(raw),receipt_SHA256=H(raw))
 except FileNotFoundError:v['receipt_missing']=True
 with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
 print(json.dumps({k:v[k]for k in('remote_root','returncode')},indent=2));print(stdout);print(stderr);assert rc==0,stderr
finally:s.close();c.close()
