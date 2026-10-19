"""Execute the actual pending-cost owner against synthetic clock/files/HTTP; no real ledger."""
from pathlib import Path
import ast,copy,hashlib,hmac,json,os,threading,time,traceback,types
B=Path(__file__).resolve().parent;R=B/'reports';C=B/'single_E3_proposal'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def fn(text,name,env):
 n=next(x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef) and x.name==name);exec(compile(ast.Module(body=[n],type_ignores=[]),'<actual single E3 CPU fixture>','exec'),env);return env[name]
def main():
 proposal=json.loads((C/'PROPOSAL.json').read_bytes());spec=proposal['spec'];text=(C/'single_E3_pending_cost_owner_v1.py').read_text('utf8');common=(B/'controllers/three_slot_common_v1.py').read_text('utf8');env0=dict(json=json,hashlib=hashlib,hmac=hmac);terminal=fn(common,'terminal',env0);valid=fn(common,'valid_ready',env0);auth=fn(common,'authenticated_row',env0);advance=fn(text,'advance_cost',dict(b=types.SimpleNamespace(terminal=terminal)));cases=[]
 for failed in (False,True):
  s=dict(now=1000.,files={},shared=None,calls=0,opened=[],closed=[],flock=[],writes=[])
  class FakePath:
   def __init__(self,name):self.name=name
   def exists(self):return False
   def __truediv__(self,name):return FakePath(name)
   def __str__(self):return '/CPU_ONLY/'+self.name
  class Server:
   def __init__(self,address,handler):
    assert address==('127.0.0.1',29754);cells=dict(zip(handler.do_POST.__code__.co_freevars,[c.cell_contents for c in handler.do_POST.__closure__]));s['shared']=cells['state']
   def serve_forever(self):pass
   def shutdown(self):pass
  def ready():
   v=dict(kind='closed_same_backend_production',key='recovery',passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,same_active_runtime_assets_and_PPO_AST=True)
   return dict(key='recovery',phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True))
  def save(path,value):
   name=path.name;s['files'][name]=copy.deepcopy(value)
   if name=='OWNER_CURRENT.json':
    s['calls']+=1;n=s['calls'];st=s['shared']
    if n==1:assert not value['go'];st['row']=ready();st['last']=s['now']
    elif n==2:
     assert set(value['go'])=={'recovery'};g=value['go']['recovery'];assert g['save_deadline']-g['learning_started_epoch']==3600 and g['nominal_end_epoch']-g['learning_started_epoch']==3900
    elif n==3:st['row']=dict(key='recovery',phase='production',returncode=1 if failed else 0,original_error=failed,terminal_all_own_children_waited=True,owner_received_terminal_epoch=s['now']+3)
  fakeb=types.SimpleNamespace(terminal=terminal,valid_ready=valid,authenticated_row=auth,PORT=29754,ident=lambda p:dict(pid=p,creation=900.),put=save)
  def open_fake(path,flags,mode):assert flags&os.O_EXCL and flags&os.O_CREAT;s['opened'].append(str(path));return 321
  def sleep_fake(dt):s['now']+=dt;assert s['now']<1050
  env=dict(Path=Path,b=fakeb,B=FakePath('OWNER'),RESERVATION=FakePath('RESERVATION'),APPROVAL_ID=proposal['proposal_id'],HOST='127.0.0.1',os=types.SimpleNamespace(getpid=lambda:1234,O_CREAT=os.O_CREAT,O_EXCL=os.O_EXCL,O_RDWR=os.O_RDWR,open=open_fake,write=lambda fd,data:s['writes'].append(data),fsync=lambda fd:None,close=lambda fd:s['closed'].append(fd)),fcntl=types.SimpleNamespace(LOCK_EX=1,LOCK_NB=2,LOCK_UN=8,flock=lambda fd,op:s['flock'].append(op)),time=types.SimpleNamespace(time=lambda:s['now'],sleep=sleep_fake),threading=types.SimpleNamespace(Lock=threading.Lock,Thread=lambda **kw:types.SimpleNamespace(start=lambda:None)),http=types.SimpleNamespace(server=types.SimpleNamespace(BaseHTTPRequestHandler=object,ThreadingHTTPServer=Server)),json=json,hmac=hmac,hashlib=hashlib,traceback=traceback,advance_cost=advance)
  own=fn(text,'owner',env);cfg=dict(experts={'recovery':copy.deepcopy(spec)},approval_id=proposal['proposal_id'],explicit_offline_cost_approval=True,deferred_experts=['h1','e2'],token='[REDACTED]',run_id='CPU_ONLY')
  bad=copy.deepcopy(cfg);bad['explicit_offline_cost_approval']=False
  try:own(bad)
  except AssertionError:pass
  else:raise AssertionError('Approval guard failed')
  assert not s['opened'];own(cfg);final=s['files']['COHORT_FINAL.json'];cost=final['pending_cost']['cost'];assert cost['actual_production_seconds']==6. and cost['actual_returncode']==(1 if failed else 0) and cost['duration_bound_passed'];assert final['original_cost_settled'] is False and final['pending_cost_record_complete'];assert s['opened']==['/CPU_ONLY/RESERVATION'] and s['closed']==[321] and s['flock']==[3,8];assert s['files']['OWNER_EXIT_ACTUAL.json']['reservation_retained'];assert 'h1' not in final['go'] and 'e2' not in final['go'];cases.append(dict(case='postGO_failure_actual_cost_retained' if failed else 'single_success_pending_not_settled',actual_seconds=cost['actual_production_seconds'],approval_guard_rejected_before_IO=True,only_one_E3_GO=True,no_canonical_access=True))
 # Repeated terminal reports cannot double-charge, nor can an earlier receipt refund time.
 g={'learning_started_epoch':10};r={'terminal_all_own_children_waited':True,'returncode':0,'owner_received_terminal_epoch':20};cost=advance({},g,{},18);cost=advance(cost,g,r,30);assert cost['actual_production_seconds']==10;assert advance(cost,g,r,40)==cost;cases.append(dict(case='repeat_terminal_once_no_refund',passed=True))
 for key in ('h1','e2'):
  raw=json.dumps(dict(run_id='CPU',epoch=10,row=dict(key=key,manifest_SHA='unused'))).encode();token=b'CPU';sig=hmac.new(token,raw,hashlib.sha256).hexdigest()
  try:auth(raw,sig,token,'CPU',{'recovery':spec},10)
  except AssertionError:pass
  else:raise AssertionError('unscheduled participant admitted')
 cases.append(dict(case='H1_and_E2_signed_rows_rejected',passed=True))
 old=(B/'controllers/three_slot_finite_node_v1.py').read_text('utf8');node=(C/'three_slot_finite_node_local_owner_v1.py').read_text('utf8');assert ast.dump(ast.parse(old))==ast.dump(ast.parse(node.replace('http://127.0.0.1:','http://10.24.4.210:')))
 report=dict(epoch=time.time(),passed=True,proposal_id=proposal['proposal_id'],cases=cases,owner_SHA=hashlib.sha256(text.encode()).hexdigest(),node_SHA=hashlib.sha256(node.encode()).hexdigest(),production_node_AST_only_endpoint_changed=True,actual_owner_and_cost_code_executed_synthetic_only=True,no_remote_GPU_Task_or_real_ledger_IO=True,not_a_new_accounting_authorization=True,actual_owner_GO_PPO=None)
 put('SINGLE_E3_PENDING_COST_OWNER_CPU_ACTUAL.json',report);print(json.dumps(dict(single_E3_pending_cost_CPU_passed=True,cases=len(cases),requires_specific_human_approval=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('SINGLE_E3_PENDING_COST_CPU_V2_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_real_account_or_remote_IO=True));raise
