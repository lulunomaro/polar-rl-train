from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True);S=N/'source';S.mkdir(exist_ok=True)
B=T/'D435I_FRONT_DEPTH_ACTUAL_ZERO_PT_SOURCE_V250_20261101'
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
def replace(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
c=(B/'source/contract250.py').read_text('utf8').replace('NEW250_D435I_FRONT_DEPTH_CAMERA_12CONTROLS_ZERO_PT','NEW254_D435I_IDEAL_FORWARD_RAY_DEPTH_12CONTROLS_ZERO_PT').replace("t['num_envs']==10","t['num_envs']==1")
(S/'contract254.py').write_text(c,encoding='utf8')
w=(B/'source/evaluate250_front_depth_zero_PT_UNUSED_once.py').read_text('utf8').replace('250','254')
w=replace(w,"ENABLE_CAMERAS='1'","ENABLE_CAMERAS='0'");w=w.replace("'--headless','--enable_cameras','--device'","'--headless','--device'").replace("'--num_envs','10'","'--num_envs','1'").replace('cfg.scene.num_envs=10','cfg.scene.num_envs=1').replace("from isaaclab.sensors import CameraCfg","from isaaclab.sensors import RayCasterCameraCfg\n from isaaclab.sensors.ray_caster.patterns import PinholeCameraPatternCfg")
a=w.index(' cfg.scene.d435i=CameraCfg(');b=w.index(' real=sdk.Mixed209Env',a)
replacement=''' ground_file=OUT/'FORWARD_RAY254_GROUND_AND_270MM.usda'
 points=[(-10.,-10.,0.),(10.,-10.,0.),(10.,10.,0.),(-10.,10.,0.)]+[(x,y,z)for z in(0.,.27)for x,y in[(1.25,-.75),(2.75,-.75),(2.75,.75),(1.25,.75)]]
 cube=[(0,3,2),(0,2,1),(4,5,6),(4,6,7),(0,4,7),(0,7,3),(1,2,6),(1,6,5),(0,1,5),(0,5,4),(3,7,6),(3,6,2)]
 faces=[(0,1,2),(0,2,3)]+[tuple(i+4 for i in f)for f in cube]
 text='#usda 1.0\\n( defaultPrim = "Ground" metersPerUnit = 1 upAxis = "Z" )\\n'
 text+='def Mesh "Ground" ( prepend apiSchemas = ["PhysicsCollisionAPI", "MaterialBindingAPI"] ) {\\n'
 text+='point3f[] points = '+str(points)+'\\nint[] faceVertexCounts = '+str([3]*len(faces))+'\\nint[] faceVertexIndices = '+str([i for f in faces for i in f])+'\\n'
 text+='uniform token subdivisionScheme = "none"\\nbool doubleSided = true\\nrel material:binding:physics = </Ground/Material>\\n'
 text+='def Material "Material" ( prepend apiSchemas = ["PhysicsMaterialAPI"] ) { float physics:staticFriction = 0.5 float physics:dynamicFriction = 0.5 float physics:restitution = 0.5 }\\n}\\n'
 ground_file.write_text(text,encoding='utf8')
 put('ACTUAL254_GENERATED_TERRAIN_METADATA.json',dict(path=str(ground_file),bytes=ground_file.stat().st_size,SHA=hashlib.sha256(text.encode()).hexdigest(),physical_and_ray_mesh_same_USD=True,plane0_and270mm_box=True,not_privileged_heightmap=True))
 cfg.scene.ground=AssetBaseCfg(prim_path='/World/ground',spawn=sim_utils.UsdFileCfg(usd_path=str(ground_file)),init_state=AssetBaseCfg.InitialStateCfg(pos=(0.,0.,0.)))
 cfg.scene.d435i=RayCasterCameraCfg(prim_path=cfg.scene.robot.prim_path+'/chassis',update_period=0.,mesh_prim_paths=['/World/ground'],max_distance=4.,data_types=['distance_to_image_plane'],
  pattern_cfg=PinholeCameraPatternCfg(focal_length=24.,horizontal_aperture=48.*math.tan(math.radians(87./2)),vertical_aperture=48.*math.tan(math.radians(58./2)),width=84,height=48),
  offset=RayCasterCameraCfg.OffsetCfg(pos=(.15,0.,.15),rot=(0.,math.sin(math.radians(5)),0.,math.cos(math.radians(5))),convention='world'))
'''
w=w[:a]+replacement+w[b:]
w=w.replace("vec.step(actions);real.sim.render();camera.update(real.step_dt,force_recompute=True)","vec.step(actions);camera.update(real.step_dt,force_recompute=True)").replace('torch.zeros((10,6)','torch.zeros((1,6)')
w=w.replace("camera='actual installed6.1.14 CameraCfg'","camera='actual installed6.1.14 RayCasterCameraCfg; geometric environment depth'")
w=w.replace("camera_render_read_hz=50","camera_ray_read_hz=50").replace("real_sim_depth_frames=True","real_sim_depth_frames=True,ray_depth_not_RTX_or_real_D435i_stereo=True,self_occlusion_and_stereo_noise_not_modelled=True")
(S/'evaluate254_front_depth_zero_PT_UNUSED_once.py').write_text(w,encoding='utf8')
parent=(B/'source/target250_single_N1_parent_UNUSED.py').read_text('utf8').replace('250','254');(S/'target254_single_N1_parent_UNUSED.py').write_text(parent,encoding='utf8')
(S/'depth_stair247.py').write_bytes((B/'source/depth_stair247.py').read_bytes())
caller=(B/'run_ROOT250_NEW240_mean_regression_once.py').read_text('utf8').replace('250','254').replace('MOD4_D435I_FRONT_DEPTH_ZERO_PT254','MOD4_D435I_FORWARD_RAY_DEPTH254').replace('num_envs=10,controls_per_case_max=12','num_envs=1,controls_per_case_max=12')
caller=replace(caller,"pattern='run_ROOT254_|","pattern='run_ROOT254_|read253_|read252_|read251_|run_ROOT250_|")
(N/'run_ROOT254_NEW240_mean_regression_once.py').write_text(caller,encoding='utf8')
files=sorted(S.glob('*.py'))+[N/'run_ROOT254_NEW240_mean_regression_once.py',Path(__file__).resolve()]
for p in files:ast.parse(p.read_text('utf8'),filename=str(p))
assert "ENABLE_CAMERAS='0'"in w and 'real.sim.render()'not in w and 'RayCasterCameraCfg' in w
report=R/'ROOT254_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json';put(report,dict(passed=True,epoch=time.time(),source_AST=len(files),model_raw_SDK_GPU_remote_reads=0,original250_RTX_failure_preserved=True,source251_API_bound=True,source252253_metadata_false_scope='Plain Python cannot resolve isaaclab_physx before App; prior namespace hypothesis not established. No retry of those source entries.',sensor_backend='ActualSDK forward ray depth image, same physical staticUSDmesh. Not ground truth heightmap, not hardware stereo simulation.',actual_case_pending=True))
idx=N/'INDEX254_NEW240_MEAN_REGRESSION_FROZEN.json';put(idx,dict(epoch=time.time(),kind='FROZEN_FORWARD_RAY_DEPTH_ZERO_PT_SOURCE',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]],actual_learning=False))
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),AST=len(files))))
