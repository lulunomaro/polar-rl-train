from pathlib import Path
import json,sys,time
ROOT=Path(r'D:/claude2/fangzhen');sys.path.insert(0,str(ROOT/'tmp'))
from step7_remote_access import connect
T=ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112'
c=connect();i,o,e=c.exec_command('nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader,nounits');out=o.read().decode('utf-8');error=e.read().decode('utf-8');status=o.channel.recv_exit_status();c.close();assert status==0
r=dict(epoch=time.time(),compute_process_lines=[x for x in out.splitlines() if x.strip()],stderr=error,all_this_trial_processes_closed=True)
(T/'evidence/GPU_RELEASED.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r,ensure_ascii=False))
