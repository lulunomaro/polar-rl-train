"""Frozen CPU audit: no PPO/optimizer updates and no changes to the running job."""
from pathlib import Path
import sys,json,time,hashlib,datetime
import numpy as np,torch,mujoco as mj
from torch import nn
D=Path(__file__).resolve().parent;T=D.parent;R=T.parents[2];sys.path[:0]=[str(T),str(T/'support')]
from mod4v3_ppo_v1.history_common import LocalHistoryActor,H
import evaluate_student200 as ev
torch.set_num_threads(1);torch.manual_seed(67)
def put(f,d):f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def array_metrics(a):return dict(mean=np.mean(a,axis=0).tolist(),minimum=np.min(a,axis=0).tolist(),maximum=np.max(a,axis=0).tolist())
def histories(obs):return np.stack([obs[np.maximum(0,np.arange(k-H+1,k+1))]for k in range(len(obs))]).astype(np.float32).reshape(len(obs),-1)
def replay_real_state():
 src=T/'evidence/checkpoint_evals/model_020m/single_step/start_+000mm/rollout.npz';a=np.load(src);dest=D/'state_reconstruction';dest.mkdir();xml,root,_=ev.model_xml(dest,.2)
 spec=ev.RobotSpec(**json.loads((ev.D/'runtime/core/template_spec.json').read_text())['spec']);runtime=json.loads((ev.PLANT/'runtime_config.json').read_text());default=ev._q_from_runtime(runtime,spec.joint_names);bank=json.loads((ev.D/'plant/reset_bank.json').read_text());sem=json.loads((ev.PLANT/'semantics.json').read_text());bq,bz=ev._q_from_bank(bank,sem,spec.joint_names);env=ev.Mod4v3Mujoco(str(xml),spec,default,bq,bz,action_clip=6.);m,d=env.m,env.d;m.opt.timestep=.0025
 ik=ev.Mod4Retarget();fit=ik.fit(np.sqrt(.3466**2+ik.lateral_offset**2),0.);d.qpos[:]=fit['qpos'];d.qpos[:3]=[0,0,.3466+.0625+.001];d.qpos[3:7]=[1,0,0,0];d.qvel[:]=0;mj.mj_forward(m,d)
 qa=np.array([m.jnt_qposadr[m.joint(n).id]for n in ev.NAMES])[ev.PPO_TO_NATIVE];va=np.array([m.jnt_dofadr[m.joint(n).id]for n in ev.NAMES])[ev.PPO_TO_NATIVE];tires=[m.geom(s+'_tire').id for s in ['left','right']];bodies=m.geom_bodyid[tires];platform=m.geom('native_teacher_platform').id
 def contact():
  force=np.zeros((2,3));platform_contact=np.zeros(2,bool)
  for j in range(d.ncon):
   c=d.contact[j];f=np.zeros(6);mj.mj_contactForce(m,d,j,f);world=np.asarray(c.frame).reshape(3,3).T@f[:3]
   for i,b in enumerate(bodies):
    if m.geom_bodyid[c.geom1]==b:force[i]-=world
    if m.geom_bodyid[c.geom2]==b:force[i]+=world
    if platform in (c.geom1,c.geom2)and b in(m.geom_bodyid[c.geom1],m.geom_bodyid[c.geom2])and f[0]>5:platform_contact[i]=True
  return np.linalg.norm(force,axis=1),platform_contact
 labels=[];q=[];v=[];contacts=[];peak=contact()[0];qerr=qdobs_error=0.
 for k,action in enumerate(a['actions']):
  rot=d.xmat[env.base_id].reshape(3,3);labels.append(np.r_[rot.T@d.qvel[:3],(peak>5.).astype(float)]);q.append(d.qpos[qa].copy());v.append(d.qvel[va].copy());contacts.append(contact()[1]);qdobs_error=max(qdobs_error,float(np.abs(d.qvel[va]*.1-a['obs'][k,16:22]).max()));force=[];at=torch.from_numpy(action[ev.PPO_TO_NATIVE]).reshape(1,6)
  for j in range(8):
   tau=env._torque(at).numpy().reshape(-1)
   if j%4==0:d.ctrl[env.act_ids[:4]]=tau[:4]
   d.ctrl[env.act_ids[4:]]=tau[4:];mj.mj_step(m,d)
   if j%2==1:force.append(contact()[0])
  peak=np.asarray(force[-3:]).max(0);qerr=max(qerr,float(np.abs(d.qpos-a['qpos'][k]).max()))
 assert qerr<1e-10 and qdobs_error<2e-6,(qerr,qdobs_error)
 result=dict(targets=np.asarray(labels,np.float32),actual_joint_pos=np.asarray(q),actual_joint_vel=np.asarray(v),platform_contact_pre=np.asarray(contacts),obs=a['obs'],history=histories(a['obs']),actions=a['actions'],trace=a['trace']);np.savez_compressed(D/'reconstructed_student20.npz',**result)
 return result,dict(source=str(src),max_replayed_qpos_error=qerr,max_pre_obs_joint_velocity_error=qdobs_error,frames=len(q),no_teacher_controller_instances=True,optimizer_updates=0,PPO_updates=0)
