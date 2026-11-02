"""New software-only CPU proof of the frozen raw35 mean evaluator.
Creates/reads its own SYNTHETIC full checkpoint, never a selected native model.
"""
from pathlib import Path
import json,sys,hashlib,shlex,time
R=Path(__file__).resolve().parent;S=R/'source_eval_a1_raw35_v1';out=R/'reports/A1_FROZEN_MEAN_POLICY_CPU_V1.json';marker=R/'A1_FROZEN_MEAN_POLICY_CPU_V1_ONCE.json';assert not out.exists()and not marker.exists();files={}
for name,sha in [('frozen_a1_raw35_v1.py','1ea4bcfa1081d63d0da2136fedf8c9fafa508d7bb2155095352da496327e4a21'),('remote_cpu_synthetic_check_v1.py','c8bcfed4826b2e37f0231c20967bdcb76934656be40aced2400312bf7d48d899')]:
 raw=(S/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha;files[name]=raw
native=json.loads((R/'SCHEDULE_CONFIG_REPAIRED_OWNER_DISPATCH_ONCE.json').read_bytes())['root'];job=native+'/source_checks/A1_FROZEN_MEAN_SOFTWARE_CPU_V1_'+str(time.time_ns());resultdir=job+'/NEW_SYNTHETIC_MEAN_RESULT';worker=native+'/roles/E0/worker_sources';value=dict(kind='SYNTHETIC_FROZEN_A1_MEAN_SOFTWARE_CPU_PURPOSE_V1',remote_root=job,source_SHA={n:hashlib.sha256(v).hexdigest()for n,v in files.items()},native_expert_BPTT_steps=0,original_PT_SDK_GPU_C_GO_lock_mutations=0);marker.write_text(json.dumps(value,indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 s.mkdir(job)
 for name,raw in files.items():
  with s.open(job+'/'+name,'wb')as f:f.write(raw)
 argv=[job+'/remote_cpu_synthetic_check_v1.py','--new-output',resultdir];bootstrap="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';sys.path[:0]=%r;sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%([job,worker,worker+'/sm_deps'],argv,argv[0]);cmd="CUDA_VISIBLE_DEVICES='' "+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(bootstrap)
 i,o,e=c.exec_command(cmd,timeout=300);i.close();txt=o.read().decode(errors='replace');err=e.read().decode(errors='replace');rc=o.channel.recv_exit_status();receipt=None
 try:
  with s.open(resultdir+'/REMOTE_CPU_SYNTHETIC_RESULTS_V1.json','rb')as f:receipt=json.loads(f.read())
 except OSError:pass
 value.update(returncode=rc,stdout=txt,stderr=err,receipt=receipt);out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2));assert rc==0,(rc,err)
finally:s.close();c.close()
