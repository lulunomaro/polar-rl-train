"""New CPU import-only predecode check: no PT/FINAL/TASK/raw, no model instances."""
from pathlib import Path
import json,sys,time,shlex,hashlib
R=Path(__file__).resolve().parent;out=R/'reports/REPLAY_DIAGNOSTIC_IMPORT_PREDECODE_V1.json';marker=R/'REPLAY_DIAGNOSTIC_IMPORT_PREDECODE_V1_STARTED_ONCE.json';assert not out.exists()and not marker.exists()
v=json.loads((R/'reports/REPLAY_CONSISTENCY_TORCH_SMOKE_V1.json').read_bytes());assert v['returncode']==0 and v['receipt']['status']=='PASS'and v['receipt']['production_checkpoint_raw_FINAL_TASK_opens']==0
source=v['remote_root'];assert source.startswith('/home/lc01/Zonglin Li/zonglin2/tasks/REPLAY_CONSISTENCY_TORCH_SMOKE_V1_')
B='/home/lc01/Zonglin Li/zonglin2';base=B+'/tasks/MOD4V1_SUPERMIMIC_BPTT8_V1_20261102_181251_1793614371303119100/roles/E0/worker_sources';job=B+'/tasks/REPLAY_DIAGNOSTIC_IMPORT_PREDECODE_V1_'+str(time.time_ns());result=job+'/SOURCE_RUNTIME_IMPORT_PREDECODE_V1.json'
code='''import os,sys,random,json,hashlib,importlib.util
from pathlib import Path
from types import SimpleNamespace
os.environ['CUDA_VISIBLE_DEVICES']='';sys.dont_write_bytecode=True
source=SOURCE;sys.path[:0]=[source,DEPS]
p=Path(source)/'replay_consistency_diagnostic_v1.py';assert hashlib.sha256(p.read_bytes()).hexdigest()=='a372478e40d1eb0b569f1f6c86d45f285031ab5399e00efe61b20bdc2f462eec'
spec=importlib.util.spec_from_file_location('_new_import_predecode_diagnostic',p);d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
args=SimpleNamespace(bridge_source=Path(source)/'native_supermimic_bridge.py',core_source=Path(source)/'ctx_reward_full_resume_candidate_v3.py',raw35_source=Path(source)/'command_tracking_torch_candidate_v1.py',cache_source=Path(source)/'frozen_a1_raw35_v1.py',vendor_parent=Path(VENDOR),dependency_path=[Path(DEPS)])
before=random.getstate();rt=d.source_runtime(args);same=random.getstate()==before
value=dict(kind='SOURCE_RUNTIME_IMPORT_PREDECODE_CPU_ONLY_V1',Python_RNG_unchanged_across_exact_source_runtime=same,CUDA_initialized=rt.t.cuda.is_initialized(),sources=rt.sources,checkpoint_FINAL_TASK_raw_opens=0,WM_aux_policy_or_optimizer_instances=0,native_updates=0)
with open(RESULT,'x',encoding='utf-8')as f:json.dump(value,f,indent=2)
print(json.dumps(value,indent=2));assert same and not rt.t.cuda.is_initialized()
'''
code=code.replace('source=SOURCE','source='+repr(source)).replace('DEPS',repr(base+'/sm_deps')).replace('VENDOR',repr(base)).replace('RESULT',repr(result))
marker.write_text(json.dumps(dict(epoch=time.time(),remote_root=job,source=source,PT_reads=0),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 s.mkdir(job);i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=180);i.close();text=o.read().decode('utf-8','replace');err=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status();value=dict(kind='ACTUAL_REPLAY_DIAGNOSTIC_IMPORT_PREDECODE_CHECK_V1',remote_root=job,returncode=rc,stdout=text,stderr=err,original_checkpoint_or_raw_reads=0);out.write_text(json.dumps(value,indent=2),encoding='utf-8')
 with s.open(result,'rb')as f:value['receipt']=json.loads(f.read())
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0;print(json.dumps(dict(report=str(out),returncode=rc,receipt=value['receipt']),indent=2))
finally:s.close();c.close()
