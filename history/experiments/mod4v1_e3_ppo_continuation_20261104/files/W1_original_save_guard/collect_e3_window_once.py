"""Sole metadata observer. Never opens PT/raw or touches foreign processes/locks/C."""
from pathlib import Path
import json,time,sys
D=Path(__file__).resolve().parent;stage=json.loads((D/'STAGE_RESULT.json').read_bytes());root=stage['root'];assert(D/'DISPATCH_RESULT.json').exists()and not(D/'OBSERVER_STARTED_ONCE.json').exists();(D/'OBSERVER_STARTED_ONCE.json').write_text(json.dumps(dict(epoch=time.time(),root=root,cap_seconds=6600,interval_seconds=30)),encoding='utf8');sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();start=time.monotonic();previous=None
names=['OWNER_STARTED.json','PREGO_RESOURCE_WAIT.json','OWNER_CURRENT.json','OWNER_ORIGINAL_ERROR.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_WAITED_ACTUAL.json','roles/E3/ROOT_ADMISSION_ACTUAL.json','roles/E3/GO_PRODUCTION.json','roles/E3/WORKER_IDENTITY_ACTUAL.json','roles/E3/PARENT_WAITED_ACTUAL.json','roles/E3/production/LIVE_WHOLE20K_FULLRESTORE_BEFORE_PPO.json','roles/E3/production/latest_complete.json','roles/E3/production/FINAL.json','roles/E3/production/ENV_CLOSE_RETURNED.json','roles/E3/production/APP_CLOSING.json','roles/E3/production/APP_CLOSED.json','roles/E3/production/WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','roles/E3/production/ORIGINAL_PPO_ERROR_BEFORE_FINAL_SAVE.json','roles/E3/production/SOURCE_FINAL_READ_COUNTS.json']
def read(name):
 try:
  a=s.stat(root+'/'+name);assert a.st_size<4*1024*1024
  with s.open(root+'/'+name,'rb')as f:return json.loads(f.read())
 except FileNotFoundError:return None
try:
 while True:
  v={n:read(n)for n in names};latest=v['roles/E3/production/latest_complete.json'];fin=v['roles/E3/production/FINAL.json'];rest=v['roles/E3/production/LIVE_WHOLE20K_FULLRESTORE_BEFORE_PPO.json'];go=v['roles/E3/GO_PRODUCTION.json'];outer=v['OWNER_WAITED_ACTUAL.json'];exit=v['OWNER_EXIT_ACTUAL.json'];state=dict(epoch=time.time(),root=root,GO_published=go is not None,live_full20k_restore_receipt_published=rest is not None,actual_PPO_updates=(fin or latest or{}).get('actual_new_PPO_updates'),latest_complete=latest,closed=outer is not None and exit is not None,metadata=v)
  temp=D/'CURRENT.tmp';temp.write_text(json.dumps(state,indent=2),encoding='utf8');temp.replace(D/'CURRENT.json');key=(state['GO_published'],state['live_full20k_restore_receipt_published'],state['actual_PPO_updates'],state['closed'])
  if key!=previous:print('E3_PROGRESS '+json.dumps({k:a for k,a in state.items()if k not in('metadata','latest_complete')}),flush=True);previous=key
  if state['closed']:
   waited=v['roles/E3/PARENT_WAITED_ACTUAL.json']or{};err=v['roles/E3/production/WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json']or v['roles/E3/production/ORIGINAL_PPO_ERROR_BEFORE_FINAL_SAVE.json'];qualified=bool(fin and fin.get('passed_execution')and fin.get('actual_new_PPO_updates',0)>0 and(fin.get('final')or{}).get('full_live_core_STD_optimizer_DR_history_RNG_queue_verified')and waited.get('terminal_all_own_children_waited')and waited.get('returncode')==0 and exit.get('all_own_children_waited')and exit.get('original_cost_settled')and exit.get('original_private_finite_authority_leases_released')and not exit.get('errors')and outer.get('actual_parent_p_wait_returned')and outer.get('returncode')==0 and not outer.get('controller_errors')and not err)
   state.update(training_execution_qualified=qualified,skill_qualification=False);logs={}
   for name in('OWNER_STDOUT_STDERR.log','roles/E3/PPO_FULL_STDOUT_STDERR.log'):
    try:
     size=s.stat(root+'/'+name).st_size
     with s.open(root+'/'+name,'rb')as f:f.seek(max(0,size-20000));logs[name]=f.read().decode('utf8','replace')
    except FileNotFoundError:logs[name]=None
   state['diagnostic_log_tails']=logs;(D/'TRAIN_CLOSED_RESULT.json').write_text(json.dumps(state,indent=2),encoding='utf8');print('E3_CLOSED '+json.dumps(dict(qualified=qualified,actual_new_PPO_updates=state['actual_PPO_updates'],final=(fin or{}).get('final'),errors=err,parent_errors=exit.get('errors'))),flush=True);break
  if time.monotonic()-start>=6600:(D/'OBSERVER_TIMEOUT.json').write_text(json.dumps(dict(epoch=time.time(),root=root,original_parent_not_extended_or_signalled=True),indent=2),encoding='utf8');break
  time.sleep(30)
finally:s.close();c.close()
