"""Replace an unexecuted scalar-only snapshot assumption, not physical or model semantics."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent
stage=json.loads((D/'STAGE_E0_SCUT_PROBE_ADMISSION4_RESULT.json').read_bytes())
assert stage['returncode']==0 and stage['owner_dispatched']is False and stage['selected_PT_stat_hash_decode']==0
assert not(D/'DISPATCH_E0_SCUT_PROBE_ADMISSION4_ONCE.json').exists()and not(D/'DISPATCH_E0_SCUT_PROBE_ADMISSION4_RESULT.json').exists()
api=D/'sdk_scut_tensor_math_abi_source_v1/utils/warp/proxy_array.py';api_text=api.read_text(encoding='utf8');assert 'return self._warp.shape'in api_text and 'self._torch_cache = wp.to_torch(self._warp)'in api_text
old="torch.is_tensor(view) and tuple(view.shape) == tuple(value.shape)"
new="torch.is_tensor(view) and tuple(view.shape[:len(value.shape)]) == tuple(value.shape)"
outputs={}
for a,b in [('worker_e0_scut_v14_probe_v4.py','worker_e0_scut_v14_probe_v5.py'),('worker_e0_scut_v14_hour_v2.py','worker_e0_scut_v14_hour_v3.py')]:
 s=(D/a).read_text(encoding='utf8');assert s.count(old)==1;t=s.replace(old,new);assert t.replace(new,old)==s;outputs[D/b]=t
s=(D/'stage_e0_scut_probe_nonpt_v4.py').read_text(encoding='utf8').replace('worker_e0_scut_v14_probe_v4.py','worker_e0_scut_v14_probe_v5.py').replace('stage_e0_scut_probe_nonpt_v4.py','stage_e0_scut_probe_nonpt_v5.py');outputs[D/'stage_e0_scut_probe_nonpt_v5.py']=s
truth='SCUT_PROBE4_UNDISPATCHED_VECTOR_VIEW_PREFLIGHT.json'
for kind in('stage','dispatch','collect'):
 s=(D/(kind+'_e0_scut_probe_admission4_once.py')).read_text(encoding='utf8').replace('E0_SCUT_PROBE_ADMISSION4_','E0_SCUT_PROBE_ADMISSION5_').replace('e0_scut_probe_admission4_','e0_scut_probe_admission5_').replace('worker_e0_scut_v14_probe_v4.py','worker_e0_scut_v14_probe_v5.py').replace('stage_e0_scut_probe_nonpt_v4.py','stage_e0_scut_probe_nonpt_v5.py')
 if kind=='stage':
  a='D=Path(__file__).resolve().parent;';assert s.count(a)==1;s=s.replace(a,a+"viewfix=json.loads((D/'"+truth+"').read_bytes());assert viewfix['prior_staged_only_no_dispatch_marker']is True and viewfix['no_recipe_model_or_shape_contract_change']is True;")
  a='c=connect72();sftp=c.open_sftp()';assert s.count(a)==1
  check="\nfor rel in('OWNER_STARTED.json','OUTER_OWNER_IDENTITY.json','roles/E0/GO_PRODUCTION.json'):\n try:sftp.lstat("+repr(stage['root'])+"+'/'+rel)\n except FileNotFoundError:pass\n else:sftp.close();c.close();raise RuntimeError('Previously staged purpose unexpectedly started: '+rel)\n"
  s=s.replace(a,a+check)
 outputs[D/(kind+'_e0_scut_probe_admission5_once.py')]=s
for p,s in outputs.items():assert not p.exists();ast.parse(s);compile(s,str(p),'exec')
p=D/truth;assert not p.exists()
for target,s in outputs.items():target.write_text(s,encoding='utf8',newline='\n')
p.write_text(json.dumps(dict(kind='UNEXECUTED_STAGED_SOURCE_PREFLIGHT_OBSERVER_CORRECTION_NOT_RUNTIME_FAILURE',prior_root=stage['root'],prior_stage=stage,prior_staged_only_no_dispatch_marker=True,reason='ProxyArray.shape is Warp array dimensions; cached Torch vector/quaternion view can append component axes. Preserve array-shape prefix and Torch type, clone the complete actual view. Field-specific reward/contact/model shape gates remain unchanged.',SDK_source=str(api),SDK_source_SHA=hashlib.sha256(api.read_bytes()).hexdigest(),old_expression=old,new_expression=new,inverse_source_exact_except_expression=True,no_recipe_model_or_shape_contract_change=True,initial_actor_critic_norm_STD_Adam_LR_iteration_acceptance_unchanged=True,source_weights_SDK_GPU_C_operations=0,hour_prepared_only=True,goal_complete=False),indent=2,allow_nan=False),encoding='utf8')
print('New probe5/hour3 cached vector-view prefix check compiled; unexecuted A4 kept unchanged; all physical/reward/model/exact-initial gates retained; no SDK/PT/GO/hour execution.')
