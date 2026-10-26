from pathlib import Path
import ast,copy,hashlib,hmac,importlib.util,json,sys,time,traceback
from types import SimpleNamespace
N=Path(__file__).resolve().parent;D=N/'controllers_v2';R=N/'reports';A=N/('owner_control_CPU_attempt_'+str(time.time_ns()));A.mkdir()
sys.path.insert(0,str(D));import mixed86_protocol_v1 as protocol
sp=importlib.util.spec_from_file_location('owner86_transport_source',D/'forwarded_original_owner_control_v1.py');network=importlib.util.module_from_spec(sp);sp.loader.exec_module(network)
ns={'hashlib':hashlib,'hmac':hmac,'json':json,'time':time}
tree=ast.parse((D/'three_slot_common_v1.py').read_text('utf8'))
for name in ('terminal','charge_values','authenticated_row'):
 node=next(v for v in tree.body if isinstance(v,ast.FunctionDef) and v.name==name);exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual common pure function>','exec'),ns)
cases=[]
def test(name,fn):
 try:fn();cases.append(dict(name=name,passed=True))
 except BaseException:cases.append(dict(name=name,passed=False,error=traceback.format_exc()))

def charge_overlap():
 c=dict(charged_training_seconds=2268000-587957.6840648651,remaining_training_seconds=587957.6840648651)
 initial=c['remaining_training_seconds'];a=dict(experts={},charged_expert_seconds=0.)
 go={k:dict(learning_started_epoch=s,max_parent_seconds=3900) for k,s in zip(('h1','e2','recovery'),(100,110,120))}
 ns['charge_values'](c,a,go,{},150)
 rows={k:dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=e) for k,e in (('h1',165),('recovery',175))}
 ns['charge_values'](c,a,go,rows,190);rows['e2']=dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=205)
 ns['charge_values'](c,a,go,rows,210);before=copy.deepcopy(c);ns['charge_values'](c,a,go,rows,210)
 assert c==before and a['charged_expert_seconds']==215 and abs(initial-c['remaining_training_seconds']-215)<1e-8
 assert [a['experts'][k]['charged_seconds'] for k in ('h1','e2','recovery')]==[65,95,55]

def overcap_truth():
 c=dict(charged_training_seconds=0.,remaining_training_seconds=2268000.);a=dict(experts={},charged_expert_seconds=0.)
 ns['charge_values'](c,a,{'e2':dict(learning_started_epoch=100,max_parent_seconds=3900)},{'e2':dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=4005)},4005)
 assert a['experts']['e2']['charged_seconds']==3905 and a['experts']['e2']['duration_bound_passed'] is False and c['remaining_training_seconds']==2268000-3905

def native_fixture():
 spec=dict(key='e2',finite_method_test=True,h1_step270_method_test=True,native_continuation=True,source_SHA=protocol.SOURCES['e2'][0],source_Adamstep=829700,bootstrap_source_SHA=protocol.BOOTSTRAP_SHA,GPU_UUID=protocol.GPUS['e2'],execution_backend='target72',manifest_SHA='1'*64,candidate_pins={'source_guard':'2'*64},reference_artifact_SHA=protocol.REFERENCE_SHA,adapter_CPU_report_SHA='3'*64,objective_contract_SHA='4'*64)
 value=dict(passed=True,kind='UNISUPERMIMIC_FUDAN_NATIVE85_CONTINUATION_SOURCE_SDK_CPU_V86',source_SHA=spec['source_SHA'],bootstrap_SHA=protocol.BOOTSTRAP_SHA,bootstrap_Adam=829700,GPU_UUID=spec['GPU_UUID'],execution_backend='target72',candidate_pins=spec['candidate_pins'],reference_artifact_SHA=spec['reference_artifact_SHA'],adapter_CPU_report_SHA=spec['adapter_CPU_report_SHA'],objective_contract_SHA=spec['objective_contract_SHA'],source_native_iteration=68,source_world_updates=680,source_policy_updates=58,metadata_helper_bytes=2536,metadata_helper_SHA='c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e',actual_runtime_order_readback=False)
 for flag in ('actual_installed_CPU_passed','actual_H1_source_SDK_CPU_passed','native85_fullstate_source_CPU_passed','source_original85_cost_allout_passed','native_continuation_restore_required','not_production_E2_source_or_skill_qualification','original_H1_270_physics_source_exact','reference_and_adapter_actual_CPU_validated'):value[flag]=True
 def row(v):return dict(key='e2',phase='ready',manifest_SHA=spec['manifest_SHA'],original_error=False,closed_source_CPU=dict(actual_CPU_waited_EXIT0=True,value=v,SHA=protocol.digest(v)))
 assert protocol.native_valid_ready(row(value),spec)
 for key in value:
  changed=copy.deepcopy(value);changed[key]=None
  assert not protocol.native_valid_ready(row(changed),spec),key
 changed=copy.deepcopy(spec);changed['source_SHA']=protocol.BOOTSTRAP_SHA
 assert not protocol.native_valid_ready(row(value),changed)

