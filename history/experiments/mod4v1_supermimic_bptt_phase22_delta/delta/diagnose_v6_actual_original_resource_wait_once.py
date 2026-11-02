"""One actual V6 original-lock wait diagnosis; never acquires/clears any lock.
Read only canonical summary, exact known lock kernel rows and two authorized GPUs.
"""
from pathlib import Path
import sys,json,shlex,time
R=Path(__file__).resolve().parent;out=R/'reports/A1_V6_ACTUAL_ORIGINAL_RESOURCE_WAIT_DIAGNOSIS_V1.json';assert not out.exists();m=json.loads((R/'A1_NATIVE_V6_ORIGINAL_OWNER_DISPATCH_ONCE.json').read_bytes());root=m['root'];sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
code=r'''
from pathlib import Path
import json,time,os,subprocess
B=Path('/home/lc01/Zonglin Li/zonglin2');D=B/'state/mod4_single_canonical_authority_20261026';C=json.loads((D/'TRAINING_BUDGET_10H.json').read_bytes());locks=[D/'native_floor_supervisor.lock',D/'autonomy_controller.lock',B/'state/finite_environment_validation.lock']+[B/('state/three_expert_v2_'+u+'.lock')for u in('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d')];kernel=Path('/proc/locks').read_text().splitlines();rows=[]
for p in locks:
 try:
  st=p.stat();key=f'{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}:{st.st_ino}';rows.append(dict(path=str(p),kernel_records=[x for x in kernel if key in x]))
 except FileNotFoundError:rows.append(dict(path=str(p),missing=True))
def query(args):
 p=subprocess.run(['nvidia-smi']+args,capture_output=True,text=True,timeout=20);return dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
summary={k:v for k,v in C.items()if any(w in k.lower()for w in('active','owner','remaining','charged','generation','mode','reserve'))}
print(json.dumps(dict(epoch=time.time(),canonical_summary=summary,lock_records=rows,gpu=query(['--id=GPU-16828f91-2b45-b646-8dc0-9481138e2842,GPU-c27eecbd-6838-7290-1cd2-37e34522213d','--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits']),compute_apps=query(['--id=GPU-16828f91-2b45-b646-8dc0-9481138e2842,GPU-c27eecbd-6838-7290-1cd2-37e34522213d','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']),source_models_SDK_Cwrites_lock_mutations_or_foreign_signals=0),indent=2))
'''
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();txt=o.read().decode(errors='replace');err=e.read().decode(errors='replace');rc=o.channel.recv_exit_status();value=dict(kind='READONLY_ACTUAL_V6_PREGO_RESOURCE_WAIT_NOT_NATIVE_BPTT',root=root,parent=m['parent'],returncode=rc,stderr=err,actual=json.loads(txt)if rc==0 else None,stdout_if_error=txt if rc else None);out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2));assert rc==0,(rc,err)
finally:c.close()
