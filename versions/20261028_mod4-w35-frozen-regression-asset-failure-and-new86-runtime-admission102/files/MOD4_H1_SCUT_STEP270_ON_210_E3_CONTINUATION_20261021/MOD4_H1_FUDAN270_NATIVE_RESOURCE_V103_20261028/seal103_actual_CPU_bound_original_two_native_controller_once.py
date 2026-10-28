from pathlib import Path
import ast,copy,hashlib,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';OLD=L/'TWO101_PRODUCER_FIXED_NATIVE20_ORIGINAL_OWNER_SOURCE_V1';C=L/'TWO103_FUDAN270_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.write_text(s,encoding='utf8')
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
helper=__import__('runpy').run_path(str(T/'MOD4_H1_FLAT20_NATIVE_RESOURCE_V100_20261028/seal_two100_actual_CPU_bound_original_owner_once.py'),run_name='definitions_only');assign=helper['assign'];rep=helper['rep'];replace_def=__import__('runpy').run_path(str(T/'MOD4_H1_FLAT20_NATIVE_RESOURCE_V100_20261028/prepare_target20_two_saved99_native_payloads_once.py'),run_name='definitions_only')['replace_def']
def main():
 assert not C.exists();C.mkdir();R=C/'reports';R.mkdir()
 prep=read(N/'reports/TWO103_BANK_READER_V4_PAYLOADS_PREPARED_ACTUAL.json');actual=read(N/'reports/TWO103_V3_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json');assert actual['passed']
 old=read(OLD/'reports/TWO101_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json');specs={};protocols={};bykey={};runid='TWO103_FUDAN_REAL270_NATIVE_SEEDS27_28_'+str(time.time_ns());stage='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_TWO103_FUDAN270_NATIVE_2610v103'
 fields=('source_SHA','source_progress','source_native_iteration','source_qualification_kind','native_seed','native_learning_seed','native_reference_SHA','changed_plant700_to_nominal400','input_start_mode','fudan_step_task','task_focused_real_replay')
 for mode,p in prep['payloads'].items():
  task=p['task'];key=p['logical_slot'];result=actual['results'][mode];v=result['value'];root=result['actual_job_root']
  assert result['passed'] and result['proof']['actual_waited'] and result['proof']['returncode']==0 and v['own_FK_reward_and_goal_source_CPU_passed'] and v['physical_initial_seed']==task['native_seed']
  spec=copy.deepcopy(old['experts'][key])
  for k in ('source101_metadata_only_producer_reference_fix','source100_original_fullstate_CPU_SHA','stance_reference_revision','flat_jump_target_m','user_authorized_height_change_5_to20'):spec.pop(k,None)
  spec.update({k:task[k] for k in fields});spec.update(key=key,logical_slot=key,canonical_worker_key='h1',GPU_UUID=p['GPU_UUID'],job_root=root,CPU_path=root+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json',CPU_proof_path=root+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json',source_CPU_SHA=result['proof']['report_SHA'],CPU_waited_proof_SHA=result['proof_SHA'],payload_manifest_SHA=p['manifest_SHA'],source_contract_SHA=p['source_contract_SHA'],payload_manifest_path=root+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json',source_contract_path=root+'/FLAT90_SOURCE_CONTRACT_ACTUAL.json',run_id=runid,worker_SHA=H(Path(p['payload'])/'h1_native_flat90_worker_v1.py'))
  name='h1_next72_protocol_actual95_v2.py' if key=='h1' else 'h1_seed28_next72_protocol_v100.py';s=(OLD/'owner'/name).read_text('utf8')
  for k,value in [('JOB',root),('SOURCE',spec['source_SHA']),('REFERENCE',spec['native_reference_SHA']),('PROGRESS',spec['source_progress']),('KIND',spec['source_qualification_kind'])]:s=assign(s,k,value)
  lines=s.splitlines(keepends=True)
  for i,line in enumerate(lines):
   if line.startswith(" require(s.get('source101_metadata_only_producer_reference_fix')"):lines[i]=''
   if line.startswith(" require(s.get('input_start_mode')=="):lines[i]=" require(s.get('input_start_mode')=="+repr(task['input_start_mode'])+" and s.get('fudan_step_task')=="+repr(task['fudan_step_task'])+",'exact Fudan103 own270 task')\n"
   if line.startswith(" require(s.get('native_learning_seed')==27 and s.get('task_focused_real_replay')=="):lines[i]=" require(s.get('native_learning_seed')==27 and s.get('task_focused_real_replay')=="+repr(task['task_focused_real_replay'])+",'exact Fudan103 replay/source learning seed')\n"
  s=''.join(lines)
  s=replace_def(s,'validate_cpu_value',(N/'source_templates/protocol_validate_CPU.txt').read_text('utf8'))
  for name2 in ('flat_go_fields','validate_payload'):
   tree=ast.parse(s);node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name2);ls=s.splitlines(keepends=True);part=''.join(ls[node.lineno-1:node.end_lineno])
   part=rep(part,"'source101_metadata_only_producer_reference_fix','source100_original_fullstate_CPU_SHA','flat_jump_target_m','user_authorized_height_change_5_to20','input_start_mode','stance_reference_revision'","'fudan_step_task','input_start_mode'")
   part=part.replace('actual_H1_flat05_scope_admitted=True,actual_H1_step270_scope_admitted=False','actual_H1_flat05_scope_admitted=False,actual_H1_step270_scope_admitted=True')
   s=''.join(ls[:node.lineno-1])+part+'\n'+''.join(ls[node.end_lineno:])
  ast.parse(s);protocols[key]=s;specs[key]=spec;bykey[key]=mode
 for role in ['owner','node_h1','node_h1_seed28']:
  d=C/role;d.mkdir()
  for p in (OLD/role).iterdir():
   if p.is_file() and p.suffix=='.py':write(d/p.name,p.read_text('utf8'))
  write(d/'h1_next72_protocol_actual95_v2.py',protocols['h1']);write(d/'h1_seed28_next72_protocol_v100.py',protocols['h1_seed28'])
 for name in ('two95_finite_owner_authority72_v1.py','three_slot_common_v1.py','forwarded_original_owner_control_v1.py'):
  assert (C/'owner'/name).read_bytes()==(OLD/'owner'/name).read_bytes(),'original owner/common/forward bytes '+name
 for key,spec in specs.items():
  d=C/('node_'+key);put(d/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json',dict(key=key,source_SHA=spec['source_SHA'],worker_SHA=spec['worker_SHA'],source_CPU_SHA=spec['source_CPU_SHA'],files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(d.iterdir()) if p.is_file()]));spec['manifest_SHA']=H(d/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json')
 public=dict(run_id=runid,owner_root=stage+'/owner',owner_name='two95_finite_owner_authority72_v1.py',owner_source=str(C/'owner'),node_roots={k:stage+'/node_'+k for k in specs},node_sources={k:str(C/('node_'+k)) for k in specs},node_names={k:'two95_native_slot_node_v1.py' for k in specs},authority_generation=old['authority_generation'],scheduling_authority=old['scheduling_authority'],deferred_experts=[],expected_closed_remaining=actual['results']['seed27']['resource']['remaining'],experts=specs,task_templates=copy.deepcopy(specs),not_GPU_resource_admitted=True,no_GO=True)
 sys.path.insert(0,str(C/'owner'))
 import mixed72_next_protocol_v1 as dispatch
 assert dispatch.validate_schedule(public);negative=0
 for key,spec in specs.items():
  p=dispatch.module_for(spec);value=actual['results'][bykey[key]]['value'];assert p.validate_cpu_value(value,spec);p.validate_waited_value(actual['results'][bykey[key]]['proof'],spec)
  for field in ['source_SHA','GPU_UUID','logical_slot','input_start_mode','fudan_step_task','native_seed']:
   wrong=copy.deepcopy(spec);wrong[field]={} if field=='fudan_step_task' else -1 if field=='native_seed' else 'bad'
   try:p.validate_spec(wrong)
   except (ValueError,KeyError,TypeError):negative+=1
   else:raise AssertionError('invalid specification accepted '+key+'/'+field)
  for field in ['source_SHA','GPU_UUID','logical_slot','fudan_step_task','physical_initial_seed']:
   wrong=copy.deepcopy(value);wrong[field]={} if field=='fudan_step_task' else -1 if field=='physical_initial_seed' else 'bad'
   try:p.validate_cpu_value(wrong,spec)
   except (ValueError,KeyError,TypeError):negative+=1
   else:raise AssertionError('invalid CPU binding accepted '+key+'/'+field)
 put(R/'TWO103_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json',public)
 put(R/'TWO103_SEALED_ORIGINAL_WRITER_AND_FUDAN_ROUTING_CPU_ACTUAL.json',dict(passed=True,epoch=time.time(),actual_two_CPU_reports_and_external_wait0_bound=True,original_owner_common_forward_bytes_exact=True,negative_cases=negative,not_GPU_or_GO_admitted=True,resource_snapshots={k:v['resource']['resource'] for k,v in actual['results'].items()}))
 put(C/'FROZEN_UNUSED_TWO103_FUDAN270_CONTROLLER_INDEX_V1.json',dict(frozen=True,unused=True,files=[dict(relative=p.relative_to(C).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(C.rglob('*')) if p.is_file()]))
 print(json.dumps(dict(sealed_actual_CPU=True,no_GO=True,negative_cases=negative,original_writer_bytes_exact=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  if (C/'reports').exists():put(C/'reports/TWO103_CONTROLLER_PREPARER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_network_or_model_action=True))
  raise
