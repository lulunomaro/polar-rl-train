"""Actual target installed-source admission, exactly one load per source file."""
from pathlib import Path
import os,sys,json,time,traceback,importlib.util,importlib.metadata,argparse
os.environ['CUDA_VISIBLE_DEVICES']=''
B=Path(__file__).resolve().parent;J=B/'job0'
sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps'),str(B/'lib'),str(J/'runtime/isaac/mod4')]
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)

def main():
 import torch,psutil
 from dataclasses import dataclass,asdict
 from native_flat90_source_guard_v1 import check_payload,H,read,contained,require
 from native88_installed_cpu_helpers_v1 import frozen_bootstrap,rsl_roundtrip,asset_composition_readback,extract,validate_native_optimizer,exact
 from native88_source_guard_v1 import finite_tree
 from native88C_to_flat_migration_v1 import validate_source,SOURCE_PINS,SOURCE_REFERENCE_SHA,KIND
 p=psutil.Process();put(J/'FLAT90_SOURCE_CPU_STARTED_ACTUAL.json',dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),exe=p.exe(),cwd=p.cwd(),before_model_load=True))
 torch.set_num_threads(2);checked=check_payload(B);c=checked['contract'];task=checked['task']
 sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))
 rsl=Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)))
 old=read(B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json')
 versions={}
 for name in ('isaaclab','rsl-rl-lib','torch'):
  try:versions[name]=importlib.metadata.version(name)
  except importlib.metadata.PackageNotFoundError:versions[name]='not_registered_distribution'
 require(versions==old['expected_installed_versions'],'installed SDK/RSL/torch versions')
 for row in old['expected_actual_RSL_sources']:
  require(H(contained(rsl,row['relative']))==row['SHA'],'actual RSL source pin')
 require(H(sdk/'utils/math.py')==old['expected_actual_SDK_math_SHA'],'SDK math pin')
 from native87_encoder_actual_sdk_adapter_v1 import source_API_CPU_check
 encoder=source_API_CPU_check(sdk/'managers/observation_manager.py',old['expected_actual_SDK_observation_manager_SHA'],J/'runtime/isaac/mod4/mod4_task.py',old['expected_runtime_joint_names'])
 from native87_sdk_tensor_ingress_cpu_v1 import check as ingress_check
 ingress=ingress_check(B,sdk,expected_base_SHA=old['expected_actual_SDK_base_articulation_data_SHA'],expected_physx_SHA=old['expected_actual_SDK_physx_articulation_data_SHA'])
 from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source
 bank=check_runtime_source(J/'runtime/isaac/mod4');require(bank['passed'],'actual installed exact reset source')
 put(J/'FLAT90_SOURCE_MODEL_READ_INTENT_ACTUAL.json',dict(native_SHA=task['source_SHA'],bootstrap_SHA=task['bootstrap_source_SHA'],each_model_load_max1=True,no_old_environment_restore=True))
 full=torch.load(J/'source'/task['source_filename'],map_location='cpu',weights_only=False)
 witness=torch.load(J/'source'/task['bootstrap_source_filename'],map_location='cpu',weights_only=False)
 finite_tree(full);finite_tree(witness)
 native,pub=validate_source(full,SOURCE_PINS['native_contract'],SOURCE_PINS['native_args'],task['source_progress'],SOURCE_REFERENCE_SHA)
 frozen=frozen_bootstrap(full,witness);rsl_proof=rsl_roundtrip(B,witness)
 from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel
 from supermimic_wheel_leg_v3.networks import Policy,Critic
 args=native['args'];modules={}
 wm=AugmentedWheelLegWorldModel(context_dim=31,hidden=args['wm_hidden'],num_joints=30,auxiliary_dim=54,action_dim=6)
 pi=Policy(86,1460,hist=10,z_dim=32,num_joints=6,hidden=args['policy_hidden'])
 critic=Critic(1625,hidden=args['critic_hidden'])
 for name,opt,module,betas in [('wm','opt_wm',wm,(.9,.999)),('pi','opt_pi',pi,(.9,.95)),('critic','opt_v',critic,(.9,.999))]:
  module.load_state_dict(native[name],strict=True);require(exact(module.state_dict(),native[name]),'all model/norms literal '+name)
  modules[name]=validate_native_optimizer(module,native[opt],betas)
 asset=asset_composition_readback(B,old,read(B/old['actual_asset_report_relative']))
 from native_flat_jump_adapter_v1 import OwnFlatJumpReference,OwnFlatJumpMdp,encode_frame
 from supermimic_wheel_leg_v3.geometry import unflatten_state
 doc=read(B/task['native_reference_relative']);provider=OwnFlatJumpReference(doc).bind_named_order(old['expected_runtime_joint_names'],scope='source_CPU_fixture')
 mdp=OwnFlatJumpMdp(provider,read(J/'assets/import_contract.json'),read(B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json'),old['actual_encoder_joint_names'])
 cls=extract(B/'source/supermimic_wheel_leg_v3/learner.py',('SuperMimicConfig',),dict(dataclass=dataclass))['SuperMimicConfig']
 config=extract(B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py',('config_for',),dict(SuperMimicConfig=cls))['config_for'](27)
 require(asdict(config)==args,'target same architecture/config/seed')
 ref,_=provider.query(encode_frame(torch.tensor([210]),torch.tensor([0])))
 state=unflatten_state(torch.cat((ref,torch.zeros(1,54)),-1));a=torch.zeros(1,6);xi=torch.zeros(1,31)
 require(mdp.obs(state,a,xi,torch.tensor([210])).shape==(1,86) and mdp.goal(torch.tensor([210]),10).shape==(1,1460),'new installed MDP shape')
 require(torch.isfinite(mdp.reward(state,torch.tensor([210]),a,a)).all(),'new actual installed analytic reward')
 from flat91_mask_aware_goal_conditioning_v1 import masked_goal_conditioning,validate_goal_source
 goal=mdp.goal(torch.tensor([210]),10);validate_goal_source(goal);conditioned=masked_goal_conditioning(pi.goal_norm(goal),goal).reshape(1,10,146)
 require((conditioned[...,13:73]==0).all() and (conditioned[...,73:]==goal.reshape(1,10,146)[...,73:]).all(),'actual source mask-aware conditioning')
 require(mdp.valid_imagination_start(torch.tensor([468,499]),32).all() and not mdp.valid_imagination_start(torch.tensor([500]),32).any(),'new actual preterminal starts reach unchanged timeout500')
 require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')
 value=dict(passed=True,logical_slot=task['logical_slot'],canonical_worker_key=task['canonical_worker_key'],kind=KIND,source_SHA=task['source_SHA'],source_progress=task['source_progress'],worker_SHA=H(B/'h1_native_flat90_worker_v1.py'),payload_manifest_SHA=checked['manifest_SHA'],source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),
  runtime_clock=dict(physics_dt_s=.0025,control_dt_s=.01,decimation=4,policy_hz=100),nominal_gas_N=400,
  source_native_fullstate_finite=True,all_native_modules_norms_threeoptimizers_strict_restore_CPU_passed=True,frozen_RSL832460_exact=frozen['passed'],actual_source_SDK_CPU_passed=encoder['passed'] and ingress['passed'],no_GPU_yet=True,GPU_UUID=task['GPU_UUID'],execution_backend='target72',num_envs=4096,flat_objective=True,
  actual_installed_versions=versions,encoder=encoder,ingress=ingress,reset_bank=bank,native_modules=modules,frozen_bootstrap=frozen,RSL=rsl_proof,asset=asset,
  terminal_exposure_source_CPU_passed=True,imagination_terminal_exposure=task['imagination_terminal_exposure'],mask_aware_goal_source_CPU_passed=True,goal_conditioning=task['goal_conditioning'],source_native_args_exact=True,initial_loads=dict(native91=1,normal86=1),source_model_environment_RNG_not_restored=True,actual_PhysX_precontrol_still_required=True)
 put(J/'FLAT90_SOURCE_SDK_CPU_ACTUAL.json',value)
 print(json.dumps(dict(passed=True,kind=KIND,no_actual_GPU_training_yet=True)))

if __name__=='__main__':
 try:main()
 except BaseException:
  put(J/('FLAT90_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(original_error=traceback.format_exc(),no_retry=True));raise
