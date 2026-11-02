"""UnusedV4sameSDKworkers as V3; boundedoriginalresourcewait releasesallpartials, zeroModelSDKuntiltrueadmission."""
from pathlib import Path
import json,ast,hashlib
R=Path(__file__).resolve().parent;S=R/'NINE_N80_PARALLEL_SOURCE_V3';D=R/'NINE_N80_PARALLEL_SOURCE_V4';assert not D.exists();D.mkdir()
for p in S.iterdir():
 if p.is_file():(D/p.name).write_bytes(p.read_bytes())
p=D/'single_gpu_group_supervisor.py';s=p.read_text(encoding='utf-8');start=s.index('  for path in(OWN/');end=s.index("  put('ACTUAL_GROUP_ADMISSION.json'",start);replacement="""  class BusyResource(Exception):pass
  wait_until=time.monotonic()+1800;wait_rows=[]
  while True:
   candidate=None
   try:
    for path in(OWN/'state'/('three_expert_v2_'+uuid+'.lock'),OWN/'state/finite_environment_validation.lock'):
     candidate=path.open('rb+');fcntl.flock(candidate,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(candidate);candidate=None
    canonical=OWN/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json';raw=canonical.read_bytes();c=json.loads(raw);assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['remaining_training_seconds']>c['finite_minimum_remaining_seconds']
    if c['active_segment']is not None:raise BusyResource('Originalcanonicalhasactiveowner;nointerference')
    apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
    if uuid in apps:raise BusyResource('Selectedcardhasexistingcomputeprocess')
    res=nvidia(uuid)
    if res['free_MiB']<23500 or res['utilization_percent']!=0:raise BusyResource('Selectedcardnotemptyatfreshadmission')
    assert psutil.virtual_memory().available>96*1024**3 and shutil.disk_usage(B).free>25*1024**3
    break
   except (BlockingIOError,BusyResource)as busy:
    if candidate is not None:candidate.close()
    for fd in reversed(locks):fcntl.flock(fd,fcntl.LOCK_UN);fd.close()
    locks.clear();wait_rows.append(dict(epoch=time.time(),reason=str(busy),locks_held=0,SDK_or_selected_model_opened=False,canonical_writes=0,remaining_wait_seconds=max(0,wait_until-time.monotonic())));put('BOUNDED_ORIGINAL_RESOURCE_WAIT.json',wait_rows)
    if time.monotonic()>=wait_until:raise TimeoutError('Originalresourcewait1800sexpiredwithoutSDK/model/foreignactions')
    time.sleep(15)
""";s=s[:start]+replacement+s[end:];ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n')
rows=[]
for p in D.glob('*.py'):
 raw=p.read_bytes();ast.parse(raw.decode('utf-8'));rows.append(dict(relative=p.name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
(D/'PARENT_FIVE_SOURCE_INDEX_V5.json').write_text(json.dumps(dict(kind='SAME_V3_WORKERS_ONLY_BOUNDED_ORIGINAL_RESOURCE_WAIT_1800S',files=rows,same_workers_asV3=True,original_GPU_privateEX_globalfiniteEX_unchanged=True,partial_locks_released_whilewaiting=True,SDK_PT_GO_budgetwrite_whilewaiting=0,oldV3_resource_busy_scope_closed=True),indent=2),encoding='utf-8')
s=(R/'stage_and_dispatch_nine_single_gpu_eval_v3_once.py').read_text(encoding='utf-8').replace('NINE_N80_PARALLEL_SOURCE_V3','NINE_N80_PARALLEL_SOURCE_V4').replace('PARENT_FIVE_SOURCE_INDEX_V4.json','PARENT_FIVE_SOURCE_INDEX_V5.json').replace('NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V3.json','NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V4.json').replace('MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V3_','MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V4_');p=R/'stage_and_dispatch_nine_single_gpu_eval_v4_once.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n')
s=(R/'collect_nine_single_gpu_v3_until_closed_once.py').read_text(encoding='utf-8').replace('V3','V4').replace('started<2700','started<4500');p=R/'collect_nine_single_gpu_v4_until_closed_once.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n');print('V4_AST_PASS / workersidenticalV3 / originalprivateEX+finiteEXonly / waits1800swithoutpartials')
