"""CPUsyntheticsoftwaretestwhileoriginalGPUresourcewait. Notatraininggrant, GoalBPTT0.
NoSDK/GPU/teacherPT/raw/Cwriteorphysicaltaskrestart."""
from pathlib import Path
import sys,json,shlex
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
out=R/'reports/SYNTHETIC_CPU_SOFTWARE_AUTOGRAD_V1.json';assert not out.exists();m=json.loads((R/'SUPERMIMIC_EIGHT_V1_DISPATCH_ONCE.json').read_bytes());root=m['root'];source=R/'source_runtime/synthetic_cpu_contract_check.py';c=connect72();s=c.open_sftp()
try:
 remote=root+'/SYNTHETIC_CPU_SOFTWARE_CHECK_V1.py';s.put(str(source),remote);code="import sys,runpy;sys.path[:0]=[%r,%r];runpy.run_path(%r,run_name='__main__')"%(root+'/roles/E0/worker_sources',root+'/roles/E0/worker_sources/sm_deps',remote);i,o,e=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=180);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();v=dict(kind='SOURCE_SOFTWARE_SYNTHETIC_CPU_RUN_NOT_REAL_EXPERT_BPTT',returncode=rc,stdout=txt,stderr=err,actual_native_expert_BPTT_updates=0,PT_raw_SDK_GPU_C_GO_operations=0);out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(out);print(json.dumps(v,indent=2));assert rc==0,(rc,err)
finally:s.close();c.close()
