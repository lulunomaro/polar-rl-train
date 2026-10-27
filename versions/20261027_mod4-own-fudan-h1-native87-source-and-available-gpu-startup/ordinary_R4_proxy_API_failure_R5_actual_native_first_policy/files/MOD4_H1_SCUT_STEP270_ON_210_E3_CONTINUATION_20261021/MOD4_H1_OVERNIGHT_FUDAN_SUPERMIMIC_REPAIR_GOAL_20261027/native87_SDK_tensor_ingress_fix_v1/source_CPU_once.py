"""One new portable bridge proxy-ingress integration. No real SDK/model/physics."""
from pathlib import Path
import ast,copy,hashlib,json,sys,tempfile
import torch
D=Path(__file__).resolve().parent;L=D.parent;N=L.parent/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';B=N/'payloads_r4/h1'
sys.path[:0]=[str(D),str(B/'source'),str(B/'job0/runtime/isaac/mod4')]
from native87_sdk_tensor_ingress_cpu_v1 import check,EXPECTED_BASE_SHA,EXPECTED_PHYSX_SHA
assert (D/'ACTUAL_BACKEND_SOURCE_LINEAGE.json').is_file()
checks=[]
def yes(v,name):
 assert v,name
 checks.append(name)
with tempfile.TemporaryDirectory(prefix='native87_source_only_SDK_layout_fixture_') as temp:
 root=Path(temp)/'source/isaaclab/isaaclab';base=root/'assets/articulation/base_articulation_data.py';physx=root.parents[1]/'isaaclab_physx/isaaclab_physx/assets/articulation/articulation_data.py'
 base.parent.mkdir(parents=True);physx.parent.mkdir(parents=True)
 S=N/'saved_actual_SDK_source'
 base.write_bytes((S/'actual_base_articulation_data_for_R5_tensor_view.py.txt').read_bytes())
 physx.write_bytes((S/'actual_physx_articulation_data_for_R5_tensor_view.py.txt').read_bytes())
 value=check(B,root,expected_base_SHA=EXPECTED_BASE_SHA,expected_physx_SHA=EXPECTED_PHYSX_SHA)
 yes(value['passed'] and value['fixture_only'] and value['actual_SDK_instance_or_scene_created'] is False,'portable_real_bridge_ingress_full_CPU_fixture_passed')
 try:check(B,root,expected_base_SHA='a'*64,expected_physx_SHA=EXPECTED_PHYSX_SHA)
 except ValueError:checks.append('wrong_Task_contract_SDK_source_SHA_rejected_before_fixture')
 else:raise AssertionError('wrong source contract accepted')
 physx.write_bytes(physx.read_bytes()+b' ')
 try:check(B,root,expected_base_SHA=EXPECTED_BASE_SHA,expected_physx_SHA=EXPECTED_PHYSX_SHA)
 except ValueError:checks.append('changed_actual_source_bytes_rejected_before_fixture')
 else:raise AssertionError('changed installed-source layout accepted')
new=ast.parse((D/'native_wheel_leg_bridge_v4.py').read_bytes());old=ast.parse((D/'ORIGINAL_R4_BRIDGE_BYTES.txt').read_bytes())
def filtered(tree):
 t=copy.deepcopy(tree)
 for node in t.body:
  if isinstance(node,ast.ImportFrom) and node.module=='actual_DR_memory_getter_v1':node.names=[x for x in node.names if x.name!='tensor']
  if isinstance(node,ast.ClassDef) and node.name=='NativeWheelLegBridge':node.body=[x for x in node.body if not isinstance(x,ast.FunctionDef) or x.name!='current']
 return ast.dump(t)
yes(filtered(new)==filtered(old),'entire_bridge_except_tensor_import_and_current_AST_exact_including_terminal_step_actions_rewards')
def current(tree):return next(x for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='NativeWheelLegBridge' for x in n.body if isinstance(x,ast.FunctionDef) and x.name=='current')
yes([ast.dump(x) for x in current(new).decorator_list]==[ast.dump(x) for x in current(old).decorator_list],'current_original_inference_decorator_unchanged')
fields=[ast.unparse(c.args[0]) for c in ast.walk(current(new)) if isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id=='tensor']
yes(fields==['r.data.root_state_w','r.data.joint_pos','r.data.joint_vel','r.data.applied_torque'],'exactly_four_SDK_ingress_existing_views')
yes((D/'ORIGINAL_READONLY_GETTER_BYTES.txt').read_bytes()==(B/'source/actual_DR_memory_getter_v1.py').read_bytes(),'original_readonly_tensor_normalizer_byteexact_not_modified')
yes(not torch.cuda.is_initialized(),'local_test_no_CUDA')
result=dict(passed=True,count=len(checks)+value['count'],checks=checks,portable_target_CPU_fixture=value,
 source_scope='saved actual SDK source copies in temporary declared source-layout fixture; not installed local SDK',
 actual_SDK_scene_model_actor_physics_network=False,old_fixture_tests_not_rerun=True)
with (D/'SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(passed=True,count=result['count'])))
