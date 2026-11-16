"""Exercise real admitted data, retained actor and gradients without optimizer steps."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,torch
T=Path(__file__).resolve().parent;R=T.parents[2]
sys.path.insert(0,str(R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/runtime/core'))
from play_ppo_flatv1 import ActorMLP
from skill_supervision import SkillSupervision
keep=R/'deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt'
sha=hashlib.sha256(keep.read_bytes()).hexdigest();actor=ActorMLP()
actor.load_state_dict(torch.load(keep,map_location='cpu',weights_only=False)['actor_state_dict'],strict=False)
initial={k:v.clone()for k,v in actor.state_dict().items()}
teacher=SkillSupervision(actor.mlp,keep);x=teacher.obs[teacher.obs[:,-7]>.5][:64];mask=torch.ones(len(x))
loss=teacher.loss(actor,x,mask);assert float(loss['keep_loss'].detach())<1e-12
loss['loss'].backward();assert any(p.grad is not None and p.grad.abs().max()>0 for p in actor.parameters())
assert all(torch.isfinite(p.grad).all() for p in actor.parameters()if p.grad is not None)
assert all(p.grad is None for p in teacher.keep_teacher.parameters())
assert all(torch.equal(v,initial[k])for k,v in actor.state_dict().items())
assert hashlib.sha256(keep.read_bytes()).hexdigest()==sha
source_manifest=json.loads((T/'source_adapter/SOURCE_MANIFEST.json').read_text());source=Path(source_manifest['teacher_repository'])
assert all(hashlib.sha256((source/k).read_bytes()).hexdigest()==h for k,h in source_manifest['sha256'].items())
sys.path.insert(0,str(T/'source_adapter'));from play_wasd import SerialSimulation
sim=SerialSimulation('20 cm 单台阶');platform=sim.m.geom('local_step').id
assert abs(sim.d.geom_xpos[platform,2]+sim.m.geom_size[platform,2]-.2)<1e-9
for _ in range(20):sim.step(set())
sim.close()
result=dict(qualified_dataset_frames=len(teacher.obs),qualified_episodes=len(teacher.manifest['entries']),current_actor_unchanged=True,current_checkpoint_unchanged=True,frozen_keep_teacher_no_grad=True,gradient_finite=True,keep_loss=float(loss['keep_loss'].detach()),skill_loss=float(loss['skill_loss'].detach()),source_inputs_hashes_match=True,frozen_source_adapter_loaded=True,source_step_readback_m=.2,optimizer_steps=0,PPO_updates=0,actor_dim=35,critic_dim=78,action_dim=6)
(T/'PIPELINE_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
