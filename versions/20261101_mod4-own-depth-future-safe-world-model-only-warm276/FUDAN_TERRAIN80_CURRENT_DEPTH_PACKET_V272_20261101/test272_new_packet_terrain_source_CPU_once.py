from pathlib import Path
import ast,hashlib,importlib.util,json,os,sys,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
N=Path(__file__).resolve().parent;S=N/'source';R=N/'reports';sys.path.insert(0,str(S))
with(R/'ROOT272_NEW_PACKET_TERRAIN_SOURCE_CPU_CONSUMED.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),old_fixtures_models_assets_raw_SDK_GPU_remote=0),f)
import original_height_query272,native_geometry272,observed_support_context271
assert callable(original_height_query272.OriginalHeightQuery272._get_heights)
assert 'visible_floor_z_m'in observed_support_context271.CurrentDepthPacket271.__dataclass_fields__ and'T_world_heading'in observed_support_context271.CurrentDepthPacket271.__dataclass_fields__
w=(S/'evaluate272_front_depth_zero_PT_UNUSED_once.py').read_text('utf8');c=(N/'run_ROOT272_NEW240_mean_regression_once.py').read_text('utf8');p=(S/'target272_single_N1_parent_UNUSED.py').read_text('utf8')
assert 'cfg.scene.num_envs=80'in w and 'TerrainMixed272Env'in w and 'actual_resource_admission_SHA'in w and "'/World/ground/original_Fudan_STAIRS3'"in w
assert 'num_envs=80,controls_per_case_max=64'in c and 'ram>32*1024**3'in p
assert all(k in w for k in('visible_floor_z_m','T_world_heading','sensor_pose_native13','environment_origins_world'))
assert 'original_dynamic_curriculum_not_claimed=True'in(S/'terrain_only272.py').read_text('utf8')
assert not torch.cuda.is_initialized()
report=R/'ROOT272_NEW_SOURCE_INTERFACE_CPU_RETURNED.json'
with report.open('x',encoding='utf8')as f:json.dump(dict(passed=True,epoch=time.time(),groups=3,scope='New terrain+packet source/AST and dependency import joins, not old numeric fixtures or SDK',models_raw_assets_SDK_GPU_remote=0,CUDA_initialized=False,actual_SDK_pending=True),f,indent=2)
files=json.loads((N/'SOURCE272_FILES_BEFORE_CPU.json').read_bytes())['files']
for q in(report,R/'ROOT272_NEW_PACKET_TERRAIN_SOURCE_CPU_CONSUMED.json',N/'SOURCE272_FILES_BEFORE_CPU.json'):files.append(dict(path=str(q),bytes=q.stat().st_size,SHA=hashlib.sha256(q.read_bytes()).hexdigest()))
idx=N/'INDEX272_NEW240_MEAN_REGRESSION_FROZEN.json'
with idx.open('x',encoding='utf8')as f:json.dump(dict(kind='FROZEN_ORIGINAL_FUDAN_TERRAIN80_CURRENT_DEPTH_PACKET_SOURCE',epoch=time.time(),files=files),f,indent=2)
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest())))
