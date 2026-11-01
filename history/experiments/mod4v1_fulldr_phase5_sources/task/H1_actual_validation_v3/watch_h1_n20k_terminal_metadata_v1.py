"""Own H1 terminal JSON watcher45s; no model/GPU/SDK/lock/budget operation."""
from pathlib import Path
import datetime,json,runpy,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect72
loc=json.loads((B/'CURRENT_N20K_CASE.json').read_text(encoding='utf-8'));root=loc['remote_root'];started=time.monotonic();checks=[];report=T/'reports'/('H1_n20k_terminal_watch_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');client=sf=None
try:
 client=connect72();sf=client.open_sftp()
 def read(name):
  try:
   with sf.open(root+'/'+name,'r') as f:return json.load(f)
  except (FileNotFoundError,EOFError):return None
  except OSError as e:
   if getattr(e,'errno',None)==2:return None
   raise
 while True:
  final=read('FINAL.json');closed=read('PARENT_EXIT_SCOPE.json');children=read('CHILDREN.json')
  checks.append(dict(epoch=time.time(),elapsed_s=time.monotonic()-started,has_FINAL=final is not None,has_exit=closed is not None,children=children,passed=final.get('passed') if final else None))
  terminal=bool(closed and closed.get('all_own_children_waited'))
  value=dict(kind='OWN_H1_N20K_METADATA_WATCH_NO_MODEL_OR_RESOURCE_ACTION',remote_root=root,checks=checks,terminal=terminal,final=final,exit_scope=closed,model_reads=0,locks_held=False,canonical_access=False)
  report.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
  if terminal or time.monotonic()-started>1240:break
  time.sleep(45)
 print(json.dumps(dict(terminal=terminal,report=str(report),final=final,exit_scope=closed),ensure_ascii=False,indent=2))
finally:
 if sf:sf.close()
 if client:client.close()
if terminal:
 sys.argv=['collect_h1_case_v2.py','--mode','n20k'];runpy.run_path(str(B/'collect_h1_case_v2.py'),run_name='__main__')
