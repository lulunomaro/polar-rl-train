"""Future normal close only: one NEW formal native load + one frozen witness."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent;N=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028';R=N/'reports';B=N/'payloads/h1'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def read(p):return json.loads(Path(p).read_bytes())

def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 v=read(R/'THREE93_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL_V1.json')
 assert v['actual_finite_returned'] and v['canonical_None'] and v['original_owner_private_shared_locks_free']
 terminal=v['terminals']['h1'];assert terminal['returncode']==0 and not terminal['original_error'] and not terminal['errors'] and terminal['terminal_all_own_children_waited']
 assert v['formals']['h1']['passed'] and v['published']['h1']['twohost_complete_SHA'] and v['unique_original_segment']['experts']['h1']['duration_bound_passed']
 assert 0<v['original_fee_by_slot']['h1']<=3900 and v['original_fee_by_slot']['h1_210']==51.172107219696045
 assert v['unique_original_segment']['charged_expert_seconds']==v['original_fee_seconds']==sum(v['original_fee_by_slot'].values())
 assert v['failed210_rawrc0_not_success'] and v['terminals']['h1_210']['original_error'] and not v['terminals']['h1_210']['final'] and v['all_three_original_nodes_workers_owner_out']
 pub=v['published']['h1'];model=Path(pub['local_path']);assert model.resolve()==(N/'current_closed93_models/h1/formal/model_final.pt').resolve()
 put('NATIVE93_NEW_FORMAL_INITIAL_CPU_STARTED_ACTUAL.json',dict(epoch=time.time(),purpose='One new formal flat native fullstate initial qualification after original settled close',model=pub,no_native_source91_input_redecode=True,model_loads_planned=dict(NEWformal=1,normal86_frozen_witness=1),optional_diagnostic='Saved normalizer count and five analytic flat-goal normalization ranges during this SAME initial load; no actor or WM forward'))
 import torch
 torch.set_num_threads(2)
 sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps'),str(B/'job0/runtime/isaac/mod4')]
 from native88_source_guard_v1 import finite_tree
 from native88_installed_cpu_helpers_v1 import frozen_bootstrap,validate_native_optimizer,exact
 from native88C_to_flat_migration_v1 import verify_saved_migration,NATIVE_CONTRACT
 before=model.stat();assert before.st_size==pub['bytes']
 with model.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==pub['SHA']
 full=torch.load(model,map_location='cpu',weights_only=False)
 witness=torch.load(B/'job0/source/H1_closed86_policy_only_update138.pt',map_location='cpu',weights_only=False)
 finite_tree(full);finite_tree(witness);publication=full['UniSuperMimic_publication']
 assert full['UniSuperMimic_test_contract']==NATIVE_CONTRACT
 verify_saved_migration(full,publication)
 assert publication['native88_migration_window']==pub['original_producer']['native88_migration_window']
 counters=publication['native88_migration_window']['counters'];native=full['UniSuperMimic_H1_test'];args=native['args']
 assert native['iteration']==publication['native_iteration']==counters['native_iteration'] and native['iteration']>9256
 assert counters['new_world_updates']>=640 and counters['new_policy_updates']>0
 assert publication['world_updates']==92560+counters['new_world_updates'] and publication['policy_updates']==9000+counters['new_policy_updates']
 assert full['UniSuperMimic_obs_history'].shape==(4096,10,86) and full['UniSuperMimic_bridge_ep_step'].shape==(4096,)
 frozen=frozen_bootstrap(full,witness)
 from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel
 from supermimic_wheel_leg_v3.networks import Policy,Critic
 modules={'wm':AugmentedWheelLegWorldModel(context_dim=31,hidden=args['wm_hidden'],num_joints=30,auxiliary_dim=54,action_dim=6),'pi':Policy(86,1460,hist=10,z_dim=32,num_joints=6,hidden=args['policy_hidden']),'critic':Critic(1625,hidden=args['critic_hidden'])}
 summaries={}
 for name,opt,betas in [('wm','opt_wm',(.9,.999)),('pi','opt_pi',(.9,.95)),('critic','opt_v',(.9,.999))]:
  module=modules[name];module.load_state_dict(native[name],strict=True);assert exact(module.state_dict(),native[name])
  summary=validate_native_optimizer(module,native[opt],betas)
  expected=publication['world_updates'] if name=='wm' else publication['policy_updates'] if name=='pi' else 20*publication['policy_updates']
  assert summary['min_step']==summary['max_step']==expected
  summaries[name]=summary
 from spring_pressure_checkpoint import validate_saved_pressure
 from gas_damping_checkpoint import validate_saved_damping
 from chassis_pd_checkpoint import validate_saved_chassis_pd
 validate_saved_pressure(full['spring_pressure_state'],4096);validate_saved_damping(full['gas_damping_state'],4096);validate_saved_chassis_pd(full['chassis_PD_state'],4096)
 assert full['spring_pressure_recipe']['nominal_stiffness_N_m']==2000 and full['physical_action_delay_state']['control_us']==10000
 assert full['H1_step270_task_state']['version']==270 and not torch.cuda.is_initialized()
 norm_counts={name:{k:float(x) for k,x in module.state_dict().items() if k.endswith('.count') and x.numel()==1} for name,module in modules.items()}
 from native_flat_jump_adapter_v1 import OwnFlatJumpReference
 provider=OwnFlatJumpReference(read(B/'source/OWN_FLAT5CM_TASK_REFERENCE_SOURCE.json'),order_scope='source_CPU_fixture')
 frames=torch.tensor([0,200,210,225,300],dtype=torch.long);goals=provider.future_goal(frames,10)
 from flat91_mask_aware_goal_conditioning_v1 import masked_goal_conditioning
 with torch.no_grad():normalized=masked_goal_conditioning(modules['pi'].goal_norm(goals),goals)
 shaped_goals=goals.reshape(5,10,146)
 shaped_norm=normalized.reshape(5,10,146)
 unknown=shaped_goals[...,73:]==0
 critic_norm=modules['critic'].norm
 critic_goal_mean=critic_norm.mean[-1460:]
 critic_goal_std=critic_norm.std()[-1460:]
 critic_raw_normalized=(goals-critic_goal_mean)/critic_goal_std
 critic_goal_normalized=masked_goal_conditioning(critic_raw_normalized,goals).reshape(5,10,146)
 goal_ranges=dict(actual_age_cases=frames.tolist(),max_abs_per_case=normalized.abs().amax(-1).tolist(),median_abs_per_case=normalized.abs().median(-1).values.tolist(),unknown_value_columns_per_case=unknown.sum((-1,-2)).tolist(),policy_normalized_unknown_value_max=shaped_norm[...,:73][unknown].abs().max().item(),critic_normalized_unknown_value_max=critic_goal_normalized[...,:73][unknown].abs().max().item(),critic_goal_normalized_max_per_case=critic_goal_normalized.abs().amax((-1,-2)).tolist(),actual_selected_mask_encoding=True,critic_raw_before_encoding_max_per_case=critic_raw_normalized.abs().amax(-1).tolist(),critic_raw_before_encoding_argmax_per_case=critic_raw_normalized.abs().argmax(-1).tolist(),post_encoding_critic_argmax_per_case=critic_goal_normalized.reshape(5,1460).abs().argmax(-1).tolist(),only_goal_normalizer_arithmetic_no_policy_forward=True,not_a_new_gate_or_causal_failure_claim=True)
 put('NATIVE93_FORMAL_NATIVE_FULLSTATE_INITIAL_CPU_AND_COST_ACTUAL.json',dict(epoch=time.time(),passed=True,model=pub,full_finite_native_modules_norms_threeopts=True,native_optimizers=summaries,progress=publication['native88_migration_window'],frozen_normal86_RSL_actor9critic8STD6_17Adam832460_literal=frozen,nominal400_and100Hz_recipe=True,source_native91_input_not_redecoded=True,formal_initial_model_loads=dict(NEWformal=1,normal86=1),saved_normalizer_counts=norm_counts,optional_flat_goal_normalization=goal_ranges,original_fee_seconds=v['original_fee_seconds'],original_normal_duration=True,original_account_settled_and_allout=True,closing_remaining_snapshot=v['closing_remaining_snapshot'],not_PPO_or_frozen_skill_graduation=True,no_actor_WM_forward_GPU_SDK_physics_or_account_write=True))
 after=model.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 events=pub['original_producer'].get('original_H1_events',{})
 flat=events.get('flat_real_physics_events',{})
 put('NATIVE93_FORMAL_COMPLETED_PHYSICS_EVENTS_TEXT_SCOPE_ACTUAL.json',dict(original_events=events,formal_completed_control_rows=counters['completed_fresh_controls'],flat_callbacks=flat.get('callbacks'),coverage_matches_complete_controls=flat.get('callbacks')==4*counters['completed_fresh_controls'],optional_diagnostic_not_model_gate=True,not_frozen_evaluation_or_skill_graduation=True,no_model_reread=True))
 print(json.dumps(dict(passed=True,native_method_source_qualified=True,skill_not_inferred=True)))

if __name__=='__main__':
 try:main()
 except BaseException:put('NATIVE93_INITIAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_retry_or_promotion=True));raise
