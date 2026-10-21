from pathlib import Path
import json,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
READ=r'''
from pathlib import Path
import json,os,psutil,subprocess,time
B=Path(v['parent']['root']);read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
assert read(B/'PARENT_IDENTITY.json')['creation']==v['parent']['creation'];until=time.monotonic()+40
while not (B/'out/ACTUAL_STEP270_TERRAIN_AND_REWARD_TASK.json').exists() and not list((B/'out').glob('*ORIGINAL_ERROR*.json')) and not (B/'PARENT_EXIT_ACTUAL.json').exists() and time.monotonic()<until:time.sleep(.5)
own=[]
for p in psutil.process_iter(['pid','cmdline','create_time','status']):
 try:
  if p.pid!=os.getpid() and p.info['status']!=psutil.STATUS_ZOMBIE and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):own.append(dict(**p.info,exe=p.exe()))
 except psutil.Error:pass
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);mine=[x for x in compute.splitlines() if int(x.split(',')[1].strip()) in {p['pid'] for p in own}];assert all('GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e' in x for x in mine)
print(json.dumps(dict(epoch=time.time(),root=str(B),own_actual_process_snapshot=own,actual_own_GPU_snapshot=mine,actual_step270_terrain=read(B/'out/ACTUAL_STEP270_TERRAIN_AND_REWARD_TASK.json'),actual_geometry_clock=read(B/'out/GEOMETRY_AND_CLOCK_ACTUAL.json'),actual_GPU_receipt=read(B/'out/ACTUAL_OWN_GPU.json'),prefix_metadata=read(B/'out/VALID_PREFIX_INDEX.json'),parent_complete=read(B/'PARENT_COMPLETE_ACTUAL.json'),parent_exit=read(B/'PARENT_EXIT_ACTUAL.json'),errors={str(p.relative_to(B)):read(p) for p in list((B/'out').glob('*ORIGINAL_ERROR*.json'))+list(B.glob('PARENT_ORIGINAL_ERROR.json'))},no_midrun_raw_download_no_optimizer_no_budget_write=True)))
'''
try:
 q=json.loads((R/'STEP270_NATIVE32_V3_DETACHED_ACTUAL_STARTED.json').read_bytes());(R/'STEP270_NATIVE32_V3_FIRST_METADATA_STARTED.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),bound_parent=q['parent']),indent=2));c=d.t.connect()
 try:v=d.code(c,d.t.PY,READ,dict(parent=q['parent']),timeout=60)
 finally:c.close()
 (R/'STEP270_NATIVE32_V3_FIRST_METADATA_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps({k:v[k] for k in ('epoch','own_actual_process_snapshot','actual_own_GPU_snapshot','actual_step270_terrain','parent_complete','parent_exit','errors')}))
except BaseException:
 (R/'STEP270_NATIVE32_V3_FIRST_METADATA_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True),indent=2));raise
