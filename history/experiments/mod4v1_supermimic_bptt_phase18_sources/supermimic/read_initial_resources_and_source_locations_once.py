"""NewhumanSuperMimicBPTTgoal: readonlyactualGPU/originalauthority/sourcefolders. NoPT/raw/SDK/flock/GO/Cwrites/foreignsignal."""
from pathlib import Path
import sys,json,shlex
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
out=R/'reports/INITIAL_ACTUAL_RESOURCES_AND_SUPERMIMIC_SOURCE_LOCATIONS_V1.json';assert not out.exists();code=r'''from pathlib import Path
import subprocess,json,time,psutil,shutil
B=Path('/home/lc01/Zonglin Li/zonglin2');C=B/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json';c=json.loads(C.read_bytes());a=c['active_segment'];roots=[]
for rel in('tasks','src','supermimic','SuperMimic','runtime_exports'):
 p=B/rel
 if p.is_dir():
  items=[]
  for x in p.iterdir():
   if (rel=='tasks'and any(t in x.name.lower()for t in('supermimic','unisuper','sm_e0','e0_sm')))or rel!='tasks':items.append(dict(name=x.name,directory=x.is_dir()))
  roots.append(dict(path=str(p),entries=items[-100:]))
def cmd(a):
 p=subprocess.run(a,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=20);return dict(argv=a,stdout=p.stdout,stderr=p.stderr,returncode=p.returncode)
print(json.dumps(dict(kind='READONLY_NEW_SUPERMIMIC_BPTT_GOAL_INITIAL_RESOURCES_NOT_ADMISSION',epoch=time.time(),GPU=cmd(['/usr/bin/nvidia-smi','--query-gpu=index,uuid,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits']),compute=cmd(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']),actual_kernel_locks=cmd(['lslocks','--json','--output','PID,COMMAND,TYPE,MODE,PATH']),RAM_available=psutil.virtual_memory().available,disk_free=shutil.disk_usage(B).free,canonical=dict(path=str(C),authority_generation=c['authority_generation'],charged_training_seconds=c['charged_training_seconds'],remaining_training_seconds=c['remaining_training_seconds'],finite_minimum_remaining_seconds=c['finite_minimum_remaining_seconds'],budget_mode=c.get('budget_mode',c.get('mode')),active_owner=None if a is None else{k:a.get(k)for k in('owner_run_id','owner_parent_pid','kind','started_epoch')},charged_plus_remaining=c['charged_training_seconds']+c['remaining_training_seconds']),source_locations=roots,model_raw_SDK_or_Cwrite_or_resource_lock_operations=0)))'''
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(txt);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(out);print(json.dumps(v,indent=2))
finally:c.close()
