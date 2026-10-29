"""Two genuine native roles; original owner/common/forward bytes preserved, no GO."""
from pathlib import Path
import ast,copy,hashlib,json,shutil,time,sys,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
A=L/'TWO114_WM_HEADING_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1';OLDQ=L/'TWO114_WM_HEADING_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'
B=L/'TWO116_DIRECT_COMMAND_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1';Q=L/'TWO116_DIRECT_COMMAND_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:f.write(s)
def rep(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def assign(s,k,v):
 node=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==k for t in x.targets));lines=s.splitlines(keepends=True)
 return ''.join(lines[:node.lineno-1])+k+'='+repr(v)+'\n'+''.join(lines[node.end_lineno:])
def module(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sys.modules[n]=m;sp.loader.exec_module(m);return m
def main():
 assert not B.exists() and not Q.exists();(B/'reports').mkdir(parents=True);(Q/'reports').mkdir(parents=True)
 specs={};values={}
 for seed in (27,28):
  mode='seed'+str(seed);sf='NEW116_ONE_TYPED_REWARD_PAYLOAD_PREPARED_SOURCE_ONLY.json' if seed==27 else 'NEW116_SEED28_TYPED_REWARD_PAYLOAD_PREPARED_SOURCE_ONLY.json'
  rf='NEW116_ACTUAL_SOURCE_SDK_FULLSTATE_REWARD_CPU_RETURNED_ACTUAL.json' if seed==27 else 'NEW116_SEED28_ACTUAL_SOURCE_SDK_FULLSTATE_REWARD_CPU_RETURNED_ACTUAL.json'
  item=read(R/sf);value=read(R/rf);assert value['passed'] and value['actual_CPU_waited_EXIT0'] and value['proof']['actual_waited'] and not value['errors']
  item.update(logical_slot=item['task']['logical_slot'],source_kind=item['task']['source_qualification_kind']);specs[mode]=item;values[mode]=value
 original=read(A/'reports/TWO114_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json');public=copy.deepcopy(original)
 public.update(run_id='TWO116_DIRECT_COMMAND_WHEEL_HEIGHT_'+str(time.time_ns()),owner_source=str(B/'owner'),owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_TWO116_DIRECT_COMMAND_2610v116/owner',expected_closed_remaining=values['seed27']['resource']['remaining_snapshot'])
 for mode,item in specs.items():
  k=item['logical_slot'];s=public['experts'][k];task=item['task'];v=values[mode];job=item['job_root']
  for f in ('source_SHA','source_progress','source_native_iteration','native_seed','native_reference_SHA','source_qualification_kind','input_start_mode','fudan_step_task','task_focused_real_replay','imagination_terminal_exposure','native_learning_seed','goal_conditioning','own_step_objective_qualification_SHA'):s[f]=copy.deepcopy(task[f])
  s.update(run_id=public['run_id'],job_root=job,CPU_path=job+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json',CPU_proof_path=job+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json',source_CPU_SHA=v['proof']['report_SHA'],CPU_waited_proof_SHA=v['proof_SHA'],payload_manifest_SHA=item['manifest_SHA'],source_contract_SHA=item['source_contract_SHA'],payload_manifest_path=job+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json',source_contract_path=job+'/FLAT90_SOURCE_CONTRACT_ACTUAL.json',worker_SHA=H(Path(item['payload'])/'h1_native_flat90_worker_v1.py'))
  public['node_sources'][k]=str(B/('node_'+k));public['node_roots'][k]='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_TWO116_DIRECT_COMMAND_2610v116/node_'+k
 for role in ('owner','node_h1','node_h1_seed28'):
  for p in (A/role).glob('*.py'):
   dest=B/role/p.name;dest.parent.mkdir(exist_ok=True)
   if p.name not in ('h1_next72_protocol_actual95_v2.py','h1_seed28_next72_protocol_v100.py'):shutil.copy2(p,dest);continue
   k='h1' if p.name.startswith('h1_next') else 'h1_seed28';old=original['experts'][k];new=public['experts'][k];s=p.read_text(encoding='utf8')
   for name,v in [('JOB',new['job_root']),('SOURCE',new['source_SHA']),('REFERENCE',new['native_reference_SHA']),('PROGRESS',new['source_progress']),('KIND',new['source_qualification_kind'])]:s=assign(s,name,v)
   for field in ('fudan_step_task','task_focused_real_replay','imagination_terminal_exposure'):s=rep(s,repr(old[field]),repr(new[field]))
   s=rep(s,repr(old['input_start_mode']),repr(new['input_start_mode']))
   needle=" require(v.get('fudan_step_task')==s['fudan_step_task']"
   s=rep(s,needle," require(v.get('reward116_actual_installed_readback',{}).get('passed') is True and v['reward116_actual_installed_readback']['actual_own_bank_poses']==133 and v['reward116_actual_installed_readback']['stationary_height_bonus_exact_zero'] and v['reward116_actual_installed_readback']['actual_selected_sum_literal'],'actual installed direct wheel-height116 reward readback')\n"+needle)
   ast.parse(s);write(dest,s)
 for k,spec in public['experts'].items():
  folder=B/('node_'+k);put(folder/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json',dict(key=k,source_SHA=spec['source_SHA'],worker_SHA=spec['worker_SHA'],source_CPU_SHA=spec['source_CPU_SHA'],files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(folder.iterdir()) if p.is_file()]));spec['manifest_SHA']=H(folder/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json')
 public['task_templates']=copy.deepcopy(public['experts']);put(B/'reports/TWO116_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json',public)
 activation=(A/'activate_TWO114_fudan270_WM_heading_original_single_writer_UNUSED_once.py').read_text(encoding='utf8').replace('TWO114','TWO116');ast.parse(activation);write(B/'activate_TWO116_direct_command_original_single_writer_UNUSED_once.py',activation)
 for n in ('two95_finite_owner_authority72_v1.py','three_slot_common_v1.py','forwarded_original_owner_control_v1.py','single_writer72_authority_V85M_source.py'):assert (B/'owner'/n).read_bytes()==(A/'owner'/n).read_bytes()
 checked=[];negative=[]
 for mode,item in specs.items():
  k=item['logical_slot'];spec=public['experts'][k];name='h1_next72_protocol_actual95_v2.py' if k=='h1' else 'h1_seed28_next72_protocol_v100.py';p=module('new114_'+k,B/'owner'/name)
  p.validate_spec(spec);p.validate_cpu_value(values[mode]['value'],spec);p.validate_waited_value(values[mode]['proof'],spec)
  sys.path[:0]=[str(Path(item['payload'])/'source'),item['payload']]
  for n in ('native88C_to_flat_migration_v1','native116_command_reward_pins_v1'):sys.modules.pop(n,None)
  import native88C_to_flat_migration_v1 as migration
  go=dict(p.flat_go_fields(spec),source_SHA=spec['source_SHA'],max_parent_seconds=3900,exit_headroom_seconds=300);migration.assert_declared_admission('h1',item['task'],go)
  for f in ('source_SHA','native_reference_SHA','source_qualification_kind','source_CPU_SHA','CPU_waited_proof_SHA','worker_SHA','payload_manifest_SHA','source_contract_SHA','job_root','logical_slot','native_seed','GPU_UUID'):
   bad=copy.deepcopy(spec);bad[f]=None
   try:p.validate_spec(bad)
   except (ValueError,TypeError,KeyError):negative.append([k,f])
   else:raise AssertionError('bad114spec '+f)
  for f in ('candidate_WM_source_SHA','source_CPU_report_SHA','changed_input_columns','raw_cue_scale'):
   bad=copy.deepcopy(spec);bad['fudan_step_task']['world_model_input_heading'][f]=None
   try:p.validate_spec(bad)
   except (ValueError,TypeError,KeyError):negative.append([k,'WM.'+f])
   else:raise AssertionError('bad114WMcue '+f)
  for field in ('target_each_wheel_bottom_m','reward_API_SHA','command_core_SHA','source_CPU_SHA','quiet_speed_sigma_m_s','max_step_reward'):
   bad=copy.deepcopy(spec);bad['fudan_step_task']['command_reward116'][field]=None
   try:p.validate_spec(bad)
   except (ValueError,TypeError,KeyError):negative.append([k,'command116.'+field])
   else:raise AssertionError('bad116command '+field)
  checked.append(k)
 for p in OLDQ.glob('*.py'):
  s=p.read_text(encoding='utf8').replace(A.name,B.name).replace(OLDQ.name,Q.name).replace('MOD4_H1_FUDAN270_WM_WORLD_HEADING_RESOURCE_V114_20261029',N.name)
  s=s.replace('TWO114','TWO116').replace('NATIVE114','NATIVE116').replace('NEW114','NEW116').replace('closed114','closed116').replace('input_native111','input_native114').replace('continue_qualified111_fixed_world_WM_heading114','continue_qualified114_direct_world_command_both_wheel_height116').replace('mod4.native111_to_fudan270.target114.WM_heading.v1','mod4.native114_to_fudan270.target116.direct_command_wheel_height.v1')
  if p.name.startswith('observe_'):
   node=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NATIVE' for t in x.targets));code=ast.literal_eval(node.value)
   needle="  wm114=read(out/'WM114_ACTUAL_GPU_LOADED_NORM_AND_INPUT_READBACK_BEFORE_CONTROL.json')"
   insertion="  reward116=read(out/'REWARD116_ACTUAL_GPU_RESET_POSE_AND_SELECTED_TERMS_BEFORE_CONTROL.json');assert reward116['passed'] and reward116['actual_phase_or_physics_not_mutated']\n  assert positive['producer']['command_reward116']==spec['fudan_step_task']['command_reward116'] and positive['producer']['reward_source_SHA']==spec['fudan_step_task']['command_reward116']['reward_API_SHA']\n"
   code=rep(code,needle,insertion+needle)
   s=assign(s,'NATIVE',code)
  ast.parse(s)
  for x in ast.parse(s).body:
   if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CODE','OWNER','NATIVE') for t in x.targets):ast.parse(ast.literal_eval(x.value))
  write(Q/p.name.replace('TWO114','TWO116').replace('NEW114','NEW116'),s)
 put(B/'reports/TWO116_GENERATED_GO_CLOSURE_AND_NEGATIVE_SPEC_CPU_ACTUAL.json',dict(passed_source_CPU_only=True,epoch=time.time(),actual_CPU_roles=checked,negative_cases=negative,original_owner_account_common_forward_bytes_exact=True,models_read=0,GO=False,first_reader_N87_full_precontrol_and_newWM_readback_bound=True))
 for root,name in ((B,'FROZEN_UNUSED_TWO116_ORIGINAL_WRITER_INDEX_V1.json'),(Q,'FROZEN_UNUSED_TWO116_FIRST_CLOSING_CPU_INDEX_V1.json')):put(root/name,dict(frozen=True,unused=True,files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(root.rglob('*')) if p.is_file()]))
 put(R/'TWO116_ACTUAL_TWO_CPU_BOUND_SOURCE_AND_ALL_READERS_FROZEN_ACTUAL.json',dict(passed=True,epoch=time.time(),controller=str(B),readers=str(Q),run_id=public['run_id'],roles=checked,negative_cases=len(negative),no_GO_yet=True))
 print(json.dumps(dict(controller_source_ready=True,actual_CPU_roles=checked,negative_cases=len(negative),GO=False)))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('PREPARE116_CONTROLLER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),traceback=traceback.format_exc(),no_GO_or_remote=True));raise
