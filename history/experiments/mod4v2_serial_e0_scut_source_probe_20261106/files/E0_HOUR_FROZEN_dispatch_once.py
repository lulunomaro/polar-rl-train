"""Dispatch this one new staged E0 eval; outer controller really waits the parent."""
from pathlib import Path
import hashlib,json,shlex,time
from E0_HOUR_FROZEN_stage import D,OWN,connect,need,put,read_json
CONTROLLER=r"""from pathlib import Path
import json,os,subprocess,time
B=Path(__file__).resolve().parent
assert not(B/'OUTER_OWNER_WAIT_ACTUAL.json').exists()
def put(name,value):
 p=B/name;q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(value,indent=2));os.replace(q,p)
with (B/'OWNER_STDOUT_STDERR.log').open('xb') as log:
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'E0_HOUR_FROZEN_parent.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 put('OUTER_OWNER_IDENTITY.json',dict(epoch=time.time(),controller_pid=os.getpid(),original_owner_pid=p.pid))
 rc=p.wait()
 put('OUTER_OWNER_WAIT_ACTUAL.json',dict(epoch=time.time(),controller_pid=os.getpid(),original_owner_pid=p.pid,actual_wait_returncode=rc,original_owner_reaped=True))
"""

def main():
 marker=D/'E0_HOUR_FROZEN_DISPATCH_ONCE.json';result=D/'E0_HOUR_FROZEN_DISPATCH_RESULT.json';need(not marker.exists() and not result.exists(),'This eval purpose dispatch once only');stage=read_json(D/'E0_HOUR_FROZEN_STAGE_RESULT.json');need(stage['returncode']==0 and stage['source_stage_only'] is True and stage['parent_dispatched'] is False and stage['selected_PT_stat_hash_read_decode']==0,'Only actual new source stage')
 root=stage['root'];need(root.startswith(OWN+'/tasks/E0_HOUR_FROZEN_'),'New E0 eval root only');put(marker,dict(epoch=time.time(),root=root,one_parent_submission=True,no_resource_lock_budget_or_GO_in_dispatcher=True))
 launch="""from pathlib import Path
import hashlib,json,os,subprocess
B=Path(__ROOT__)
assert hashlib.sha256((B/'GROUP_PLAN.json').read_bytes()).hexdigest()==__PLAN_SHA__
assert not(B/'PARENT_STARTED.json').exists() and not(B/'OUTER_OWNER_IDENTITY.json').exists()
with (B/'OUTER_CONTROLLER_STDOUT_STDERR.log').open('xb') as log:
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'E0_HOUR_FROZEN_OUTER_WAIT_CONTROLLER.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 print(json.dumps(dict(controller_pid=p.pid,root=str(B),actual_parent_wait_pending=True,SDK_PT_or_GO_not_observed_by_dispatcher=True)))
""".replace('__ROOT__',repr(root)).replace('__PLAN_SHA__',repr(stage['plan_SHA']))
 client=connect();ftp=client.open_sftp()
 try:
  name=root+'/E0_HOUR_FROZEN_OUTER_WAIT_CONTROLLER.py'
  try:ftp.lstat(name)
  except FileNotFoundError:pass
  else:raise FileExistsError(name)
  with ftp.open(name,'wb') as stream:stream.write(CONTROLLER.encode())
  stdin,stdout,stderr=client.exec_command(shlex.quote(OWN+'/run-python.sh')+' -B -c '+shlex.quote(launch),timeout=30);stdin.close();out=stdout.read().decode();err=stderr.read().decode();rc=stdout.channel.recv_exit_status();value=dict(epoch=time.time(),root=root,returncode=rc,stdout=out,stderr=err,outer_actual_parent_wait_still_required=True);put(result,value);print(json.dumps(value,indent=2));need(rc==0,'Original dispatcher error retained; no automatic retry')
 finally:ftp.close();client.close()

if __name__=='__main__':main()
