from pathlib import Path
import sys,json,base64,time
D=Path(__file__).resolve().parent;R=D/'reports';root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
assert not (R/'EVALUATOR_HANDOVER_LAUNCHED.json').exists();v=json.loads((R/'CURRENT_ACTUAL.json').read_text());assert v['reports']['HANDOVER_COMPLETED.json']['old_launch_permission_retired']
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval()
try:
 code=r'''
from pathlib import Path
import subprocess,json,time
D=Path('D:/MOD4_async_eval/closure_episode_clock2500_v15');assert not (D/'HANDOVER_LAUNCHED.json').exists()
p=subprocess.Popen(['D:/claude2/fangzhen/.venv-isaaclab/Scripts/pythonw.exe',str(D/'handover_eval_idle.py')],cwd=D,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)
v=dict(epoch=time.time(),CPU_handover_pid=p.pid,previous_jobs_finish_before_idle_retirement=True,new_scope_pending_actual_results=True,no_training_or_canonical_authority=True);(D/'HANDOVER_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
'''
 enc=base64.b64encode(code.encode()).decode();cmd='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
 _,o,e=c.exec_command(cmd,timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);(R/'EVALUATOR_HANDOVER_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
