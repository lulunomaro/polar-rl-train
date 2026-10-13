from pathlib import Path
import time,json,traceback
import transport_249_only as t
P=Path(__file__).resolve().parent;R=P/'reports'
q=R/'REFERENCE17B_INTERACTIVE_SSH_PARENT_ACTUAL.json';assert not q.exists()
code=r'''
import psutil,json,time
from pathlib import Path
p=psutil.Process(32952);assert abs(p.create_time()-1791907053.5134008)<.001
assert p.ppid()==23320
parent=psutil.Process(p.ppid())
actual=dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),exe=p.exe(),parent=p.ppid(),parent_creation=parent.create_time(),parent_argv=parent.cmdline(),parent_exe=parent.exe())
assert Path(actual['exe']).name.lower()=='ssh.exe'
assert Path(actual['parent_exe']).name.lower() in ('powershell.exe','pwsh.exe','cmd.exe')
assert not any(x in ' '.join(actual['parent_argv']).lower() for x in ['mirror_target','eval_worker','rpc','poller','retry'])
print(json.dumps(dict(epoch=time.time(),known_interactive_ssh=actual,only_existing_interactive_terminal_classified=True,no_kill_or_connection_to210=True)))
'''
c=None
try:
 c=t.connect();result=t.py(c,code);q.write_text(json.dumps(result,indent=2),encoding='utf8')
 guard=t.py(c,t.guard_code());assert guard['new_root_unused']
 r=R/'REFERENCE17B_ROLE_REVIEWED_INITIAL_RESOURCE_SLOT_ACTUAL.json';assert not r.exists();r.write_text(json.dumps(guard,indent=2),encoding='utf8')
 print(json.dumps(dict(parent=result,slot_report=str(r),lock_free=True,GPU_free_MiB=guard['GPU']['free_MiB'],RAM=guard['RAM_available'],Dfree=guard['durable_D_free'],GPUchild_absent=True)))
except Exception:
 p=R/('REFERENCE17B_PARENT_ROLE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(traceback=traceback.format_exc(),only249=True,no_signals_or_GPU=True),indent=2));raise
finally:t.close(c)
