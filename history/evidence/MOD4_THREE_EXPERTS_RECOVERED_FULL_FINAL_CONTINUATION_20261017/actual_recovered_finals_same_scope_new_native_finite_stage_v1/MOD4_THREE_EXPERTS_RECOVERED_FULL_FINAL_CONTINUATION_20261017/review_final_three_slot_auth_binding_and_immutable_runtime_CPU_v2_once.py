from pathlib import Path
import sys,types,importlib.util,json,time,hashlib,hmac,ast,traceback
U=Path(__file__).resolve().parent;R=U/'reports'
def main():
 sys.modules.setdefault('fcntl',types.SimpleNamespace());sp=importlib.util.spec_from_file_location('final_three_slot_common_CPU',U/'three_slot_common_v1.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);token=b'CPU-fixture-only-no-runtime-capability';specs={k:dict(manifest_SHA=hashlib.sha256(k.encode()).hexdigest()) for k in b.CAPS};count=0
 for key in specs:
  message=dict(run_id='CPU_fixture',epoch=100.,row=dict(key=key,manifest_SHA=specs[key]['manifest_SHA'],phase='native_CPU_review_running'));raw=json.dumps(message).encode();sig=hmac.new(token,raw,hashlib.sha256).hexdigest();assert b.authenticated_row(raw,sig,token,'CPU_fixture',specs,101)[0]==key
  for which in ('signature','run','age','future','key','manifest'):
   v=json.loads(raw);signature=sig
   if which=='signature':signature='0'*64
   if which=='run':v['run_id']='wrong'
   if which=='age':v['epoch']=40
   if which=='future':v['epoch']=161
   if which=='key':v['row']['key']='unregistered'
   if which=='manifest':v['row']['manifest_SHA']='wrong'
   bad=json.dumps(v).encode()
   if which!='signature':signature=hmac.new(token,bad,hashlib.sha256).hexdigest()
   try:b.authenticated_row(bad,signature,token,'CPU_fixture',specs,101)
   except (AssertionError,KeyError):count+=1
   else:raise AssertionError(which)
 hashes={}
 for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_slot_resource_v1.py','prepare_recovered_three_finals_same_scope_next_finite_payloads_CPU_once.py','deploy_recovered_three_finals_new_native_then_original_owner_once.py'):
  p=U/name;raw=p.read_bytes();ast.parse(raw.decode());hashes[name]=hashlib.sha256(raw).hexdigest()
 code=(U/'deploy_recovered_three_finals_new_native_then_original_owner_once.py').read_text();assert 'from stdin_only_finite_launch_v1 import launch' in code and 'json.dumps(cfg)' not in code and 'all_targets_CPU_complete=True' in code
 out=dict(epoch=time.time(),passed_CPU_only=True,authenticated_wrong_signature_run_age_future_slot_manifest_cases_rejected=count,final_runtime_sources=hashes,prior33_readiness_cost_cases_report_preserved=True,per_slot_native_before_own_GO_all_nodes_registered_not_all_native_wait=True,original_runtime_OS_fcntl_HTTP_SDK_actual_execution_still_required=True,capability_only_SSH_stdin_child_stdin_static_binding_reviewed=True,no_actual_capability_fixture_or_credential=True,no_live_worker_mutation_or_GPU_or_budget=True);p=R/'THREE_SLOT_FINAL_AUTH_NEGATIVES_AND_RUNTIME_CPU_V2_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THREE_SLOT_AUTH_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_actual_runtime_or_GPU_mutation=True),f,indent=2)
  raise
