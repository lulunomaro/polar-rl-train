"""Root sequential transport dispatch only, then returns; no evaluator replays."""
from pathlib import Path
import sys,json,time,os,subprocess,importlib.util,traceback
D=Path(__file__).resolve().parent;E=D/'curb140_frozen35_3060_v1';R=D/'reports'
def main():
 p=R/'CURB140_NEW_FROZEN_NATIVE120_FINITE_DISPATCH_STARTED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),actual_alive_only_transport_owner210_72_249=True,only_new_CURB140_native120_no_PPO=True),indent=2),encoding='utf8');spec=importlib.util.spec_from_file_location('actual_new140_dispatch',E/'dispatch_curb113_frozen3060_unused_case_once.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);c=None
 try:
  c=m.t.connect();guard=m.t.py(c,m.t.guard_code());assert guard['shared_OS_lock_free'] and guard['new_root_unused'];root=str(Path(m.ROOT).parent).replace('\\','/');v=m.t.py(c,"from pathlib import Path;import json;B=Path("+repr(root)+");assert B.resolve().is_relative_to(Path('D:/MOD4_async_eval').resolve()) and not B.exists();B.mkdir();print(json.dumps(dict(new_owned_parent=str(B),no_GPU_or_PPO=True)))");(R/'CURB140_NEW_EVAL_PARENT_CREATED_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 finally:m.t.close(c)
 sys.argv=[str(E/'dispatch_curb113_frozen3060_unused_case_once.py'),'--steps','120','--execute-own-unused-case'];m.main()
if __name__=='__main__':
 try:main()
 except BaseException:(R/('CURB140_NEW_EVAL_DISPATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),unknown_mutation_actual_readonly_before_continuation_no_blind_replay=True),indent=2),encoding='utf8');raise