def authentication():
 token=b'synthetic-not-a-secret';specs={'e2':{'manifest_SHA':'1'*64}};row=dict(key='e2',manifest_SHA='1'*64)
 raw=json.dumps(dict(epoch=100,run_id='synthetic',row=row)).encode();sig=hmac.new(token,raw,hashlib.sha256).hexdigest()
 assert ns['authenticated_row'](raw,sig,token,'synthetic',specs,100)==('e2',row)
 for sign,run,now in ((sig[:-1]+'x','synthetic',100),(sig,'wrong',100),(sig,'synthetic',161)):
  try:ns['authenticated_row'](raw,sign,token,run,specs,now)
  except AssertionError:pass
  else:raise AssertionError('bad signed row admitted')

def borrowed_channel_close():
 class Channel:
  closed=0
  def close(self):self.closed+=1
 c=Channel();network._ResponseOwnedChannelSocket(c).close();assert c.closed==0

def HTTP_response_owned_until_auth():
 originals=(network._ssh,network.http.client.HTTPConnection)
 spec=dict(key='h1',execution_backend='source210',run_id='synthetic',token='[REDACTED]')
 body=json.dumps({'go':None,'stop':False}).encode();signature=hmac.new(spec['token'].encode(),body,hashlib.sha256).hexdigest()
 for corrupt in (False,True):
  events=[]
  class Channel:
   def settimeout(self,x):assert x==15
   def close(self):events.append('rawclose')
  channel=Channel()
  class Transport:
   def open_channel(self,kind,dest,origin,timeout):assert kind=='direct-tcpip' and dest==('127.0.0.1',29754);return channel
  class Response:
   status=200
   def read(self):assert 'rawclose' not in events;events.append('read');return body
   def getheader(self,name):return signature if not corrupt else 'bad'
  class Connection:
   def __init__(self,*a,**kw):self.sock=None
   def request(self,*a,**kw):assert hmac.compare_digest(kw['headers']['X-Own-Signature'],hmac.new(spec['token'].encode(),kw['body'],hashlib.sha256).hexdigest())
   def getresponse(self):return Response()
   def close(self):events.append('HTTPclose');self.sock.close()
  network._ssh=lambda s:SimpleNamespace(get_transport=lambda:Transport());network.http.client.HTTPConnection=Connection
  try:
   value=network.send(spec,{'key':'h1'},29754);assert not corrupt and value=={'go':None,'stop':False}
  except AssertionError:assert corrupt
  assert events==['read','HTTPclose','rawclose']
 network._ssh,network.http.client.HTTPConnection=originals

for name,fn in [('actual_charge_three_overlaps_sumonce',charge_overlap),('overcap_fully_charged_false_duration',overcap_truth),('typed_native_ready_positive_and_each_field_rejected',native_fixture),('original_signed_row_authentication_tamper_rejection',authentication),('borrowed_HTTP_socket_not_raw_owner',borrowed_channel_close),('SSH_body_fullread_HMAC_then_rawclose_success_and_failure',HTTP_response_owned_until_auth)]:test(name,fn)
value=dict(epoch=time.time(),passed=all(c['passed'] for c in cases),cases=cases,no_actual_account_socket_SSH_model_or_GPU=True,specimen='synthetic accounting and transport carriers only; actual old charge/auth functions AST extracted')
(A/'OWNER86_ACCOUNT_READY_AND_CONTROL_CPU_ACTUAL.json').write_text(json.dumps(value,indent=2),'utf8')
print(json.dumps(value));assert value['passed']
