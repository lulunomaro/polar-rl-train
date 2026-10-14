"""Prepare a new native3060 full80 port of the actual original protocol; no GPU."""
from pathlib import Path
import ast,hashlib,json,time,shutil,zipfile
D=Path(__file__).resolve().parent;W=D.parent
R=W/'MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014';assert not R.exists();R.mkdir();(R/'reports').mkdir()
old=W/'MOD4_E1_WAVE35_SECOND_BOUNDED_20261011/wave50_worldmesh_scope/frozen_history_flat_WAVE50_WORLDMESH.py'
raw=old.read_text();tree=ast.parse(raw)
main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
s=ast.get_source_segment(raw,main)
s=s.replace('def main():','def run_full80(args,O,L,save):').replace('    assert args.steps == 1500','    assert args.steps in (120,1500)')
s=s.replace('cfg.scene.num_envs = args.num_envs','cfg.scene.num_envs = args.num_envs\n    cfg.sim.device=args.device\n    for k,v in dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20).items():setattr(cfg.sim.physics,k,v)')
s=s.replace('r.data.root_pos_w.torch[:, :2]','tensor(r.data.root_pos_w)[:, :2]').replace('torch.equal(r.data.joint_pos, e._rough_probe_expected_q)','torch.equal(tensor(r.data.joint_pos), e._rough_probe_expected_q)')
s=s.replace('    rawforces = []','    rawforces = []\n    hardware_rows=[]')
s=s.replace('rawforces.append(cpu(wp.to_torch(raw).reshape(80, 2, 3)))','rawforces.append(cpu(wp.to_torch(raw).reshape(80, 2, 3)))\n        hardware_rows.append(actual_substep_hardware_and_COM(e))')
s=s.replace("'applied_torque', 'joint_vel')}","'applied_torque', 'joint_vel', 'policy_obs', 'processed_action', 'guarded_leg_targets')}")
s=s.replace("joint_vel=cpu(r.data.joint_vel))","joint_vel=cpu(r.data.joint_vel), processed_action=cpu(e.action_manager.action), guarded_leg_targets=cpu(e.action_manager.get_term('legs').processed_actions))")
s=s.replace('        action = policy(vec.get_observations())','        obs=vec.get_observations()\n        action = policy(obs)')
s=s.replace('episode=episode.copy(), **phase)','episode=episode.copy(), policy_obs=cpu(obs[\'policy\']), **phase)')
s=s.replace("    initial = dict(root=js(r.data.root_state_w), q=js(r.data.joint_pos), parameters=e.chassis_pd_audit(), assignments=assignments(e), reset=e._rough_probe_reset_receipt)","    initial = dict(root=js(r.data.root_state_w), q=js(r.data.joint_pos), parameters=e.chassis_pd_audit(), assignments=assignments(e), reset=e._rough_probe_reset_receipt, actual_all_physical_parameters=params(e))")
s=s.replace('    cap = e._integrated_contact',"    source=torch.load(args.checkpoint,map_location='cpu',weights_only=False)\n    assert source['E1_terrain_state']['num_envs']==20000\n    assert source['E1_terrain_state']['geometry_triangles_sha256']==ray.geometry.receipt()['triangles_sha256']\n    assert source['E1_terrain_state']['ordered_partition_triangles_sha256']==e.scene.terrain.exact_partition_receipt['triangle_world_f32_order_sha256']\n    actor=policy.__closure__[0].cell_contents\n    assert len(actor.state_dict())==9 and all(torch.equal(v.cpu(),source['actor_state_dict'][k]) for k,v in actor.state_dict().items())\n    save('INITIAL_ACTUAL.json',initial)\n    save('FROZEN_POLICY_SOURCE_ACTUAL.json',dict(source_SHA=observer.checkpoint_sha256,source_saved_envs=20000,fixture_envs=80,actual_actor_nine_GPU_tensors_source_exact=True,only_actor_loaded=True,no_training_DR_projection=True,no_PPO=True))\n    cap = e._integrated_contact")
s=s.replace("    data['targets_m_s'] = cpu(targets)","    data['targets_m_s'] = cpu(targets)\n    assert len(hardware_rows)==args.steps*4\n    for k in hardware_rows[0]['arrays']:data['physical_hardware_'+k]=np.stack([r['arrays'][k] for r in hardware_rows])\n    data['physical_mass_weighted_COM_world']=np.stack([r['mass_weighted_COM_world'] for r in hardware_rows])\n    save('SUBSTEP_HARDWARE_COM_ACTUAL.json',dict(callbacks=len(hardware_rows),motor_torque_speed_bounds_exact=True,COM_frame_max_error_m=max(r['COM_frame_error_m'] for r in hardware_rows),original_COM_formula_tolerance_m=1e-5,no_parameter_setters=True,hardware_calibrated=False))")
s=s.replace('np.arange(1500)','np.arange(args.steps)').replace(', 1500).min(0)',', args.steps).min(0)').replace('actualcallbacks == 6000','actualcallbacks == args.steps*4').replace('v - calls0[k] == 6000','v - calls0[k] == args.steps*4')
s=s.replace('steps=1500, num_envs=80, seconds=15.0','steps=args.steps, num_envs=80, seconds=args.steps*.01')
s=s.replace('    e.close()',"    save('COMPLETE_ACTUAL.json',dict(passed_data_contract=True,case_id=args.case_id,protocol=result['protocol'],checkpoint_sha256=observer.checkpoint_sha256,num_envs=80,steps=args.steps,callbacks=actualcallbacks,ordinary=result['actual_union_ordinary'],truncation=result['actual_union_truncation'],ground_error_m=ground_error,query=result['route_scope']['query_worldmesh_evidence'],raw=dict(path=str(npz),bytes=npz.stat().st_size,sha256=hashlib.sha256(npz.read_bytes()).hexdigest()),original_report=dict(path=str(output),sha256=hashlib.sha256(output.read_bytes()).hexdigest()),native120_not_full15s=args.steps==120,no_PPO=True,qualification_claimed=False))\n    e.close()")
preamble='''"""New native backend port, original80 placement/commands/termination/physical loop retained."""
from pathlib import Path
import json,time,hashlib,numpy as np,torch,warp as wp
import mod4_task as task
from g4_cad_wave_geometry import configure_g4 as configure_intro
from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv
from e1_terrain_training_health import declared_truncation_terms,ORDINARY_TERMS,INTEGRITY_TERMS,TRUNCATION_TERMS
from e1_full_pose_reset import query
from frozen_history_policy import build_frozen_policy
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from factor_runtime_3060_reference17b_v1 import cpu,js,tensor,params,actual_substep_hardware_and_COM
'''
assign=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='assignments')
runtime=preamble+'\n'+ast.get_source_segment(raw,assign)+'\n\n@torch.inference_mode()\n'+s+'\n'
compile(runtime,'full80_runtime_native_v1.py','exec')
Q=R/'payload';shutil.copytree(W/'MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014/payload',Q)
(Q/'full80_runtime_native_v1.py').write_text(runtime,encoding='utf8')
worker=(Q/'paired_direct3060_reference17b_v1.py').read_text()
worker=worker.replace('a.num_envs==8','a.num_envs==80').replace('MOD4_3060_LINUX20K_FINAL_REFERENCE_20261014','MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014').replace("H(D/'factor_runtime_3060_reference17b_v1.py')","H(D/'full80_runtime_native_v1.py')")
worker=worker.replace('from factor_runtime_3060_reference17b_v1 import run_factor','from full80_runtime_native_v1 import run_full80').replace('run_factor(a,O,D,save)','a.output=str(O/\'probe.json\');run_full80(a,O,D,save)')
worker=worker.replace("p.add_argument('--num-envs',type=int,default=8)","p.add_argument('--num-envs',type=int,default=80)")
(Q/'paired_full80_native_v1.py').write_text(worker,encoding='utf8');compile(worker,'paired_full80_native_v1.py','exec')
parent=(Q/'run_direct3060_reference17b_parent_v1.py').read_text().replace('paired_direct3060_reference17b_v1.py','paired_full80_native_v1.py').replace('factor_runtime_3060_reference17b_v1.py','full80_runtime_native_v1.py')
(Q/'run_full80_native_parent_v1.py').write_text(parent,encoding='utf8');compile(parent,'run_full80_native_parent_v1.py','exec')
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert H(Q/'source/model_32411_17b.pt')=='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
old_manifest=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'
rows=[dict(relative=str(p.relative_to(Q)).replace('\\','/'),bytes=p.stat().st_size,sha256=H(p)) for p in Q.rglob('*') if p.is_file() and p!=old_manifest and '__pycache__' not in p.parts]
old_manifest.write_text(json.dumps(dict(protocol='approved_E1_G4_derived50mm_worldmesh_actualray_approach040_fullroute_behavior_v2',new_native3060_full80_port=True,original_protocol_source=dict(path=str(old),sha256=H(old)),file_rows=rows),indent=2),encoding='utf8')
pack=R/'FULL80_NATIVE_SOURCE_V1.zip'
with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED) as z:
 for p in Q.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:z.write(p,str(p.relative_to(Q)).replace('\\','/'))
