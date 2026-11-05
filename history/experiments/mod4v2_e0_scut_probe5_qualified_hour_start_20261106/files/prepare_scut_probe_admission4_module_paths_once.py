"""New actual-closed purpose: count registered activation USE SITES, and snapshot actual cached ProxyArray views."""
from pathlib import Path
import ast,json
D=Path(__file__).resolve().parent;c=json.loads(Path(json.loads((D/'E0_SCUT_PROBE_ADMISSION3_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());m=c['metadata'];end=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];case=c['cases']['E0'];f=case['V2_MIGRATION_FINAL.json']
assert c['closed']is True and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0
assert case['V2_NATIVE_INITIALIZED.json']is not None and case['SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json']is None and f['new_updates']==0 and 'Original 256/128/64 ELU morphology/interface differs: actor'in f['error']
log=(D/'SCUT_PROBE3_CLOSED_MODEL_LOG.txt').read_text(encoding='utf8');assert all(x in log for x in('Actor Model: MLPModel','Linear(in_features=35, out_features=256','Linear(in_features=38, out_features=256','(1): ELU(alpha=1.0)','(3): ELU(alpha=1.0)','(5): ELU(alpha=1.0)','(obs_normalizer): Identity()'))
def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def patch(s):
 s=once(s,'for name, child in module.named_modules():','for name, child in module.named_modules(remove_duplicate=False):')
 s=once(s,"linear_layers=linears, activations=activations, normalization=norms,","linear_layers=linears, activations=activations, normalization=norms,\n            activation_count_semantics='registered paths; shared ELU objects counted at each use site',")
 s=once(s,"        if isinstance(value, torch.Generator):", "        from isaaclab.utils.warp import ProxyArray\n        if isinstance(value, ProxyArray):\n            view = value.torch\n            need(torch.is_tensor(view) and tuple(view.shape) == tuple(value.shape),\n                 'Cached SDK ProxyArray view shape/type differs')\n            return view.detach().cpu().clone()\n        if isinstance(value, torch.Generator):")
 a="    need(data is not None and torch.is_tensor(data.net_forces_w_history),\n         'Real contact history cache ABI missing')\n    history = data.net_forces_w_history"
 b="    need(data is not None, 'Real contact history cache ABI missing')\n    reward_module = importlib.import_module(type(state).__module__)\n    history = reward_module._tensor_view(getattr(data, 'net_forces_w_history', None), torch,\n                                         'cached contact_sensor._data.net_forces_w_history')"
 return once(s,a,b)
outputs={D/'worker_e0_scut_v14_probe_v4.py':patch((D/'worker_e0_scut_v14_probe_v3.py').read_text(encoding='utf8'))}
outputs[D/'worker_e0_scut_v14_hour_v2.py']=patch((D/'worker_e0_scut_v14_hour_v1.py').read_text(encoding='utf8'))
s=(D/'stage_e0_scut_probe_nonpt_v3.py').read_text(encoding='utf8').replace('worker_e0_scut_v14_probe_v3.py','worker_e0_scut_v14_probe_v4.py').replace('stage_e0_scut_probe_nonpt_v3.py','stage_e0_scut_probe_nonpt_v4.py');outputs[D/'stage_e0_scut_probe_nonpt_v4.py']=s
truth_name='SCUT_PROBE_THIRD_CLOSED_MODULE_ENUMERATION_FAILURE.json'
for kind in('stage','dispatch','collect'):
 s=(D/(kind+'_e0_scut_probe_admission3_once.py')).read_text(encoding='utf8').replace('E0_SCUT_PROBE_ADMISSION3_','E0_SCUT_PROBE_ADMISSION4_').replace('e0_scut_probe_admission3_','e0_scut_probe_admission4_').replace('worker_e0_scut_v14_probe_v3.py','worker_e0_scut_v14_probe_v4.py').replace('stage_e0_scut_probe_nonpt_v3.py','stage_e0_scut_probe_nonpt_v4.py')
 if kind=='stage':
  a='D=Path(__file__).resolve().parent;';assert s.count(a)==1;s=s.replace(a,a+"third=json.loads((D/'"+truth_name+"').read_bytes());assert third['actually_closed_waited_settled_released']is True and third['initial_checkpoint_accepted']is False and third['actual_PPO_updates']==0;")
 outputs[D/(kind+'_e0_scut_probe_admission4_once.py')]=s
for p,s in outputs.items():assert not p.exists();ast.parse(s);compile(s,str(p),'exec')
truth=D/truth_name;assert not truth.exists()
for p,s in outputs.items():p.write_text(s,encoding='utf8',newline='\n')
truth.write_text(json.dumps(dict(kind='CLOSED_SCUT_NATIVE_PASSED_INITIAL_MODULE_OBSERVER_FAILED_NOT_SKILL',root=c['root'],actual_owner_exit=end,actual_outer_wait=outer,actually_closed_waited_settled_released=True,native_before_PT_passed=True,source_runner_load_and_actor_state_exact_guard_reached='Control-flow evidence: exception at morphology gate after exact(actor.state_dict,source) check; not an independent published acceptance',initial_checkpoint_accepted=False,learner_loaded_receipt_published=False,actual_PPO_updates=0,error=f['error'],actual_model_print_path=str(D/'SCUT_PROBE3_CLOSED_MODEL_LOG.txt'),old_sources_and_hour_v1_preserved=True,new_registered_path_enumeration_not_weight_or_network_change=True,standard_named_modules_default_deduplicates_shared_modules=True,local_MLP_copy_provenance='mod4_standing_step200_rlbptt_20261103/scut_recipe_v18/localdeps/rsl_rl/modules/mlp.py:48-78: one activation_mod reused; actual runtime module print has all three ELU sites; exact current MLP-source byte identity not claimed',cached_proxy_snapshot_uses_same_strict_Tensor_or_actual_ProxyArray_torch_view=True,no_sensor_refresh_or_extra_physics_RNG_observation=True,no_reward_formula_or_threshold_change=True,hour_v2_only_prepared_not_dispatched=True,model_SDK_GPU_or_C_execution_by_preparer=0,goal_complete=False),indent=2,allow_nan=False),encoding='utf8')
print('Registered-use-site morphology and readonly cached-view snapshot repaired in NEW probe4/hour2 sources; dimensions,3ELU and all weight/norm/Adam exact gates retained. No SDK/model/hour execution.')
