"""ReadonlyexacttwoGPU private+finiteinodeholders/currentGPU metadata. No kill/lockclear/model/SDK/budgetwrite."""
from pathlib import Path
import json,shlex,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;code="""from pathlib import Path
import json,time,subprocess,psutil
B=Path('/home/lc01/Zonglin Li/zonglin2');U=['GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'];lines=Path('/proc/locks').read_text().splitlines();locks=[]
for p in[B/'state'/('three_expert_v2_'+u+'.lock')for u in U]+[B/'state/finite_environment_validation.lock']:
 inode=p.stat().st_ino;matches=[]
 for line in lines:
  a=line.split()
  if len(a)>=6 and a[5].rsplit(':',1)[-1]==str(inode):
   pid=int(a[4]);row={'kernel_lockline':line,'holder_pid':pid}
   try:
    proc=psutil.Process(pid);cmd=proc.cmdline();row.update(creation=proc.create_time(),elapsed_seconds=time.time()-proc.create_time(),same_project_referenced=any(str(B)in x for x in cmd),project_script_paths=[x for x in cmd if x.startswith(str(B))and x.endswith('.py')])
   except psutil.NoSuchProcess:row['exited_during_snapshot']=True
   matches.append(row)
 locks.append({'path':str(p),'inode':inode,'holders':matches})
gpus=[]
for u in U:gpus.append(subprocess.check_output(['/usr/bin/nvidia-smi','-i',u,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip())
c=json.loads((B/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());a=c['active_segment'];print(json.dumps({'kind':'EXACT_ORIGINAL_LOCK_AND_GPU_READONLY_SNAPSHOT','epoch':time.time(),'locks':locks,'GPUs':gpus,'original_canonical_minimal':{'authority_generation':c['authority_generation'],'remaining_training_seconds':c['remaining_training_seconds'],'active_owner_pid':None if a is None else a.get('owner_parent_pid'),'active_kind':None if a is None else a.get('kind')},'model_or_SDK_or_foreign_actions_or_ledgerwrites':0}))
""";c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(text)
finally:c.close()
p=R/'reports'/('NINE_EVAL_EXACT_LOCK_HOLDER_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(v,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(v,indent=2))
