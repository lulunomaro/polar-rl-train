"""NEW Torch CPU software smoke for sealed replay diagnostic, no selected PT or SDK."""
from pathlib import Path
import sys,json,hashlib,time,shlex,ast
R=Path(__file__).resolve().parent
marker=R/'REPLAY_CONSISTENCY_TORCH_SMOKE_V1_STARTED_ONCE.json';out=R/'reports/REPLAY_CONSISTENCY_TORCH_SMOKE_V1.json'
assert not marker.exists()and not out.exists()
D=R/'source_replay_consistency_diagnostic_v1'
spec={
 'replay_consistency_diagnostic_v1.py':(D/'replay_consistency_diagnostic_v1.py',42537,'a372478e40d1eb0b569f1f6c86d45f285031ab5399e00efe61b20bdc2f462eec'),
 'smoke.py':(D/'torch_cpu_synthetic_smoke_v1/smoke.py',14049,'a56cf1ea2751357c118731175253cc676307362ca2de95e3b7f6705869ca7dd5'),
 'native_supermimic_bridge.py':(R/'source_runtime/native_supermimic_bridge.py',13125,'8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29'),
 'ctx_reward_full_resume_candidate_v3.py':(R/'source_quality_microtrain_resume_alias_v2/ctx_reward_full_resume_candidate_v3.py',36941,'20fd4945a0f2345c17505316560ae6d358fcce147c6988f62a08d867e084e749'),
 'command_tracking_torch_candidate_v1.py':(R/'source_command_review_v1/command_tracking_torch_candidate_v1.py',None,'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223'),
 'frozen_a1_raw35_v1.py':(R/'source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py',19226,'1ea4bcfa1081d63d0da2136fedf8c9fafa508d7bb2155095352da496327e4a21')}
payload={};pins={}
for name,(p,size,sha)in spec.items():
 raw=p.read_bytes();assert(size is None or len(raw)==size)and hashlib.sha256(raw).hexdigest()==sha;ast.parse(raw);payload[name]=raw;pins[name]=dict(bytes=len(raw),SHA=sha,path=str(p))
B='/home/lc01/Zonglin Li/zonglin2';base=B+'/tasks/MOD4V1_SUPERMIMIC_BPTT8_V1_20261102_181251_1793614371303119100/roles/E0/worker_sources';job=B+'/tasks/REPLAY_CONSISTENCY_TORCH_SMOKE_V1_'+str(time.time_ns());script=job+'/smoke.py';result=job+'/TORCH_CPU_SYNTHETIC_SMOKE_V1.json'
marker.write_text(json.dumps(dict(epoch=time.time(),kind='NEW_CPU_ONLY_SYNTHETIC_REPLAY_SMOKE',root=job,source_pins=pins,original_model_reads=0,SDK_or_CUDA_or_canonical_operations=0),indent=2),encoding='utf-8')
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('New smoke purpose root already exists')
 s.mkdir(job)
 for name,raw in payload.items():
  with s.open(job+'/'+name,'wb')as f:f.write(raw)
 argv=[script,'--diagnostic',job+'/replay_consistency_diagnostic_v1.py','--bridge-source',job+'/native_supermimic_bridge.py','--core-source',job+'/ctx_reward_full_resume_candidate_v3.py','--raw35-source',job+'/command_tracking_torch_candidate_v1.py','--cache-source',job+'/frozen_a1_raw35_v1.py','--vendor-parent',base,'--dependency-path',base+'/sm_deps','--output',result]
 code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1';sys.path[:0]=%r;sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%([job,base+'/sm_deps'],argv,script)
 i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=300);i.close();text=o.read().decode('utf-8','replace');err=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status()
 value=dict(kind='ACTUAL_TORCH_CPU_SYNTHETIC_REPLAY_SMOKE_V1',remote_root=job,source_pins=pins,returncode=rc,stdout=text,stderr=err,actual_original_checkpoint_reads=0,native_BPTT=0,SDK_canonical_GPU_operations=0)
 out.write_text(json.dumps(value,indent=2),encoding='utf-8')
 assert rc==0,err
 with s.open(result,'rb')as f:receipt=json.loads(f.read())
 value['receipt']=receipt;out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert receipt['status']=='PASS'and receipt['native_BPTT_updates']==0 and receipt['CUDA_initialized']is False
 print(json.dumps(dict(report=str(out),status=receipt['status'],tested=receipt['tested'],T=receipt['T'],N=receipt['N'],H16_windows=receipt['H16_windows'],no_actual_original_checkpoint_or_SDK_or_native_updates=True),indent=2))
finally:s.close();c.close()
