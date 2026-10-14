"""New source only. All prior physical/failed scopes stay byte unchanged."""
from pathlib import Path
import sys,json,time,hashlib,shutil,zipfile,ast,traceback
A=Path(__file__).resolve().parent;W=A.parent;OLD=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_FULL80_20261015/payload';N=W/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_20261015';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not N.exists();Q=N/'payload';R=N/'reports';Q.mkdir(parents=True);R.mkdir()
 m=json.loads((OLD/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').read_bytes())
 for row in m['file_rows']:
  p=OLD/row['relative'];assert H(p)==row['sha256'];q=Q/row['relative'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 # Independent modified runtime retains original physical loop and observer algebra.
 p=Q/'full80_runtime_native_v1.py';s=p.read_text();replacements={
  'from g4_cad_wave_geometry import configure_g4 as configure_intro':'from g3_cad_wave_geometry import configure_g3 as configure_intro',
  'from g4_cad_wave_geometry import profile':'from g3_cad_wave_geometry import profile',
  "from frozen_history_policy import build_frozen_policy":"from s4_transition_rule_adapter_v1 import build_route_pair",
  "np.asarray(wave_profile['normalized_height'])*.05":"np.asarray(wave_profile['normalized_height'])*.035",
  'sampled.max() <= 0.050001':'sampled.max() <= 0.035001',
  "family='CAD_derived50mm_wave'":"family='CAD_derived35mm_wave'",
  "vec, policy, observer = build_frozen_policy(RslRlVecEnvWrapper(e, clip_actions=6.0), args.checkpoint, e.device)":"vec, policy, observer = build_route_pair(RslRlVecEnvWrapper(e, clip_actions=6.0), args.checkpoint, e.device,O,save)",
  "    actor=policy.__closure__[0].cell_contents\n    assert len(actor.state_dict())==9 and all(torch.equal(v.cpu(),source['actor_state_dict'][k]) for k,v in actor.state_dict().items())":"    pair_source=json.loads((O/'S4_FROZEN_PAIR_SOURCE_ACTUAL.json').read_bytes())\n    assert pair_source['all18_actor_std_GPU_source_exact'] and pair_source['optimizer_updates']==0",
  'actual_actor_nine_GPU_tensors_source_exact=True,only_actor_loaded=True':'actual_anchor_actor_nine_GPU_tensors_source_exact=True,all18_pair_actor_std_exact=True,only_actor_loaded=False,new_gate_critic_fixture_unused_for_rule=True',
  '    phase = {}':'    phase = {}\n    e._s4_before_reset_route_phase=phase',
  "protocol='approved_E1_G4_derived50mm_worldmesh_actualray_approach040_fullroute_behavior_v2'":"protocol='approved_S4_E0_WAVE35_rule_original35_worldmesh_actualray_approach040_transition_v1'",
  'WAVE50_WORLDMESH_QUERY_ACTUAL':'S4_WAVE35_WORLDMESH_QUERY_ACTUAL'}
 for old,new in replacements.items():assert s.count(old)==1,old;s=s.replace(old,new)
 p.write_text(s,encoding='utf8')
 # Ensure exactly the declared substitutions account for the complete original runtime.
 restored=s
 for old,new in reversed(list(replacements.items())):assert restored.count(new)==1,new;restored=restored.replace(new,old)
 assert restored==(OLD/'full80_runtime_native_v1.py').read_text()
 anchor='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
 p=Q/'paired_full80_parameter_bound_v2.py';s=p.read_text();assert s.count('cfcefb1c46b33d6028bf6663921fac12a58a5abfdba782e1480a18ac84de541b')==1
 s=s.replace('cfcefb1c46b33d6028bf6663921fac12a58a5abfdba782e1480a18ac84de541b',anchor).replace('MOD4_3060_BODYFRAME_PHASE_FINAL_FULL80_20261015',N.name);p.write_text(s,encoding='utf8')
 refs=[];pair=json.loads((W/'MOD4_S4_E0_WAVE35_ROUTER_NATIVE_20261015/payload_v2/S4_PAIR_SOURCE_MANIFEST.json').read_bytes())
 for row in pair['sources']:
  p=W/'MOD4_S4_E0_WAVE35_ROUTER_NATIVE_20261015/payload_v2/source'/Path(row['local_path']).name;assert H(p)==row['sha256']
  dest=Q/'source'/p.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest)
  refs.append(dict(expert=row['expert'],local_path='D:/MOD4_async_eval/'+N.name+'/payload/source/'+p.name,sha256=row['sha256'],bytes=p.stat().st_size))
 pair.update(sources=refs,first_stateless_native_flat120_only=False,original35_transition_newscope=True,full_route_before_gate_learning_required=True);(Q/'S4_PAIR_SOURCE_MANIFEST.json').write_text(json.dumps(pair,indent=2),encoding='utf8')
 for p in (A/'s4_transition_rule_adapter_v1.py',A/'s4_shared_feedback_hardtop1_v1.py',W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014/hard_top1_frozen_expert_CPU_component_v1.py'):shutil.copy2(p,Q/p.name)
 # Old provenance and CPU validators stay available; unused cfce source weight is never bundled.
 rows=[]
 for p in sorted(Q.rglob('*')):
  if not p.is_file() or p.suffix in ('.pt','.zip') or p.name=='REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json':continue
  if p.suffix=='.py':compile(p.read_text(encoding='utf8'),str(p),'exec')
  rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)))
 m.update(file_rows=rows,S4_transition_scope=dict(only_source_pair=refs,geometry='original g3 35mm tenwaves and original flat supports',entry_approach_m=.4,after_margin_m=.2,seed=20260928,num_envs=80,route_steps_admitted=(120,1500),no_newgeometry_tensor_setter=True,no_RNG_or_extra_control_added=True,policy_rule_only=True,gate_training_admitted=False,physical_runtime_changed_only_declared_source_pair_and_original35_geometry=True))
 (Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 z=N/'S4_ORIGINAL35_TRANSITION_RULE_SOURCE_V1.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:
  for row in rows:out.write(Q/row['relative'],row['relative'])
  out.write(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json','REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')
  for row in refs:out.write(Q/'source'/Path(row['local_path']).name,'source/'+Path(row['local_path']).name)
 report=dict(epoch=time.time(),prepared_CPU_source_only=True,package=dict(path=str(z),bytes=z.stat().st_size,sha256=H(z)),new_root='D:/MOD4_async_eval/'+N.name,manifest=dict(path=str(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),sha256=H(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')),worker=dict(path=str(Q/'paired_full80_parameter_bound_v2.py'),sha256=H(Q/'paired_full80_parameter_bound_v2.py')),runtime=dict(path=str(Q/'full80_runtime_native_v1.py'),sha256=H(Q/'full80_runtime_native_v1.py')),source_pair=refs,original_G3_geometry_bytes_exact=True,original_runtime_undeclared_diff_none=True,declared_source_policy_and_35_geometry_substitutions=list(replacements),original_clock_DR_reset_q30_entry_command_reward_hardware_unmodified=True,new_sameoriginal_W35_geometry_SHA_must_pass_actual_native=True,no_SSH_GPU_PPO_or_budgetwrite=True,own_native_fullstate_gate_learning_not_yet_admitted=True)
 p=R/'S4_ORIGINAL35_TRANSITION_RULE_SOURCE_CPU_PREPARED_ACTUAL.json';p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),package=report['package'],source_files=len(rows),GPU_admitted=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (A/'reports'/('S4_TRANSITION_SOURCE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_SSH_GPU=True),indent=2),encoding='utf8');raise
