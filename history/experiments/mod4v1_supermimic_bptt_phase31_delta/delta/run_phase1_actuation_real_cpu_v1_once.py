"""One NEW original action queue/tap real CPU purpose; never SDK/selected PT/CUDA/C."""
from pathlib import Path
import sys,time,json,hashlib,ast,shlex
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_ACTUATION_REAL_CPU_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/ACTUATION_REAL_CPU_V1_STARTED_ONCE.json';assert not out.exists()and not marker.exists();payload={};pins={}
for folder,source,expected in [('fixture','source_phase1_actuation_real_cpu_fixture_v1','14d7223d09842dddb8e90ab7ee236f3a87aff30e671fab6ef6fe36dad79a9a5a'),('tap','source_phase1_actuation_capture_v1','ed77f3a3b0ce7aea6f904a09be8d038097bfb00729d57bec94feae5ab67bd081')]:
 D=R/source;sealraw=(D/'SOURCE_SEAL.json').read_bytes();assert hashlib.sha256(sealraw).hexdigest()==expected;seal=json.loads(sealraw);assert len(seal['files'])==8;payload[folder+'/SOURCE_SEAL.json']=sealraw;pins[folder+'/SOURCE_SEAL.json']=dict(bytes=len(sealraw),SHA256=expected)
 for name,meta in seal['files'].items():
  path=(D/name).resolve();assert path.is_relative_to(D);raw=path.read_bytes();assert len(raw)==meta['bytes']and hashlib.sha256(raw).hexdigest()==meta['sha256'];payload[folder+'/'+name]=raw;pins[folder+'/'+name]=meta
qp=R/'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/action_delay_physics_queue.py';raw=qp.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha=='a4238c581611ef7cdb710692291ddac48e076364b0587f631eb71fd6a7d15eb8';payload['original/action_delay_physics_queue.py']=raw;pins['original/action_delay_physics_queue.py']=dict(bytes=len(raw),SHA256=sha)
script_name='phase1_actuation_real_cpu_v1.py';raw=(R/'PAPER_ALIGNED_REBUILD_20261103'/script_name).read_bytes();ast.parse(raw);payload[script_name]=raw;pins[script_name]=dict(bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest());B='/home/lc01/Zonglin Li/zonglin2';job=B+'/tasks/PHASE1_ACTUATION_REAL_CPU_V1_'+str(time.time_ns());script=job+'/'+script_name;result=job+'/ACTION_CPU_RESULT_V1.json'
marker.write_text(json.dumps(dict(kind='NEW_PHASE1_ORIGINAL_QUEUE_TORCH_CPU_FIXTURE',epoch=time.time(),remote_root=job,source_pins=pins,SDK_model_GPU_canonical_operations=0),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('New CPU action root exists')
 s.mkdir(job)
 for folder in ('fixture','tap','original'):s.mkdir(job+'/'+folder)
 for name,data in payload.items():
  with s.open(job+'/'+name,'wb')as f:f.write(data)
 code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1';sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(job,[script,'--source-dir',job,'--output',result],script)
 i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=180);i.close();stdout=o.read().decode('utf-8','replace');stderr=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status();v=dict(kind='ACTUAL_PHASE1_ORIGINAL_ACTION_QUEUE_TORCH_CPU_V1',remote_root=job,source_pins=pins,returncode=rc,stdout=stdout,stderr=stderr,native_BPTT_updates=0,selected_model_raw_or_SDK_GPU_canonical_operations=0);out.write_text(json.dumps(v,indent=2),encoding='utf-8');assert rc==0,stderr
 with s.open(result,'rb')as f:v['receipt']=json.loads(f.read())
 out.write_text(json.dumps(v,indent=2),encoding='utf-8');r=v['receipt'];assert r['status']=='PASS'and r['case_N']==[2,3]and r['normal_apply_ticks_total']==864 and not r['actual_native_binding_pass']
 print(json.dumps(dict(report=str(out),status=r['status'],N=r['case_N'],totals=[x['totals']for x in r['cases']],source_global_RNG_unchanged=r['global_Python_Torch_CPU_RNG_unchanged'],actual_native_binding_pass=r['actual_native_binding_pass'],gate=r['stage1_status']),indent=2))
finally:s.close();c.close()