def counterfactual(actor,x,h,truth,selected):
 with torch.no_grad():
  z=actor.encoder(h);base=actor.mlp(torch.cat((x,z),-1)).clamp(-6,6);out={};ref=base[selected]
  variants={'zero_latent':torch.zeros_like(z),'oracle_vx_only':z.clone(),'oracle_all5':truth,'repeated_current_history':actor.encoder(x[:,None,:].repeat(1,12,1).flatten(1)),'shuffled_latent':z[torch.randperm(len(z))]}
  variants['oracle_vx_only'][:,0]=truth[:,0]
  for key,changed in variants.items():
   y=actor.mlp(torch.cat((x,changed),-1)).clamp(-6,6);delta=(y-base)[selected]
   out[key]=dict(action_abs_change_mean=delta.abs().mean().item(),action_abs_change_max=delta.abs().max().item(),signed_change_per_action=delta.mean(0).tolist(),mean_action=y[selected].mean(0).tolist())
  first=actor.mlp[0];c35=x@first.weight[:,:35].T;cz=z@first.weight[:,35:].T
  result=dict(estimated=array_metrics(z[selected].numpy()),physical_truth=array_metrics(truth[selected].numpy()),velocity_MAE_m_s=(z[selected,:3]-truth[selected,:3]).abs().mean(0).tolist(),actual_actions=array_metrics(ref.numpy()),latent_activation_norm_ratio=(cz[selected].norm(dim=-1)/(c35[selected].norm(dim=-1)+1e-9)).mean().item(),counterfactual=out)
 return result

