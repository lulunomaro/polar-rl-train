from pathlib import Path
import ast,copy,hashlib,json,os,sys,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
N=Path(__file__).resolve().parent;P=N/'package_v2';R=N/'reports';sys.path[:0]=[str(P),str(N)]
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
put('ROOT188_NEW_LITERAL_STAIRS3_CPU_PURPOSE_CONSUMED.json',dict(epoch=time.time(),purpose='First exact STAIRS3 reward source/config and selected terrain-boundary fixture',model_reads=0,original_old_fixtures_reexecuted=False))
try:
 import torch
 from types import SimpleNamespace
 from literal_stairs3_original_config import OriginalStairs3Cfg,class_to_dict
 from literal_stairs3_original_methods import OriginalStairs3Methods
 from stairs3_measured_boundary188 import LiteralStairs3Kernel,REQUIRED
 from literal_stairs3_original_terrain import Terrain
 before=torch.random.get_rng_state().clone();groups=[]
 old=(N/'upstream/plane/logs/wheel_legged/上台阶3/legged_robot.py').read_text(encoding='utf8');oa=ast.parse(old);oc=next(x for x in oa.body if isinstance(x,ast.ClassDef) and x.name=='LeggedRobot')
 new=(P/'literal_stairs3_original_methods.py').read_text(encoding='utf8');na=ast.parse(new);nc=next(x for x in na.body if isinstance(x,ast.ClassDef))
 selected={x.name:x for x in nc.body};original={x.name:x for x in oc.body if isinstance(x,ast.FunctionDef)}
 for name,node in selected.items():assert ast.get_source_segment(old,original[name])==ast.get_source_segment(new,node),name
 groups.append(dict(name='all31_original_method_text_literal',passed=True,methods=len(selected)))
 scales=class_to_dict(OriginalStairs3Cfg.rewards.scales)
 expected={'tracking_lin_vel':1.5,'tracking_lin_vel_enhance':1.5,'tracking_ang_vel':1.,'base_height':1.,'base_height_enhance':1.,'nominal_state':-1.,'lin_vel_z':-.1,'ang_vel_xy':-.05,'orientation':-10.,'dof_vel':-5e-5,'dof_acc':-2.5e-7,'torques':-.0001,'action_rate':-.05,'action_smooth':-.05,'collision':-1.,'dof_pos_limits':-1.}
 assert scales==expected and OriginalStairs3Cfg.rewards.clip_single_reward==1 and not OriginalStairs3Cfg.rewards.only_positive_rewards
 groups.append(dict(name='exact16_general_reward_scales_and_clip_dt',passed=True,scales=scales,clip_single_reward=1))
 n=8
 frame=dict(commands=torch.tensor([[0.,0.,.25,0.]]).expand(n,4).clone(),base_lin_vel=torch.zeros(n,3),base_ang_vel=torch.zeros(n,3),projected_gravity=torch.tensor([[0.,0.,-1.]]).expand(n,3).clone(),base_height=torch.full((n,),.25),torques=torch.zeros(n,6),dof_vel=torch.zeros(n,6),dof_acc=torch.zeros(n,6),dof_pos=torch.zeros(n,6),dof_pos_limits=torch.tensor([[-1.,1.]]).expand(6,2).clone(),actions=torch.zeros(n,6),last_actions=torch.zeros(n,6,2),theta0=torch.zeros(n,2),contact_forces=torch.empty(n,0,3),penalised_contact_indices=torch.empty(0,dtype=torch.long))
 core=LiteralStairs3Kernel(n,'cpu',.02);value=core.bind_and_compute_once(frame,1).clone();assert torch.allclose(value,torch.full_like(value,.06),atol=1e-7,rtol=0)
 groups.append(dict(name='original_aggregate_three_positive_terms_and_single_dt',passed=True,reward=value.tolist()))
 f={k:v.clone() if torch.is_tensor(v) else v for k,v in frame.items()};f['base_height']-=.1
 badheight=core.bind_and_compute_once(f,2).clone();assert (badheight<value).all()
 f={k:v.clone() if torch.is_tensor(v) else v for k,v in frame.items()};f['torques']+=40;f['actions']+=1
 rough=core.bind_and_compute_once(f,3).clone();assert (rough<value).all()
 groups.append(dict(name='height_error_and_command_effort_cost_preserved',passed=True,good=float(value[0]),height_error=float(badheight[0]),effort_change=float(rough[0])))
 rejects=[]
 for label,change,tick in [('missing_height',lambda x:x.pop('base_height'),4),('bad_command_shape',lambda x:x.update(commands=torch.zeros(n,3)),5),('nonfinite_dq',lambda x:x.update(dof_vel=torch.full((n,6),float('nan'))),6),('foreign_nonempty_collision_set',lambda x:x.update(penalised_contact_indices=torch.tensor([0])),7),('duplicate_reward',lambda x:None,3)]:
  x=dict(frame);change(x)
  try:core.bind_and_compute_once(x,tick)
  except (ValueError,RuntimeError):rejects.append(label)
  else:raise AssertionError('Missing rejection '+label)
 groups.append(dict(name='five_input_and_once_per_control_rejections',passed=True,rejected=rejects))
 cfg=SimpleNamespace(**class_to_dict(OriginalStairs3Cfg.terrain));assert cfg.mesh_type=='trimesh' and cfg.terrain_proportions==[0.,0.,0.,.5,.5,0.]
 # CPU purpose generates the same original raw heightfield, without importing
 # SDK or cooking triangles. The actual selected task remains trimesh.
 cfg.mesh_type='heightfield';terrain=Terrain(cfg,32)
 assert terrain.height_field_raw.shape==(1300,2100) and terrain.env_origins.shape==(10,20,3)
 assert terrain.height_field_raw.dtype.name=='int16'
 groups.append(dict(name='original_Fudan200tile_stairs_curriculum_heightfield',passed=True,source_mesh_type='trimesh',CPU_fixture_only_skips_mesh_converter=True,shape=list(terrain.height_field_raw.shape),rows=10,cols=20,initial_max_level=5,nominal_tread=.7,actual_integer_tread_pixels=int(.7/.1),configured_step_heights=[.05+.18*i/10 for i in range(10)],quantized_step_heights_m=[int((.05+.18*i/10)/.005)*.005 for i in range(10)],heightfield_SHA=hashlib.sha256(terrain.height_field_raw.tobytes()).hexdigest(),GPU_or_PhysX_validated=False))
 assert torch.equal(before,torch.random.get_rng_state()) and not torch.cuda.is_initialized()
 report=dict(epoch=time.time(),passed=True,groups=groups,group_count=len(groups),model_reads=0,NN_constructors=0,CUDA_initialized=False,SDK_or_physics_calls=0,original_reward_methods31_text_exact=True,source_reward_weights_unchanged=True,CPU_RNG_unchanged=True,not_runtime_admission_or_policy_success=True)
 put('ROOT188_NEW_LITERAL_STAIRS3_REWARD_TERRAIN_CPU_RETURNED_ACTUAL.json',report)
 print(json.dumps(dict(passed=True,groups=len(groups),original_methods31_text_exact=True,reward_weights=16,terrain_shape=list(terrain.height_field_raw.shape),CUDA_initialized=False)))
except BaseException:
 put('ROOT188_LITERAL_STAIRS3_CPU_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry=True));raise
