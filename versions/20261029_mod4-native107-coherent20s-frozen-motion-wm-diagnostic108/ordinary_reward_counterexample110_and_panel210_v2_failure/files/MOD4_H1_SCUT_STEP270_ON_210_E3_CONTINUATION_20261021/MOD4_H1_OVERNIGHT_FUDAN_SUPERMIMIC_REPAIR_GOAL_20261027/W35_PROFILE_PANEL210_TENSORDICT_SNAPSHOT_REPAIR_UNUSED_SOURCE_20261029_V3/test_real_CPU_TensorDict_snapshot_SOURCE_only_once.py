"""Real TensorDict CPU synthetic data only. No saved models/SDK/raw/GPU query."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import importlib.util
import json
from pathlib import Path
import time
import traceback
from collections import UserDict
from types import SimpleNamespace
import torch
import tensordict
from tensordict import TensorDict

D=Path(__file__).resolve().parent


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def instance(module):
    p=object.__new__(module.W35DomainPanel);p.t=torch;p.real=SimpleNamespace(num_envs=4);p.selected=torch.tensor([1,3],device='cpu');p.frame={};return p
def decode_key(k):
    if k['kind']=='none':return None
    if k['kind']=='tuple':return tuple(decode_key(x) for x in k['items'])
    return k['value']
def expect_error(call,typ):
    try:call()
    except typ:return True
    return False


def main():
    torch.set_num_threads(1)
    m=load('selected_v3_snapshot_CPU',D/'w35_profile_env_domain_panel_v1.py')
    old=load('old_snapshot_CPU_reproduce',D.parent/'W35_PROFILE_ENV_DOMAIN_PANEL_UNUSED_SOURCE_20261029_V1/w35_profile_env_domain_panel_v1.py')
    p=instance(m);previous=instance(old)
    policy=torch.arange(140,dtype=torch.float32,device='cpu').reshape(4,35)
    critic=torch.arange(152,dtype=torch.float64,device='cpu').reshape(4,38)
    flag=torch.tensor([[True],[False],[True],[False]],device='cpu')
    count=torch.arange(4,dtype=torch.int64,device='cpu').reshape(4,1)
    obs=TensorDict(dict(policy=policy,critic=critic,nested=TensorDict(dict(flag=flag,count=count),batch_size=[4],device='cpu')),batch_size=[4],device='cpu')
    leaves=[obs['policy'],obs['critic'],obs['nested','flag'],obs['nested','count']]
    values=[x.clone() for x in leaves];pointers=[x.data_ptr() for x in leaves];versions=[x._version for x in leaves]
    before_rng=torch.get_rng_state().clone();original_id=id(obs)
    snapshot=p._snapshot(obs)
    after_rng=torch.get_rng_state().clone()
    checks=dict(
        reproduce_actual_old_TensorDict_rejection=expect_error(lambda:previous._snapshot(obs),TypeError),
        true_TensorDictBase= isinstance(obs,tensordict.TensorDictBase),
        original_batch4_selected_batch2=snapshot['original_batch_size']==[4] and snapshot['snapshot_batch_size']==[2],
        container_type_device_keys=snapshot['container_type']=='tensordict.TensorDictBase' and snapshot['original_device']=='cpu' and set(snapshot['entries'])=={'policy','critic','nested'},
        policy_shape_dtype_values=snapshot['entries']['policy']['shape']==[2,35] and snapshot['entries']['policy']['original_shape']==[4,35] and snapshot['entries']['policy']['dtype']=='torch.float32' and snapshot['entries']['policy']['value']==policy[[1,3]].tolist(),
        critic_float64_values=snapshot['entries']['critic']['dtype']=='torch.float64' and snapshot['entries']['critic']['value']==critic[[1,3]].tolist(),
        nested_bool_int64=snapshot['entries']['nested']['entries']['flag']['dtype']=='torch.bool' and snapshot['entries']['nested']['entries']['count']['dtype']=='torch.int64',
        no_input_mutation_or_replacement=id(obs)==original_id and all(torch.equal(x,y) and x.data_ptr()==ptr and x._version==v for x,y,ptr,v in zip(leaves,values,pointers,versions)),
        no_CPU_RNG_advance=torch.equal(before_rng,after_rng),
    )
    p.requested(torch.arange(24,dtype=torch.float32,device='cpu').reshape(4,6),obs)
    checks['actual_requested_observation_path'] = p.frame['observations_given_to_original_actor']==snapshot and p.frame['raw_actor_ingress6']['shape']==[2,6]
    tuple_td=TensorDict({('observation','policy'):policy,('observation','critic'):critic},batch_size=[4],device='cpu')
    tuple_snapshot=p._snapshot(tuple_td)
    checks['TensorDict_tuple_paths_preserved_as_nested_keys']=set(tuple_snapshot['entries']['observation']['entries'])=={'policy','critic'}
    ordinary=dict(version=1,cache=dict(legs=policy),private_RNG=torch.arange(4,dtype=torch.uint8,device='cpu'))
    checks['existing_string_dict_format_exact']=p._snapshot(ordinary)==previous._snapshot(ordinary)
    checks['global_RNG_axis_not_selected']=p._snapshot(ordinary)['private_RNG']['shape']==[4] and not p._snapshot(ordinary)['private_RNG']['axis0_is_selected_env']
    mixed=UserDict({1:policy,'1':critic,(2,'x',None):flag,None:count,False:policy,.25:critic})
    mixed_snapshot=p._snapshot(mixed)
    decoded=[decode_key(x['key']) for x in mixed_snapshot['entries']]
    checks['legal_typed_mapping_keys_lossless']=decoded==list(mixed) and type(decoded[0]) is int and type(decoded[1]) is str and len(decoded)==6
    checks['nested_Mapping_and_TensorDict']=p._snapshot(UserDict(dict(observation=obs,mixed=mixed)))['observation']==snapshot
    bad_td=TensorDict(dict(policy=policy,unsupported=object()),batch_size=[4],device='cpu')
    checks['real_TensorDict_unsupported_value_rejected']=expect_error(lambda:p._snapshot(bad_td),TypeError)
    checks['unsupported_mapping_key_rejected']=expect_error(lambda:p._snapshot({object():policy}),TypeError)
    checks['nonfinite_mapping_key_rejected']=expect_error(lambda:p._snapshot({float('nan'):policy}),TypeError)
    checks['unsupported_value_not_stringified']=expect_error(lambda:p._snapshot(object()),TypeError)
    selected=p.selected;p.selected=torch.tensor([7],device='cpu')
    checks['invalid_selected_index_not_padded']=expect_error(lambda:p._snapshot(obs),IndexError);p.selected=selected
    json.dumps(snapshot,allow_nan=False);json.dumps(mixed_snapshot,allow_nan=False)
    checks['JSON_roundtrip_nested_keys_data']=json.loads(json.dumps(mixed_snapshot))==mixed_snapshot
    assert all(checks.values()),checks
    out=dict(epoch=time.time(),passed=True,kind='real_CPU_TensorDict_synthetic_API_only',torch_version=torch.__version__,tensordict_version=tensordict.__version__,device='cpu',checks=checks,
             not_exact_target_API_claim=True,target_Torch2_10_cu128_and_actual_TensorDict_version_native24_pending=True,
             no_saved_model_NPZ_raw_SDK_actor_forward_or_GPU_query=True)
    with (D/'REAL_CPU_TENSORDICT_SYNTHETIC_POSITIVE_NEGATIVE_ACTUAL.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2)
    print(json.dumps(out))


if __name__=='__main__':
    try:main()
    except BaseException:
        with (D/('reports/ORIGINAL_REAL_CPU_TENSORDICT_FIXTURE_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(passed=False,error=traceback.format_exc(),no_model_or_remote=True),f,indent=2)
        raise