def main():
 start=time.perf_counter();real,reconstruction=replay_real_state();raw=np.load(T/'skill_dataset/history_skills.npz');manifest=json.loads((T/'skill_dataset/MANIFEST.json').read_text());poolx=torch.from_numpy(raw['obs']);poolh=torch.from_numpy(raw['history']).flatten(1);pooly=torch.from_numpy(raw['actions']);pooltruth=torch.from_numpy(raw['targets']);rx=torch.from_numpy(real['obs']);rh=torch.from_numpy(real['history']);rt=torch.from_numpy(real['targets']);models={};report={};parent=torch.load(T/'weights/model_step000.pt',map_location='cpu',weights_only=False)
 for name in ['model_step000','model_010m','model_020m','model_040m']:
  path=T/'weights'/(name+'.pt');checkpoint=torch.load(path,map_location='cpu',weights_only=False);model=LocalHistoryActor().load_checkpoint(checkpoint).eval();models[name]=model
  with torch.no_grad():
   z=model.encoder(poolh);pred=model(poolx,poolh).clamp(-6,6);mse=(pred-pooly).square();segments={}
   for j,label in enumerate(manifest['semantic_names']):
    mask=raw['semantic_id']==j;segments[label]=dict(frames=int(mask.sum()),sum6_MSE=mse[mask].sum(-1).mean().item(),action_MAE_per_dimension=(pred[mask]-pooly[mask]).abs().mean(0).tolist(),rear_mean_absolute_error=(pred[mask][:,[1,3]]-pooly[mask][:,[1,3]]).abs().mean().item())
   W=checkpoint['actor_state_dict']['mlp.0.weight'];W0=parent['actor_state_dict']['mlp.0.weight'];mlpkeys=[k for k in checkpoint['actor_state_dict']if k.startswith('mlp.')];drift=torch.sqrt(sum((checkpoint['actor_state_dict'][k]-parent['actor_state_dict'][k]).square().sum()for k in mlpkeys));norm=torch.sqrt(sum(parent['actor_state_dict'][k].square().sum()for k in mlpkeys))
   report[name]=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),iteration=checkpoint['iter'],latent_column_norm=W[:,35:].norm().item(),original35_column_norm=W[:,:35].norm().item(),MLP_relative_parameter_drift=(drift/norm).item(),offline_teacher_velocity_MAE_m_s=(z[:,:3]-pooltruth[:,:3]).abs().mean(0).tolist(),offline_teacher_contact_accuracy=((z[:,3:]>.5)==(pooltruth[:,3:]>.5)).float().mean().item(),segments=segments)
   if name in ['model_020m','model_040m']:
    report[name]['on_frozen_student20_wall_states']=counterfactual(model,rx,rh,rt,np.arange(146,161));report[name]['on_frozen_student20_pre_wall']=counterfactual(model,rx,rh,rt,np.arange(100,146))
 # Exact prediction replay check: no new policy rollout is scored here.
 with torch.no_grad():
  exact=models['model_020m'](rx,rh).clamp(-6,6);prediction_error=float((exact-torch.from_numpy(real['actions'])).abs().max())
 # Teacher/user action comparison uses explicit windows, not falsely identical observations.
 S=R/'sources/local/MOD4V3_FIXED200_DAGGER_SEMANTIC_10M_20261116';oldmanifest=json.loads((S/'skill_dataset/MANIFEST.json').read_text());entry=next(e for e in oldmanifest['episodes']if e['source']=='nominal_teacher'and e['start_offset_mm']==0);teacher=np.load(Path(entry['result']).parent/'observation_action_pairs.npz');first=int(entry['first_contact_frame']);lift=int(entry['first_lift_frame']);teacher_actions=teacher['actions'][first:lift+1];student_actions=real['actions'][146:161]
 action_comparison=dict(teacher_window_frames=[first,lift],teacher_window_root='nominal center original source, contact to first lift, different observations from student',teacher_actions=array_metrics(teacher_actions),student_window_frames=[146,160],student_actions=array_metrics(student_actions),student_actual_joint_pos=array_metrics(real['actual_joint_pos'][146:161]),student_observation_joint_pos=array_metrics(real['obs'][146:161,10:14]),PPO_action_order=['LF','LR','RF','RR','WL','WR'])
 # Frozen BC/keep gradients. No optimizer.step and no fabricated PPO gradients.
 teacher_net=nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,6));frozen=torch.load(T/'comprehensive_keep_teacher.pt',map_location='cpu',weights_only=False);teacher_net.load_state_dict({k.removeprefix('mlp.'):v for k,v in frozen['actor_state_dict'].items()if k.startswith('mlp.')},strict=True);teacher_net.requires_grad_(False);normal=np.load(T/'normal_bank.npz');nx=torch.from_numpy(normal['obs']);nh=nx[:,None,:].repeat(1,12,1).flatten(1);ny=torch.from_numpy(normal['target_actions']);gradients={}
 critical=np.flatnonzero(np.isin(raw['semantic_id'],[3,4]));cruise=np.flatnonzero(raw['semantic_id']==1);prewall=np.flatnonzero(raw['origin']==1)
 for name in ['model_020m','model_040m']:
  model=models[name];params=list(model.mlp.parameters());vecs={};losses={};newnorms={};rng=np.random.default_rng(67)
  banks={'critical_contact_lift':rng.choice(critical,1024,replace=True),'cruise':rng.choice(cruise,1024,replace=True),'prewall_recovery':rng.choice(prewall,1024,replace=True),'whole_weighted_skill':rng.choice(len(poolx),1024,replace=True,p=raw['sampling_weight'].astype(float)/raw['sampling_weight'].sum())}
  for label,ids in banks.items():
   y=model(poolx[ids],poolh[ids]).clamp(-6,6);loss=(y-pooly[ids]).square().sum(-1).mean();g=torch.autograd.grad(loss,params);vecs[label]=torch.cat([v.flatten()for v in g]).detach();losses[label]=float(loss.detach());newnorms[label]=g[0][:,35:].norm().item()
  keep=(model(nx,nh).clamp(-6,6)-ny).square().sum(-1).mean();g=torch.autograd.grad(keep,params);vecs['normal_keep_reset_history']=torch.cat([v.flatten()for v in g]);losses['normal_keep_reset_history']=float(keep.detach());newnorms['normal_keep_reset_history']=g[0][:,35:].norm().item()
  ids=banks['prewall_recovery'];normalx=poolx[ids].clone();normalx[:,28:35]=normalx.new_tensor([1,0,0,0,0,0,0])
  with torch.no_grad():paired_target=teacher_net(normalx).clamp(-6,6)
  pair=(model(poolx[ids],poolh[ids]).clamp(-6,6)-paired_target).square().sum(-1).mean();g=torch.autograd.grad(pair,params);vecs['paired_stair_prewall']=torch.cat([v.flatten()for v in g]);losses['paired_stair_prewall']=float(pair.detach());newnorms['paired_stair_prewall']=g[0][:,35:].norm().item()
  cos={}
  for label in ['cruise','prewall_recovery','normal_keep_reset_history','paired_stair_prewall']:
   u=vecs['critical_contact_lift'];v=vecs[label];cos['critical_vs_'+label]=float(torch.dot(u,v)/(u.norm()*v.norm()+1e-12))
  gradients[name]=dict(losses=losses,norms={k:v.norm().item()for k,v in vecs.items()},new_latent_column_gradient_norms=newnorms,cosines=cos,actual_PPO_gradient_measured=False,scope='fixed1024 CPU banks; normal keep uses repeated-frame reset history; paired target sampled at same physical prewall observations; not actual on-policy minibatch')
 # Mathematical demonstration: small objective scalar does not imply small gradient.
 theta=torch.zeros((),requires_grad=True);A=torch.tensor([1.,-1.]);feature=torch.tensor([1.,-1.]);ratio=torch.exp(theta*feature);loss=torch.maximum(-A*ratio,-A*ratio.clamp(.9,1.1)).mean();derivative=torch.autograd.grad(loss,theta)[0]
 live=json.loads((T/'evidence/training/LATEST_PROGRESS.json').read_text());course=live.get('terrain',{}).get('single_step_curriculum',{});protected=json.loads((T/'evidence/PROTECTED_INPUTS.json').read_text());unchanged=all(hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256']for row in protected)
 final=dict(date=datetime.datetime.now().astimezone().isoformat(),PPO_updates=0,optimizer_updates=0,running_training_modified=False,teacher_assistance_in_student_scoring=False,reconstruction=reconstruction,student20_prediction_reproduction_error=prediction_error,action_comparison=action_comparison,models=report,offline_gradients=gradients,encoder_loss_formula='online velocity MSE + .5 online contact MSE + .5 offline velocity MSE + .25 offline contact MSE; not velocity MAE',surrogate_math_counterexample=dict(objective=float(loss.detach()),gradient=float(derivative)),actual_PPO_gradient_logged=False,live=dict(epoch=live['epoch'],iteration=live['iteration'],training_elapsed_seconds=live['training_elapsed_seconds'],losses=live['losses'],course=course),all_protected_inputs_unchanged=unchanged,wall_seconds=time.perf_counter()-start)
 put(D/'RESULT.json',final);print('FROZEN_AUDIT_COMPLETE',json.dumps(dict(reconstruction=reconstruction,prediction_error=prediction_error,wall_seconds=final['wall_seconds'],protected=unchanged)))
 for name in ['model_020m','model_040m']:
  v=report[name]['on_frozen_student20_wall_states'];print(name,'LATENT_ABLATION',json.dumps(dict(norm_ratio=v['latent_activation_norm_ratio'],velocity_MAE=v['velocity_MAE_m_s'],actual_actions=v['actual_actions'],variants=v['counterfactual']),ensure_ascii=False));print(name,'GRADIENTS',json.dumps(gradients[name],ensure_ascii=False))
if __name__=='__main__':main()
