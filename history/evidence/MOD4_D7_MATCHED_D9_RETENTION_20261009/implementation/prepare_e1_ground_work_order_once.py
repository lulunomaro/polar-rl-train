"""Audit actual earlier shallow-terrain sources and prepare the approved E1 scope.

No installed simulator imports, asset imports, learning, or live source writes.
"""
from pathlib import Path
import sys,json,hashlib,time,shlex,ast
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'NEXT_S3_E1_SHALLOW_TERRAIN_WORK_ORDER.json').exists()
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
code=r'''
from pathlib import Path
import json,hashlib,time
P=Path('/home/egde/rl_candidates/MOD4_CONTINUOUS_MIX_BASELINE_20261006/isaac/mod4')
A=Path('/home/egde/rl_candidates/MOD4_SCUT_ROUGH_V1_ADAPTER_20261002')
files=[P/n for n in ('rough_intro_runtime.py','rough_intro_reset.py','rough_reset_tensor.py','rough_intro_chunked_terrain.py','rough_intro_probe.py')]+[A/n for n in ('rough_recipe.py','rough_ground.py','MOD4_RESET_COLLISION_BANK.json','MOD4_RESET_COLLISION_BANK.npz')]
rows=[]
for p in files:
 raw=p.read_bytes();row=dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
 if p.suffix in ('.py','.json'):row['text']=raw.decode('utf8')
 rows.append(row)
print(json.dumps(dict(epoch=time.time(),files=rows,no_simulator_import_or_GPU=True)))
'''
try:
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
finally:c.close()
folder=R/'e1_source_audit';folder.mkdir(exist_ok=True)
for row in v['files']:
 if 'text' in row:
  (folder/Path(row['path']).name).write_text(row['text'],encoding='utf8')
  if row['path'].endswith('.py'):ast.parse(row['text'])
  local=B/'MOD4_CONTINUOUS_MIX_BASELINE_20261006/isaac/mod4'/Path(row['path']).name
  if local.exists():assert local.read_bytes()==row['text'].encode('utf8')
