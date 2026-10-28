"""One NEW99 continue97 native formal load plus frozen86 witness, only after actual closure."""
from pathlib import Path
import hashlib,json,os,sys,time,traceback
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent
N=T/'MOD4_H1_FLAT05_STANCE_START_COMPARE_RESOURCE_V99_20261028';B=N/'payloads/continue97';R=HERE/'reports'
C=L/'TWO99_CORRECT_NORMAL900_TWO_NATIVE_COLLECTOR_SOURCE_V1'
COLLECTED=C/'reports/TWO99_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json'
MODEL=C/'current_closed99_models/h1/formal/model_final.pt'

def read(p):return json.loads(Path(p).read_bytes())
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)

def closure(v):
 assert v['actual_one72_finite_returned'] and v['canonical_None'] and v['all_two_original_owner_nodes_workers_out'] and v['original_private_shared_writer_locks_free'] and v['original_owner_private72_shared_locks_free']
 assert v['cohort']['original_cost_settled'] and v['owner_exit']['original_cost_settled']
 go=v['cohort']['go'];segment=v['unique_original_segment'];assert set(go)==set(segment['experts'])=={'h1','restart'}
 assert segment['owner_parent_pid']==go['h1']['original_owner_pid']==go['restart']['original_owner_pid']
 assert segment['charged_expert_seconds']==v['original_fee_seconds']==sum(v['original_fee_by_slot'].values())
 for key in go:
  row=segment['experts'][key]
  assert row['started_epoch']==go[key]['learning_started_epoch'] and row['duration_bound_passed'] and 0<row['charged_seconds']<=3900 and row['charged_seconds']==v['original_fee_by_slot'][key]
 terminal=v['terminals']['h1'];assert terminal['returncode']==0 and not terminal['original_error'] and not terminal['errors'] and terminal['terminal_all_own_children_waited']
 assert terminal['actual_exit']['actual_waited'] and terminal['actual_exit']['returncode']==0
 assert v['formals']['h1']['passed']
 p=v['published']['h1'];assert p['twohost_complete_SHA'] and p['source_stat_unchanged'] and p['NEW_formal_transfer_count']==1 and Path(p['local_path']).resolve()==MODEL.resolve()
 return p

