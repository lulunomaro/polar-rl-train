"""Actual reverse SSH/dependency CPU admission, no owner/listener/Task/GO."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def main():
 ready=json.loads((R/'EXPANDED210_OWNER72_DEPS_V2_ACTUAL_CPU_FINITE_RETURNED_ACTUAL.json').read_bytes());assert ready['actual_finite_returned'] and ready['actual_target210_CPU_passed']
 binding_raw=(R/'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json').read_bytes();binding=json.loads(binding_raw)
 src=(N/'controllers_v2/forwarded_original_owner_control_v1.py').read_text('utf8')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('same_authorized_72_password_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
 secret=memory.recover();client=None
 put('REVERSE210_OWNER72_TRANSPORT_CPU_STARTED_ACTUAL.json',dict(epoch=time.time(),only_source_control_dependency_and_pinned_SSH_CPU=True,no_owner_listener_or_GPU_model_Task_GO=True))
 try:
  client=route.connect()
  code="from pathlib import Path;import hashlib,json,runpy,time;B=Path('/mnt/mod4_linux_durable_20261013/mod4_owner72_reverse_control_CPU_v86_20261026');owned=B.parent;assert B.resolve().is_relative_to(owned.resolve()) and owned.is_mount() and not B.exists();B.mkdir();source=v['source'].encode();assert hashlib.sha256(source).hexdigest()==v['source_SHA'];p=B/'forwarded_original_owner_control_v1.py'\nwith p.open('xb') as f:f.write(source)\nraw=v['binding_raw'].encode();assert hashlib.sha256(raw).hexdigest()==v['binding_SHA']\nwith (B/'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json').open('xb') as f:f.write(raw)\nmodule=runpy.run_path(str(p),run_name='source210_owner72_CPU_only');s=dict(key='h1',execution_backend='source210',owner_ssh_password=v['secret72'],owner_control_dependency_binding_SHA=v['binding_SHA']);ssh=None;channel=None\ntry:\n ssh=module['_ssh'](s);t=ssh.get_transport();assert t.is_authenticated();pin=hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest();assert pin=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';channel=t.open_channel('direct-tcpip',('127.0.0.1',22),('127.0.0.1',0),timeout=10);channel.settimeout(10);banner=channel.recv(128);assert banner.startswith(b'SSH-');result=dict(epoch=time.time(),passed=True,source210_to_original72_authenticated=True,original72_pin_SHA256=pin,direct_tcpip_to_owner_host_loopback22_banner=True,full_owner29754_HTTP_HMAC_not_executed_no_listener=True,source_SHA=v['source_SHA'],dependency_binding_SHA=v['binding_SHA'],actual_dependency_CPU_verified=True,no_owner_or_canonical_IO_or_model_or_GPU=True)\nfinally:\n if channel:channel.close()\n module['close']();s['owner_ssh_password']=None;v['secret72']=None\nprint(json.dumps(result))"
  result=d.code(client,route.PY,code,dict(source=src,source_SHA=hashlib.sha256(src.encode()).hexdigest(),binding_raw=binding_raw.decode(),binding_SHA=hashlib.sha256(binding_raw).hexdigest(),secret72=secret),timeout=120)
  put('REVERSE210_OWNER72_TRANSPORT_CPU_FINITE_RETURNED_ACTUAL.json',dict(actual_finite_returned=True,**result,no_actual_owner29754_connection_or_training=True))
  print(json.dumps(dict(passed=result['passed'],pinned_reverse_SSH_CPU=True,no_training=True)))
 finally:
  secret=None
  if client:client.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('REVERSE210_OWNER72_TRANSPORT_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_auto_retry_same_root_or_once=True,no_training_or_budget_write=True));raise
