"""Matched remote MuJoCo player comparison, with frozen actors/gate on CUDA."""
from pathlib import Path
import hashlib,json,os,sys,time,traceback,types
B=Path(__file__).resolve().parent;O=B/'out';O.mkdir();P=B/'player'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (O/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 import numpy as np,torch,mujoco
 import torch.nn.functional as F
 torch.set_num_threads(1);assert torch.cuda.is_available() and '4090' in torch.cuda.get_device_name(0)
 cfg=json.loads((B/'CONFIG.json').read_bytes());cp={}
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
  def __init__(self,path):self.path=Path(path);self.input_width=35;self.last=None
  def __call__(self,obs):
   x=torch.as_tensor(np.asarray(obs,dtype=np.float32).reshape(1,35),device='cuda:0');assert torch.isfinite(x).all() and x[0,28]==1 and x[0,29:35].abs().sum()==0
   logits=F.linear(F.elu(F.linear(F.elu(F.linear(x,gate['w1'],gate['b1'])),gate['w2'],gate['b2'])),gate['w3'],gate['b3'])
   options=torch.stack((actor(x,actors['E0']),actor(x,actors['W35'])),dim=1);gate_choice=int(logits.argmax(1).item());choice=gate_choice if self.variant=='auto' else 0 if self.variant=='E0' else 1
   raw=options[:,choice].clamp(-6,6);self.last=dict(observation=x[0].cpu().numpy(),logits=logits[0].cpu().numpy(),gate_choice=gate_choice,choice=choice,expert_actions=options[0].clamp(-6,6).cpu().numpy())
   return raw[0].cpu().numpy()
 stub=types.ModuleType('policy_runtime');stub.OnnxPolicy=FrozenCudaPolicy;sys.modules['policy_runtime']=stub;sys.path.insert(0,str(P));from rm7v7_moe_sim import RM7V7MoESim
 sim=RM7V7MoESim();actual_policy=sim.policy.base;assert isinstance(actual_policy,FrozenCudaPolicy)
 import subprocess
 compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
 own=[r for r in compute.splitlines() if len(r.split(','))>=2 and r.split(',')[1].strip()==str(os.getpid())];assert own and all(cfg['GPU_UUID'] in r for r in own)
 put('ACTUAL_CUDA_SOURCE_AND_PROTOCOL.json',dict(epoch=time.time(),pid=os.getpid(),own_GPU_compute_rows=own,device_name=torch.cuda.get_device_name(0),torch_version=torch.__version__,mujoco_version=mujoco.__version__,numpy_version=np.__version__,physics_backend='MuJoCo CPU physics on remote Linux host, same copied player XML/assets/adapter. Frozen policy inference CUDA on4090.',original_player_manifest=sim.delivery,protocol=cfg,original_gate_embedded_experts_literal_exact=True,no_optimizer=True,no_local_simulation=True))
 cases=[];start=time.monotonic()
 for variant in ('auto','E0','W35'):
  for target in (.3,.6,1.2,-.6):
   name=variant+'_vx_'+str(target).replace('-','minus').replace('.','p');sim.reset_route('flat_run');actual_policy.variant=variant;sim.select_skill(0);initial=np.r_[sim.data.qpos.copy(),sim.data.qvel.copy()];initial_SHA=hashlib.sha256(initial.tobytes()).hexdigest();rows=[];observations=[];logits=[];choices=[];qpos=[];qvel=[];actions=[];options=[];vx=0.;fault=None;previous=None;switches=0;action_jumps=[];first=sim.base_position.copy()
   with torch.inference_mode():
    for i in range(500):
     vx+=float(np.clip(target-vx,-.008,.008));sim.command.vx=vx;sim.command.wz=0.;sim.step_control();h=sim.health();assert h['finite'];v=np.zeros(6);mujoco.mj_objectVelocity(sim.model,sim.data,mujoco.mjtObj.mjOBJ_BODY,sim.chassis_id,v,1);a=sim.last_action.copy();last=actual_policy.last;choice=last['choice']
     switched=previous is not None and choice!=previous;switches+=int(switched)
     if actions and switched:action_jumps.append(float(np.linalg.norm(a-actions[-1])))
     previous=choice;rows.append([float(sim.data.time),vx,float(v[3]),h['upright_cos'],float(sim.base_position[2]),h['closure_error_m'],h['mimic_error_rad'],float(v[2])]);observations.append(last['observation']);logits.append(last['logits']);choices.append([last['gate_choice'],choice]);qpos.append(sim.data.qpos.copy());qvel.append(sim.data.qvel.copy());actions.append(a);options.append(last['expert_actions'])
     if h['upright_cos']<.60 or sim.base_position[2]<.12:fault=dict(control=i+1,health=h);break
     assert time.monotonic()-start<600,'Finite comparison duration limit'
   r=np.asarray(rows);n=len(rows);tail=r[max(0,n-100):];path=O/(name+'.npz');np.savez_compressed(path,state=r,observation=np.asarray(observations),logits=np.asarray(logits),choices=np.asarray(choices),qpos=np.asarray(qpos),qvel=np.asarray(qvel),action=np.asarray(actions),expert_actions=np.asarray(options),initial_qpos_qvel=initial)
   selected=np.asarray(choices)[:,1];delta=np.linalg.norm(np.diff(np.asarray(actions),axis=0),axis=1);summary=dict(case=name,variant=variant,target_vx=target,controls=n,sim_seconds=float(sim.data.time),initial_state_SHA=initial_SHA,delta_xyz=(sim.base_position-first).tolist(),tail_actual_vx_mean=float(tail[:,2].mean()),tail_abs_velocity_error_mean=float(np.abs(tail[:,2]-tail[:,1]).mean()),max_tilt_deg=float(np.degrees(np.arccos(np.clip(r[:,3].min(),-1,1)))),fault=fault,selected_expert_counts={'E0':int((selected==0).sum()),'W35':int((selected==1).sum())},expert_switches=switches,switched_action_delta_L2_max=max(action_jumps,default=0.),all_action_delta_L2_max=float(delta.max()) if len(delta) else 0.,last_health=sim.health(),artifact=dict(path=str(path),bytes=path.stat().st_size,SHA=H(path)));put(name+'_COMPLETE.json',summary);cases.append(summary)
 assert len({x['initial_state_SHA'] for x in cases})==1,'Comparison initial physical states not exact'
 assert all(torch.equal(w.cpu(),frozen[role][k]) for role,sd in actors.items() for k,w in sd.items())
 put('FINAL.json',dict(epoch=time.time(),passed_frozen_execution=True,cases=cases,all12_initial_physical_states_literal_SHA_equal=True,actor9_STD_unchanged=True,gate_not_updated=True,no_optimizer_training_or_budget_write=True,matched_backend_player_adapter=True,not_PhysX_or_skill_graduation=True,elapsed_seconds=time.monotonic()-start))
 print(json.dumps(dict(passed=True,cases=len(cases),faults=sum(x['fault'] is not None for x in cases))))
if __name__=='__main__':
 try:main()
 except BaseException:put('ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
