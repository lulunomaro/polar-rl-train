"""Local source-contract checks only; actual target SDK and admission still required."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026';Q=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
try:
 q=read(R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');assert q['normal_H1_E2_E3_no_method_scope'] and q['source_production_windows']=={'h1':'82Q','recovery':'82Q','e2':'80'}
 checked={};rejected=[]
 for key,spec in q['specs'].items():
  B=Path(q['payloads'][key]);role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
  for path in B.glob('*.py'):ast.parse(path.read_bytes(),filename=str(path))
  metadata=B/'same_optimized_source_contract_metadata_candidate_v1.py';assert metadata.stat().st_size==2536 and H(metadata)=='c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e'
  ns={};exec(compile(metadata.read_bytes(),str(metadata),'exec'),ns)
  proof=read(B/'CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json');prior=read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json');current=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  auth=read(B/'NORMAL_THREE_83B_PRODUCTION_SOURCE_AUTH_ACTUAL.json');roletree=ast.parse((B/role).read_bytes())
  authasserts=[x for x in ast.walk(roletree) if isinstance(x,ast.Assert) and any(isinstance(y,ast.Name) and y.id=='auth' for y in ast.walk(x))]
  assert authasserts
  for stmt in authasserts:
   if any(isinstance(x,ast.Name) and x.id=='closure' for x in ast.walk(stmt)):continue
   exec(compile(ast.Module(body=[stmt],type_ignores=[]),'actual_auth_assert','exec'),dict(auth=auth,spec=spec,B=B,role=role,H=H))
  v=ns['validate_closed69_metadata'](proof,key,prior['source_Adamstep']);assert (v['source_SHA'],v['source_Adam'])==(spec['source_SHA'],spec['source_Adamstep'])
  ns['validate_same_optimized_protected_inventory'](prior,current)
  tree=ast.parse((B/role).read_bytes());f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='strict_same_V8_root_inventory');scope={};exec(compile(ast.Module(body=[f],type_ignores=[]),'inventory','exec'),scope)
  before={r['relative']:r for r in prior['files']};after={r['relative']:r for r in current['files']};scope['strict_same_V8_root_inventory'](before,after,role,key)
  changed=[rel for rel,row in before.items() if rel.endswith('.py') and (rel not in after or after[rel]['SHA']!=row['SHA'])];assert set(changed)==({role,'recovery_worker.py'} if key=='recovery' else {role})
  original=(P if key=='e2' else Q)/'payloads'/key
  for rel,row in after.items():
   if rel.endswith('.py') and rel not in changed:assert H(B/rel)==H(original/rel)==row['SHA'],(key,rel)
  assert not spec.get('finite_method_test') and not spec.get('h1_step270_method_test') and spec['policy_hz']==(100 if key=='h1' else 50)
  if key=='recovery':
   f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='exact_recovery_step');scope={'ast':ast};exec(compile(ast.Module(body=[f],type_ignores=[]),'saved_adam','exec'),scope);scope['exact_recovery_step']((original/'recovery_worker.py').read_text('utf8'),(B/'recovery_worker.py').read_text('utf8'),prior['source_Adamstep'],spec['source_Adamstep'])
  for label,mutate in [('wrong_source_step',lambda x:x['models'][key].__setitem__('Adam',x['models'][key]['Adam']+1)),('duration_false',lambda x:x['models'][key]['actual_cost'].__setitem__('duration_bound_passed',False)),('active_not_closed',lambda x:x.__setitem__('all_owner_nodes_children_actual_out',False)),('missing_STD',lambda x:x['models'][key]['all17_changed']['actor_state_dict'].remove('distribution.std_param')),('fee_zero',lambda x:x['models'][key]['actual_cost'].__setitem__('charged_seconds',0))]:
   bad=copy.deepcopy(proof);mutate(bad)
   try:ns['validate_closed69_metadata'](bad,key,prior['source_Adamstep'])
   except (AssertionError,KeyError):rejected.append(key+':'+label)
   else:raise AssertionError('negative admitted '+key+':'+label)
  bad=copy.deepcopy(after);bad['unapproved_added.py']={'SHA':'0'*64,'bytes':0}
  try:scope['strict_same_V8_root_inventory'](before,bad,role,key)
  except (AssertionError,KeyError):rejected.append(key+':added_python')
  else:raise AssertionError('added python admitted')
  checked[key]=dict(source_SHA=v['source_SHA'],source_Adam=v['source_Adam'],changed_Python=changed,protected_exact=True,metadata_CRLF_exact=True)
 for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py'):
  assert (N/'controllers'/name).read_bytes()==(P/'controllers'/name).read_bytes(),name
 for path in N.glob('*.py'):ast.parse(path.read_bytes(),filename=str(path))
 closure=read(N/'payloads/e2/CURRENT_DISPLACED_NATIVE_82Q_CLOSURE_ACTUAL.json');assert closure['passed'] and closure['qualification_scope']=='production_h1_recovery_pair_and_separate_native_method_diagnostic' and set(closure['models'])=={'h1','recovery'} and closure['native_method']['present'] is False and closure['native_method']['original_terminal']['original_error']
 assert closure['remaining_actual_snapshot']==606200.6205716133 and q['specs']['e2']['previous_runtime_root'].endswith('three_experts_2610v80/e2') and q['specs']['e2']['displaced_runtime_root'].endswith('mixed_supermimic_2610v82q/e2')
 put('NORMAL83_SOURCE_LINEAGE_NORMAL_CONTROLLERS_AND_NEGATIVE_CPU_ACTUAL.json',dict(epoch=time.time(),passed_source_CPU_only=True,checks=checked,rejections=rejected,original_three_controller_bytes_exact=True,normal_E2_source80_independent_of_failed_native_resource82Q=True,no_model_reload_actorforward_physics_GPU=True,not_actual_installed_SDK_or_GO=True))
 print(json.dumps(dict(sourceCPU=True,rejections=len(rejected),actual_target_admission_still_required=True)))
except BaseException:
 put('NORMAL83_SOURCE_LINEAGE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),not_training_error=True));raise
