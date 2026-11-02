"""Only own oldmetadatawaiter PIDguard; never student/GPU1peer action.
Cancel only BEFORE any SDKdispatch token/children; preserve original files.
"""
from pathlib import Path
import datetime,json,shlex,sys,traceback
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect72
loc=json.loads((B/'SLOPE135_CURRENT_FRESH80_CASE.json').read_bytes());root=loc['remote_root'];pid=loc['parent']['pid'];creation=loc['parent']['creation'];BASE='/home/lc01/Zonglin Li/zonglin2'
code="""from pathlib import Path
import json,os,signal,time,psutil,subprocess
B=Path(%r);pid=%r;creation=%r;r={'own_root':str(B),'own_pid':pid,'expected_creation':creation,'foreign_process_actions':False}
def read(n):
 p=B/n
 return json.loads(p.read_bytes()) if p.is_file() else None
for n in ['PARENT_STARTED.json','CHILDREN.json','SDK_DISPATCH_ONCE.json','RESOURCE_WAIT_CHECKS.json','FINAL.json','PARENT_EXIT_SCOPE.json']:r[n]=read(n)
if r['CHILDREN.json'] is None and r['SDK_DISPATCH_ONCE.json'] is None and r['FINAL.json'] is None:
 try:p=psutil.Process(pid)
 except psutil.NoSuchProcess:p=None
 if p is not None:
  assert abs(p.create_time()-creation)<.02 and any(str(B/'supervise_e1_actual.py')==x for x in p.cmdline())
  p.suspend()
  if not (B/'CHILDREN.json').exists() and not (B/'SDK_DISPATCH_ONCE.json').exists():
   p.kill();p.wait(timeout=15);r.update(own_metadata_waiter_cancelled=True,no_SDK_token_or_child_at_frozen_cancel=True,own_process_waited=True,originalPT_reads=0)
   ownlocks=[line for line in Path('/proc/locks').read_text().splitlines() if len(line.split())>4 and line.split()[4]==str(pid)];assert not ownlocks;r['kernel_own_PID_locks_after_exit']=ownlocks
   with (B/'OWN_METADATA_WAIT_CANCELLED_FOR_NEW_GPU0_PERMISSION.json').open('x') as f:json.dump(r,f,indent=2)
  else:p.resume();r['not_cancelled_due_to_dispatch_race']=True
 else:r['own_process_already_gone_no_child_token']=True
else:r['existing_actual_scope_not_interrupted']=True
if r.get('own_metadata_waiter_cancelled') or r.get('FINAL.json') is not None:
 line=subprocess.check_output(['/usr/bin/nvidia-smi','-i','0','--query-gpu=index,uuid,name','--format=csv,noheader,nounits'],text=True).strip();v=[x.strip() for x in line.split(',')];assert v[0]=='0' and v[1].startswith('GPU-16828') and v[2]=='NVIDIA GeForce RTX 4090';r['new_GPU0_identity_only']={'index':0,'UUID':v[1],'name':v[2]}
print(json.dumps(r))
"""%(root,pid,creation)
client=None;report=dict(kind='OWN_GPU1_METADATAWAITER_SCOPE_TRANSITION_NO_STUDENT_ACTION',root=root)
try:
 client=connect72();i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(rc=rc,stdout=stdout,stderr=stderr);assert rc==0;report['actual']=json.loads(stdout)
except BaseException:report.update(error=traceback.format_exc());raise
finally:
 if client:client.close()
 out=T/'reports'/('SLOPE135_gpu1_waiter_gpu0_permission_metadata_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 with (B/'SLOPE135_GPU0_PERMISSION_TRANSITION_METADATA.json').open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(report=str(out),data=report.get('actual'),rc=report.get('rc')),ensure_ascii=False,indent=2))
