from pathlib import Path
import json,base64,hashlib,sys,time,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';T=R+'/temporary_scope2048_memory20GB_left_repair_20261013'
def call(code,timeout=35):
 b=base64.b64encode(code.encode()).decode();return powershell(connect(),"[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+b+"'))\"",timeout=timeout)
def main():
 receipt=D/'reports/TEMP2048_SEQUENCE_TASK_DISPATCH_ACTUAL.json';assert not receipt.exists()
 actual=json.loads(call("""from pathlib import Path;import json,hashlib,time,os,psutil
r=Path('"""+R+"""');t=Path('"""+T+"""');mf=t/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';m=json.loads(mf.read_bytes())
assert m['num_envs']==2048 and m['requested_memory_limit_bytes']==20000000000 and not (t/'SEQUENCE_ONCE_CONSUMED.json').exists()
assert psutil.virtual_memory().available>=22000000000
lease=dict(epoch=time.time(),case_id='temporary2048_memory20GB_sequence_v1',approved_GPU_scope=True,mode='sdk',scope_root=str(t),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=hashlib.sha256(mf.read_bytes()).hexdigest(),human20GB_temporary_branch_authorized=True,not_old20k_lease=True)
p=t/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';assert not p.exists()
with p.open('xb') as f:f.write(json.dumps(lease,indent=2).encode());f.flush();os.fsync(f.fileno())
print(json.dumps(dict(lease_path=str(p),manifest_path=str(mf),scope=str(t),RAM_available_bytes=psutil.virtual_memory().available,approved_new_sequence=True)))
"""))
 ps="& '"+T+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+T+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+T+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+T+"/attempts/temporary2048_sdk_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+T+"/runtime2048' -StageMode sdk -TrainSeconds 3600 -StartApprovedLease"
 out=powershell(connect(),ps,timeout=40)
 receipt.write_text(json.dumps(dict(epoch=time.time(),actual=actual,registration_stdout=out,task_name='MOD4_Windows4090_Repair_20261013_temporary2048_memory20GB_sequence_v1',registration_and_start_requested_once=True,actual_PPO_not_yet_inferred=True,actual_GPU_receipts_required=True),indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(receipt),new_task_dispatched=True,PPO_not_claimed=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('TEMP2048_LAUNCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),unknownoutcome_actualread_before_any_retry=True),indent=2),encoding='utf8');raise
