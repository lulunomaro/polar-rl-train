"""Matched remote MuJoCo player comparison, with frozen actors/gate on CUDA."""
from pathlib import Path
import hashlib,json,os,sys,time,traceback,types
B=Path(__file__).resolve().parent;O=B/'out';O.mkdir();P=B/'player'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (O/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 sys.path.insert(0,'/home/lc01/Zonglin Li/zonglin2/tasks/MoE_small_curb_contact_4090_2410v1/isolated_python_deps')
 import numpy as np,torch,mujoco,onnxruntime as ort
 assert mujoco.__version__=='3.14.0' and ort.__version__=='1.30.0'
 ort.disable_telemetry_events()
 assert str(Path(mujoco.__file__).resolve()).startswith('/home/lc01/Zonglin Li/zonglin2/tasks/MoE_small_curb_contact_4090_2410v1/isolated_python_deps') and str(Path(ort.__file__).resolve()).startswith('/home/lc01/Zonglin Li/zonglin2/tasks/MoE_small_curb_contact_4090_2410v1/isolated_python_deps')
 import torch.nn.functional as F
 torch.set_num_threads(1);assert torch.cuda.is_available() and '4090' in torch.cuda.get_device_name(0)
 cfg=json.loads((B/'CONFIG_V2.json').read_bytes());cp={}
 for role,row in cfg['checkpoints'].items():
  path=B/row['relative'];assert H(path)==row['SHA'];cp[role]=torch.load(path,map_location='cpu',weights_only=False)
 actors={};frozen={}
 for role in ('E0','W35'):
  cpu=cp[role]['actor_state_dict'];assert len(cpu)==9 and cpu['mlp.0.weight'].shape==(256,35);assert all(torch.isfinite(x).all() for x in cpu.values());frozen[role]={k:x.clone() for k,x in cpu.items()};actors[role]={k:x.to('cuda:0') for k,x in cpu.items()}
 gs=cp['gate148']['actor_state_dict'];keys=['distribution.std_param']+[f'mlp.{i}.{s}' for i in (0,2,4,6) for s in ('weight','bias')]
 for i,role in enumerate(('E0','W35')):
  assert all(torch.equal(gs[f'experts.{i}.frozen_{n}'],frozen[role][key]) for n,key in enumerate(keys))
 gate={k.removeprefix('gate.'):v.to('cuda:0') for k,v in gs.items() if k.startswith('gate.')};assert set(gate)=={'w1','b1','w2','b2','w3','b3'}
 def actor(x,w):
  for n in (0,2,4,6):
   x=F.linear(x,w[f'mlp.{n}.weight'],w[f'mlp.{n}.bias'])
   if n!=6:x=F.elu(x)
  return x
 class FrozenCudaPolicy:
  variant='auto'
  def __init__(self,path):self.path=Path(path);self.input_width=35;self.last=None;self.sessions={role:ort.InferenceSession(str(B/'policy'/(('hybrid_moe' if role=='auto' else role)+'.onnx')),providers=['CPUExecutionProvider']) for role in ('auto','E0','W35')}
  def __call__(self,obs):
   x=torch.as_tensor(np.asarray(obs,dtype=np.float32).reshape(1,35),device='cuda:0');assert torch.isfinite(x).all() and x[0,28]==1 and x[0,29:35].abs().sum()==0
   logits=F.linear(F.elu(F.linear(F.elu(F.linear(x,gate['w1'],gate['b1'])),gate['w2'],gate['b2'])),gate['w3'],gate['b3'])
   options=torch.stack((actor(x,actors['E0']),actor(x,actors['W35'])),dim=1);gate_choice=int(logits.argmax(1).item());choice=gate_choice if self.variant=='auto' else 0 if self.variant=='E0' else 1
   raw=self.sessions[self.variant].run(['action'],{'observation':x.cpu().numpy()})[0][0];candidate=options[0].clamp(-6,6).cpu().numpy();error=np.max(np.abs(candidate-np.clip(raw,-6,6)),axis=1);actual_choice=int(error.argmin()) if self.variant=='auto' else choice;self.last=dict(observation=x[0].cpu().numpy(),logits=logits[0].cpu().numpy(),gate_choice=gate_choice,choice=actual_choice,expert_actions=candidate,CUDA_reference_parity_error=float(error[actual_choice]))
   return raw
 stub=types.ModuleType('policy_runtime');stub.OnnxPolicy=FrozenCudaPolicy;sys.modules['policy_runtime']=stub;sys.path.insert(0,str(P));from rm7v7_moe_sim import RM7V7MoESim
 sim=RM7V7MoESim();actual_policy=sim.policy.base;assert isinstance(actual_policy,FrozenCudaPolicy)
 import subprocess
 compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
 own=[r for r in compute.splitlines() if len(r.split(','))>=2 and r.split(',')[1].strip()==str(os.getpid())];assert own and all(cfg['GPU_UUID'] in r for r in own)
 put('ACTUAL_CUDA_SOURCE_AND_PROTOCOL.json',dict(epoch=time.time(),pid=os.getpid(),own_GPU_compute_rows=own,device_name=torch.cuda.get_device_name(0),torch_version=torch.__version__,mujoco_version=mujoco.__version__,onnxruntime_version=ort.__version__,primary_policy_backend='ORT CPUExecutionProvider, same package versions as human Windows player; CUDA4090 frozen actor/gate references only',numpy_version=np.__version__,physics_backend='MuJoCo CPU physics on remote Linux host, same copied player XML/assets/adapter. Frozen policy inference CUDA on4090.',original_player_manifest=sim.delivery,protocol=cfg,original_gate_embedded_experts_literal_exact=True,no_optimizer=True,no_local_simulation=True))

 cases=[];start=time.monotonic();real_step=mujoco.mj_step;physics=[];contacts=[];names={};physics_index=0
 tire_ids=[mujoco.mj_name2id(sim.model,mujoco.mjtObj.mjOBJ_GEOM,n) for n in ('left_tire','right_tire')]
 def instrumented(model,data,*args,**kwargs):
  nonlocal physics_index
  real_step(model,data,*args,**kwargs);physics_index+=1
  count=[0,0];normal_sum=[0.,0.];ground_count=0;max_force=0.;max_geom=-1
  for j in range(data.ncon):
   c=data.contact[j];g1=int(c.geom1);g2=int(c.geom2);b1=int(model.geom_bodyid[g1]);b2=int(model.geom_bodyid[g2])
   if not ((b1==0) != (b2==0)):continue
   robot=g2 if b1==0 else g1;ground=g1 if b1==0 else g2;wrench=np.zeros(6);mujoco.mj_contactForce(model,data,j,wrench);ground_count+=1
   for g in (g1,g2):
    if g not in names:names[g]=dict(name=mujoco.mj_id2name(model,mujoco.mjtObj.mjOBJ_GEOM,g),body=mujoco.mj_id2name(model,mujoco.mjtObj.mjOBJ_BODY,int(model.geom_bodyid[g])))
   f=float(abs(wrench[0]));
   if f>max_force:max_force=f;max_geom=ground
   for k,g in enumerate(tire_ids):
    if robot==g:count[k]+=1;normal_sum[k]+=f
   contacts.append([physics_index,g1,g2,float(c.dist),*c.pos.copy(),*c.frame.copy(),*wrench])
  rot=data.xmat[sim.chassis_id].reshape(3,3);upright=float(rot[2,2]);wheels=[float(data.qvel[sim.qvel[n]]) for n in ('left_wheel_spin','right_wheel_spin')]
  physics.append([float(data.time),*data.qpos[:3].copy(),*data.qvel[:6].copy(),upright,*wheels,*count,*normal_sum,ground_count,max_force,max_geom,*data.ctrl.copy(),*data.actuator_force.copy(),*data.actuator_velocity.copy()])
 mujoco.mj_step=instrumented
 for variant in ('auto','E0','W35'):
  for target in (.6,1.2):
   name=variant+'_vx_'+str(target).replace('.','p');sim.reset_route('flat_run');actual_policy.variant=variant;sim.select_skill(0);initial=np.r_[sim.data.qpos.copy(),sim.data.qvel.copy()];initial_SHA=hashlib.sha256(initial.tobytes()).hexdigest();physics=[];contacts=[];physics_index=0;rows=[];obs=[];logits=[];choice=[];qpos=[];qvel=[];actions=[];vx=0.;fault=None;boundary=None
   with torch.inference_mode():
    for i in range(500):
     vx+=float(np.clip(target-vx,-.008,.008));sim.command.vx=vx;sim.command.wz=0.;sim.step_control();health=sim.health();assert health['finite'];v=np.zeros(6);mujoco.mj_objectVelocity(sim.model,sim.data,mujoco.mjtObj.mjOBJ_XBODY,sim.chassis_id,v,1);last=actual_policy.last;rows.append([float(sim.data.time),vx,float(v[3]),health['upright_cos'],float(sim.base_position[2]),health['closure_error_m'],health['mimic_error_rad'],last['CUDA_reference_parity_error']]);obs.append(last['observation']);logits.append(last['logits']);choice.append([last['gate_choice'],last['choice']]);qpos.append(sim.data.qpos.copy());qvel.append(sim.data.qvel.copy());actions.append(sim.last_action.copy())
     if health['upright_cos']<.60 or sim.base_position[2]<.12:fault=dict(control=i+1,health=health);break
     if sim.base_position[0]>-5.5:boundary=dict(control=i+1,reason='Original flat route endpoint reached; later wall/terrain not included in small-curb classification');break
     assert time.monotonic()-start<600,'Finite contact experiment duration'
   path=O/(name+'.npz');np.savez_compressed(path,state=np.asarray(rows),observation=np.asarray(obs),logits=np.asarray(logits),choices=np.asarray(choice),qpos=np.asarray(qpos),qvel=np.asarray(qvel),action=np.asarray(actions),physics=np.asarray(physics,dtype=np.float64),contacts=np.asarray(contacts,dtype=np.float64).reshape(-1,22),initial_qpos_qvel=initial)
   r=np.asarray(rows);p=np.asarray(physics);ch=np.asarray(choice)[:,1];summary=dict(case=name,variant=variant,target_vx=target,controls=len(rows),physics_callbacks=len(physics),expected_callbacks=len(rows)*sim.decimation,initial_state_SHA=initial_SHA,fault=fault,route_endpoint_stop=boundary,max_root_z_m=float(p[:,3].max()),min_root_z_m=float(p[:,3].min()),max_root_upward_v_m_s=float(p[:,6].max()),max_contact_normal_force_N=float(p[:,18].max()),both_tire_no_contact_callbacks=int(((p[:,13]+p[:,14])==0).sum()),max_tilt_deg=float(np.degrees(np.arccos(np.clip(p[:,10].min(),-1,1)))),expert_switches=int((ch[1:]!=ch[:-1]).sum()),selected_expert_counts={'E0':int((ch==0).sum()),'W35':int((ch==1).sum())},max_CUDA_reference_parity_error=float(r[:,7].max()),artifact=dict(path=str(path),bytes=path.stat().st_size,SHA=H(path)),last_health=sim.health());assert summary['physics_callbacks']==summary['expected_callbacks'];put(name+'_COMPLETE.json',summary);cases.append(summary)
 assert len({x['initial_state_SHA'] for x in cases})==1
 assert all(torch.equal(w.cpu(),frozen[role][k]) for role,sd in actors.items() for k,w in sd.items())
 put('CONTACT_AND_PHYSICS_COLUMNS.json',dict(contact_columns=['physics_index','geom1','geom2','dist','posX','posY','posZ']+[f'frame{i}' for i in range(9)]+[f'local_wrench{i}' for i in range(6)],physics_columns=['time','x','y','z','vx','vy','vz','wx','wy','wz','upright','left_wheel_rad_s','right_wheel_rad_s','left_tire_contacts','right_tire_contacts','left_tire_normal_N','right_tire_normal_N','ground_contact_count','max_ground_normal_N','max_ground_geom']+[f'ctrl{i}' for i in range(6)]+[f'actuator_force{i}' for i in range(6)]+[f'actuator_velocity{i}' for i in range(6)],geometry_names=names,contact_scope='Actual mj_step followed by mj_contactForce readback at every0.5ms step, cached solver contact frame; no fresh mj_forward or force injection. Contacts and velocities may represent solver/integration stages; do not treat an approximate power integral as an exact energy proof.',no_contact_callback_missing=True))
 put('FINAL.json',dict(epoch=time.time(),passed_frozen_execution=True,cases=cases,all6_initial_physical_states_literal_SHA_equal=True,actor9_STD_unchanged=True,gate_not_updated=True,no_optimizer_training_or_budget_write=True,primary_MuJoCo_3_14_ORT_1_30_on_remote4090_host=True,no_local_simulation=True,not_exact_original_human_command_history=True,elapsed_seconds=time.monotonic()-start))
 print(json.dumps(dict(passed=True,cases=len(cases),faults=sum(x['fault'] is not None for x in cases))))
if __name__=='__main__':
 try:main()
 except BaseException:put('ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
