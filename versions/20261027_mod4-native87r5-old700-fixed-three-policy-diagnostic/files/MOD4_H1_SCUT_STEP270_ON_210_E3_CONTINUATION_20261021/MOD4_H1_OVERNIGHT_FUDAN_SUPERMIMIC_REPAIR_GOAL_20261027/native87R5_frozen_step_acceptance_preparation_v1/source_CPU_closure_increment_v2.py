"""Only new source/metadata additions after consumed28-check report; no replay."""
from pathlib import Path
import ast,copy,hashlib,io,json,sys,traceback
from types import SimpleNamespace as S
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));out=HERE/'SOURCE_CPU_CLOSURE_INCREMENT_V2_ACTUAL.json';assert not out.exists()
checks=[]
def ok(name,v=True):assert v,name;checks.append(name)
def refuse(name,f):
 try:f()
 except (ValueError,AssertionError,KeyError):ok(name);return
 raise AssertionError('negative accepted '+name)
try:
 import torch
 import native87R5_frozen_acceptance_driver_v1 as d
 from native87R5_frozen_acceptance_contract_v1 import SEEDS,GPU_BACKENDS
 from aggregate_native87R5_frozen_three_seed_CPU_unused_once import summarize
 from prepare_native87R5_closed_frozen_selection_unused_once import bind_new_eval
 # Existing SDK ingress view helper only, no actual scene or model import.
 N=HERE.parents[1]/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';sys.path.insert(0,str(N/'payloads_r5/h1/source'))
 from actual_DR_memory_getter_v1 import tensor
 class Proxy:
  def __init__(self,t):self.torch=t
 names=['body'+str(i) for i in range(31)];contact_names=names[::-1]
 fields=dict(root_state_w=torch.zeros(1,13),joint_pos=torch.zeros(1,30),joint_vel=torch.zeros(1,30),applied_torque=torch.zeros(1,30),body_pos_w=torch.zeros(1,31,3),body_quat_w=torch.zeros(1,31,4))
 rawforce=torch.arange(93.).reshape(1,31,3)
 phase=S(age_control=torch.tensor([100]),request_for_action=torch.tensor([True]),takeoff_count=torch.tensor([1]),landing_count=torch.tensor([1]),recovery_count=torch.tensor([0]),crossed=torch.ones(1,2,dtype=torch.bool),goal=S(success=torch.tensor([False]),stable_ticks=torch.tensor([12])),last_measured=dict(step_platform_contact=torch.ones(1,2,dtype=torch.bool),step_footprint_inside=torch.ones(1,2,dtype=torch.bool)))
 env=S(scene={'robot':S(data=S(**{k:Proxy(v) for k,v in fields.items()}),body_names=names)},h1_phase=phase,h1_contact_names=contact_names,h1_sensor=S(contact_view=S(get_net_contact_forces=lambda **kw:Proxy(rawforce))),physics_dt=.0025,_integrated_contact=S(history=torch.zeros(1,3,2,3)),action_manager=S(action=torch.zeros(1,6)),_sensor_mild=S(episode=torch.tensor([1])),_physics_action_delay=S(queue=S(groups={'legs':dict(applied=torch.ones(1,4)),'wheels':dict(applied=2*torch.ones(1,2))})))
 frames=d.ActualFrames(env,io.StringIO(),tensor,dict(available=False));state=frames.state()
 ok('real_frame_reader_SDK_proxy_view_and31body_contact_named_reorder',torch.equal(state['body_contact_force31'],rawforce[0].flip(0)))
 ok('original_cached_footprints_platform_contact_preserved',set(state['actual_original_success_caches'])=={'step_platform_contact','step_footprint_inside'})
 ok('perphysics_processed_applied6_queue_not_action_manager',torch.equal(state['physical_applied_processed6'],torch.tensor([1.,1.,1.,1.,2.,2.])))
 text=(HERE/'native87R5_frozen_acceptance_driver_v1.py').read_text('utf8')
 ok('control_stores_already_available_packed127_xi31_no_new_read',"packed127_for_action=s[0],xi31_for_action=xi[0]" in text)
 plan=dict(passed=True,purpose='MOD4_native87R5_formal_frozen_3seed_step_acceptance',source_run_id='AVAILABLE_TWO_H1_OWN_FUDAN_NATIVE87R5_fixture',selection=dict(selected_key='h1',selection_scope='fixed_h1_diagnostic_no_valid_recovery_landing_cross_evidence'),source_model=dict(SHA='a'*64),source_qualification=dict(formal_FINAL_passed=True,initial_whole_CPU_passed=True,original_fee_allout_passed=True),evidence_pins=dict(cpu=dict(SHA='b'*64)),GPU_original_locks=dict(h1=['lease'],recovery=['private','shared']))
 q=bind_new_eval(plan,eval_root='/new/eval',runtime_root='/new/eval/runtime',model_eval_relative='formal_native.pt',GPU_UUID=next(k for k,v in GPU_BACKENDS.items() if v=='target72'),eval_code_pins={},evidence_eval_relatives=dict(cpu='evidence/cpu.json'))
 ok('pure_binding_fixed3seeds_newN1_no_model_or_runtime_copy',q['seeds']==list(SEEDS) and q['selected_GPU_original_locks']==['private','shared'])
 cases={}
 for seed in SEEDS:
  status=dict(seed=seed,source_identity=dict(model=q['source_model']),policy_parameters_and_saved_normalizers_literal_unchanged=True,termination='actual_original_done',controls=100,physics_callbacks=400,last_original_state=dict(success=False,takeoff_count=1,landing_count=0,recovery_count=0,stable_callback_ticks=0,actual_original_success_caches={}),last_termination_terms=dict(exact_terms_available=True,values=dict(closure=True)))
  cases[seed]=dict(status=status,authority=dict(passed=True,no_account_write=True,no_canonical_copy=True,canonical_unchanged=True,canonical_SHA='c'*64),function_return=dict(passed=True),close_or_original_errors=[])
 result=summarize(q,cases);ok('three_failed_goals_remain_zero_success_no_cherrypick',result['case_count']==3 and result['original_goal_success_count']==0)
 missing=copy.deepcopy(cases);missing.pop(SEEDS[1]);refuse('missing_fixed_case_cannot_qualify',lambda:summarize(q,missing))
 bad=copy.deepcopy(cases);bad[SEEDS[0]]['close_or_original_errors']=['primary'];refuse('primary_error_even_rc0_cannot_qualify',lambda:summarize(q,bad))
 q210=bind_new_eval(plan,eval_root='/new/eval',runtime_root='/new/eval/runtime',model_eval_relative='formal_native.pt',GPU_UUID=next(k for k,v in GPU_BACKENDS.items() if v=='source210'),eval_code_pins={},evidence_eval_relatives=dict(cpu='evidence/cpu.json'),external72_readonly_guard=dict(eval_relative='ready.json',SHA='d'*64))
 cases210=copy.deepcopy(cases)
 for row in cases210.values():row['authority']['canonical_unchanged']=False
 refuse('source210_ready_alone_never_qualifies_without72_waited_EXIT',lambda:summarize(q210,cases210))
 readyexit=dict(passed=True,canonical_bytes_unchanged=True,root_waited_release_received=True,no_account_write_or_copy=True,canonical_SHA='c'*64)
 ok('source210_exit_proof_explicitly_required',summarize(q210,cases210,readyexit)['passed'])
 for p in HERE.glob('*.py'):ast.parse(p.read_bytes())
 ok('final_all_Python_AST_and_no_CUDA',not torch.cuda.is_initialized())
 result=dict(passed=True,checks=len(checks),check_names=checks,fixture_only=True,actual_SDK_scene_model_policy_forward_or_physics=False,real_model_open_hash=False,actual3seed_acceptance_not_executed=True)
 with out.open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
 print(json.dumps(dict(passed=True,checks=len(checks),fixture_only=True)))
except BaseException:
 with (HERE/'SOURCE_CPU_CLOSURE_V2_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(passed=False,error=traceback.format_exc(),checks=checks),f,indent=2)
 raise