def main(shared_witness=None):
 assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and R.is_dir()
 v=read(COLLECTED);pub=closure(v)
 put('NATIVE99_continue97_NEW_FORMAL_INITIAL_WHOLE_CPU_STARTED_ACTUAL.json',dict(epoch=time.time(),purpose='Initial NEW99 continue97 native formal qualification after actual original two-slot closure',model=pub,model_loads_planned=dict(NEWformal=1,frozen_normal86=1 if shared_witness is None else 0,shared_normal86_reused=shared_witness is not None,input_native97_or_native0=0),no_actor_WM_forward_or_extra_stats=True))
 import torch
 torch.set_num_threads(2);assert not torch.cuda.is_initialized()
 sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps'),str(B/'job0/runtime/isaac/mod4')]
 from native88_source_guard_v1 import finite_tree
 from native88_installed_cpu_helpers_v1 import frozen_bootstrap,validate_native_optimizer,exact
 from native88C_to_flat_migration_v1 import verify_saved_migration,NATIVE_CONTRACT,SOURCE_PINS,SOURCES
 before=MODEL.stat();assert before.st_size==pub['bytes'] and not MODEL.is_symlink()
 with MODEL.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==pub['SHA']
 full=torch.load(MODEL,map_location='cpu',weights_only=False)
 witness=shared_witness if shared_witness is not None else torch.load(B/'job0/source/H1_closed86_policy_only_update138.pt',map_location='cpu',weights_only=False)
 finite_tree(full);finite_tree(witness)
 p=full['UniSuperMimic_publication'];native=full['UniSuperMimic_H1_test'];window=p['native88_migration_window'];count=window['counters']
 assert full['UniSuperMimic_test_contract']==NATIVE_CONTRACT;verify_saved_migration(full,p);assert native['args']==SOURCE_PINS['native_args']
 assert window==pub['original_producer']['native88_migration_window']
 assert native['iteration']==p['native_iteration']==count['native_iteration']>SOURCES['h1']['updates']
 assert p['world_updates']==SOURCES['h1']['world_updates']+count['new_world_updates'] and p['policy_updates']==SOURCES['h1']['policy_updates']+count['new_policy_updates']
 assert count['new_world_updates']>=640 and count['new_policy_updates']>0 and count['completed_fresh_controls']>=64
 assert full['UniSuperMimic_obs_history'].shape==(4096,10,86) and full['UniSuperMimic_bridge_ep_step'].shape==(4096,)
 producer=p['producer'];assert producer['native_learning_seed']==producer['physical_initial_seed']==27 and producer['task_focused_real_replay']==NATIVE_CONTRACT['task_focused_real_replay']
 assert producer['input_start_mode']=='continue97' and producer['stance_reference_revision']==NATIVE_CONTRACT['stance_reference_revision']
 assert window['schema']=='mod4.native99.stance_continue97.objective_window.v1' and window['reference_SHA']==NATIVE_CONTRACT['stance_reference_revision']['reference_SHA']
 entry=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py'
 assert producer['bridge_source_SHA']==hashlib.sha256(entry.read_bytes()).hexdigest()
 assert window['prewrite_preload_validation']['actual_new_gas_parameters_passed'] and window['prewrite_preload_validation']['actual_original_preload_active']
 frozen=frozen_bootstrap(full,witness)
 from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel
 from supermimic_wheel_leg_v3.networks import Policy,Critic
 args=native['args'];modules=dict(wm=AugmentedWheelLegWorldModel(context_dim=31,hidden=args['wm_hidden'],num_joints=30,auxiliary_dim=54,action_dim=6),pi=Policy(86,1460,hist=10,z_dim=32,num_joints=6,hidden=args['policy_hidden']),critic=Critic(1625,hidden=args['critic_hidden']))
 summaries={}
 for key,opt,betas in [('wm','opt_wm',(.9,.999)),('pi','opt_pi',(.9,.95)),('critic','opt_v',(.9,.999))]:
  module=modules[key];module.load_state_dict(native[key],strict=True);assert exact(module.state_dict(),native[key])
  summary=validate_native_optimizer(module,native[opt],betas)
  expected=p['world_updates'] if key=='wm' else p['policy_updates'] if key=='pi' else 20*p['policy_updates']
  assert summary['min_step']==summary['max_step']==expected;summaries[key]=summary
 from spring_pressure_checkpoint import validate_saved_pressure
 from gas_damping_checkpoint import validate_saved_damping
 from chassis_pd_checkpoint import validate_saved_chassis_pd
 validate_saved_pressure(full['spring_pressure_state'],4096);validate_saved_damping(full['gas_damping_state'],4096);validate_saved_chassis_pd(full['chassis_PD_state'],4096)
 assert full['spring_pressure_recipe']['nominal_stiffness_N_m']==2000 and full['physical_action_delay_state']['control_us']==10000 and full['H1_step270_task_state']['version']==270
 assert not torch.cuda.is_initialized();after=MODEL.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 put('NATIVE99_continue97_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json',dict(passed=True,epoch=time.time(),model=pub,progress=window,fullfinite_modules_norms_threeopts_strict=True,native_optimizer_steps=summaries,frozen_normal86_literal=frozen,model_loads=dict(NEWformal=1,frozen_normal86=1 if shared_witness is None else 0,shared_normal86_reused=shared_witness is not None,input_native97_or_native0=0),gas400_and_native100Hz=True,signed_aliases_saved_learning_seed_and_actual_IO_entry_bound=True,original_two_fees=v['original_fee_seconds'],closing_snapshot=v['closing_remaining_snapshot'],original_normal_duration_account_settled_and_allout=True,no_actor_WM_forward_GPU_SDK_physics_or_account_write=True,qualified_method_not_PPO_or_skill_graduation=True))
 print(json.dumps(dict(passed=True,formal_native_method_qualified=True,skill_not_inferred=True)))

if __name__=='__main__':
 try:main()
 except BaseException:put('NATIVE99_continue97_NEW_FORMAL_INITIAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_repeat_initial_load_or_partial_promotion=True));raise