runtime=next(x['text'] for x in v['files'] if x['path'].endswith('rough_intro_runtime.py'))
reset=next(x['text'] for x in v['files'] if x['path'].endswith('rough_intro_reset.py'))
assert 'class RoughIntroEnv(Mod4Env)' in runtime and 'terrain.terrain_generator.num_rows=40' in runtime and 'terrain.terrain_generator.num_cols=40' in runtime
assert '(.01,.02)' in runtime and '(.03,.08)' in runtime and '(.02,.05)' in runtime and '(0.,.01)' in runtime
assert 'ChunkedTerrainImporter' in runtime and 'refresh_ground(self)' in runtime
assert 'max_contact_data_count_per_prim=64' in runtime and 'filter_prim_paths_expr=[]' in runtime
assert 'surface_sampling_not_continuous_nonpenetration=True' in reset
annotation=read(R/'SELECTION_READ_MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json')
selected=read(R/'SELECTED_D7_BEHAVIOR_SOURCE.json');actual=read(B/'MOD4_D7_FULL_CONTRACT_20261009/reports/D7_CURRENT_ACTUAL.json')
remain=actual['actual_tail_adjusted_remaining_seconds'];reserve=min(18*3600,.13*remain)
order=dict(id='NEXT-S3-E1-APPROVED-SHALLOW-TERRAIN-WORK-ORDER-001',epoch=time.time(),existing_approved_S3_scope=True,new_human_approval_generated=False,master_SHA_unchanged=sha(B/'polar-rl-train/history/plans/MOD4_MOE_MASTER_PLAN.md'),status='actual_old_geometry_source_audited_new_D7_terrain_adapter_not_deployed',source_audit=v,
 E0_source_for_independent_E1_admission=selected['source'],E0_source_selected_on_actual_full_paired_behavior=True,source_not_directory_max_or_discarded_preflight=True,E1_and_E0_separate_actor_critic_optimizer_std_and_save_roots=True,old_E1_23621_23733_task_candidates_require_actual_scope_comparison_not_automatic_acceptance=True,
 first_geometry=dict(profile='mod4_intro_gentle_v1',tiny_bar_height_m=[.01,.02],positive_slope_ratio=[.03,.08],inverted_slope_ratio=[.02,.05],random_height_m=[0.,.01],difficulty=[0.,.25],rows=40,columns=40,triangles_exact_chunk_max_faces=25000,terrain_origins_used=False,independent_environment_grid=True),
 first_commands=dict(standing_fraction=.2,body_vx_m_s=[-.3,.3],body_vy=0,yaw=0,no_terrain_spin_in_initial_shallow_scope=True),
 RM_annotation_id=annotation['id'],RM_annotation_ref='MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md/json',RM_annotation_exact_preserved=True,
 future_stair_entrance=dict(part='383/BREP_424 central_upper/central_upper_down',rise_mm=49.5617556,run_mm=49.5617556,local_chamfer_angle_deg=45,first_shallow_scope_does_not_install_this_geometry=True,own_new_ground_contact_reset_contract_required=True,route='approach before lip, both wheels cross, main slope/stair, deck support; down/reverse/oblique/stop-start; stair yaw0',separate_100mm_part280_281_not_in_current5cm_admission=True),
 future_spin=dict(include='flat/wide highway, both rough roads preserving CAD wave/location/direction, central island connection slope, highway connection slope and trapezoid highland slope surfaces',exclude='dog tunnel interior, stair treads/edges and stair-top decks',surface_and_clearance_mask_not_whole_part_AABB=True,no_privileged_terrain_actor_gate_input=True,progression_rad_s=[1,2,4,6,8,10,'4pi'],pure_before_directional_moving=True,not_initial_E1_spin_admission=True),
 required_before_E1_learning=[
 'Isolate the actual D7 277-source implementation and transitive frozen rough recipe/raycast/reset bank. The earlier RoughIntroEnv inherits Mod4Env and lacks D1-D7; never execute it as the new full-DR expert.',
 'Create a new terrain environment on actual ChassisPDMod4Env while retaining sensor/feedback/action/spring/gas/COM-PD ordering, selected reset private CUDA RNG and clean38 critic. Rebind only new terrain task command/reset/ground terms; no teacher or terrain IDs for actor/gate.',
 'Retain actual triangle/winding and chunking, independent grid, full30q CAD reset bank and per-call footprint rays. No floor fallback. Prove selected rows/reset neutral actions, root placement, cache invalidation and D7 COM principal-axis roundtrip within original numerical contracts.',
 'Read actual ground height/normals before termination and reward at the same physical tick; audit actual root/chassis/wheel samples and contact impulse integration. Preserve world-Z meaning where reused; do not call it terrain normal-load or terrain-slip certification. Flat rolling proxy inactive only for yaw0 shallow task.',
 'First actual 2.5ms32-4 small SDK plus20k ground/contact/reset/parameter/readback, then only the genuinely new terrain128x2 and20kx4 complete discarded PPO scope on the same canonical. Reuse valid clock/DR math/SDK, no repeated45min clock experiment.',
 'Compare actual task behavior of fully sourced candidates under matched terrain/commands/DR/fullroot30q; signed forward/backward progress, full segments/prefixes and old-skill retention. Select by actual balanced evidence, not old candidate label or max iteration.',
 'Complete D9 development scope review and mainD7 natural fullsave/oldlaunch closed/real parent guardian children exits/two locks/unique settlement/emptyactive-Sactive before any new unique bounded E1 learning authority; settlement-in-progress is waiting, never clearactive or re-charge.',
 'E1 learns its new task with inherited DR without repeating nine DR lessons; freeze E0 source and do not overwrite its expert. Blocks<=2h/save25/15s local guardian with parallel frozen3060 cases; keep gate/expert budget available.'
 ],
 budget_snapshot=dict(B_seconds=remain,repair_reserve_seconds=reserve,remaining_after_repair_reserve_seconds=remain-reserve,new_budget_seconds=0,not_reservation_ledger_transaction=True),
 missing_hardware_calibration=['D6 absolute zero-joint-friction bounds','D8 actual load/inertia/point/duration','spring force-stroke'],S8_dangerous_reset_requires_later_specific_approval=True,MoE_gate_not_trained=True,E1_adapter_SDK_PPO_learning_executor_deployed=False,GPU_PPO_canonical_or_live_source_mutations=0)
(R/'NEXT_S3_E1_SHALLOW_TERRAIN_WORK_ORDER.json').write_text(json.dumps(order,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(dict(actual_old_source_files=len(v['files']),first_geometry=order['first_geometry'],E1_fullDR_adapter_deployed=False,repair_reserve_hours=reserve/3600,RM_annotation=annotation['id'],new_GPU_PPO_canonical_transactions=0)))
