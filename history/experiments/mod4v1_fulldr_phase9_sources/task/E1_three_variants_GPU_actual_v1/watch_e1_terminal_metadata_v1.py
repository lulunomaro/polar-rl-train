"""Owncase terminalmetadata45s only; no GPU/model/lease/budget operations."""
from pathlib import Path
import argparse,datetime,json,runpy,sys,time
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect72
p=argparse.ArgumentParser();p.add_argument('--locator',type=Path,required=True);a=p.parse_args();loc=json.loads(a.locator.read_bytes());root=loc['remote_root'];name=loc['canonical'];report=T/'reports'/(name+'_own_terminal_watch_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');start=time.monotonic();checks=[];client=sf=None;terminal=False
try:
 client=connect72();sf=client.open_sftp()
 def read(n):
  try:
   with sf.open(root+'/'+n,'r') as f:return json.load(f)
  except OSError as e:
   if getattr(e,'errno',None)==2:return None
   raise
 while True:
  final=read('FINAL.json');closed=read('PARENT_EXIT_SCOPE.json');children=read('CHILDREN.json');terminal=bool(closed and closed.get('all_own_children_waited'));checks.append(dict(epoch=time.time(),elapsed_s=time.monotonic()-start,has_final=final is not None,has_exit=closed is not None,passed=(final or {}).get('passed'),children=children))
  report.write_text(json.dumps(dict(kind='OWN_E1_TERMINAL_METADATA_WATCH_ZEROLOCK_ZERO_MODEL',root=root,checks=checks,terminal=terminal,final_passed=(final or {}).get('passed'),exit_scope=closed,sourcePT_reads=0,canonical_access=False),indent=2),encoding='utf-8')
  if terminal or time.monotonic()-start>3300:break
  time.sleep(45)
 print(json.dumps(dict(terminal=terminal,passed=(final or {}).get('passed'),children=children,exit_scope=closed,watch_report=str(report)),indent=2))
finally:
 if sf:sf.close()
 if client:client.close()
if terminal:
 sys.argv=['collect_e1_own_case_v1.py','--locator',str(a.locator)];runpy.run_path(str(B/'collect_e1_own_case_v1.py'),run_name='__main__')
