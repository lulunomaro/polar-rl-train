"""Read-only first W35 GPU/PPO receipts. Never weights, owner mutation or retry."""
from pathlib import Path
import json,time
SOURCE='36825921fb3e4a368791be7802c8ff16977e899240ac21ed2c067b2287bb9393'
WORKER='0ec27aae56bba060bac4ca1b68c5e977ad89da6c6abda0272bc46596460b6254'
CPU='d022ee93254dbf268c9b743ca0624951680b3f17e9ac791b317a95e2794f35cc'
JOB=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_2610v91/w35')

def read(p):return json.loads(p.read_bytes()) if p.is_file() else None

def snapshot(request):
 owner=Path(request['owner_root']);out=JOB/'adaptation'
 current=read(owner/'OWNER_CURRENT.json') or {};go=(current.get('go') or {}).get('w35')
 result=dict(epoch=time.time(),run_id=request['run_id'],actual_GO=go,source_fullrestore=read(out/'SOURCE_FULLRESTORE_ZERO_VERIFIED.json'),native24=read(out/'CLOCK_GAS400_NATIVE24_ACTUAL.json'),preload=read(out/'GAS400_ORIGINAL_PRELOAD_ACTUAL_FIRST_PREWRITE.json'),positive_PPO=read(out/'PPO_POSITIVE_CURRENT.json'),final=read(out/'FINAL.json'),APP_CLOSING=read(out/'APP_CLOSING.json'),APP_CLOSED=read(out/'APP_CLOSED.json'),original_errors=[dict(path=str(p),value=read(p)) for p in sorted(out.glob('*ORIGINAL_ERROR*.json'))],node_original_error=read(JOB.parent/'node_w35/NODE_ORIGINAL_ERROR.json'),owner_original_error=read(owner/'OWNER_ORIGINAL_ERROR.json'),scheduled_experts=current.get('scheduled_experts'),owner_current_epoch=current.get('epoch'),not_skill_or_WM_dataset=True)
 result['first_positive_PPO_observed']=False
 if go:
  assert go['source_SHA']==SOURCE and go['worker_SHA']==WORKER and go['source_CPU_SHA']==CPU and go['run_id']==request['run_id'] and go['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
  assert set(current['scheduled_experts'])=={'h1','w35'}
 if result['positive_PPO']:
  r=result['positive_PPO'];n=r['new_updates'];assert go and n>=1 and r['Adam_step']==646800+20*n and r['not_skill_qualified'] is True
  full=result['source_fullrestore'];native=result['native24'];preload=result['preload']
  assert full['source_SHA']==SOURCE and full['original_actor9_critic8_STD_17Adam_LR_D1_D7_exact'] is True and full['actual_algorithm_learning_rate']==.00001
  assert native['passed'] is True and native['controls']==24 and native['physics_callbacks']==192 and native['feedback_samples']==48 and native['actual_RewardManager_dt_s']==.02 and native['no_optimizer_update'] is True
  assert preload['actual_original_preload'] is True and preload['nominal_force_N_each']==400
  result['first_positive_PPO_observed']=True
 return result

def watch(request,max_wait_seconds=780,emit=None):
 assert 0<max_wait_seconds<=780
 deadline=time.time()+max_wait_seconds;last=0
 while True:
  value=snapshot(request)
  if emit and time.time()-last>=25:emit(dict(stage='W35_FIRST_GPU_METADATA_PROGRESS',value=value));last=time.time()
  if value['first_positive_PPO_observed'] or value['original_errors'] or value['node_original_error'] or value['owner_original_error'] or time.time()>=deadline:
   value['observer_returned']=True;value['weights_not_read_or_hashed']=True;return value
  time.sleep(3)