note=dict(epoch=time.time(),CPU_prepared=True,source_original_protocol=dict(path=str(old),sha256=H(old)),original80_tile_rows_ids_div2_and_columns_ids_mod2_9m_mirror_layout_preserved=True,original27forward27reverse26standing_group_ids_mod3=True,original_full_bank_normal_reset_and_clearance_unchanged=True,original15s_040approach_1N_bothwheel_before_after200mm_no_relaxation=True,actual_native_loop_added_only_readonly_hardware_COM_and_actor_input_witness=True,native_eval_capacity_config_same_as_actual_direct3060_baseline_small_eval_only=True,CPU_compiled=True,source_SHA=H(Q/'source/model_32411_17b.pt'),worker=dict(path=str(Q/'paired_full80_native_v1.py'),sha256=H(Q/'paired_full80_native_v1.py')),runtime=dict(path=str(Q/'full80_runtime_native_v1.py'),sha256=H(Q/'full80_runtime_native_v1.py')),manifest=dict(path=str(old_manifest),sha256=H(old_manifest)),package=dict(path=str(pack),bytes=pack.stat().st_size,sha256=H(pack)),source_files=len(rows),actual_GPU_native120_full1500_and_behavior_NOT_passed=True,no_PPO_or_GPU_launch=True,qualified50=False)
(R/'reports/FULL80_NATIVE_CPU_PORT_PREPARED_ACTUAL.json').write_text(json.dumps(note,indent=2),encoding='utf8')
print(json.dumps(dict(root=str(R),package_SHA=note['package']['sha256'],CPU_prepared=True,GPU_started=False,source_SHA=note['source_SHA'])))
