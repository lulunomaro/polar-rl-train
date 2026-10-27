"""New source-only patch generation and bounded semantic/API metadata fixture.

Does not run old fixtures, a real SDK, USD, model, actor or physical simulation.
"""
from pathlib import Path
from types import SimpleNamespace as S
import ast,copy,hashlib,json,sys,traceback
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));L=HERE.parents[1];T=L.parent;N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';B=N/'payloads_r5/h1'
from gas400_source_patcher_v1 import prepare,SPECS,RT,REPLACEMENTS,GAS,QHI,SHA,contract_overlay,patch_python,replace_json_scalars,usda_override
from gas400_migration_contract_v1 import declare_transfer,validate_new_publication
from gas400_sdk_admission_candidate_v1 import check_actual_new_gas
def put(name,value):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
checks=[]
def ok(name,v=True):assert v,name;checks.append(name)
def refuse(name,f):
 try:f()
 except (ValueError,AssertionError,KeyError):ok(name);return
 raise AssertionError('negative accepted '+name)
def diff(a,b,path=()):
 if type(a) is not type(b):return [(path,a,b)]
 if isinstance(a,ast.AST):
  return [v for key in a._fields for v in diff(getattr(a,key),getattr(b,key),path+(key,))]
 if isinstance(a,dict):
  assert set(a)==set(b);return [v for key in a for v in diff(a[key],b[key],path+(key,))]
 if isinstance(a,(list,tuple)):
  assert len(a)==len(b);return [v for i,(x,y) in enumerate(zip(a,b)) for v in diff(x,y,path+(i,))]
 return [] if a==b else [(path,a,b)]
