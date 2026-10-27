"""UNEXECUTED target admission: one native R5 + one normal86 initial CPU load.

No SDK App, physical environment, replay allocation or network. Original D0-D7
new plant readback is mandatory postGO, before first physical control/new Pi.
"""
from pathlib import Path
import os,sys,argparse,json,time,traceback,importlib.util,importlib.metadata,ast
os.environ['CUDA_VISIBLE_DEVICES']=''
B=Path(__file__).resolve().parent;J=B/'job0'
sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps'),str(B/'lib'),str(J/'runtime/isaac/mod4')]

def put(path,value):
    with Path(path).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)

def factory_source_check(B,c):
    from native88_source_guard_v1 import contained,require
    path=contained(B,c.get('worker_relative','h1_native88_changed_plant_worker_v1.py'));tree=ast.parse(path.read_bytes())
    assignments=[(ast.unparse(t),ast.unparse(n.value)) for n in ast.walk(tree) if isinstance(n,ast.Assign) for t in n.targets]
    require(('N','4096') in assignments and ('c.scene.num_envs','N') in assignments and ('c.episode_length_s','5.0') in assignments,'actual pinned fresh4096/5s factory source')
    text=path.read_text('utf8')
    require('install_step270_save_contract' in text and 'validate_precontrol_actual' in text and "J/'GO_PRODUCTION.json'" in text.replace(' ',''),'original fullsave, actual gate and J/GO wiring')
    require('native_own_fudan88_gas400_training_v2' in text and "task['bootstrap_source_filename']" in text,'native run / separate RSL bootstrap path')
    return dict(passed=True,source_only=True,new_environment_count4096=True,timeout5s=True,original_fullsave_installer_retained=True,actual_GPU_runtime_pending=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--slot',required=True);p.add_argument('--num-envs',required=True,type=int);p.add_argument('--seed',required=True,type=int);p.add_argument('--source-scope',required=True);args=p.parse_args()
    import torch,psutil
    torch.set_num_threads(2)
    own=psutil.Process(os.getpid())
    put(J/'NATIVE88_SOURCE_CPU_STARTED_ACTUAL.json',dict(pid=own.pid,exe=own.exe(),argv=own.cmdline(),creation=own.create_time(),cwd=own.cwd(),purpose='new changed-plant88 installed-source CPU admission',before_any_model_load=True))
    from native88_source_guard_v1 import check_payload,H,read,require,contained,validate_output_native_contract
    from native88_protocol_v1 import KIND,PIN_FIELDS,READY_FLAGS,BOOTSTRAP_SHA,digest
    from native88_installed_cpu_helpers_v1 import (frozen_bootstrap,strict_native_restore,rsl_roundtrip,asset_composition_readback,objective_source_CPU_check,extract)
    checked=check_payload(B);c=checked['contract'];task=checked['task'];docs=checked['documents']
    output_contract=extract(B/'source/native88_gas400_migration_v1.py',('NATIVE_CONTRACT',))['NATIVE_CONTRACT']
    validate_output_native_contract(output_contract)
    require(args.slot==task['key'] and args.seed==task['native_seed'] and args.num_envs==4096 and args.source_scope=='native_models_only_fresh400N_environment','typed CLI/source scope')
    role=dict(checked=True,scope='target72_original_loopback_not_required',actual_installed_dependencies_verified=False,network_used=False)
    if task['key']=='h1':
        from forwarded_original_owner_control_v1 import verify_dependencies
        verify_dependencies({'owner_control_dependency_binding_SHA':task['owner_control_dependency_binding_SHA']})
        role=dict(checked=True,scope='source210_h1_exact_installed_dependency_SHA_and_import',actual_installed_dependencies_verified=True,binding_SHA=task['owner_control_dependency_binding_SHA'],network_used=False,secret_used=False)
    sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))
    rsl=Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)))
    from native87_encoder_actual_sdk_adapter_v1 import source_API_CPU_check,EXPECTED_OBSERVATION_MANAGER_SHA
    require(task['expected_actual_SDK_observation_manager_SHA']==c['expected_actual_SDK_observation_manager_SHA']==EXPECTED_OBSERVATION_MANAGER_SHA,'pinned actual encoder API source')
    encoder=source_API_CPU_check(sdk/'managers/observation_manager.py',task['expected_actual_SDK_observation_manager_SHA'],J/'runtime/isaac/mod4/mod4_task.py',c['expected_runtime_joint_names'])
    from native87_sdk_tensor_ingress_cpu_v1 import check as tensor_ingress_check
    for field in ('expected_actual_SDK_base_articulation_data_SHA','expected_actual_SDK_physx_articulation_data_SHA'):require(task[field]==c[field],'Task actual SDK source '+field)
    ingress=tensor_ingress_check(B,sdk,expected_base_SHA=c['expected_actual_SDK_base_articulation_data_SHA'],expected_physx_SHA=c['expected_actual_SDK_physx_articulation_data_SHA'])
    require(encoder['passed'] is True and ingress['passed'] is True,'actual installed SDK source/API checks')
    m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');actual=[]
    expected_RSL=c['expected_actual_RSL_sources'];require(expected_RSL==m['expected_actual_RSL_sources'],'RSL manifest/contract pins')
    for row in expected_RSL:
        path=contained(rsl,row['relative']);require(path.is_file() and path.stat().st_size==row['bytes'] and H(path)==row['SHA'],'actual installed RSL source '+row['relative']);actual.append(dict(relative=row['relative'],SHA=row['SHA']))
    require(H(sdk/'utils/math.py')==c['expected_actual_SDK_math_SHA']==m['expected_actual_SDK_math_SHA'],'actual SDK math source')
    versions={}
    for name in ('isaaclab','rsl-rl-lib','torch'):
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]='not_registered_distribution'
    require(versions==c['expected_installed_versions'],'installed SDK/RSL/torch versions')
    # This file is an unused actual target entry. No local fixture calls main.
    # Models are decoded exactly once each; nothing restores their old plant.
    put(J/'NATIVE88_SOURCE_CPU_MODEL_READ_INTENT_ACTUAL.json',dict(purpose='fresh88 source qualification only',native_source_SHA=task['source_SHA'],separate_normal86_witness_SHA=BOOTSTRAP_SHA,each_initial_load_maximum=1,old_environment_restore=False,no_actor_WM_forward=True))
    native=torch.load(J/'source'/task['source_filename'],map_location='cpu',weights_only=False)
    put(J/'NATIVE88_NATIVE_SOURCE_INITIAL_LOAD_RETURNED_ACTUAL.json',dict(source_SHA=task['source_SHA'],one_initial_load_returned=True))
    witness=torch.load(J/'source'/task['bootstrap_source_filename'],map_location='cpu',weights_only=False)
    put(J/'NATIVE88_NORMAL_WITNESS_INITIAL_LOAD_RETURNED_ACTUAL.json',dict(source_SHA=BOOTSTRAP_SHA,one_initial_load_returned=True))
    frozen=frozen_bootstrap(native,witness)
    modules=strict_native_restore(native,B,c,task)
    rsl_result=rsl_roundtrip(B,witness)
    factory=factory_source_check(B,c)
    asset=asset_composition_readback(B,c,docs['actual_asset_report'])
    objective=objective_source_CPU_check(B,c,task)
    from step270_reward_installed_CPU_v1 import check as reward_check
    from step270_boundary_installed_CPU_v1 import check as boundary_check
    from sampling_acceleration_installed_CPU_v2 import check as sampling_check
    reward=reward_check(B,sdk/'managers/reward_manager.py',reference_path=B/'reference_sources/V5_h1_step270_path_reward_v1.py')
    boundary=boundary_check(B);sampling=sampling_check(B,'h1')
    require(not torch.cuda.is_initialized(),'CPU entry initialized CUDA')
    # Every flag has a concrete successful check above. Runtime flags are kept
    # separate and false; no dictionary comprehension fabricates admission.
    flags=dict(
        role_control_dependency_metadata_closure_checked=role['checked'],
        actual_installed_source_SDK_CPU_passed=encoder['passed'] and ingress['passed'] and versions==c['expected_installed_versions'],
        actual_ordered30_encoder_SDK_source_passed=encoder['passed'],
        actual_SDK_tensor_ingress_CPU_passed=ingress['passed'],
        whole_native_R5_fullstate_finite_CPU_passed=modules['passed'],
        all_native_modules_norms_threeoptimizers_strict_restore_CPU_passed=modules['passed'],
        frozen_normal86_RSL832460_wholepolicy_roundtrip_CPU_passed=frozen['passed'] and rsl_result['passed'],
        source_R5_original_fee_allout_qualified=docs['qualified_R5_pair_report']['original_canonical_cost_settled'] is True,
        native700N_environment_DR_not_restored=modules['old_environment_replay_history_and_RNG_not_restored'],
        fresh400N4096_factory_source_passed=factory['passed'],
        actual_USD_four_attribute_composition_source_passed=asset['passed'],
        independent_own_step_objective_source_CPU_passed=objective['passed'],
        manifest_exact_python_protected_runtime_passed=checked['model_bytes_verified'],
        original_physical_V8_clock_control_success_save_retained=reward['passed'] and boundary['passed'] and sampling['passed'] and factory['original_fullsave_installer_retained'],
        actual_fresh_GPU_before_first_control_still_required=not torch.cuda.is_initialized())
    require(set(flags)==set(READY_FLAGS) and all(v is True for v in flags.values()),'all exact ready flags require successful actual CPU evidence')
    value=dict(passed=True,kind=KIND,source_SHA=task['source_SHA'],source_progress=task['source_progress'],bootstrap_SHA=BOOTSTRAP_SHA,bootstrap_Adam=832460,
        native_continuation_restore_required=True,native_environment_state_from_source=False,
        configured_environment_count=4096,actual_environment_count=None,actual_GPU_runtime_readback_passed=False,
        actual_GPU_fresh4096_DR_readback_passed=False,actual_PhysX400N_runtime_readback_passed=False,
        GPU_UUID=task['GPU_UUID'],execution_backend=task['execution_backend'],seed=task['native_seed'],method_config=task['method_config'],
        candidate_pins=c['candidate_pins'],**{k:(checked['manifest_SHA'] if k=='manifest_SHA' else task[k]) for k in PIN_FIELDS},**flags,
        role_control_dependency_CPU=role,actual_installed_versions=versions,actual_RSL_sources=actual,
        actual_encoder_API=encoder,actual_tensor_ingress=ingress,native_models_strict_restore=modules,frozen_RSL_witness=frozen,installed_RSL_roundtrip=rsl_result,
        factory_source=factory,asset_CPU_readback=asset,new_objective_source_CPU=objective,output_native_contract_source=output_contract,original_V8_RewardManager_CPU=reward,boundary_CPU=boundary,sampling_CPU=sampling,
        initial_model_loads=dict(native_R5=1,normal86_frozen_witness=1),CUDA_initialized=False,
        actual_GPU_before_first_control_required=True,no_actual_environment_or_training=True,changed_plant_not_exact_PhysX_resume=True)
    destination=J/'NATIVE88_CHANGED_PLANT_SOURCE_SDK_CPU_ACTUAL.json';put(destination,value)
    require(H(destination)==digest(value),'CPU report canonical bytes')
    print(json.dumps(dict(passed=True,kind=KIND,CPU_only=True,actual_GPU_readback=False)))

if __name__=='__main__':
    try:main()
    except BaseException:
        try:put(J/('NATIVE88_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(passed=False,original_error=traceback.format_exc(),no_retry=True))
        except BaseException:pass
        raise
