from pathlib import Path
import os,sys,json,hashlib,time,traceback
T=Path(__file__).resolve().parent;B=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028/payload';F=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/H1_99_STANCE_GOAL_AND_CLEAN_START_SOURCE_V1';R=F/'reports'
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2,allow_nan=False)
def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 proof=json.loads((R/'EARLIEST_NATIVE0_ONE_TRANSFER_TWOHOST_SHA_RETURNED_ACTUAL.json').read_bytes());assert proof['passed'] and proof['twohost_fullSHA'] and proof['new_concrete_restart_source_transfer_count']==1
 p=Path(proof['local_path']);before=p.stat();assert before.st_size==97824121
 with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==proof['SHA']=='5fb246002e39d487ca7b4ad3b5d4171f8065b0ce7ddf26368a95944e4eb32a1d'
 put('EARLIEST_NATIVE0_INITIAL_RESTART_CPU_LOAD_INTENT_ACTUAL.json',dict(epoch=time.time(),purpose='Initial wholeCPU qualification of human-requested protected before-control0 native restart source; capture complete source pins in this one load',model=proof,planned_model_loads=dict(earliest_native0=1,normal86witness=1,current_native97=0),no_actor_WM_forward_GPU_or_physics=True))
 import torch
 torch.set_num_threads(2);assert not torch.cuda.is_initialized();sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps'),str(B/'job0/runtime/isaac/mod4')]
 from native88_source_guard_v1 import finite_tree
 from native88_installed_cpu_helpers_v1 import frozen_bootstrap,exact
 from supermimic_wheel_leg_v3.networks import Policy,Critic
 from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel
 ck=torch.load(p,map_location='cpu',weights_only=False);witness=torch.load(B/'job0/source/H1_closed86_policy_only_update138.pt',map_location='cpu',weights_only=False);finite_tree(ck);finite_tree(witness)
 native=ck['UniSuperMimic_H1_test'];pub=ck['UniSuperMimic_publication'];args=native['args'];frozen=frozen_bootstrap(ck,witness)
 observed=dict(native_iteration=native['iteration'],world_updates=pub['world_updates'],policy_updates=pub['policy_updates'],native_optimizer_state_sizes={k:len(native[k]['state']) for k in ('opt_wm','opt_pi','opt_v')},native_args=args,native_contract=ck['UniSuperMimic_test_contract'],producer=pub['producer'],publication={k:v for k,v in pub.items() if k not in ('producer',)},top_level_keys=list(ck),normalization_counts={k:{name:float(value) for name,value in native[k].items() if name.endswith('.count')} for k in ('wm','pi','critic')})
 put('EARLIEST_NATIVE0_DECODED_SOURCE_PINS_BEFORE_ASSERTS_ACTUAL.json',observed)
 assert native['iteration']==pub['native_iteration']==0 and pub['world_updates']==pub['policy_updates']==0
 assert args['hist']==10 and args['goal_frames']==10 and args['z_dim']==32 and args['amp']=='none' and args['test_hidden_dims'] is None and args['seed']==27
 with torch.random.fork_rng(devices=[]):modules=dict(wm=AugmentedWheelLegWorldModel(context_dim=31,hidden=args['wm_hidden'],num_joints=30,auxiliary_dim=54,action_dim=6),pi=Policy(86,1460,hist=10,z_dim=32,num_joints=6,hidden=args['policy_hidden']),critic=Critic(1625,hidden=args['critic_hidden']))
 summaries={}
 for name,opt,betas in [('wm','opt_wm',(.9,.999)),('pi','opt_pi',(.9,.95)),('critic','opt_v',(.9,.999))]:
  module=modules[name];module.load_state_dict(native[name],strict=True);assert exact(module.state_dict(),native[name]);state=native[opt];assert state['state']=={} and len(state['param_groups'])==1
  group=state['param_groups'][0];assert tuple(group['betas'])==betas and group['params']==list(range(len(list(module.parameters())))) and group['lr']==args['lr']
  summaries[name]=dict(parameter_count=len(list(module.parameters())),strict_full_state_loaded=True,optimizer_state_empty_before_any_update=True,group=group)
 assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={832460}
 after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns) and not torch.cuda.is_initialized()
 put('EARLIEST_NATIVE0_TYPED_INITIAL_RESTART_SOURCE_CPU_ACTUAL.json',dict(passed=True,epoch=time.time(),kind='MOD4_PROTECTED_PREUPDATE0_NATIVE127_RESTART_SOURCE_INITIAL_CPU_V1',model=proof,source_pins=observed,strict_module_and_empty_native_optimizer_summaries=summaries,frozen_normal86=frozen,whole_tree_finite=True,source_plant700_states_not_for_restore_to400=True,source_normalizers_literal_included_one_initial_frame_is_not_training=True,source_not_learned_formal_policy_or_skill=True,model_loads=dict(earliest_native0=1,normal86witness=1,current_native97=0),no_actor_WM_forward_GPU_physics_remote_or_account=True,requires_NEW_typed400_flat99_source_and_actual_SDK_admission_before_GO=True))
 print(json.dumps(dict(passed=True,before_any_native_optimizer_update=True,source_progress=[native['iteration'],pub['world_updates'],pub['policy_updates']],native_optimizer_sizes=observed['native_optimizer_state_sizes'],source_normalization_counts=observed['normalization_counts'])))
if __name__=='__main__':
 try:main()
 except BaseException:put('EARLIEST_NATIVE0_INITIAL_RESTART_CPU_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_model_reload_or_partial_promotion=True));raise
