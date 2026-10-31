from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True)
with (R/'PREPARE194_SOURCE_ONCE_STARTED.json').open('x') as f:json.dump(dict(epoch=time.time()),f)
D=N/'train_package';D.mkdir()
O=T/'FUDAN_STAIRS3_LITERAL_REWARD_TERRAIN_400N50_ADAPT_V188_20261031'
shutil.copytree(O/'train_package/payload',D/'payload')
original=T/'FUDAN_ISAACLAB_LITERAL_COLD_PPO_RESOURCE_V184_20261031/package_A_v3/literal_harness_v1'
for name in ('literal_original_methods.py','literal_original_config.py'):shutil.copyfile(original/name,D/name)
src=T/'OWN_MOD4_LITERAL_FUDAN_LAB_ADAPTER_SOURCE_V184_20261031/source'
for name in ('mod4_literal_math184.py','mod4_literal_math184_v2.py'):shutil.copyfile(src/name,D/name)
for name in ('jump194_boundary.py','jump194_sdk.py'):shutil.copyfile(N/name,D/name)
shutil.copyfile(O/'zonglin2_app_launcher.py',D/'zonglin2_app_launcher.py')
old=json.loads((O/'train_package/TASK188.json').read_bytes())
task={**old,'schema':'mod4.literal-original-JUMP.plane.own400N50.D0-D7.two-hour.v194',
 'kind':'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR',
 'literal_reward_snapshot':'jump/wheel_legged_gym/envs/base/legged_robot.py',
 'reward_core_source':str(D/'literal_original_methods.py'),
 'source_reward_CPU_fixture':'ROOT194_NEW_LITERAL_JUMP50_SOURCE_CPU_ACTUAL.json',
 'single_reward_clip':2.5,'reward_selected16':json.loads((T/'MOD4_DELIVERED_FUDAN_JUMP4999_REUSE_RESOURCE_V186_20261031/TASK186.json').read_bytes())['reward_weights'],
 'terrain_mesh_type':'plane','terrain_curriculum':'No geometric curriculum on original flat plane',
 'maximum_parent_seconds':7500,'save_deadline_seconds':7200,'exit_headroom_seconds':300,
 'duration_authority':'User explicitly requested two hours of flat JUMP adaptation on2026-10-31; no new budget grant. Original raw fee arithmetic retained.',
 'commands':dict(vx=[-2.1,2.1],yaw=[-2.,2.],height=[.12,.15],resample_seconds=20.),
 'target_DR_rng_sensor_queue_states_explicitly_new':True,
 'reward_source_functions_and_weights_literal_not_claiming_foreign_plant_identity':True,
 'scope':'Retain delivered4999 full PPO; original JUMP16 on plane. MOD4 physical guards and external SDK mappings remain explicit.'}
for key in ('terrain_rows','terrain_cols','initial_max_level','terrain_proportions','terrain_step_width','terrain_step_height_formula','terrain_physical_vertical_quantization','original_Fudan_terrain_class_literal','terrain_CPU_raw_heightfield_SHA','reward_source_CPU_report_SHA'):
 task.pop(key,None)
(D/'TASK194.json').write_text(json.dumps(task,indent=2,ensure_ascii=False),encoding='utf8')
# Reuse the functioning full-state worker; change only task/reward binding and
# the explicitly authorized two-hour finite deadline. No physical source edits.
s=(O/'run188_literal_stairs3_40050_worker.py').read_text(encoding='utf8')
s=s.replace('TASK188.json','TASK194.json').replace('literal_stairs3_400N50','literal_jump194_400N50').replace('max_parent_seconds\']==3900','max_parent_seconds\']==7500')
s=s.replace("'plane/logs/wheel_legged/上台阶3'","'jump/wheel_legged_gym/envs/base/legged_robot.py'")
s=s.replace('import stairs3_sdk188 as sdk','import jump194_sdk as sdk').replace('sdk.Stairs3Mod4Env','sdk.JumpMod4Env')
s=s.replace('typed_STAIRS3_188_task','typed_JUMP194_task').replace('OriginalSTAIRS3','OriginalJUMP194').replace('STAIRS3','JUMP194').replace('source188_config_only_no_old_main','source194_config_only_no_old_main')
s=s.replace('original_clip_single_reward=1','original_clip_single_reward=2.5')
s=s.replace("  stairs3_curriculum_state=dict(levels=cpu(real.literal.terrain_levels),types=cpu(real.literal.terrain_types),\n   episode_sums=cpu(real.literal.episode_sums),last_actions=cpu(real.last_actions),last_velocity=cpu(real.last_velocity),last_root=cpu(real.last_root)),",
"  original_jump_reward_memory=dict(episode_sums=cpu(real.literal.episode_sums),base_air_time=cpu(real.literal.base_air_time),last_contacts=cpu(real.literal.last_contacts),contact_filt=cpu(real.literal.contact_filt),was_in_flight=cpu(real.literal.was_in_flight),last_actions=cpu(real.last_actions),last_root=cpu(real.last_root)),")
s=s.replace("  Fudan_terrain=sdk.DATA['geometry'],initial_terrain_level_min=int(real.literal.terrain_levels.min()),initial_terrain_level_max=int(real.literal.terrain_levels.max()),\n  original_collision_penalty_selected_body_names=[],empty_is_original_config_not_measured_zero_force=True,",
"  Fudan_terrain=dict(mesh_type='plane',static_friction=.5,dynamic_friction=.5,restitution=.5),measured_mapping=real.binding_receipt(),")
s=s.replace("terrain_level_mean=float(real.literal.terrain_levels.float().mean()),terrain_level_max=int(real.literal.terrain_levels.max()),", "original_jump_diagnostic=real.stats194,")
s=s.replace("MOD4 state mapping/reset treatment", "explicit measured MOD4 mapping with literal JUMP flight-history reset semantics")
s=s.replace("source_reward_no_edits=True", "source_reward_no_edits=True,measured_mapping=real.binding_receipt()")
s=s.replace("'OriginalSTAIRS3 reward/terrain'","'Original JUMP reward/plane'")
s=s.replace('FudanJUMP194 reward/terrain','FudanJUMP194 reward/plane')
s=s.replace('original_JUMP194_reward_and_terrain=True','original_JUMP194_reward_and_plane=True')
s=s.replace("'model_final_complete');raise SavedStop()","'model_final_complete');raise SavedStop()")
ast.parse(s)
assert 'terrain_levels' not in s and 'last_velocity' not in s and 'sdk.DATA' not in s
(D/'run194_literal_jump_plane_worker.py').write_text(s,encoding='utf8')
shutil.copyfile(D/'run194_literal_jump_plane_worker.py',N/'run194_literal_jump_plane_worker.py')
known={r['relative']:r for r in json.loads((O/'TRAIN188_COMPLETE_MANIFEST.json').read_bytes())['files']}
rows=[]
for p in sorted(D.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(D).as_posix()
 if p.suffix.lower() in ('.usd','.usda','.npz','.npy'):
  r=known[rel];assert p.stat().st_size==r['bytes'];sha=r['SHA']
 else:
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if p.suffix=='.py':ast.parse(raw)
 rows.append(dict(relative=rel,local_relative='train_package/'+rel,bytes=p.stat().st_size,SHA=sha))
(N/'TRAIN194_COMPLETE_MANIFEST.json').write_text(json.dumps(dict(schema=task['schema'],files=rows,model_files=0),indent=2),encoding='utf8')
print(json.dumps(dict(files=len(rows),bytes=sum(r['bytes'] for r in rows),original_jump_selected=True,maximum_training_seconds=7200,no_models_read=True)))
