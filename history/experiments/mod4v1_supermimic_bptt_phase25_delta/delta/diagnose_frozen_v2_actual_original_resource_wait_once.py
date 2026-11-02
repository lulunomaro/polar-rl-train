"""One bounded read-only explanation of actual project's frozen-eval lock wait.
Only own process identity, known project locks/C summary and authorized GPUs.
No source/model/raw/SDK run, C write, lock acquisition, foreign signal or parent.
"""
from pathlib import Path
import sys,json,shlex
R=Path(__file__).resolve().parent;out=R/'reports/FROZEN_E3_W35_BATCH_V2_ACTUAL_ORIGINAL_RESOURCE_WAIT_DIAGNOSIS_V1.json';assert not out.exists();d=json.loads((R/'reports/FROZEN_E3_W35_BATCH_V2_ACTUAL_PARENT_DISPATCH_V1.json').read_bytes());m=d['receipt'];root=d['root'];pid=m['parent']['pid'];ticks=str(m['parent']['linux_start_ticks']);sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
code=r'''
from pathlib import Path
import json,time,os,subprocess,shutil
root=Path(ROOT);pid=PID;ticks=TICKS;stat=Path('/proc')/str(pid)/'stat';own=None
try:
 text=stat.read_text();fields=text[text.rfind(')')+2:].split();assert fields[19]==ticks;own=dict(pid=pid,state=fields[0],linux_start_ticks=fields[19])
except FileNotFoundError:own=dict(pid=pid,exists=False)
if(root/'ACTUAL_GROUP_ADMISSION.json').exists():
 print(json.dumps(dict(epoch=time.time(),own_parent=own,already_published_actual_admission=True,no_resource_query_needed=True,model_SDK_Cwrites_signals=0)));raise SystemExit(0)
B=Path('/home/lc01/Zonglin Li/zonglin2');D=B/'state/mod4_single_canonical_authority_20261026';C=json.loads((D/'TRAINING_BUDGET_10H.json').read_bytes());locks=[D/'native_floor_supervisor.lock',D/'autonomy_controller.lock',B/'state/finite_environment_validation.lock']+[B/('state/three_expert_v2_'+u+'.lock')for u in('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d')];kernel=Path('/proc/locks').read_text().splitlines();rows=[]
for p in locks:
 try:
  st=p.stat();key=f'{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}:{st.st_ino}';rows.append(dict(path=str(p),kernel_records=[x for x in kernel if key in x.split()]))
 except FileNotFoundError:rows.append(dict(path=str(p),missing=True))
def query(args):
 p=subprocess.run(['nvidia-smi']+args,capture_output=True,text=True,timeout=20);return dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
summary={k:v for k,v in C.items()if any(w in k.lower()for w in('active','owner','remaining','charged','generation','mode','reserve'))}
mem=next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:'))
print(json.dumps(dict(epoch=time.time(),own_parent=own,already_published_actual_admission=False,canonical_summary=summary,lock_records=rows,available_memory=mem,disk_free_bytes=shutil.disk_usage(B).free,gpu=query(['--id=GPU-16828f91-2b45-b646-8dc0-9481138e2842,GPU-c27eecbd-6838-7290-1cd2-37e34522213d','--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits']),compute_apps=query(['--id=GPU-16828f91-2b45-b646-8dc0-9481138e2842,GPU-c27eecbd-6838-7290-1cd2-37e34522213d','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']),source_models_raw_SDK_Cwrites_lock_mutations_foreign_signals=0),indent=2))
'''.replace('ROOT',repr(root)).replace('PID',repr(pid)).replace('TICKS',repr(ticks))
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();v=dict(kind='READONLY_ACTUAL_FROZEN_V2_ORIGINAL_RESOURCE_WAIT_DIAGNOSIS',root=root,returncode=rc,stderr=err,actual=json.loads(text)if rc==0 else None,stdout_if_error=text if rc else None);out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2));assert rc==0,err
finally:c.close()
