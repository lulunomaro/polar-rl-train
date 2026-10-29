"""UNEXECUTED target CPU entry. One bootstrap torch.load, no scene or GPU.

Actual4096 plant/order/DR/solver checks remain mandatory postGO precontrol.
"""
from pathlib import Path
import os,sys,argparse,json,time,importlib.util,importlib.metadata
os.environ['CUDA_VISIBLE_DEVICES']=''

def main():
    p=argparse.ArgumentParser();p.add_argument('--slot',required=True);p.add_argument('--num-envs',type=int,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--source-scope',required=True);args=p.parse_args()
    B=Path(__file__).resolve().parent;J=B/'job0'
    sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps'),str(B/'lib'),str(J/'runtime/isaac/mod4')]
    import torch
    torch.set_num_threads(2)
    from native87_source_guard_v1 import check_payload,validate_whole_policy,H,read
    from native87_protocol_v1 import KIND,READY_FLAGS,SOURCE_SHA,digest
    checked=check_payload(B);contract=checked['contract'];task=checked['task']
    role_control=dict(checked=True,scope='target72_original_loopback_not_required',actual_installed_dependencies_verified=False,network_used=False)
    if task['key']=='h1':
        from forwarded_original_owner_control_v1 import verify_dependencies
        verify_dependencies({'owner_control_dependency_binding_SHA':task['owner_control_dependency_binding_SHA']})
        role_control=dict(checked=True,scope='source210_h1_exact_installed_dependency_SHA_and_import',actual_installed_dependencies_verified=True,
            binding_SHA=task['owner_control_dependency_binding_SHA'],network_used=False,secret_used=False)
    assert args.slot==task['key'] and args.seed==task['native_seed'] and args.num_envs==4096 and args.source_scope=='policy_only_fresh_environment'
    from native87_encoder_actual_sdk_adapter_v1 import source_API_CPU_check,EXPECTED_OBSERVATION_MANAGER_SHA
    assert task['expected_actual_SDK_observation_manager_SHA']==contract['expected_actual_SDK_observation_manager_SHA']==EXPECTED_OBSERVATION_MANAGER_SHA
    actual_sdk_root=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))
    observation_API=source_API_CPU_check(actual_sdk_root/'managers/observation_manager.py',task['expected_actual_SDK_observation_manager_SHA'],
        J/'runtime/isaac/mod4/mod4_task.py',contract['expected_runtime_joint_names'])
    source=J/'source'/task['source_filename'];assert H(source)==SOURCE_SHA
    s=torch.load(source,map_location='cpu',weights_only=False) # only bootstrap model load in this CPU process
    validate_whole_policy(s)
    def exact(a,b):
        if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
        if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
        if isinstance(a,(list,tuple)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
        return type(a)==type(b) and a==b
    rsl=Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)))
    sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))
    m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');actual=[]
    for row in m['expected_actual_RSL_sources']:
        path=rsl/row['relative'];assert path.resolve().is_relative_to(rsl.resolve()) and path.stat().st_size==row['bytes'] and H(path)==row['SHA'];actual.append(dict(path=str(path),SHA=H(path)))
    assert H(sdk/'utils/math.py')==m['expected_actual_SDK_math_SHA']
    versions={}
    for name in ('isaaclab','rsl-rl-lib','torch'):
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]='not_registered_distribution'
    assert versions==contract['expected_installed_versions'],'target installed versions differ from pinned binder'
    from tensordict import TensorDict
    from rsl_rl.models import MLPModel
    from rsl_rl.algorithms import PPO
    from types import SimpleNamespace
    obs=TensorDict(dict(policy=torch.zeros(1,35),critic=torch.zeros(1,38)),batch_size=[1]);groups=dict(actor=['policy'],critic=['critic'])
    cfg=read(J/'original_run_manifest.json')['env'];hidden=[int(x) for x in cfg['RM_HIDDEN_DIMS'].split(',')]
    actor=MLPModel(obs,groups,'actor',6,hidden_dims=hidden,activation='elu',distribution_cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=float(cfg['RM_INIT_STD']),std_type='scalar'))
    critic=MLPModel(obs,groups,'critic',1,hidden_dims=hidden,activation='elu');optimizer=torch.optim.Adam(list(actor.parameters())+list(critic.parameters()),lr=.0001)
    holder=SimpleNamespace(actor=actor,critic=critic,optimizer=optimizer,rnd=None)
    assert PPO.load(holder,s,None,True) is True
    assert all(exact(obj.state_dict(),s[name]) for name,obj in [('actor_state_dict',actor),('critic_state_dict',critic),('optimizer_state_dict',optimizer)])
    from native87_tiny_API_fixture_v1 import check
    fixture=check(B,contract,task)
    from step270_reward_installed_CPU_v1 import check as reward_check
    from step270_boundary_installed_CPU_v1 import check as boundary_check
    from sampling_acceleration_installed_CPU_v2 import check as sampling_check
    original_reward=reward_check(B,sdk/'managers/reward_manager.py',reference_path=B/'reference_sources/V5_h1_step270_path_reward_v1.py')
    boundary=boundary_check(B);sampling=sampling_check(B,'h1')
    assert not torch.cuda.is_initialized()
    value=dict(passed=True,kind=KIND,source_SHA=SOURCE_SHA,bootstrap_SHA=SOURCE_SHA,bootstrap_Adam=832460,source_normal_PPO_update=138,
        native_continuation_restore_required=False,native_environment_state_from_source=False,source_environment_count=20000,
        configured_environment_count=4096,actual_environment_count=None,episode_timeout_s=5.,
        actual_GPU_runtime_readback_passed=False,actual_GPU_fresh4096_DR_readback_passed=False,
        GPU_UUID=task['GPU_UUID'],execution_backend=task['execution_backend'],seed=task['native_seed'],method_config=task['method_config'],
        candidate_pins=contract['candidate_pins'],**{k:task[k] for k in ('native87_contract_SHA','qualified_H1_report_SHA','previous86_closure_SHA','reference_artifact_SHA','objective_contract_SHA')},
        **{k:True for k in READY_FLAGS},actual_installed_versions=versions,actual_RSL_sources=actual,
        actual_observation_manager_API_source_CPU_passed=observation_API['passed'],actual_observation_manager_source_CPU=observation_API,
        expected_actual_SDK_observation_manager_SHA=task['expected_actual_SDK_observation_manager_SHA'],
        role_control_dependency_CPU=role_control,owner_control_dependency_binding_SHA=task.get('owner_control_dependency_binding_SHA'),
        CPU_fixture=fixture,original_V8_RewardManager_CPU=original_reward,boundary_CPU=boundary,sampling_CPU=sampling,
        CUDA_initialized=False,actual_GPU_before_first_control_required=True,no_actual_environment_or_training=True)
    # Source/previous86 proofs are pinned inventory metadata, validated separately
    # from any bootstrap environmental state; no source env reshape occurs.
    from native87_protocol_v1 import validate_saved_source_and_closure
    validate_saved_source_and_closure(read(B/contract['qualified_H1_report_relative']),read(B/contract['previous86_typed_close_relative']),read(B/contract['previous86_authority_close_relative']))
    destination=J/'NATIVE87_POLICY_ONLY_FRESH4096_SOURCE_SDK_CPU_ACTUAL.json'
    with destination.open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
    assert H(destination)==digest(value)
    print(json.dumps(dict(passed=True,kind=KIND,CPU_only=True,actual_GPU_readback=False)))

if __name__=='__main__':main()
