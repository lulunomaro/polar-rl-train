"""Consume successful owner/phase snapshot; read only missing target identities."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def main():
 q=json.loads((R/'THREE_GPU86B_ACTUAL_OWNER_NODES_DETACHED.json').read_bytes());owner=json.loads((R/'THREE_GPU86B_FIRST_OWNER_SIGNED_GO_POLICY_SNAPSHOT_RETURNED_ACTUAL.json').read_bytes())
 assert owner['status']=='positive_updates_and_phase_exposure' and owner['native_first_policy']['policy_updates']>58 and owner['phase_exposure_observed']
 source=next(ast.literal_eval(x.value) for x in ast.parse((N/'observe_three_gpu86B_first_GO_updates_phase_finite_V2_unused_once.py').read_text('utf8')).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TARGET_READ' for t in x.targets))
 bad="expected=[p.cmdline()[0],'-u','-B',str(B/spec['production_script'])]+(['--phase','production'] if key=='h1' else ['--job','0','--phase','production']);assert p.cmdline()==expected"
 good="assert node['pid']==v['node_detached_pid'] and np.cmdline()[-1]==str(B/'three_slot_finite_node_v1.py');expected=np.cmdline()[:-1]+[str(B/spec['production_script'])]+(['--phase','production'] if key=='h1' else ['--job','0','--phase','production']);assert p.cmdline()==expected"
 assert source.count(bad)==1;source=source.replace(bad,good,1)
 original="first=json.loads((B/'job0/production/FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json').read_bytes());"
 assert source.count(original)==1;source=source.replace(original,"first=v['cached_native_first'];",1)
 original="phase=B/'job0/production/NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json';extra=dict(native_first=first,restore=restore,runtime_order=runtime,phase=json.loads(phase.read_bytes()) if phase.exists() else None)"
 assert source.count(original)==1;source=source.replace(original,"extra=dict(native_first=first,restore=restore,runtime_order=runtime,phase=v['cached_phase'])",1)
 compile(source,'<missing-only loader-aware target proof>','exec')
 put('FIRST_OBSERVER_V2_LOADER_ARGV_ASSUMPTION_AND_V3_MISSING_ONLY_CLASSIFICATION_ACTUAL.json',dict(epoch=time.time(),classification='READER_ASSUMED_DIRECT_PYTHON_BUT_72_USES_EXISTING_GLIBC_LOADER',owner_signed_GO_native_positive_and_phase_snapshot_already_actual=True,source_request_guard_stays_exact_full_exe_argv_create=True,correct_expected_prefix_from_same_approved_node_runtime=True,no_owner_or_first_policy_or_phase_or_PT_reread=True,missing_target_source_SHA=hashlib.sha256(source.encode()).hexdigest(),original_false_preserved=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('known72_authorized_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
 secret=memory.recover();client=None;targets={}
 try:
  client=d.connect72(secret)
  for key in ('e2','recovery'):
   targets[key]=d.code(client,d.PY72,source,dict(root=q['roots'][key],key=key,spec=q['specs'][key],row=owner['current']['rows'][key],run_id=q['run_id'],node_detached_pid=q['nodes'][key]['detached_pid'],cached_native_first=owner['native_first_policy'],cached_phase=owner['phase_sampling']),timeout=60)
  client.close();client=None;client=route.connect();key='h1'
  targets[key]=d.code(client,route.PY,source,dict(root=q['roots'][key],key=key,spec=q['specs'][key],row=owner['current']['rows'][key],run_id=q['run_id'],node_detached_pid=q['nodes'][key]['detached_pid'],cached_native_first=owner['native_first_policy'],cached_phase=owner['phase_sampling']),timeout=60)
  result=dict(epoch=time.time(),passed=True,actual_finite_returned=True,run_id=q['run_id'],go=owner['go'],authority72=owner,targets=targets,all3_unique_expected_UUIDs_verified=True,native_restored_and_new_policy_updates_verified=True,phase_exposure_observed=True,owner_phase_snapshot_epoch=owner['epoch'],first_positive_scope_is_snapshot_not_continuous_alive=True,no_skill_or_FINAL_claim=True)
  put('THREE_GPU86B_FIRST_GO_PPO_NATIVE_POLICY_PHASE_ACTUAL.json',result);print(json.dumps(dict(passed=True,run_id=q['run_id'],native_first_newPi=owner['native_first_policy']['policy_updates'],first_newPi_after_control=owner['native_first_policy']['before_control'],sampled_jump_starts=sum(owner['phase_sampling']['bands'][x] for x in ('100to135','136to179')),all3_UUIDs=True,no_skill_claim=True)))
 finally:
  secret=None
  if client:client.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('MISSING_TARGET86B_V3_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry_or_training_hotpatch=True));raise
