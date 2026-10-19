"""Exercise actual owner/charge code with an in-memory synthetic ledger and no sockets/GPU."""
from pathlib import Path
import ast,copy,hashlib,hmac,json,os,threading,time,traceback,types
B=Path(__file__).resolve().parent;R=B/'reports'
def put_report(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def function(text,name,env):
 n=next(x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef) and x.name==name);exec(compile(ast.fix_missing_locations(ast.Module(body=[n],type_ignores=[])),'<actual CPU source>','exec'),env);return env[name]
def main():
 prep=json.loads((R/'TWO_AVAILABLE_SOURCE_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());common=(B/'controllers/three_slot_common_v1.py').read_text('utf8');ownertext=(B/'controllers/three_slot_finite_owner_available_two_v1.py').read_text('utf8');env0=dict(json=json,hashlib=hashlib,hmac=hmac)
 terminal=function(common,'terminal',env0);charge=function(common,'charge_values',env0);valid=function(common,'valid_ready',env0);auth=function(common,'authenticated_row',env0);cases=[]
 for fail_e2 in (False,True):
  state=dict(now=1000.,ticks=0,current_calls=0,ledger=dict(active_segment=None,completed_segments=[],authorized_training_seconds=1188000,budget_extensions=list(range(7)),charged_training_seconds=0.,remaining_training_seconds=1188000.),files={},locks=[],released=0,shared=None)
  class LockFile:
   def __init__(self):self.closed=False
   def close(self):self.closed=True
  class LockPath:
   def open(self,*a):x=LockFile();state['locks'].append(x);return x
  def flock(f,op):
   if op==8:state['released']+=1
  class Server:
   def __init__(self,address,handler):
    cells=dict(zip(handler.do_POST.__code__.co_freevars,[c.cell_contents for c in handler.do_POST.__closure__]));state['shared']=cells['shared']
   def serve_forever(self):pass
   def shutdown(self):pass
  def ready(k):
   spec=prep['specs'][k];v=dict(kind='closed_same_backend_production',key=k,passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,same_active_runtime_assets_and_PPO_AST=True)
   return dict(key=k,phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True))
  def synthetic_put(path,value):
   name=Path(path).name
   if name=='CPU_SYNTHETIC_BUDGET.json':state['ledger']=copy.deepcopy(value);return
   state['files'][name]=copy.deepcopy(value)
   if name=='OWNER_CURRENT.json':
    state['current_calls']+=1;n=state['current_calls'];shared=state['shared']
    if n==1:assert not value['go'];shared['rows']['e2']=ready('e2')
    elif n==2:assert not value['go'];shared['rows']['recovery']=ready('recovery')
    elif n==3:
     assert set(value['go'])=={'e2','recovery'} and 'h1' not in shared['rows'];shared['rows']['e2']=dict(key='e2',phase='production',returncode=1 if fail_e2 else 0,original_error=fail_e2,terminal_all_own_children_waited=True,owner_received_terminal_epoch=state['now']+3)
    elif n==4:assert not value['stop_by_slot']['recovery'] and value['original_canonical_active']
    elif n==5:shared['rows']['recovery']=dict(key='recovery',phase='production',returncode=0,terminal_all_own_children_waited=True,owner_received_terminal_epoch=state['now']+3)
  def synthetic_sleep(seconds):
   state['ticks']+=1;assert state['ticks']<20;state['now']+=seconds
  fake_b=types.SimpleNamespace(C=Path('/CPU_SYNTHETIC_BUDGET.json'),LOCKS=(LockPath(),LockPath()),CAPS=dict(h1=3900,e2=3900,recovery=3900),PORT=29754,put=synthetic_put,read=lambda p:copy.deepcopy(state['ledger']),terminal=terminal,charge_values=charge,valid_ready=valid,ident=lambda pid:dict(pid=pid,creation=state['now']))
  env=dict(Path=Path,os=os,time=types.SimpleNamespace(time=lambda:state['now'],sleep=synthetic_sleep),json=json,threading=types.SimpleNamespace(Lock=threading.Lock,Thread=lambda **kw:types.SimpleNamespace(start=lambda:None)),http=types.SimpleNamespace(server=types.SimpleNamespace(BaseHTTPRequestHandler=object,ThreadingHTTPServer=Server)),hmac=hmac,hashlib=hashlib,fcntl=types.SimpleNamespace(LOCK_EX=1,LOCK_NB=2,LOCK_UN=8,flock=flock),traceback=traceback,b=fake_b,B=Path('/CPU_ONLY_OWNER'),put=synthetic_put)
  owner=function(ownertext,'owner',env);owner(dict(experts=copy.deepcopy(prep['specs']),token='[REDACTED]',run_id='CPU_ONLY',scheduling_authority='human_requested_available_experts',deferred_experts=['h1']))
  ledger=state['ledger'];assert ledger['active_segment'] is None and len(ledger['completed_segments'])==1;segment=ledger['completed_segments'][0];assert set(segment['experts'])=={'e2','recovery'} and 'h1' not in segment['experts'];assert abs(segment['charged_expert_seconds']-12.)<1e-9 and abs(segment['charged_expert_seconds']-sum(x['charged_seconds'] for x in segment['experts'].values()))<1e-9;assert ledger['charged_training_seconds']+ledger['remaining_training_seconds']==1188000 and ledger['authorized_training_seconds']==1188000 and len(ledger['budget_extensions'])==7
  assert len(state['locks'])==state['released']==2 and all(x.closed for x in state['locks']);assert state['files']['COHORT_FINAL.json']['deferred_experts_without_GO']==['h1'];assert state['files']['OWNER_EXIT_ACTUAL.json']['original_cost_settled'];assert all(x['max_parent_seconds']==3900 for x in segment['experts'].values());assert state['files']['COHORT_FINAL.json']['go']['e2']['save_deadline']-state['files']['COHORT_FINAL.json']['go']['e2']['learning_started_epoch']==3600
  cases.append(dict(case='one_failed_slot_other_continues' if fail_e2 else 'two_successful_independent_slots',only_two_real_GO_and_charge=True,H1_never_registered_or_faked=True,first_slot_does_not_GO_before_both_scheduled_ready=True,canonical_single_writer_settles_once=True,synthetic_sum_seconds=segment['charged_expert_seconds'],original_total_and_two_locks_unchanged=True))
 token=bytes(range(32));raw=json.dumps(dict(run_id='CPU_AUTH',epoch=1000,row=dict(key='h1',manifest_SHA='not_participant'))).encode();signature=hmac.new(token,raw,hashlib.sha256).hexdigest()
 try:auth(raw,signature,token,'CPU_AUTH',prep['specs'],1000)
 except AssertionError:cases.append(dict(case='unscheduled_H1_authenticated_row_rejected',passed=True))
 else:raise AssertionError('H1 row unexpectedly accepted')
 spec=prep['specs']['e2'];row=ready('e2');row['closed_source_CPU']['value']['source_SHA']='0'*64;assert not valid(row,spec);cases.append(dict(case='wrong_closed_source_readiness_rejected',passed=True))
 put_report('AVAILABLE_TWO_OWNER_SCHEDULING_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,source_owner=str(B/'controllers/three_slot_finite_owner_available_two_v1.py'),source_owner_SHA=hashlib.sha256(ownertext.encode()).hexdigest(),actual_owner_and_charge_function_code_executed_on_in_memory_synthetic_fixture=True,cases=cases,only_scheduling_domain_and_listener_registration_changed=True,original_charge_values_and_account_AST_unchanged=prep['original_charge_values_and_account_function_AST_equal'],canonical_path_locks_caps_time_guards_budget_unchanged=True,no_real_canonical_file_opened_or_written=True,no_socket_or_remote_or_GPU_or_task_or_native=True,not_actual_PPO_or_skill_qualification=True))
 print(json.dumps(dict(two_participant_owner_CPU_passed=True,cases=len(cases),no_real_account_or_remote_access=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put_report('AVAILABLE_TWO_OWNER_CPU_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),synthetic_CPU_only_no_real_account_IO=True));raise
