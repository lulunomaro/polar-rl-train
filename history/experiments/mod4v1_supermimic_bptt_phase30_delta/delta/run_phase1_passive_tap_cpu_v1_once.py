"""One new CPU purpose, frozen component + original classes; no SDK or selected PT."""
from pathlib import Path
import sys,json,hashlib,ast,time,shlex
R=Path(__file__).resolve().parent;D=R/'source_phase1_passive_sensor_capture_v1';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PASSIVE_TAP_CPU_V1_STARTED_ONCE.json';out=R/'reports/PHASE1_PASSIVE_TAP_CPU_V1.json';assert not marker.exists()and not out.exists();sealraw=(D/'SOURCE_SEAL.json').read_bytes();assert hashlib.sha256(sealraw).hexdigest()=='3d5fd4febf9232a8113b4d93dbf8d3d6a19658690e973d6485c1aedc39e18881';seal=json.loads(sealraw);assert len(seal['files'])==13;payload={'SOURCE_SEAL.json':sealraw};pins={}
for m in seal['files']:
 path=(D/m['relative']).resolve();assert path.is_relative_to(D);raw=path.read_bytes();assert len(raw)==m['bytes']and hashlib.sha256(raw).hexdigest()==m['sha256'];payload[m['relative']]=raw;pins[m['relative']]=m
source=R/'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4'
for name,sha in {'sensor_mild_math.py':'aa853a74a2c2d8840d003caab13a853bade0d761cf7966e4d13c200b929817b8','feedback_delay_mild.py':'90b339a6d3690294798befefb33e7f27cb7c3bfa0d8e38c98312e207685b5665'}.items():
 raw=(source/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha;payload[name]=raw;pins[name]=dict(bytes=len(raw),sha256=sha)
script_name='phase1_passive_tap_cpu_v1.py';raw=(R/'PAPER_ALIGNED_REBUILD_20261103'/script_name).read_bytes();ast.parse(raw);payload[script_name]=raw;pins[script_name]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest());B='/home/lc01/Zonglin Li/zonglin2';job=B+'/tasks/PHASE1_PASSIVE_TAP_CPU_V1_'+str(time.time_ns());script=job+'/'+script_name;result=job+'/TAP_CPU_RESULT_V1.json'
marker.write_text(json.dumps(dict(kind='NEW_PHASE1_FROZEN_TAP_REAL_CLASSES_CPU',epoch=time.time(),remote_root=job,source_pins=pins,SDK_model_GPU_canonical_operations=0),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('New CPU tap root already exists')
 s.mkdir(job)
 for name,data in payload.items():
  assert '/'not in name and '\\'not in name
  with s.open(job+'/'+name,'wb')as f:f.write(data)
 code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1';sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(job,[script,'--source-dir',job,'--output',result],script)
 i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=180);i.close();stdout=o.read().decode('utf-8','replace');stderr=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status();v=dict(kind='ACTUAL_PHASE1_TORCH_CPU_PASSIVE_TAP_V1',remote_root=job,source_pins=pins,returncode=rc,stdout=stdout,stderr=stderr,native_updates=0,selected_model_raw_or_SDK_GPU_canonical_operations=0);out.write_text(json.dumps(v,indent=2),encoding='utf-8');assert rc==0,stderr
 with s.open(result,'rb')as f:v['receipt']=json.loads(f.read())
 out.write_text(json.dumps(v,indent=2),encoding='utf-8');r=v['receipt'];assert r['status']=='PASS'and r['actor35_native_equality_tested']is False
 print(json.dumps(dict(report=str(out),returncode=rc,status=r['status'],fixture=r['fixture'],gate=r['stage1_status']),indent=2))
finally:s.close();c.close()
