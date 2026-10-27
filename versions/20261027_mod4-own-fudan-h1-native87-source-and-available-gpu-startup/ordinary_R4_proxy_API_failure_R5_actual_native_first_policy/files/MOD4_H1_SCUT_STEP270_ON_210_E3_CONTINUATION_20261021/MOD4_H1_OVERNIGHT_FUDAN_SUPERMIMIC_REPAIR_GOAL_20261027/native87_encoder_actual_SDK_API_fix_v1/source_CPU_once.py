"""Real SDK AST/property fragments and tiny resolved metadata; no scene/model."""
from pathlib import Path
import ast,copy,hashlib,json,sys
from types import SimpleNamespace
import torch
D=Path(__file__).resolve().parent;N=D.parent.parent/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';B=N/'payloads_r3/h1'
sys.path[:0]=[str(D),str(B/'source')]
from native87_encoder_actual_sdk_adapter_v1 import *
checks=[]
def yes(v,name):
 assert v,name
 checks.append(name)
def refuse(fn,name):
 try:fn()
 except (ValueError,KeyError,AttributeError,TypeError):checks.append(name);return
 raise AssertionError('unexpected acceptance '+name)
sdk=N/'saved_actual_SDK_source/observation_manager_6_1_14_actual.py.txt';tasksource=B/'job0/runtime/isaac/mod4/mod4_task.py'
contract=json.loads((B/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json').read_bytes());names=tuple(contract['expected_runtime_joint_names']);order=('left_crank','left_hip','right_crank','right_hip')
proof=source_API_CPU_check(sdk,EXPECTED_OBSERVATION_MANAGER_SHA,tasksource,names)
yes(proof['passed'] and proof['fixture_only'] and proof['actual_scene_or_runtime_encoder_resolution'] is False,'pinned_actual_SDK_property_field_fragments_positive')
yes(hashlib.sha256(sdk.read_bytes()).hexdigest()==EXPECTED_OBSERVATION_MANAGER_SHA and sdk.stat().st_size==34306,'actual_SDK_source34306_SHA_exact')
refuse(lambda:source_API_CPU_check(sdk,'a'*64,tasksource,names),'wrong_actual_SDK_sourceSHA_refused')
View,lineage=actual_source_view(sdk.read_bytes())
def manager():
 m=View('policy')
 m.append_resolved_metadata_fixture('policy','unrelated',SimpleNamespace(params={}))
 m.append_resolved_metadata_fixture('policy','leg_pos',SimpleNamespace(params=dict(asset_cfg=SimpleNamespace(name='robot',preserve_order=True,joint_ids=[names.index(n) for n in order]))))
 return m
def call(m):return actual_encoder_joint_names(SimpleNamespace(observation_manager=m),names,expected_leg_order=order)
m=manager();yes(call(m)==order,'actual_property_parallel_cfg_read_preserves_original_encoder_order')
yes(not hasattr(m,'get_term_cfg'),'fixture_does_not_invent_nonexistent_get_term_cfg')
m=manager();m._group_obs_term_cfgs['policy'][1].params['asset_cfg'].joint_ids=torch.tensor([names.index(n) for n in order])
yes(call(m)==order,'original_indices_supports_actual_CPU_tensor_ID_metadata')
m=manager();m._group_obs_term_names['policy'].remove('leg_pos');refuse(lambda:call(m),'term_cfg_count_mismatch_refused')
m=manager();m._group_obs_term_names['policy'][1]='wrong';refuse(lambda:call(m),'missing_leg_pos_refused')
m=manager();m.append_resolved_metadata_fixture('policy','leg_pos',m._group_obs_term_cfgs['policy'][1]);refuse(lambda:call(m),'duplicate_leg_pos_refused')
m=manager();m._group_obs_term_cfgs['policy'][1].params['asset_cfg'].preserve_order=False;refuse(lambda:call(m),'preserve_order_false_refused')
m=manager();m._group_obs_term_cfgs['policy'][1].params['asset_cfg'].joint_ids=[0,0,1,2];refuse(lambda:call(m),'duplicate_joint_ids_refused')
m=manager();m._group_obs_term_cfgs['policy'][1].params['asset_cfg'].joint_ids=slice(None);refuse(lambda:call(m),'unresolved_all_joint_slice_refused')
m=manager();m._group_obs_term_cfgs['policy'][1].params['asset_cfg'].joint_ids=[names.index(n) for n in reversed(order)];refuse(lambda:call(m),'actuator_or_reversed_order_not_mislabeled_encoder_order')
m=manager();del m._group_obs_term_cfgs;refuse(lambda:call(m),'missing_actual_private_cfg_field_refused_no_fallback')
new=ast.parse((D/'native_own_fudan87_training.py').read_bytes());old=ast.parse((D/'ORIGINAL_R3_ENTRY_BYTES.txt').read_bytes())
def without_encoder(tree):return ast.dump(ast.Module(body=[n for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name!='actual_encoder_joint_names'],type_ignores=[]))
yes(without_encoder(new)==without_encoder(old),'entire_entry_except_encoder_helper_AST_exact')
cpu=ast.parse((D/'target_native87_source_sdk_cpu_v1.py').read_bytes());main=next(n for n in cpu.body if isinstance(n,ast.FunctionDef) and n.name=='main')
calls=[n for n in ast.walk(main) if isinstance(n,ast.Call)]
probe=next(n for n in calls if isinstance(n.func,ast.Name) and n.func.id=='source_API_CPU_check')
loads=[n for n in calls if isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='torch' and n.func.attr=='load']
yes(len(loads)==1 and probe.lineno<loads[0].lineno,'actual_source_API_probe_before_only_bootstrap_load')
yes(not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='get_term_cfg' for n in ast.walk(new)),'new_entry_no_unsupported_API_call')
yes(not torch.cuda.is_initialized(),'source_CPU_no_CUDA')
with (D/'SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,count=len(checks),checks=checks,actual_saved_SDK_source_fixture=proof,
 source_fixture_not_actual_runtime=True,actual_environment_model_actor_physics_or_network=False),f,indent=2)
print(json.dumps(dict(passed=True,count=len(checks))))
