"""No optimizer steps: compare shared-actor drift, normal anchors and skill/keep gradients."""
from pathlib import Path
import sys,json,hashlib,math
import numpy as np,torch
D=Path(__file__).resolve().parent;T=D.parent;R=T.parents[2];sys.path.insert(0,str(R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/runtime/core'));from play_ppo_flatv1 import ActorMLP
torch.set_num_threads(1);torch.manual_seed(0)
def actor_at(f):
 ck=torch.load(f,map_location='cpu',weights_only=False);actor=ActorMLP();missing=actor.load_state_dict(ck['actor_state_dict'],strict=False);assert not missing.missing_keys;return actor,ck
parent,_=actor_at(T/'weights/parent_comprehensive.pt');parent.eval().requires_grad_(False)
a=np.load(T/'skill_dataset/qualified_mod4_skills.npz');sx=torch.from_numpy(a['obs']);sy=torch.from_numpy(a['actions']);sw=torch.from_numpy(a['sampling_weight']);normal_files=sorted((D/'parent_bank_r3/evaluation').glob('*_observations.npz'));normal_by_task={f.name.removesuffix('_observations.npz'):torch.from_numpy(np.load(f)['obs'])for f in normal_files};normal=torch.cat(list(normal_by_task.values()));assert torch.all(normal[:,-7:]==normal.new_tensor([1,0,0,0,0,0,0]))
with torch.no_grad():normal_target=parent(normal).clamp(-6,6)
results=[]
for name in ['parent_comprehensive','model_first_complete','model_005m','model_010m']:
 file=T/'weights'/(name+'.pt');model,ck=actor_at(file);params=list(model.parameters());original={k:v.detach().clone()for k,v in model.state_dict().items()}
 pred=model(sx).clamp(-6,6);skill=((pred-sy).square().sum(-1)*sw).sum();gskill=torch.cat([g.reshape(-1)for g in torch.autograd.grad(skill,params)])
 pred_n=model(normal).clamp(-6,6);keep=(pred_n-normal_target).square().sum(-1).mean();gkeep=torch.cat([g.reshape(-1)for g in torch.autograd.grad(keep,params)])
 dot=float(gskill@gkeep);ns=float(gskill.norm());nk=float(gkeep.norm());cos=dot/(ns*nk)if ns*nk>1e-15 else None
 with torch.no_grad():
  pred_n=model(normal).clamp(-6,6);delta=pred_n-normal_target;rmse=delta.square().mean(0).sqrt();per_task={}
  for task,x in normal_by_task.items():
   target=parent(x).clamp(-6,6);dif=model(x).clamp(-6,6)-target;per_task[task]=dict(samples=len(x),action_RMSE=dif.square().mean(0).sqrt().tolist(),action_abs_p95=torch.quantile(dif.abs(),.95,dim=0).tolist())
  # First bank frame for each task is identical physical state/commands used by parent.
  initial={task:dict(parent_action=parent(x[:1])[0].tolist(),student_action=model(x[:1])[0].tolist(),mode=x[0,-7:].tolist(),height_cmd=float(x[0,3]/5))for task,x in normal_by_task.items()}
  first_layer_delta=model.mlp[0].weight-parent.mlp[0].weight
  all_drift=math.sqrt(sum(float((v-parent.state_dict()[k]).square().sum())for k,v in model.state_dict().items()))
  # Counterfactual first-order change: direct auxiliary gradient effects on fixed normal loss.
  same_mode=sx.clone();same_mode[:,-7:]=same_mode.new_tensor([1,0,0,0,0,0,0]);mode_action_effect=float((model(sx).clamp(-6,6)-model(same_mode).clamp(-6,6)).square().mean().sqrt())
 assert all(torch.equal(v,original[k])for k,v in model.state_dict().items())
 row=dict(checkpoint=name,iteration=ck['iter'],sha256=hashlib.sha256(file.read_bytes()).hexdigest(),phase_balanced_skill_MSE_sum6=float(skill.detach()),fixed_normal_bank_keep_MSE_sum6=float(keep.detach()),gradient_skill_L2=ns,gradient_keep_L2=nk,skill_keep_gradient_dot=dot,skill_keep_gradient_cosine=cos,normal_loss_directional_derivative_minimize_skill=-dot,action_RMSE_per_motor=rmse.tolist(),implied_same_state_PD_torque_RMSE_Nm=(rmse*rmse.new_tensor([30,30,30,30,6,6])).tolist(),per_task=per_task,initial_actions=initial,shared_parameter_drift_L2=all_drift,first_layer_existing28_column_drift_L2=float(first_layer_delta[:,:28].norm()),first_layer_mode7_column_drift_L2=float(first_layer_delta[:,28:].norm()),mode_switch_action_effect_RMSE=mode_action_effect,optimizer_steps=0)
 results.append(row);print('GRADIENT_AUDIT',name,'skill',round(row['phase_balanced_skill_MSE_sum6'],4),'keep',round(row['fixed_normal_bank_keep_MSE_sum6'],4),'skillnorm',round(ns,3),'keepnorm',round(nk,3),'cos',cos,flush=True)
np.savez_compressed(D/'fixed_normal_observation_bank.npz',obs=normal.numpy(),target_actions=normal_target.numpy())
result=dict(actor_architecture='35-256-128-64-6 shared ELU MLP; no mode-specific heads',sampling='Exact phase-balanced skill weights; fixed c874 parent bank from3tasks1seed',normal_bank_samples=len(normal),teacher_frames=len(sx),rows=results,no_optimizer_steps=True,no_live_training_changes=True,not_actual_PPO_minibatch_gradient='PPO rollout minibatches not stored; do not claim measured dominance over the PPO gradient')
(D/'GRADIENT_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
