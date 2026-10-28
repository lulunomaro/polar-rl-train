from pathlib import Path
import ast,copy,hashlib,json,runpy,sys,time,traceback,importlib.util
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
A=L/'TWO104_FUDAN270_LIGHT_OCCUPANCY_ORIGINAL_OWNER_SOURCE_V1';B=L/'TWO106_FUDAN270_20S_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1';Q=L/'TWO106_FUDAN270_20S_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:f.write(s)
def rep(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def assign(s,name,value):
 x=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets));lines=s.splitlines(keepends=True);return ''.join(lines[:x.lineno-1])+name+'='+repr(value)+'\n'+''.join(lines[x.end_lineno:])
def module(name,p):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main():
 assert not B.exists() and not Q.exists();(B/'reports').mkdir(parents=True);(Q/'reports').mkdir(parents=True)
 prep=read(R/'TWO106_COHERENT20S_SEALED_PAYLOADS_ACTUAL.json');admitted=read(R/'TWO106_V3_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json');assert admitted['passed']
 original=read(A/'reports/TWO104_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json');public=copy.deepcopy(original);public.update(run_id='TWO106_FUDAN270_USER_EPISODE20_'+str(time.time_ns()),owner_source=str(B/'owner'),owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_TWO106_FUDAN270_EPISODE20_2610v106/owner',expected_closed_remaining=509633.3206150532)
 for mode,item in prep['payloads'].items():
  k=item['logical_slot'];spec=public['experts'][k];value=admitted['results'][mode];assert value['passed'] and value['actual_CPU_waited_EXIT0'];task=item['task'];job=item['job_root']
  for field in ('source_SHA','source_progress','source_native_iteration','native_seed','native_reference_SHA','source_qualification_kind','input_start_mode','fudan_step_task','task_focused_real_replay','imagination_terminal_exposure','native_learning_seed','goal_conditioning'):spec[field]=copy.deepcopy(task[field])
  spec.update(run_id=public['run_id'],job_root=job,CPU_path=job+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json',CPU_proof_path=job+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json',source_CPU_SHA=value['proof']['report_SHA'],CPU_waited_proof_SHA=value['proof_SHA'],payload_manifest_SHA=item['manifest_SHA'],source_contract_SHA=item['source_contract_SHA'],payload_manifest_path=job+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json',source_contract_path=job+'/FLAT90_SOURCE_CONTRACT_ACTUAL.json',worker_SHA=H(Path(item['payload'])/'h1_native_flat90_worker_v1.py'))
  public['node_sources'][k]=str(B/('node_'+k));public['node_roots'][k]='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_TWO106_FUDAN270_EPISODE20_2610v106/node_'+k
 # Preserve exact owner, common, single-authority and forwarding implementations.
 for role in ('owner','node_h1','node_h1_seed28'):
  for p in (A/role).glob('*.py'):
   s=p.read_text('utf8')
   if p.name in ('h1_next72_protocol_actual95_v2.py','h1_seed28_next72_protocol_v100.py'):
    key='h1' if p.name.startswith('h1_next') else 'h1_seed28';old=original['experts'][key];new=public['experts'][key]
    for name,value in [('JOB',new['job_root']),('SOURCE',new['source_SHA']),('REFERENCE',new['native_reference_SHA']),('PROGRESS',new['source_progress']),('KIND',new['source_qualification_kind'])]:s=assign(s,name,value)
    for field in ('fudan_step_task','task_focused_real_replay','imagination_terminal_exposure'):s=rep(s,repr(old[field]),repr(new[field]))
    s=rep(s,repr(old['input_start_mode']),repr(new['input_start_mode']))
    needle=" require(v.get('fudan_step_task')==s['fudan_step_task']"
    s=rep(s,needle," require(v.get('episode_clock')==s['fudan_step_task']['clock_contract'] and v.get('request_observation_clock_aligned') is True,'actual coherent20s CPU proof')\n"+needle)
   ast.parse(s);write(B/role/p.name,s)
 for key,spec in public['experts'].items():
  folder=B/('node_'+key);put(folder/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json',dict(key=key,source_SHA=spec['source_SHA'],worker_SHA=spec['worker_SHA'],source_CPU_SHA=spec['source_CPU_SHA'],files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(folder.iterdir()) if p.is_file()]));spec['manifest_SHA']=H(folder/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json')
 public['task_templates']=copy.deepcopy(public['experts']);put(B/'reports/TWO106_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json',public)
 s=(A/'activate_TWO104_fudan270_user_light_compute_original_writer_UNUSED_once.py').read_text('utf8').replace('TWO104','TWO106');ast.parse(s);write(B/'activate_TWO106_fudan270_20s_original_single_writer_UNUSED_once.py',s)
 for name in ('two95_finite_owner_authority72_v1.py','three_slot_common_v1.py','forwarded_original_owner_control_v1.py','single_writer72_authority_V85M_source.py'):assert (B/'owner'/name).read_bytes()==(A/'owner'/name).read_bytes()
 # Exact generated signed-GO task admission and adverse spec checks, no PT I/O.
 checked=[];negative=[]
 for mode,item in prep['payloads'].items():
  key=item['logical_slot'];spec=public['experts'][key];pname='h1_next72_protocol_actual95_v2.py' if key=='h1' else 'h1_seed28_next72_protocol_v100.py';protocol=module('new106_'+key,B/'owner'/pname)
  assert protocol.validate_spec(spec);value=admitted['results'][mode];protocol.validate_cpu_value(value['value'],spec);protocol.validate_waited_value(value['proof'],spec)
  root=Path(item['payload']);sys.path[:0]=[str(root/'source'),str(root)]
  for name in ('native88C_to_flat_migration_v1','native106_fudan20s_pins_v1'):sys.modules.pop(name,None)
  import native88C_to_flat_migration_v1 as migration
  go=dict(protocol.flat_go_fields(spec),source_SHA=spec['source_SHA'],max_parent_seconds=3900,exit_headroom_seconds=300)
  migration.assert_declared_admission('h1',item['task'],go)
  for field in ('source_SHA','native_reference_SHA','source_qualification_kind','source_CPU_SHA','CPU_waited_proof_SHA','worker_SHA','payload_manifest_SHA','source_contract_SHA','job_root','logical_slot','native_seed','GPU_UUID'):
   bad=copy.deepcopy(spec);bad[field]=None
   try:protocol.validate_spec(bad)
   except (ValueError,TypeError,KeyError):negative.append([key,field])
   else:raise AssertionError(('bad spec admitted',key,field))
  for field in ('episode_seconds','episode_ticks','request_end_exclusive','clock_contract'):
   bad=copy.deepcopy(spec);bad['fudan_step_task'][field]=None
   try:protocol.validate_spec(bad)
   except (ValueError,TypeError,KeyError):negative.append([key,'fudan_step_task.'+field])
   else:raise AssertionError(('wrong20s field admitted',field))
  checked.append(key)
 # New bound readers, all unused. Fix the known old observer schema before use.
 oldfirst=L/'TWO104_FUDAN270_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'
 oldclose=L/'TWO104_FUDAN270_CLOSING_INITIAL_CPU_SCHEMA_REPAIRED_SOURCE_V3'
 files=[oldfirst/'observe_TWO103_fudan270_first_NEW_native_policy_UNUSED_once.py',*[p for p in oldclose.glob('*.py')]]
 for p in files:
  s=p.read_text('utf8').replace(A.name,B.name).replace(oldfirst.name,Q.name).replace(oldclose.name,Q.name)
  s=s.replace('TWO104_ACTUAL','TWO106_ACTUAL').replace("MOD4_H1_FUDAN270_SHARED4090_RESOURCE_V104_20261029","MOD4_H1_FUDAN270_EPISODE20_RESOURCE_V106_20261029")
  s=s.replace('TWO104_ALL_FIRST_NATIVE_UPDATES_SCHEMA_REPAIRED_RETURNED_ACTUAL.json','TWO106_ALL_FIRST_POLICY_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json')
  s=s.replace('mod4.native103_to_fudan270.target103.objective_window.v1','mod4.native104_to_fudan270.target106.episode20.v1').replace('mod4.native101_to_fudan270.target103.objective_window.v1','mod4.native104_to_fudan270.target106.episode20.v1')
  if p.name.startswith('observe_'):s=s.replace('[200,500]','[200,2000]')
  if p.name.startswith('review_NEW'):
   s=s.replace("N=T/'MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028';B=N/'payloads_v4/","N=T/'MOD4_H1_FUDAN270_EPISODE20_RESOURCE_V106_20261029';B=N/'payloads/")
   s=s.replace("'continue_qualified101_fudan270'","'continue_qualified104_fudan270_clock_aligned20s'")
  s=s.replace('TWO103','TWO106').replace('NATIVE103','NATIVE106').replace('NEW103','NEW106').replace('closed103','closed106')
  ast.parse(s)
  for node in ast.parse(s).body:
   if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CODE','OWNER','NATIVE') for t in node.targets):ast.parse(ast.literal_eval(node.value))
  write(Q/p.name.replace('TWO103','TWO106').replace('NEW103','NEW106'),s)
 put(B/'reports/TWO106_GENERATED_GO_CLOSURE_AND_NEGATIVE_SPEC_CPU_ACTUAL.json',dict(passed_source_CPU_only=True,epoch=time.time(),actual_CPU_roles=checked,negative_cases=negative,original_owner_account_common_forward_bytes_exact=True,model_or_CPU_reruns=0,request_seconds=[2,20],physics_seconds_per_control=.01,actual_GPU_GO_pending=True))
 write(Q/'HANDOFF.md','New106 coherent20s task. These reader entries are frozen and unused. Direct exact entry only after fresh local exact CIM/global serial lease. First observer binds NEW106 owner; collector still normal900 owner850/node180/total1140, no time-only completion. Both NEW formals initialCPU once each with ONE shared frozen86 witness, input104 PT0. Read actual reports before old once.\n')
 for root,name in [(B,'FROZEN_UNUSED_TWO106_ORIGINAL_WRITER_INDEX_V1.json'),(Q,'FROZEN_UNUSED_TWO106_FIRST_CLOSING_CPU_INDEX_V1.json')]:put(root/name,dict(frozen=True,unused=True,files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(root.rglob('*')) if p.is_file()]))
 print(json.dumps(dict(controller_source_ready=True,actual_CPU_bound_roles=checked,negative_cases=len(negative),first_and_closing_readers_unused=True,GO=False)))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('PREPARE106_CONTROLLER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_GO_or_remote=True));raise
