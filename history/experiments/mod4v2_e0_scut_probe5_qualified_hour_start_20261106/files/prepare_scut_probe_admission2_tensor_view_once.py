"""New closed-probe purpose: strict existing Torch/ProxyArray view ABI; no reward or numeric-gate changes."""
from pathlib import Path
import json,ast,hashlib
D=Path(__file__).resolve().parent;closed=json.loads(Path(json.loads((D/'E0_SCUT_PROBE_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());m=closed['metadata'];c=closed['cases']['E0'];f=c['V2_MIGRATION_FINAL.json'];assert closed['closed']is True and all(m['OWNER_EXIT_ACTUAL.json'][k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and m['OUTER_OWNER_WAIT_ACTUAL.json']['original_owner_reaped']is True and c['V2_LEARNER_LOADED.json']is c['SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json']is None and f['new_updates']==0 and 'Unexpected robot tensor shape: joint_acc'in f['error']
outputs={};s=(D/'scut_v14_flat_reward_adapter_v2.py').read_text(encoding='utf8');original=s
helper='''def _tensor_view(value, torch_module, label):
    """Only the existing SDK zero-copy Tensor view; never reshape/cast/copy/fill a physical field."""
    if isinstance(value, torch_module.Tensor):
        return value
    from isaaclab.utils.warp import ProxyArray
    if isinstance(value, ProxyArray):
        view = value.torch
        if isinstance(view, torch_module.Tensor):
            return view
    raise Unknown("Unsupported tensor ABI for " + label + ": " + type(value).__module__ + "." + type(value).__qualname__ + " shape=" + str(getattr(value, "shape", None)))


'''
assert s.count('class _RewardState:')==1;s=s.replace('class _RewardState:',helper+'class _RewardState:')
reps=[('self.prev = torch.zeros_like(_need(action_manager, "action"))','self.prev = torch.zeros_like(_tensor_view(_need(action_manager, "action"), torch, "raw_action"))'),('value = _need(data, key)\n            if not isinstance(value, t.Tensor) or tuple(value.shape) != shape:', 'value = _tensor_view(_need(data, key), t, key)\n            if tuple(value.shape) != shape:'),('raise Unknown("Unexpected robot tensor shape: " + key)','raise Unknown("Unexpected robot tensor shape: " + key + " observed=" + str(tuple(value.shape)) + " expected=" + str(shape))'),('command = _need(_need(env, "command_manager"), "get_command")("twist")','command = _tensor_view(_need(_need(env, "command_manager"), "get_command")("twist"), t, "twist")'),('height = _need(env, "_mod4_height_cmd")','height = _tensor_view(_need(env, "_mod4_height_cmd"), t, "height")'),('forces = _need(_need(self.sensor, "data"), "net_forces_w_history")','forces = _tensor_view(_need(_need(self.sensor, "data"), "net_forces_w_history"), t, "contact_history")'),('terminated = _need(env, "reset_terminated")','terminated = _tensor_view(_need(env, "reset_terminated"), t, "reset_terminated")'),('action = env.action_manager.action','action = _tensor_view(env.action_manager.action, t, "raw_action")')]
for a,b in reps:assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
# Preserve every source formula/config/SDK order/weight/dt/numeric mask/shape predicate; inverse only the ABI edits.
back=s.replace(helper,'')
for a,b in reversed(reps):assert back.count(b)==1;back=back.replace(b,a)
assert back==original
outputs[D/'scut_v14_flat_reward_adapter_v3.py']=s;reward_sha=hashlib.sha256(s.encode()).hexdigest()
w=(D/'worker_e0_scut_v14_probe_v1.py').read_text(encoding='utf8');w=w.replace('scut_v14_flat_reward_adapter_v2','scut_v14_flat_reward_adapter_v3').replace('d9c876183aebfb39085e336d35b717c4574b2fda4e88ee73aa5f1db93722e685',reward_sha);outputs[D/'worker_e0_scut_v14_probe_v2.py']=w
st=(D/'stage_e0_scut_probe_nonpt_v1.py').read_text(encoding='utf8').replace('stage_e0_scut_probe_nonpt_v1.py','stage_e0_scut_probe_nonpt_v2.py').replace('worker_e0_scut_v14_probe_v1.py','worker_e0_scut_v14_probe_v2.py').replace('scut_v14_flat_reward_adapter_v2.py','scut_v14_flat_reward_adapter_v3.py');outputs[D/'stage_e0_scut_probe_nonpt_v2.py']=st
for kind in('stage','dispatch','collect'):
 old=f'{kind}_e0_scut_probe_once.py';new=f'{kind}_e0_scut_probe_admission2_once.py';t=(D/old).read_text(encoding='utf8').replace('E0_SCUT_PROBE_','E0_SCUT_PROBE_ADMISSION2_').replace('worker_e0_scut_v14_probe_v1.py','worker_e0_scut_v14_probe_v2.py').replace('stage_e0_scut_probe_nonpt_v1.py','stage_e0_scut_probe_nonpt_v2.py').replace('scut_v14_flat_reward_adapter_v2.py','scut_v14_flat_reward_adapter_v3.py')
 if kind=='stage':
  a='D=Path(__file__).resolve().parent;';assert t.count(a)==1;t=t.replace(a,a+"prior=json.loads((D/'SCUT_PROBE_FIRST_CLOSED_TENSOR_ABI_FAILURE.json').read_bytes());assert prior['actually_closed_waited_settled_released']is True and prior['source_learner_loaded']is False and prior['actual_PPO_updates']==0;")
 outputs[D/new]=t
for p,t in outputs.items():assert not p.exists();ast.parse(t);compile(t,str(p),'exec')
for p,t in outputs.items():p.write_text(t,encoding='utf8',newline='\n')
(D/'SCUT_PROBE_FIRST_CLOSED_TENSOR_ABI_FAILURE.json').write_text(json.dumps(dict(root=closed['root'],actually_closed_waited_settled_released=True,actual_owner_exit=m['OWNER_EXIT_ACTUAL.json'],actual_outer_wait=m['OUTER_OWNER_WAIT_ACTUAL.json'],source_learner_loaded=False,actual_PPO_updates=0,error=f['error'],SDK_source_conclusion='joint_acc/joint_vel return ProxyArray; .torch is cached zero-copy; current math/native quaternions both xyzw, no permutation',source_only_not_live_type_shape_proof=True,reward_formulas_weights_and_numeric_gates_unchanged=True,no_automatic_old_purpose_replay=True),indent=2),encoding='utf8');print(json.dumps(dict(source_AST_passed=True,recipe_inverse_exact=True,reward_v3_SHA=reward_sha,unchanged_one_update_probe=True,no_HOUR_or_other_expert_launch=True,no_SDK_or_model_execute_by_preparer=True)))