put('ENTRY_CONSUMED_SOURCE_ONLY_ACTUAL.json',dict(purpose='nominal400 source-only exact gas migration patch/SDK admission candidate',no_payload_Task_GO_SDK_model_or_GPU=True))
try:
 destination=HERE/'isolated_text_overlay_NOT_A_PAYLOAD';result=prepare(B,destination)
 ok('exact7_text_replacements_no_original_mutation',set(r['relative'] for r in result['replacements'])==REPLACEMENTS)
 changes={}
 for name in SPECS:
  old=(B/(RT+name)).read_bytes();new=(destination/(RT+name)).read_bytes();changes[name]=diff(ast.parse(old),ast.parse(new))
 expected={'spring_pressure_index_runtime.py':[(3500.,2000.),(3500.,2000.)],'spring_pressure_audit_runtime.py':[(3500,2000)],'spring_nominal_sdk_readback.py':[(3500,2000)],'spring_pressure_training_env.py':[(3500,2000),(3150,1800),(3850,2200)]}
 for name,rows in changes.items():
  numeric=[(a,b) for p,a,b in rows if type(a) in (int,float)];text=[(a,b) for p,a,b in rows if isinstance(a,str)]
  ok(name+'_only_reviewed_nominal_AST_constants_change',numeric==expected[name] and len(rows)==len(numeric)+len(text) and (len(text)==1 if name=='spring_pressure_index_runtime.py' else not text))
 for relative in ('job0/assets/import_contract.json',RT+'import_contract.json'):
  old=json.loads((B/relative).read_bytes());new=json.loads((destination/relative).read_bytes());d=diff(old,new)
  ok(relative+'_only4_gas_scalar_semantics',set(p for p,a,b in d)=={('gas_springs',n,'stiffness_n_m') for n in GAS}|{('joints',n,'limits_si',1) for n in GAS})
 oldfreeze=json.loads((B/'job0/runtime/reports/SOURCE_FREEZE.json').read_bytes());newfreeze=json.loads((destination/'job0/runtime/reports/SOURCE_FREEZE.json').read_bytes())
 fd=diff(oldfreeze,newfreeze);ok('SOURCE_FREEZE_exact5_current_source_rows_rebound_only',set(p for p,a,b in fd)=={('sha256','isaac/mod4/'+n) for n in [*SPECS,'import_contract.json']})
 for row in result['replacements']:ok('original_source_byteexact_'+row['relative'],SHA((B/row['relative']).read_bytes())==row['old_SHA'])
 reference=B/'source/MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json'
 ok('reference9223_unchanged_not_retargeted',SHA(reference.read_bytes())=='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3')
 layer=usda_override().decode('utf8');ok('tiny_layer_only4_reviewed_attribute_opinions',layer.count('float drive:linear:physics:stiffness = 2000')==2 and layer.count('float physics:upperLimit = '+repr(QHI))==2 and layer.count('over "left_gas_slide"')==layer.count('over "right_gas_slide"')==1)
 refuse('asset_dependency_path_injection_refused',lambda:usda_override('../../old/robot.usd'))
 refuse('unapproved_Python_version_refused',lambda:patch_python('spring_pressure_index_runtime.py',(B/(RT+'spring_pressure_index_runtime.py')).read_bytes()+b'\n'))
 refuse('duplicate_contract_JSON_keys_refused',lambda:replace_json_scalars(b'{"a":1,"a":2}',{('a',):(2,3)}))
 transfer=declare_transfer(dict(qualified_formal_R5_native=True,initial_whole_CPU_passed=True,role='h1',source_kind='R5_native127_obs86_static31_aux54',SHA='a'*64,native_iteration=100,world_updates=1000,policy_updates=100),adaptation_controls=64,adaptation_world_updates=10)
 adaptation=dict(actual_new_plant_backend_readback=True,original_preload_target_active_before_first_newPi=True,complete_fresh_controls=64,new_world_updates=10,zero_new_policy_updates_during_world_only_adaptation=True)
 publication=dict(world_updates=1010,policy_updates=101,native_iteration=101,same_new_preupdate_SHA_and_bytes_and_before_control=True,source_SHA='a'*64)
 ok('changed_plant_preserves_global_counts_but_requires_new_deltas',validate_new_publication(transfer,publication,adaptation)['new_policy_delta']==1)
 stale=dict(publication,policy_updates=100);refuse('old_positivePi_cannot_be_new_window_proof',lambda:validate_new_publication(transfer,stale,adaptation))
 short=dict(adaptation,complete_fresh_controls=0);refuse('oldglobal_iteration_does_not_skip_new_plant_adaptation',lambda:validate_new_publication(transfer,publication,short))
 # Duck-typed source/API metadata fixture only. No model is created or forwarded.
 import torch
 class Proxy:
  def __init__(self,value):self.torch=value
 def tensor(value):
  if torch.is_tensor(value):return value
  if hasattr(value,'torch') and torch.is_tensor(value.torch):return value.torch
  raise ValueError('existing readonly Tensor/Proxy required')
 names=['joint'+str(i) for i in range(28)]+list(GAS);ids=[28,29];n=3;nominal=torch.tensor([2000.,2000.]);factor=torch.tensor([[.9,1.1],[1.,1.],[1.05,.95]])
 k=torch.zeros(n,30);k[:,ids]=factor*nominal;d=torch.zeros(n,30);d[:,ids]=3.
 limits=torch.zeros(n,30,2);limits[:,ids]=torch.tensor([-.0267046843609,QHI]);pos_target=torch.zeros(n,30)
 data=S(joint_stiffness=Proxy(k),joint_damping=Proxy(d),joint_pos_limits=Proxy(limits),joint_pos_target=Proxy(pos_target),joint_vel_target=Proxy(torch.zeros(n,30)))
 view=S(get_dof_stiffnesses=lambda:Proxy(k),get_dof_dampings=lambda:Proxy(d),get_dof_limits=lambda:Proxy(limits),get_dof_max_forces=lambda:Proxy(torch.full((n,30),2000.)),get_dof_armatures=lambda:Proxy(torch.full((n,30),.002)))
 robot=S(joint_names=names,data=data,root_view=view,actuators={'gas_springs':S(stiffness=Proxy(k[:,ids]),damping=Proxy(d[:,ids]))})
 env=S(scene={'robot':robot},num_envs=n,physics_dt=.0025,step_dt=.01,_spring_pressure=S(ids=ids,names=list(GAS),nominal=nominal,component=S(actual_stiffness=lambda x:factor*x)),_gas_damping=S(component=S(actual_damping_Ns_per_m=lambda:torch.full((n,2),3.))),cfg=S(decimation=4,events=S(gas_spring_preload=S(params=dict(joint_names=list(GAS),targets=[.22063944109012937,.2206394410901294]))),scene=S(robot=S(spawn=S(articulation_props=S(solver_position_iteration_count=32,solver_velocity_iteration_count=4)))),sim=S(physics=S(solver_type=1))))
 initial=check_actual_new_gas(env,expected_joint_names=names,tensor=tensor)
 ok('initial_zero_preload_reported_pending_not_faked_active',initial['actual_new_gas_parameters_passed'] and not initial['actual_original_preload_active'])
 refuse('first_newPi_requires_original_step_preload_active',lambda:check_actual_new_gas(env,expected_joint_names=names,tensor=tensor,require_active_preload=True))
 pos_target[:,ids]=torch.tensor([.22063944109012937,.2206394410901294])
 ok('readonly_proxy_getters_new_k_limits_preload_source_fixture',check_actual_new_gas(env,expected_joint_names=names,tensor=tensor,require_active_preload=True)['actual_original_preload_active'])
 old=limits.clone();limits[:,ids,1]=.0352033350025
 refuse('old214mm_upper_limit_source_fixture_refused',lambda:check_actual_new_gas(env,expected_joint_names=names,tensor=tensor));limits.copy_(old)
 env._spring_pressure.nominal=torch.tensor([3500.,3500.]);refuse('old3500_nominal_source_fixture_refused',lambda:check_actual_new_gas(env,expected_joint_names=names,tensor=tensor));env._spring_pressure.nominal=nominal
 sourcefiles=[B/relative for relative in REPLACEMENTS]+[B/(RT+n) for n in ('mod4_task.py','skills_isaac.py','spring_pressure_component.py','gas_damping_factor.py','gas_damping_sdk_adapter.py','action_delay_physics_queue.py','spring_pressure_checkpoint.py','gas_damping_checkpoint.py','chassis_pd_checkpoint.py','h1_fullstate_checkpoint_v1.py')]+[B/'source/compact_episode_static31_v1.py',reference]
 put('SOURCE_INPUT_SHA_LINEAGE_ACTUAL.json',dict(source_files=[dict(path=str(p),bytes=p.stat().st_size,SHA=SHA(p.read_bytes())) for p in sorted(sourcefiles)],no_USD_PT_raw_model_read_stat_copy_or_hash=True))
 put('SOURCE_CPU_SEMANTIC_DIFF_AND_ADMISSION_FIXTURE_ACTUAL.json',dict(passed=True,checks=len(checks),check_names=checks,Python_AST_differences={name:[dict(path=list(path),old=a,new=b) for path,a,b in rows] for name,rows in changes.items()},sourcefreeze_changed_paths=[list(p) for p,a,b in fd],fixture_only=True,actual_USD_composition_or_SDK_scene_or_GPU_passed=False,real_models_read=False,old_fullsave_PPO_source_core_physics_reward_command_not_patched=True,typed_changed_plant_WM_adaptation_still_integration_pending=True))
 print(json.dumps(dict(prepared=True,checks=len(checks),replacements=len(REPLACEMENTS),fixture_only=True,actual_USD_SDK_PENDING=True)))
except BaseException:
 put('ORIGINAL_GAS400_SOURCE_PREPARATION_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),completed_checks=checks,partial_overlay_retained=True,no_original_mutation=True));raise
