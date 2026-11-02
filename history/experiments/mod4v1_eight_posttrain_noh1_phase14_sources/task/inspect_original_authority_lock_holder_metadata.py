"""Explain original-authority EX contention using canonical owner and exactlock inodes; read-only.
Doesnotacquireclearlocks, writeledger, signalprocesses, inspectenvironment orreadmodels.
"""
from pathlib import Path
import json,datetime,shlex
from project_connector import connect72
R=Path(__file__).resolve().parent
code="""from pathlib import Path
import os,json,psutil
D=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026');c=json.loads((D/'TRAINING_BUDGET_10H.json').read_bytes());active=c['active_segment'];rows=[];lines=Path('/proc/locks').read_text().splitlines()
for name in('native_floor_supervisor.lock','autonomy_controller.lock'):
 p=D/name;st=p.stat();key='%02x:%02x:%d'%(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino);hits=[]
 for line in lines:
  parts=line.split()
  if key not in parts:continue
  at=parts.index(key);pid=int(parts[at-1]);item={'kernel_lock':line,'holder_pid':pid}
  if pid>0:
   try:q=psutil.Process(pid);item.update(creation=q.create_time(),exe=q.exe(),cwd=q.cwd(),status=q.status(),parent_pid=q.ppid())
   except(psutil.NoSuchProcess,psutil.AccessDenied):pass
  hits.append(item)
 rows.append({'path':str(p),'inode_device_key':key,'kernel_holders':hits})
if active is not None:
 allowed=('kind','started_epoch','owner_parent_pid','run_id','owner_run_id','experts','charged_expert_seconds','last_account_epoch');owner={k:active[k]for k in allowed if k in active}
else:owner=None
print(json.dumps({'kind':'ORIGINAL_AUTHORITY_LOCK_CONTENTION_METADATA_READONLY','authority_generation':c['authority_generation'],'active_owner':owner,'charged_training_seconds':c['charged_training_seconds'],'remaining_training_seconds':c['remaining_training_seconds'],'locks':rows,'model_reads':0,'canonical_writes':0,'process_actions':0,'lock_acquires_or_clear':0}))
"""
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(text)
finally:c.close()
p=R/'reports'/('ORIGINAL_AUTHORITY_LOCK_HOLDER_METADATA_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(v,ensure_ascii=False,indent=2))
