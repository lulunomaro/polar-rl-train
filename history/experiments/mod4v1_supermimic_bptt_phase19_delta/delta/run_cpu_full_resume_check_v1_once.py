"""New CPU software full-resume purpose; no native task launch or model source use."""
from pathlib import Path
import sys,json,shlex
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
out=R/'reports/SYNTHETIC_CPU_FULL_RESUME_V1.json';assert not out.exists();m=json.loads((R/'SUPERMIMIC_EIGHT_V1_DISPATCH_ONCE.json').read_bytes());root=m['root'];c=connect72();s=c.open_sftp()
try:
 remote=root+'/SYNTHETIC_CPU_FULL_RESUME_CHECK_V1.py'
 try:s.stat(remote)
 except FileNotFoundError:pass
 else:raise AssertionError('CPU fullresume purpose already staged')
 s.put(str(R/'source_runtime/synthetic_cpu_full_resume_check_v1.py'),remote);code="import sys,runpy;sys.path[:0]=[%r,%r];runpy.run_path(%r,run_name='__main__')"%(root+'/roles/E0/worker_sources',root+'/roles/E0/worker_sources/sm_deps',remote)
 i,o,e=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=180);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();v=dict(kind='SYNTHETIC_CPU_ONLY_FULL_RESUME_NO_REAL_EXPERT_UPDATES',returncode=rc,stdout=txt,stderr=err,actual_native_expert_BPTT_updates=0,selected_PT_raw_SDK_GPU_C_GO_operations=0);out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(out);print(json.dumps(v,indent=2));assert rc==0,(rc,err)
finally:s.close();c.close()
