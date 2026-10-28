from pathlib import Path
import ast,copy,hashlib,json,runpy,shutil,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';N=T/'MOD4_H1_FLAT05_STANCE_START_COMPARE_RESOURCE_V99_20261028';OLD=L/'TWO97_H1_E3_NEW_FULL_CPU_OWNER_SOURCE_V1';C=L/'TWO99_GENUINE_NATIVE_START_COMPARISON_OWNER_SOURCE_V1'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def rep(s,a,b,count=1):
 assert s.count(a)==count,(a,s.count(a));return s.replace(a,b)
def ast_defs(raw,names):
 t=ast.parse(raw);return {n.name:ast.dump(n,include_attributes=False) for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names}
def main():
 assert not C.exists();C.mkdir();R=C/'reports';R.mkdir();prep=read(N/'reports/TWO99_EXACT_START_PAYLOADS_PREPARED_ACTUAL.json');actual=read(N/'reports/TWO99_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json');assert actual['passed'];oldpublic=read(OLD/'reports/TWO97_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json');runid='TWO99_STANCE_GOAL_CONTINUE97_VS_PROTECTED_NATIVE0_'+str(time.time_ns());stage='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_TWO99_NATIVE_START_COMPARE_2610v99'
 specs={};tasks={};protocols={};sources={};node_roots={};node_names={};audit=[]
 for mode in ('continue97','restart0'):
  p=prep['payloads'][mode];task=p['task'];key=p['logical_slot'];result=actual['results'][mode];value=result['value'];assert result['passed'] and result['proof']['actual_waited'] and result['proof']['returncode']==0 and value['input_start_mode']==mode and value['stance_reference_source_CPU_passed']
  spec=copy.deepcopy(oldpublic['experts']['h1']);spec.update({k:task[k] for k in ('source_SHA','source_progress','source_native_iteration','source_qualification_kind','native_seed','native_learning_seed','native_reference_SHA','changed_plant700_to_nominal400','input_start_mode','stance_reference_revision')});spec.update(key=key,logical_slot=key,canonical_worker_key='h1',GPU_UUID=p['GPU_UUID'],private_lock='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+p['GPU_UUID']+'.lock',job_root=p['job_root'],CPU_path=p['job_root']+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json',CPU_proof_path=p['job_root']+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json',source_CPU_SHA=result['proof']['report_SHA'],CPU_waited_proof_SHA=result['proof_SHA'],payload_manifest_SHA=p['manifest_SHA'],source_contract_SHA=p['source_contract_SHA'],payload_manifest_path=p['job_root']+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json',source_contract_path=p['job_root']+'/FLAT90_SOURCE_CONTRACT_ACTUAL.json',run_id=runid)
  protocol=(OLD/'owner/h1_next72_protocol_actual95_v2.py').read_text('utf8')
  for a,b in [("KEY='h1';GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'","KEY="+repr(key)+";GPU="+repr(p['GPU_UUID'])),("JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_TASK_FOCUSED_2610v97/h1'","JOB="+repr(p['job_root'])),("SOURCE='b008fc03d5de3e39217101523c7e8fc0ddebf5cd6e63699582b61053171d165e'","SOURCE="+repr(spec['source_SHA'])),("REFERENCE='b4d801a47b92a0d63378df0cea15e8c736fe489c2fd37a63399a1a2ed3d00502'","REFERENCE="+repr(spec['native_reference_SHA'])),('PROGRESS=dict(updates=10692,world_updates=106920,policy_updates=10372)','PROGRESS='+repr(spec['source_progress'])),("KIND='MOD4_NATIVE93_H1_TASK_FOCUSED95_TYPED_SOURCE_CPU_V1'","KIND="+repr(spec['source_qualification_kind']))]:protocol=rep(protocol,a,b)
  protocol=rep(protocol,"require(s.get('key')==KEY and s.get('nativeflat90') is True,'one actual logical h1 flat slot')","require(s.get('key')==KEY and s.get('nativeflat90') is True,'one actual logical native99 slot')\n require(s.get('input_start_mode')=="+repr(mode)+" and s.get('stance_reference_revision')=="+repr(spec['stance_reference_revision'])+",'exact99 start mode and grounded stance reference')")
  protocol=rep(protocol,"s.get('changed_plant700_to_nominal400') is False","s.get('changed_plant700_to_nominal400') is "+repr(spec['changed_plant700_to_nominal400']))
  protocol=rep(protocol,"require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE,'actual typed sourceCPU')","require(v.get('passed') is True and v.get('kind')==KIND and v.get('source_SHA')==SOURCE,'actual typed sourceCPU')\n require(v.get('input_start_mode')==s['input_start_mode'] and v.get('stance_reference_revision')==s['stance_reference_revision'] and v.get('stance_reference_source_CPU_passed') is True and v.get('logical_slot')==KEY and v.get('canonical_worker_key')=='h1','actual99 source kind/stance/alias CPU')")
  protocol=rep(protocol,"fields=('logical_slot',","fields=('input_start_mode','stance_reference_revision','logical_slot',")
  protocol=rep(protocol,'nativeflat90=True,changed_plant700_to_nominal400=False,','nativeflat90=True,changed_plant700_to_nominal400='+repr(spec['changed_plant700_to_nominal400'])+',')
  protocol=rep(protocol,"for k in ('task_focused_real_replay','native_learning_seed','source_SHA'","for k in ('input_start_mode','stance_reference_revision','task_focused_real_replay','native_learning_seed','source_SHA'")
  protocols[key]=protocol;specs[key]=spec;node_roots[key]=stage+'/node_'+key;node_names[key]='two95_native_slot_node_v1.py';sources[key]=str(C/('node_'+key))
 owner=(OLD/'owner/two95_finite_owner_authority72_v1.py').read_text('utf8');owner=rep(owner,"set(specs)=={'h1','e3'}","set(specs)=={'h1','restart'}").replace('Linux_TWO97_H1_E3_','Linux_TWO99_NATIVE_START_COMPARE_')
 mixed=(OLD/'owner/mixed72_next_protocol_v1.py').read_text('utf8');mixed=rep(mixed,"KEYS={'h1','e3'}","KEYS={'h1','restart'}");mixed=rep(mixed,'import E3_next72_protocol_v1 as p','import restart_next72_protocol_v99 as p')
 common=(OLD/'owner/three_slot_common_v1.py').read_text('utf8');common=rep(common,"CAPS={'h1':3900,'e3':3900}","CAPS={'h1':3900,'restart':3900}");common=rep(common,"'e3':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'","'restart':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'");common=rep(common,"assert spec['key']=='h1' and spec['canonical_worker_key']=='h1'","assert spec['key'] in ('h1','restart') and spec['canonical_worker_key']=='h1'")
 original_common=(OLD/'owner/three_slot_common_v1.py').read_text('utf8');names=('authenticated_row','charge_values','terminal','state','environment','ident');assert ast_defs(common,names)==ast_defs(original_common,names)
 old_owner_tree=ast.parse((OLD/'owner/two95_finite_owner_authority72_v1.py').read_bytes());new_owner_tree=ast.parse(owner)
 def protected_nodes(tree):
  f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='owner');return [ast.dump(n,include_attributes=False) for n in f.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ('Handler','account')]
 assert protected_nodes(old_owner_tree)==protected_nodes(new_owner_tree)
 forward=(OLD/'node_h1/forwarded_original_owner_control_v1.py').read_text('utf8');forward_new=rep(forward,"('h1','h1_210','e2')","('h1','h1_210','e2','restart')");assert forward_new.replace("('h1','h1_210','e2','restart')","('h1','h1_210','e2')")==forward
 for role in ('owner','node_h1','node_restart'):
  target=C/role;source=OLD/('owner' if role=='owner' else 'node_h1');target.mkdir()
  for p in source.iterdir():
   if p.is_file() and p.suffix=='.py':shutil.copy2(p,target/p.name)
  write(target/'three_slot_common_v1.py',common);write(target/'mixed72_next_protocol_v1.py',mixed);write(target/'h1_next72_protocol_actual95_v2.py',protocols['h1']);write(target/'restart_next72_protocol_v99.py',protocols['restart']);write(target/'forwarded_original_owner_control_v1.py',forward_new)
  if role=='owner':write(target/'two95_finite_owner_authority72_v1.py',owner)
 for key,spec in specs.items():
  target=Path(sources[key]);rows=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(target.iterdir()) if p.is_file()]
  mf=dict(key=key,source_SHA=spec['source_SHA'],worker_SHA=spec['worker_SHA'],source_CPU_SHA=spec['source_CPU_SHA'],files=rows)
  put(target/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json',mf);spec['manifest_SHA']=H(target/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json');tasks[key]=copy.deepcopy(spec)
 public=dict(run_id=runid,owner_root=stage+'/owner',owner_name='two95_finite_owner_authority72_v1.py',owner_source=str(C/'owner'),node_roots=node_roots,node_sources=sources,node_names=node_names,authority_generation=oldpublic['authority_generation'],scheduling_authority=oldpublic['scheduling_authority'],deferred_experts=[],expected_closed_remaining=531527.5335400105,experts=specs,task_templates=tasks)
 # Genuine two-slot routing and exact negative source/mode/alias checks, metadata only.
 import sys
 sys.path.insert(0,str(C/'owner'));import mixed72_next_protocol_v1 as dispatch
 assert dispatch.validate_schedule(public)
 negative_count=0
 for key,spec in specs.items():
  protocol=dispatch.module_for(spec);mode=spec['input_start_mode'];v=actual['results'][mode]['value'];assert protocol.validate_cpu_value(v,spec)
  for field in ('source_SHA','GPU_UUID','logical_slot','input_start_mode','stance_reference_revision'):
   bad=copy.deepcopy(spec);bad[field]=('bad' if field!='stance_reference_revision' else {})
   try:protocol.validate_spec(bad)
   except (ValueError,KeyError,TypeError):negative_count+=1
   else:raise AssertionError('undeclared source route passed '+key+'/'+field)
  for field in ('source_SHA','GPU_UUID','logical_slot','input_start_mode','stance_reference_revision'):
   bad=copy.deepcopy(v);bad[field]=('bad' if field!='stance_reference_revision' else {})
   try:protocol.validate_cpu_value(bad,spec)
   except (ValueError,KeyError,TypeError):negative_count+=1
   else:raise AssertionError('undeclared CPU route passed '+key+'/'+field)
 for p in C.rglob('*.py'):ast.parse(p.read_bytes())
 put(R/'TWO99_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json',public)
 put(R/'TWO99_SOURCE_CPU_ROUTING_AND_ORIGINAL_WRITER_AST_PROOF_ACTUAL.json',dict(passed=True,epoch=time.time(),real_native_slots=['h1','restart'],distinct_start_sources=True,actual_source_CPU_bound=True,negative_scopes_rejected=negative_count,original_account_nested_function_and_Handler_AST_exact=True,original_charge_values_auth_terminal_state_AST_exact=True,original_forward_HMAC_socket_body_unchanged_only_add_registered_restart_key=True,no_model_Gpu_remote_or_account_IO=True,no_GO=True))
 # Reuse original activation, replacing only native99 public names/iteration and native-only binding.
 activation=(OLD/'activate_two97_new_fullCPU_bound_original_single_writer_once_v1.py').read_text('utf8').replace('TWO97','TWO99').replace("{'h1','e3'}","{'h1','restart'}").replace("for key in ('h1','e3'):","for key in ('h1','restart'):").replace("   if key=='e3':task['actual_resource_admission']=pre['resources'][key]\n",'').replace('first_NEW_native_policy_and_E3_PPO_pending=True','two_first_NEW_native_policies_pending=True')
 parsed=ast.parse(activation);node=next(n for n in parsed.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='VERIFY' for t in n.targets))
 verify='''from pathlib import Path
import json,hashlib,sys
B=Path(v['root']);sys.path.insert(0,str(B))
for row in v['files']:
 p=B/row['relative'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
if v['role']=='owner':
 from mixed72_next_protocol_v1 import validate_schedule
 validate_schedule(v['public']);result=dict(owner_protocol_actual_sources_sealed=True)
else:
 spec=v['spec'];job=Path(spec['job_root']);target=job/'job0/FLAT90_RUNTIME_GRANT_BINDING.json';assert not target.exists()
 with target.open('x',encoding='utf8') as f:json.dump(v['task'],f,indent=2)
 from mixed72_next_protocol_v1 import module_for
 m=module_for(spec);m.validate_payload(spec,B);envelope=m.load_actual_flat_preinstalled_CPU(spec,B)
 result=dict(actual_CPU_JSON_and_original_wait_reused=True,source_CPU_SHA=envelope['SHA'],runtime_binding_path=str(target))
print(json.dumps(dict(passed=True,**result,no_model_sourceCPU_GPU_or_account_action=True)))'''
 lines=activation.splitlines(keepends=True);activation=''.join(lines[:node.lineno-1])+'VERIFY='+repr(verify)+'\n'+''.join(lines[node.end_lineno:]);write(C/'activate_two99_two_native_starts_original_single_writer_once.py',activation)
 ast.parse(activation)
 put(C/'FROZEN_TWO99_CONTROLLER_AND_SEALED_REQUEST_INDEX_V1.json',dict(frozen=True,unused=True,rows=[dict(relative=p.relative_to(C).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(C.rglob('*')) if p.is_file()]))
 print(json.dumps(dict(prepared=True,run_id=runid,keys=list(specs),negative_cases=negative_count,original_writer_account_and_HMAC_AST_preserved=True,actual_GO_pending=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  if (C/'reports').is_dir():put(C/'reports/TWO99_CONTROLLER_PREPARER_ORIGINAL_ERROR_ACTUAL.json',dict(error=__import__('traceback').format_exc(),no_remote_model_or_account_action=True))
  raise
