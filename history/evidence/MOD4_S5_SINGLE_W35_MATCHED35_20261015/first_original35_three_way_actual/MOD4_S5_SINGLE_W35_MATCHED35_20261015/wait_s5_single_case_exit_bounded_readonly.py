"""One bounded connection for the current own case only, no signal or retry."""
from pathlib import Path
import argparse,json,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';ROOT='D:/MOD4_async_eval/'+D.name
sys.path.insert(0,str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'))
import transport_249_bodyframe_current_terminal_role_v3 as t
t.ROOT=ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);a=p.parse_args();assert a.case in ('s5_single_w35_original35_120_v1','s5_single_w35_original35_1500_v1')
 q=R/(a.case+'_BOUNDED_WAIT_ACTUAL.json');assert not q.exists();c=None
 try:
  c=t.connect()
  code=r'''
from pathlib import Path
import json,time,msvcrt,psutil
R=Path(ROOT);A=R/'attempts'/CASE;O=A/'output';start=time.time();last=None
while time.time()-start<900:
 p=A/'PARENT_EXIT_RECEIPT.json'
 if p.exists():
  ex=json.loads(p.read_bytes());ids=[]
  for f in (R/(CASE+'_START_INTENT.json'),R/(CASE+'_PARENT_PID.json'),A/'DISPATCH_RECEIPT.json'):
   if not f.exists():continue
   row=json.loads(f.read_bytes())
   for pk,ck in (('pid','creation'),('parent_pid','parent_creation'),('child_pid','child_creation')):
    if pk not in row:continue
    try:
     x=psutil.Process(row[pk]);ids.append(dict(pid=x.pid,creation=x.create_time(),argv=x.cmdline(),expected_creation=row.get(ck),actual_alive=True))
    except psutil.NoSuchProcess:ids.append(dict(pid=row[pk],actual_alive=False))
  free=False
  try:
   with Path('D:/MOD4_async_eval/worker.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
   free=True
  except OSError:pass
  last=dict(epoch=time.time(),parent_exit=ex,actual_identities=ids,actual_shared_OS_lock_free=free,complete=(O/'COMPLETE_ACTUAL.json').exists(),error=(O/'ORIGINAL_ERROR.json').exists(),elapsed_bounded_wait=time.time()-start)
  if all(not x['actual_alive'] for x in ids) and free:
   print(json.dumps(dict(**last,actual_closed=True,readonly=True,no_signal_or_retry=True)));break
 time.sleep(15)
else:print(json.dumps(dict(epoch=time.time(),actual_closed=False,last=last,pending=True,readonly=True,no_signal_or_retry=True)))
'''
  v=t.py(c,'ROOT='+repr(ROOT)+'\nCASE='+repr(a.case)+'\n'+code,920);q.write_text(json.dumps(v,indent=2),encoding='utf8');assert v['actual_closed'] and v['complete'] and not v['error'] and v['parent_exit']['exit_code']==0
  print(json.dumps(dict(case=a.case,closed=True,unique_frozen_parent_seconds=v['parent_exit']['unique_actual_parent_load_run_save_exit_seconds'])))
 except BaseException:
  p=R/(a.case+'_BOUNDED_WAIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),readonly=True,no_retry=True),indent=2),encoding='utf8');raise
 finally:t.close(c)
if __name__=='__main__':main()
