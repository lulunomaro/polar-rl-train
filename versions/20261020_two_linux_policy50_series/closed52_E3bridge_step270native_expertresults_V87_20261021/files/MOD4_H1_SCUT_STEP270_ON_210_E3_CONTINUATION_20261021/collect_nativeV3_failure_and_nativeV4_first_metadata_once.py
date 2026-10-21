from pathlib import Path
import json,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
READ=r'''
from pathlib import Path
import hashlib,json,os,psutil,shutil,subprocess,time
read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None;rows=[]
for name in ('v3','v4'):
 B=Path('/mnt/mod4_linux_durable_20261013/H1step270_native32_2110'+name);own=[]
 for p in psutil.process_iter(['pid','cmdline','create_time','status']):
  try:
   if p.pid!=os.getpid() and p.info['status']!=psutil.STATUS_ZOMBIE and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):own.append(dict(**p.info,exe=p.exe()))
  except psutil.Error:pass
 ex=read(B/'PARENT_EXIT_ACTUAL.json');co=read(B/'PARENT_COMPLETE_ACTUAL.json');pending=not ex or bool(own);texts=[]
 if name=='v3':assert not pending and ex['all_own_children_waited'] and ex['own_eval_lease_released'] and co['passed'] is False
 if not pending:
  for p in B.rglob('*'):
   if p.is_file() and p.suffix in ('.json','.log') and '/job0/' not in str(p):texts.append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size))
 compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);mine=[x for x in compute.splitlines() if int(x.split(',')[1].strip()) in {p['pid'] for p in own}];assert all('GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e' in x for x in mine)
 rows.append(dict(epoch=time.time(),version=name,root=str(B),pending=pending,own_actual_process_snapshot=own,actual_own_GPU_snapshot=mine,parent_complete=co,parent_exit=ex,actual_step270_terrain=read(B/'out/ACTUAL_STEP270_TERRAIN_AND_REWARD_TASK.json'),prefix_metadata=read(B/'out/VALID_PREFIX_INDEX.json'),errors={str(p.relative_to(B)):read(p) for p in list((B/'out').glob('*ORIGINAL_ERROR*.json'))+list(B.glob('PARENT_ORIGINAL_ERROR.json'))},texts=texts,raw=[]))
print(json.dumps(dict(epoch=time.time(),rows=rows,disk_free_bytes=shutil.disk_usage('/mnt/mod4_linux_durable_20261013').free,no_midrun_raw_or_budget_write=True)))
'''
try:
 (R/'NATIVEV3_FAILURE_NATIVEV4_FIRST_METADATA_COLLECTOR_STARTED.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time()),indent=2));c=d.t.connect()
 try:
  v=d.code(c,d.t.PY,READ,{},timeout=45);sf=c.open_sftp()
  try:
   for row in v['rows']:
    dest=B/('native32_'+row['version']+'_actual');dest.mkdir()
    for x in row['texts']:
     p=dest/x['relative'];p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();sf.get(x['path'],str(p));assert p.stat().st_size==x['bytes']
  finally:sf.close()
 finally:c.close()
 v['actual_finite_transport_returned']=True;(R/'NATIVEV3_FAILURE_NATIVEV4_FIRST_METADATA_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps(dict(disk_free_bytes=v['disk_free_bytes'],rows=[{k:r[k] for k in ('version','pending','actual_own_GPU_snapshot','actual_step270_terrain','errors')} for r in v['rows']])))
except BaseException:
 (R/'NATIVEV3_FAILURE_NATIVEV4_METADATA_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True),indent=2));raise
