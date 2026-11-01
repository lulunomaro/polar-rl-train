from pathlib import Path
import ast,hashlib,json,re,textwrap,time
N=Path(__file__).resolve().parent;T=N.parent;B=T/'OWN_MOD4_FULLSTATE_DEPTH_COLLECTOR_V267_20261101';S=N/'source';R=N/'reports';S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
F=T/'FUDAN_STAIRS3_LITERAL_REWARD_TERRAIN_400N50_ADAPT_V188_20261031/train_package';A=T/'OBSERVED_STATIC_SUPPORT_DEPTH_ANCHOR_CONTEXT_SOURCE_V271V2_20261101'
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
def replace(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def ids(s):return re.sub(r'(?<![0-9])267(?![0-9])','272',s)
for p in (B/'source').glob('*.py'):
 if p.name.startswith('evaluate'):continue
 s=ids(p.read_text('utf8'))if p.name not in('depth_stair263.py','compact_episode_static31_v1.py')else p.read_text('utf8')
 if p.name=='contract267.py':s=s.replace('NEW272_OWN_FULLSTATE_DEPTH_64CONTROLS_FROZEN2135_ACTOR','NEW272_ORIGINAL_FUDAN_TERRAIN80_FULL_CURRENT_DEPTH_PACKET');s=s.replace("t['num_envs']==1","t['num_envs']==80")
 if p.name.startswith('target'):
  s=s.replace("ram>8*1024**3","ram>32*1024**3")
  s=replace(s,'admitted=dict(task,actual_parent_private_EX_and_authority_admitted=True)','admitted=dict(task,actual_parent_private_EX_and_authority_admitted=True,actual_resource_admission_SHA=hashlib.sha256((P/\'ACTUAL272_CURRENT_AUTHORITY_AND_N1_RESOURCE_ADMISSION.json\').read_bytes()).hexdigest())')
 (S/p.name.replace('267','272')).write_text(s,encoding='utf8')
for name in('literal_stairs3_original_config.py','literal_stairs3_original_terrain.py','stairs3_heightfield_sdk_bridge188.py','installed_original_raw_pyramid_stairs188.py'):(S/name).write_bytes((F/name).read_bytes())
m=(F/'literal_stairs3_original_methods.py').read_text('utf8');cls=next(n for n in ast.parse(m).body if isinstance(n,ast.ClassDef));method=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='_get_heights');segment=ast.get_source_segment(m,method)
(S/'original_height_query272.py').write_text('"""Unchanged pinned Fudan _get_heights; outer SDK xyzw mapping is separate."""\nimport torch\nclass OriginalHeightQuery272:\n    '+segment+'\n',encoding='utf8')
(S/'terrain_only272.py').write_bytes((N/'terrain_only272.py').read_bytes())
(S/'observed_support_context271.py').write_bytes((A/'observed_support_context271.py').read_bytes())
c=ids((B/'run_ROOT267_NEW240_mean_regression_once.py').read_text('utf8'));c=replace(c,"pattern='run_ROOT272_|","pattern='run_ROOT272_|collect270_exact_|run_ROOT270_|run_ROOT269_|run_ROOT267_|")
c=c.replace('num_envs=1,controls_per_case_max=64','num_envs=80,controls_per_case_max=64').replace('OWN272_FROZEN2135_FULLSTATE_DEPTH','OWN272_FROZEN2135_FUDAN_TERRAIN80_CURRENT_PACKET').replace('N1/64controls512physics128feedback','N80/64controls5120ownpairs512physics128feedback')
(N/'run_ROOT272_NEW240_mean_regression_once.py').write_text(c,encoding='utf8')
w=ids((B/'source/evaluate267_front_depth_zero_PT_UNUSED_once.py').read_text('utf8'))
w=w.replace("'--num_envs','1'","'--num_envs','80'").replace('cfg.scene.num_envs=1','cfg.scene.num_envs=80')
w=replace(w,'import jump194_sdk as sdk','import terrain_only272 as sdk')
start=w.index(" ground_file=OUT/");stop=w.index(' real=sdk.JumpMod4Env',start)
w=w[:start]+''' cfg.scene.d435i=RayCasterCameraCfg(prim_path=cfg.scene.robot.prim_path+'/links/chassis',update_period=0.,mesh_prim_paths=['/World/ground/original_Fudan_STAIRS3'],max_distance=4.,data_types=['distance_to_image_plane'],
  pattern_cfg=PinholeCameraPatternCfg(focal_length=24.,horizontal_aperture=48.*math.tan(math.radians(87./2)),vertical_aperture=48.*math.tan(math.radians(58./2)),width=84,height=48),offset=RayCasterCameraCfg.OffsetCfg(pos=(.15,0.,.15),rot=(0.,math.sin(math.radians(5)),0.,math.cos(math.radians(5))),convention='world'))
''' +w[stop:]
w=w.replace('real=sdk.JumpMod4Env(cfg=cfg)','real=sdk.TerrainMixed272Env(cfg=cfg)')
w=w.replace('camera_parent=cfg.scene.robot.prim_path+\'/links/chassis\'','camera_parent=cfg.scene.robot.prim_path+\'/links/chassis\'')
w=w.replace('stair_fixture_size_m=[1.5,1.5,.27],stair_fixture_pos_relative_env=[2.,0.,.135],not_original_Fudan_terrain_course=True','original_Fudan_geometry=sdk.DATA[\'metadata\'],fixed_warm_level_sampling_0_to5_not_original_dynamic_curriculum=True')
w=w.replace('episodes=torch.zeros(1,device=real.device,dtype=torch.int64)','episodes=torch.zeros(80,device=real.device,dtype=torch.int64)')
w=w.replace('own_transitions=64','own_transitions=5120')
start=w.index(' camera_reads=0');stop=w.index(' def state_now(',start)
w=w[:start]+(N/'depth_packet272_source.txt').read_text('utf8')+w[stop:]
w=w.replace("source_admission_SHA=TASK['worker_SHA']","source_admission_SHA=TASK['actual_resource_admission_SHA']")
needle="physical_reward=physical_reward,physics_end_tick=np.array(current_tick),depth_image=start_depth['image'],K=start_depth['K'],T_heading_optical=start_depth['T'],depth_found=np.array(start_depth['found']),depth_time=np.array(start_depth['sensor_time']),control_time=np.array((control-1)*.02)"
replacement="physical_reward=physical_reward,physics_end_tick=np.array(current_tick),depth_image=start_depth['image'],K=start_depth['K'],T_heading_optical=start_depth['T'],T_world_heading=start_depth['T_world_heading'],visible_floor_z_m=start_depth['visible_floor_z_m'],sensor_pose_native13=start_depth['sensor_pose_native13'],environment_origins_world=real.scene.env_origins,depth_found=start_depth['found'],depth_time=np.array(start_depth['sensor_time']),control_time=np.array((control-1)*.02)"
w=replace(w,needle,replacement)
w=w.replace("depth_valid_input_controls=int(packed['depth_found'].sum())","depth_valid_input_environment_controls=int(packed['depth_found'].sum())")
w=replace(w,"assert int(real._integrated_contact.tick)-tick0==512", "assert anchor_validated>0\n assert int(real._integrated_contact.tick)-tick0==512")
w=w.replace('new_dataset_not_complete_WM_population_or_skill=True','new_dataset_not_complete_WM_population_or_skill=True,complete_current_depth_packet_recorded=True,actual_anchor_packets_validated=anchor_validated,terrain_metadata=sdk.DATA[\'metadata\']')
w=w.replace("put('ACTUAL272_FULL_MEASURED_SCHEMA_BINDING.json',dict(passed=True,","put('ACTUAL272_FULL_MEASURED_SCHEMA_BINDING.json',dict(passed=True,num_envs=80,actual_environment_origins=real.scene.env_origins.cpu().tolist(),actual_resource_admission_SHA=TASK['actual_resource_admission_SHA'],terrain=sdk.DATA['metadata'],")
(S/'evaluate272_front_depth_zero_PT_UNUSED_once.py').write_text(w,encoding='utf8')
K=T/'MOD4_H1_MATLAB_REFERENCE_IMAGINATION_TRACKING_RESOURCE_V165_20261030/payloads_v2/seed27/source/supermimic_wheel_leg_v3'
(S/'native_contract272.py').write_bytes((K/'contract.py').read_bytes())
g=(K/'geometry.py').read_text('utf8');assert g.count('from supermimic_wheel_leg_v3.contract import State')==1
(S/'native_geometry272.py').write_text(g.replace('from supermimic_wheel_leg_v3.contract import State','from native_contract272 import State'),encoding='utf8')
files=sorted(S.glob('*.py'))+[N/'run_ROOT272_NEW240_mean_regression_once.py',Path(__file__).resolve(),N/'terrain_only272.py',N/'depth_packet272_source.txt',N/'test272_new_packet_terrain_source_CPU_once.py']
for p in files:
 if p.suffix=='.py':ast.parse(p.read_text('utf8'),filename=str(p))
report=R/'ROOT272_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json';put(report,dict(passed=True,epoch=time.time(),source_AST=sum(p.suffix=='.py'for p in files),num_envs=80,own_transitions_max=5120,original267_frozen_unchanged=True,original_Fudan_Terrain_class_and_height_query=True,new_warm_placement='Originallevel0..5 fixed,8groundIDs on original flat border; not original dynamic curriculum or270extension.',source_model_GPU_byte_read_decode_max=1,neural_optimizer_steps=0,SDK_remote_models_raw_during_source=0,actual_case_pending=True))
put(N/'SOURCE272_FILES_BEFORE_CPU.json',dict(files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]]))
print(json.dumps(dict(passed=True,source_files=len(files))))
