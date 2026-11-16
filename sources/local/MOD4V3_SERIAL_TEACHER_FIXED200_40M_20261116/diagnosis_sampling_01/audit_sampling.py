"""Audit frozen weights/labels and existing student rollouts; no collection/optimizer/training edits."""
from pathlib import Path
import json,hashlib,sys,datetime
import numpy as np,torch
D=Path(__file__).resolve().parent;T=D.parent;R=T.parents[2]
sys.path.insert(0,str(R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/runtime/core'));from play_ppo_flatv1 import ActorMLP
torch.set_num_threads(1);file=T/'skill_dataset/qualified_mod4_skills.npz';manifest=json.loads((T/'skill_dataset/MANIFEST.json').read_text());assert hashlib.sha256(file.read_bytes()).hexdigest()==manifest['sha256']
a=np.load(file);x=a['obs'];y=a['actions'];w=a['sampling_weight'];episode=a['episode'];group=a['phase_group'];masks={key:np.zeros(len(x),bool)for key in ['settle','cruise','contact_pre_lift','lift','swing','plant','capture','post','center205_218']};episodes=[]
for e,mm in enumerate([-60,-30,0,30,60]):
 inds=np.flatnonzero(episode==e);z=np.load(T/'teacher_collection'/f'start_{mm:+04d}mm/trace.npz');columns=list(z['columns']);tr=z['trace'];ph=z['phases'][:,0];first=int(np.flatnonzero((tr[:,columns.index('edge_l')]>0)|(tr[:,columns.index('edge_r')]>0)|(tr[:,columns.index('guide_force')]>5))[0]);lift=int(np.flatnonzero(ph=='lift')[0]);last=int(np.flatnonzero(ph!='idle')[-1]);local=np.arange(len(inds));prefix=local<first
 for key,mask in [('settle',prefix&(x[inds,0]==0)),('cruise',prefix&(x[inds,0]>0)),('contact_pre_lift',(local>=first)&(local<lift)),('post',local>last)]+[(p,ph==p)for p in ['lift','swing','plant','capture']]:masks[key][inds[mask]]=True
 episodes.append(dict(offset_mm=mm,first_contact_frame=first,first_lift_frame=lift,prelift_frames=lift-first,prelift_sampling_mass=float(w[inds[first:lift]].sum()),buckets=[int(((episode==e)&(group==g)).sum())for g in [0,1,2]],teacher_contact_prelift_pitch_peak_deg=float(np.rad2deg(np.arcsin(np.clip(x[inds[first:lift],7],-1,1))).__abs__().max()),teacher_all_pitch_peak_deg=float(np.rad2deg(np.arcsin(np.clip(x[inds,7],-1,1))).__abs__().max())))
 if e==2:masks['center205_218'][inds[205:219]]=True
buckets=[dict(bucket=g,frames=int((group==g).sum()),mass=float(w[group==g].sum()))for g in [0,1,2]];sampling={key:dict(frames=int(mask.sum()),mass=float(w[mask].sum()),expected_samples_per192=float(w[mask].sum()*192))for key,mask in masks.items()};models=[]
for name in ['model_005m','model_020m','model_025m','model_030m','model_035m','model_040m','model_final']:
 path=T/'weights'/(name+'.pt')
 if not path.exists():continue
 ck=torch.load(path,map_location='cpu',weights_only=False);model=ActorMLP();model.load_state_dict(ck['actor_state_dict'],strict=False)
 with torch.inference_mode():error=(model(torch.from_numpy(x)).clamp(-6,6).numpy()-y)**2
 errors={key:dict(per_action_MSE=float(error[mask].mean()),sum6_MSE=float(error[mask].sum(1).mean()),weighted_loss_contribution_sum6=float((error[mask].sum(1)*w[mask]).sum()),per_motor_MSE=error[mask].mean(0).tolist())for key,mask in masks.items()if mask.any()}
 row=dict(checkpoint=name,iteration=ck['iter'],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),semantic_errors=errors)
 rollout=T/'evidence/checkpoint_evals'/name/'single_step/start_+000mm/rollout.npz'
 if rollout.exists():
  z=np.load(rollout);prex=np.r_[0.,z['qpos'][:-1,0]];cross=np.flatnonzero(prex>=1.)
  if len(cross):
   i=int(cross[0]);near=(prex>=1.10)&(prex<=1.20);pitch=np.rad2deg(np.arcsin(np.clip(z['obs'][:,7],-1,1)));row['student_center']=dict(x_at_sample=float(prex[i]),frame=i,wheel_velocity_observation=z['obs'][i,20:22].tolist(),wheel_action=z['actions'][i,4:].tolist(),near_wall_pitch_peak_deg=float(np.abs(pitch[near]).max())if near.any()else None,observations_are_pre_action=True)
 models.append(row);print('MODEL',name,'critical',errors['center205_218']['per_action_MSE'],'cruise',errors['cruise']['per_action_MSE'],'post',errors['post']['per_action_MSE'],flush=True)
z=np.load(T/'teacher_collection/start_+000mm/observation_action_pairs.npz');i=int(np.flatnonzero(z['pre_qpos'][:,0]>=1.)[0]);teacher=dict(frame=i,x=float(z['pre_qpos'][i,0]),wheel_velocity_observation=z['obs'][i,20:22].tolist(),wheel_action=z['actions'][i,4:].tolist(),wheel_observation_scale=.1,wheel_actual_velocity_rad_s=(z['obs'][i,20:22]*10).tolist())
progress=json.loads((T/'evidence/training/LATEST_PROGRESS.json').read_text());closed={}
for name in ['FINAL.json','SAFE_CLOSED.json']:
 f=T/'evidence/training'/name
 if f.exists():closed[name]=json.loads(f.read_text())
result=dict(checked_at=datetime.datetime.now().astimezone().isoformat(),dataset_sha256=manifest['sha256'],original_sampling_unchanged=True,no_optimizer_steps=True,no_new_rollouts=True,buckets=buckets,episodes=episodes,sampling=sampling,teacher_center=teacher,models=models,training_readback=dict(iteration=progress['iteration'],elapsed_seconds=progress['training_elapsed_seconds'],course=progress['terrain']['single_step_curriculum'],losses=progress['losses']),closed=closed,interpretation_limits=['Static skill BC is one term of combined PPO+BC+retention; not a pureBC-only run','Teacher pitch8deg can occur in later skill phases; unsupported contact-state combinations are the coverage gap','No full PPO success does not mean zero shaped lift/progress reward','No new sampling percentages or added training budget are applied'])
(D/'AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');np.savez_compressed(D/'semantic_masks.npz',**masks)
print('SAMPLING',json.dumps(sampling));print('CLOSED',list(closed));print('AUDIT_READY')
