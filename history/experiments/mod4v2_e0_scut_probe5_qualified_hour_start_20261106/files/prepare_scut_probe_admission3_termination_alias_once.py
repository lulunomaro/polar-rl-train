"""New closed-gated probe: use the SDK's exact termination-manager mask before its first step alias exists."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent
pointer=json.loads((D/'E0_SCUT_PROBE_ADMISSION2_CLOSED_RESULT_PATH.json').read_bytes());c=json.loads(Path(pointer['path']).read_bytes());m=c['metadata'];end=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];case=c['cases']['E0'];f=case['V2_MIGRATION_FINAL.json']
assert c['closed']is True and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0
assert case['V2_LEARNER_LOADED.json']is case['SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json']is None and f['new_updates']==0 and 'Required field missing:'in f['error']and 'reset_terminated'in f['error']
sdk=(D/'sdk_scut_alignment_abi_source_v1/envs/manager_based_rl_env.py').read_bytes();assert hashlib.sha256(sdk).hexdigest()=='a963cfcdb4cd60955cd022ed709d27c99a6935685b69180bb29d74f8983f6566';assert b'self.reset_terminated = self.termination_manager.terminated'in sdk and sdk.index(b'self.reset_terminated = self.termination_manager.terminated')<sdk.index(b'self.reward_buf = self.reward_manager.compute(dt=self.step_dt)')
old=(D/'scut_v14_flat_reward_adapter_v3.py').read_text(encoding='utf8');a='_tensor_view(_need(env, "reset_terminated"), t, "reset_terminated")';b='_tensor_view(_need(_need(env, "termination_manager"), "terminated"), t, "termination_manager.terminated")';assert old.count(a)==1
new=old.replace(a,b);assert new.replace(b,a)==old;sha=hashlib.sha256(new.encode()).hexdigest();outputs={D/'scut_v14_flat_reward_adapter_v4.py':new}
w=(D/'worker_e0_scut_v14_probe_v2.py').read_text(encoding='utf8');oldsha=hashlib.sha256(old.encode()).hexdigest();assert oldsha=='c82aa2d0eb3e249afad9f439c1d8a7e5d54b628257fbb3914e802347b916fe31'and w.count(oldsha)==1
outputs[D/'worker_e0_scut_v14_probe_v3.py']=w.replace('scut_v14_flat_reward_adapter_v3','scut_v14_flat_reward_adapter_v4').replace(oldsha,sha)
st=(D/'stage_e0_scut_probe_nonpt_v2.py').read_text(encoding='utf8');outputs[D/'stage_e0_scut_probe_nonpt_v3.py']=st.replace('worker_e0_scut_v14_probe_v2.py','worker_e0_scut_v14_probe_v3.py').replace('scut_v14_flat_reward_adapter_v3.py','scut_v14_flat_reward_adapter_v4.py').replace('stage_e0_scut_probe_nonpt_v2.py','stage_e0_scut_probe_nonpt_v3.py')
truth_name='SCUT_PROBE_SECOND_CLOSED_PRESTEP_ALIAS_FAILURE.json'
for kind in('stage','dispatch','collect'):
 p=D/(kind+'_e0_scut_probe_admission2_once.py');s=p.read_text(encoding='utf8').replace('E0_SCUT_PROBE_ADMISSION2_','E0_SCUT_PROBE_ADMISSION3_').replace('e0_scut_probe_admission2_','e0_scut_probe_admission3_').replace('worker_e0_scut_v14_probe_v2.py','worker_e0_scut_v14_probe_v3.py').replace('scut_v14_flat_reward_adapter_v3.py','scut_v14_flat_reward_adapter_v4.py').replace('stage_e0_scut_probe_nonpt_v2.py','stage_e0_scut_probe_nonpt_v3.py')
 if kind=='stage':
  anchor='D=Path(__file__).resolve().parent;';assert s.count(anchor)==1;s=s.replace(anchor,anchor+"second=json.loads((D/'"+truth_name+"').read_bytes());assert second['actually_closed_waited_settled_released']is True and second['source_learner_loaded']is False and second['actual_PPO_updates']==0;")
 outputs[D/(kind+'_e0_scut_probe_admission3_once.py')]=s
for p,s in outputs.items():assert not p.exists();ast.parse(s);compile(s,str(p),'exec')
truth=D/truth_name;assert not truth.exists()
for p,s in outputs.items():p.write_text(s,encoding='utf8',newline='\n')
truth.write_text(json.dumps(dict(root=c['root'],closed_path=pointer['path'],actually_closed_waited_settled_released=True,actual_owner_exit=end,actual_outer_wait=outer,error=f['error'],source_learner_loaded=False,actual_PPO_updates=0,old_source_and_purpose_preserved=True,new_purpose_only=True,source_provenance='Actual current SDK manager_based_rl_env.py:236-240; env.reset_terminated is assigned from termination_manager.terminated immediately before reward.compute. Read same manager mask at pre-step bind, no additional step/reset/observation/RNG/zero fallback.',runtime_shape_or_admission_not_yet_proven=True,recipe_inverse_exact=True,model_SDK_GPU_or_C_execution_by_preparer=0),indent=2,allow_nan=False),encoding='utf8')
print(json.dumps(dict(new_sources_AST_compile=True,reward_v4_SHA=sha,only_termination_manager_alias_binding_changed=True,recipe_inverse_exact=True,original_bool_shape_gate_preserved=True,exact_one_PPO_probe_not_hour=True,source_or_SDK_execution=False)))
