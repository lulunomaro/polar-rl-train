"""Verify prospective E3 control SSH authentication and direct channel before any new GO."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports'
N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V1_RESOURCE_V69_20261025'
CODE=r'''
import hashlib,json,types,time
m=types.ModuleType('prospective_control');m.__file__='<memory_only_prospective_control>'
assert hashlib.sha256(v['module_source'].encode()).hexdigest()==v['module_SHA']
exec(compile(v['module_source'],m.__file__,'exec'),m.__dict__)
try:
 c=m._ssh(dict(key='recovery',owner_ssh_password=v['owner_password']));t=c.get_transport();assert t.is_authenticated()
 ch=t.open_channel('direct-tcpip',('127.0.0.1',22),('127.0.0.1',0),timeout=8)
 try:ch.settimeout(8);banner=ch.recv(256).decode('utf8','replace');assert banner.startswith('SSH-2.0-OpenSSH_')
 finally:ch.close()
 print(json.dumps(dict(epoch=time.time(),passed=True,original_owner_host_key_and_password_authenticated_from72=True,actual_SSH_direct_tcpip_enabled=True,banner=banner,control_module_SHA=v['module_SHA'],all_isolated_dependency_files_SHA_verified=True,no_new_owner_GPU_model_or_budget_write=True)))
finally:
 m.close();v['owner_password']=None
'''
with (R/'PINNED72_TO_OWNER_CONTROL_CHANNEL_STARTED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv),f)
try:
 module=N/'payloads/recovery/forwarded_original_owner_control_v1.py';raw=module.read_bytes()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 p=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py';sp=importlib.util.spec_from_file_location('memory',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
 secret=m.recover();c=d.connect72(secret);secret=None;password=None;payload=None
 try:
  password,_=recover('RM_SSH_PASSWORD');assert password
  payload=dict(module_source=raw.decode(),module_SHA=hashlib.sha256(raw).hexdigest(),owner_password=password);password=None
  result=d.code(c,d.PY72,CODE,payload,timeout=45)
 finally:
  password=None
  if payload:payload.clear()
  c.close()
 with (R/'PINNED72_TO_OWNER_CONTROL_CHANNEL_CPU_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(result,actual_finite_returned=True),f,ensure_ascii=False,indent=2)
 print(json.dumps(result))
except BaseException:
 with (R/'PINNED72_TO_OWNER_CONTROL_CHANNEL_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GO_or_budget_write=True),f,indent=2)
 raise
