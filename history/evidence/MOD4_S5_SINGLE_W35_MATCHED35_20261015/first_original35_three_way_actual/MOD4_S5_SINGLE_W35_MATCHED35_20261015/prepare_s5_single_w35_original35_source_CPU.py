"""First missing S5 cell only; original35 physics unchanged, single A0 source."""
from pathlib import Path
import ast,hashlib,json,os,shutil,sys,time,traceback,zipfile
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;W=D.parent;Q=D/'payload';R=D/'reports';ROOT='D:/MOD4_async_eval/'+D.name
P=W/'MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015';RET=W/'MOD4_S4_FIRST_GATE_RETENTION_PAIR_20261015'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 R.mkdir(exist_ok=True);assert not Q.exists()
 complete=json.loads((RET/'reports/FIRST_GATE_RETENTION_FIXED_NINE_COMPLETE.json').read_bytes());assert complete['all_nine_closed_and_CPU_admitted']
 # Old sources remain intact. Unused large gate/E0 files are not copied into this new single-policy package.
 shutil.copytree(P/'payload',Q,ignore=shutil.ignore_patterns('__pycache__','S4_gate_first_final.pt','E0_frozen_source.pt'))
 shutil.copy2(D/'s5_single_frozen35_v1.py',Q/'s5_single_frozen35_v1.py')
 source=Q/'source/E1_WAVE35_frozen_source.pt';assert H(source)=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
 original=(Q/'full80_runtime_native_v1.py').read_text(encoding='utf8');new=original
 replacements=[('from s4_transition_learned_adapter_v1 import build_route_pair','from s5_single_frozen35_v1 import build_route_pair'),("pair_source=json.loads((O/'S4_FROZEN_PAIR_SOURCE_ACTUAL.json').read_bytes())","pair_source=json.loads((O/'S5_SINGLE_POLICY_SOURCE_ACTUAL.json').read_bytes())"),("pair_source['all18_actor_std_GPU_source_exact']","pair_source['all9_actor_std_GPU_source_exact']"),('actual_anchor_actor_nine_GPU_tensors_source_exact=True,all18_pair_actor_std_exact=True,only_actor_loaded=False,trained_gate6_source_exact_critic_fixture_unused=True','actual_anchor_actor_nine_GPU_tensors_source_exact=True,all9_single_actor_std_exact=True,only_actor_loaded=True,no_gate_or_second_expert_forward=True')]
 for old,value in replacements:assert old in new;new=new.replace(old,value)
 restored=new
 for old,value in reversed(replacements):restored=restored.replace(value,old)
 assert ast.dump(ast.parse(restored))==ast.dump(ast.parse(original))
 (Q/'full80_runtime_native_v1.py').write_text(new,encoding='utf8')
 worker=(Q/'paired_full80_parameter_bound_v2.py').read_text(encoding='utf8');worker=worker.replace(P.name,D.name);compile(worker,'paired_full80_parameter_bound_v2.py','exec');(Q/'paired_full80_parameter_bound_v2.py').write_text(worker,encoding='utf8')
 sys.path[:0]=[str(Q)];from s5_single_frozen35_v1 import Single35
 ck=torch.load(source,map_location='cpu',weights_only=False);tensors=[]
 def walk(v):
  if torch.is_tensor(v):assert v.device.type=='cpu' and (not v.is_floating_point() or torch.isfinite(v).all());tensors.append(v)
  elif hasattr(v,'items'):
   for x in v.values():walk(x)
  elif isinstance(v,(tuple,list)):
   for x in v:walk(x)
 walk(ck);assert sum(v.is_floating_point() for v in tensors)==102
 gate=torch.load(P/'payload/source/S4_gate_first_final.pt',map_location='cpu',weights_only=False);x=gate['S4_shared_control_state']['cache']['policy'][:80].clone()
 rng=torch.get_rng_state().clone();c=Single35(source,80,'cpu');c.last=x[:,22:28].clone();p=c.begin(0,lambda:x)
 assert c.begin(0,lambda:(_ for _ in ()).throw(AssertionError('feedback must be cached'))) is p and c.calls==1
 from torch.nn import functional as F
 expected=x
 for i in (0,2,4,6):
  expected=F.linear(expected,ck['actor_state_dict'][f'mlp.{i}.weight'],ck['actor_state_dict'][f'mlp.{i}.bias'])
  if i!=6:expected=F.elu(expected)
 assert torch.equal(expected,p['raw_action']) and torch.equal(expected.clamp(-6,6),p['clipped_action'])
 end=torch.arange(80)%3==0;c.finish(p['clipped_action'],end);assert not c.last[end].any() and torch.equal(c.last[~end],p['clipped_action'][~end]) and c.exact()
 negatives=[]
 for name,bad in [('wrong_obs_shape',x[:,:34]),('changed_previous_actual_action',x.clone()),('non_normal_mode',x.clone()),('nonfinite',x.clone())]:
  n=Single35(source,80,'cpu');n.last=x[:,22:28].clone()
  if name=='changed_previous_actual_action':bad[:,22]+=1
  if name=='non_normal_mode':bad[:,28:35]=0
  if name=='nonfinite':bad[0,0]=float('nan')
  try:n.begin(0,lambda:bad)
  except AssertionError:negatives.append(name)
  else:raise AssertionError(name)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 m=dict(epoch=time.time(),source_SHA=H(source),source_single_policy=dict(expert='E1_WAVE35_SINGLE_A',local_path=ROOT+'/payload/source/'+source.name,sha256=H(source),bytes=source.stat().st_size,CPU_floating=102),
  no_PPO=True,only_single_actor_forward=True,S5_first_missing_single_policy_cell_not_allfaircomparison=True,
  S4_transition_scope=dict(geometry='original g3 35mm tenwaves and original flat supports',entry_approach_m=.4,after_margin_m=.2,seed=20260928,num_envs=80,route_steps_admitted=[120,1500],no_newgeometry_tensor_setter=True,no_RNG_or_extra_control_added=True),
  original_pair_payload_provenance=dict(path=str(P/'payload/REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),sha256=H(P/'payload/REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')),
  active_source_import_and_metadata_only_changes= [list(x) for x in replacements],physical_main_AST_exact_after_declared_metadata_normalization=True,
  no_training_environment_fullstate_GPU_resume_claimed=True,approved_GPU=False,status='CPU_PREPARED_ONLY_NOT_AN_ACTUAL_LEASE')
 m['file_rows']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json']
 (Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 z=D/'S5_SINGLE_W35_ORIGINAL35_V1.zip';assert not z.exists()
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
  for p in sorted(Q.rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts:archive.write(p,p.relative_to(Q).as_posix())
 report=dict(epoch=time.time(),prepared_CPU_only=True,package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),manifest=dict(path=str(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),sha256=H(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')),worker_SHA=H(Q/'paired_full80_parameter_bound_v2.py'),runtime_SHA=H(Q/'full80_runtime_native_v1.py'),source_single=m['source_single_policy'],all102_source_float_and_9actor_STD_CPU_finite=True,actual80_saved35_single_actor_all6_exact=True,duplicate_tick_feedback_once=True,selectedreset_history_exact=True,negative_inputs_rejected=negatives,CPU_RNG_unchanged_no_CUDA_or_optimizer=True,physical_main_AST_exact_after_declared_import_metadata_normalization=True,existing_rule_and_gate_results_only_reused_after_actual_firstphysics_rootq_parameters_recipes_RNGqueues_exact=True,
  old_WAVE143_historical_result_not_claimed_matched_due_different_backend_data_contract=True,no_new_learning_admitted=True,target_CPU_native_and_full_actual_pending=True)
 p=R/'S5_SINGLE_W35_ORIGINAL35_PACKAGE_CPU_PREPARED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(prepared=True,files=len(m['file_rows']),package=report['package'],new_GPU=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);p=R/('S5_SINGLE_CPU_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_no_transport=True),indent=2),encoding='utf8');raise
