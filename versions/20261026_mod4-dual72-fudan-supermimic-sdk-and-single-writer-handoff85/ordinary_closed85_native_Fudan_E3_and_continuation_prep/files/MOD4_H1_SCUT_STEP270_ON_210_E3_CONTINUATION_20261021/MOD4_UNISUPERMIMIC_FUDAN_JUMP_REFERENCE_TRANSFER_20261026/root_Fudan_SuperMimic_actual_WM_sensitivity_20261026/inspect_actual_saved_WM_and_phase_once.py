"""NEW debugging purpose: one CPU load, WM sensitivity only, no policy forward."""
from pathlib import Path
import ast,json,sys,time,traceback
import torch

HERE=Path(__file__).resolve().parent;T=HERE.parent.parent
N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026'
S=N/'payloads/e2/source';sys.path.insert(0,str(S))
from supermimic_vendor_v2.geometry import invariant_features
from supermimic_vendor_v2.networks import WorldModel
from supermimic_reference_adapter_v1 import read_json_reference,PartialReferenceImitationMdp

def summary(x):
 x=x.detach().float().flatten()
 return dict(n=x.numel(),min=float(x.min()),median=float(x.median()),mean=float(x.mean()),max=float(x.max()))

def main():
 torch.set_num_threads(4)
 intent=HERE/'NEW_PURPOSE_CPU_MODEL_READ_INTENT_ACTUAL.json'
 assert not intent.exists()
 model=N/'current_native_H1_method_fullstate/e2/native_supermimic_H1_final.pt'
 assert model.stat().st_size==140492265
 intent.write_text(json.dumps(dict(epoch=time.time(),purpose='User explicitly requests investigate why actual Fudan native85 has zero takeoff despite policy updates. Missing evidence is actual learned WM action sensitivity and latest retained phase exposure.',scope='one local CPU load of already transferred formal native85 FINAL; no requalification/old once/hash/raw/foreign model/policy forward/GPU/physics/remote call',producer_SHA='94e7f272176b4a7c485b50c1ac61f95a3ecd4460ee6a73034f9e7a47a57045af',no_checkpoint_edits=True,no_training=True),indent=2),'utf8')
 ck=torch.load(model,map_location='cpu',weights_only=False)
 native=ck['UniSuperMimic_H1_test'];args=native['args']
 assert native['iteration']==68
 phase=ck['H1_step270_task_state']['phase']['tensors']
 age=phase['age_control'].detach().cpu()
 hist=ck['UniSuperMimic_obs_history'].detach().cpu()
 assert hist.shape==(20000,10,128)
 ep=ck['UniSuperMimic_bridge_ep_step'].detach().cpu()
 actual=dict(age=summary(age),bridge_episode_step=summary(ep),
             age_before_request=int((age<100).sum()),age_in_public_request_100_to179=int(((age>=100)&(age<180)).sum()),age_after_request=int((age>=180).sum()),
             latest_cached_z=summary(hist[:,-1,0]),latest_cached_Rzz=summary(torch.linalg.cross(hist[:,-1,1:7].reshape(-1,3,2)[:,:,0],hist[:,-1,1:7].reshape(-1,3,2)[:,:,1],dim=-1)[:,2]),
             latest_cached_normalized_request=summary(hist[:,-1,127]),
             phase_field_summaries={k:summary(v) for k,v in phase.items() if torch.is_tensor(v) and v.numel()==20000 and k in ('request_for_action','request','age_control')},
             scope='single final retained snapshot and latest cached preaction history only; not whole-window age/reset/exposure rates')
 (HERE/'PARTIAL_ONE_LOAD_PHASE_AND_SCHEMA_BEFORE_WM_CPU_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),native_iteration=native['iteration'],publication_world_updates=ck['UniSuperMimic_publication']['world_updates'],actual=actual),indent=2),'utf8')
 wm=WorldModel(hidden=tuple(args['wm_hidden']),num_joints=30,context_dim=49,action_dim=6)
 wm.load_state_dict(native['wm'],strict=True);wm.eval()
 for v in wm.parameters():v.requires_grad_(False)
 ids=torch.unique(torch.cat((torch.linspace(0,19999,32).long(),torch.nonzero((age>=100)&(age<180)).flatten()[:16],torch.nonzero(age>=136).flatten()[:16])))
 obs=hist[ids,-1].clone()
 first=obs[:,1:7].reshape(-1,3,2)
 c0=torch.nn.functional.normalize(first[:,:,0],dim=-1)
 c1=torch.nn.functional.normalize(first[:,:,1]-(first[:,:,1]*c0).sum(-1,keepdim=True)*c0,dim=-1)
 rot=torch.stack((c0,c1,torch.linalg.cross(c0,c1,dim=-1)),-1)
 pos=torch.stack((torch.zeros(len(ids)),torch.zeros(len(ids)),obs[:,0]),-1)
 velocity=(rot@obs[:,7:10,None]).squeeze(-1)
 angular=(rot@obs[:,10:13,None]).squeeze(-1)
 state=(pos,rot,velocity,angular,obs[:,13:43],obs[:,43:73])
 context=obs[:,79:128]
 action=obs[:,73:79].clamp(-6,6).clone().requires_grad_(True)
 pred=wm.step(state,action,context)
 z_jac=torch.autograd.grad(pred[0][:,2].sum(),action,retain_graph=True)[0]
 vz_jac=torch.autograd.grad(pred[2][:,2].sum(),action,retain_graph=True)[0]
 q0_jac=torch.autograd.grad(pred[4][:,0].sum(),action,retain_graph=True)[0]
 ns={'torch':torch,'invariant_features':invariant_features}
 cls=next(v for v in ast.parse((S/'h1_supermimic_bridge_v1.py').read_text('utf8')).body if isinstance(v,ast.ClassDef) and v.name=='H1GoalMdp')
 exec(compile(ast.Module(body=[cls],type_ignores=[]),'<actual H1GoalMdp>','exec'),ns)
 ref=read_json_reference(N/'payloads/e2/reference/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json')
 mapping=json.loads((N/'current_three_closed_text/e2/job0/production/NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json').read_bytes())
 ref=ref.for_offline_joint_order(mapping['actual_robot_joint_names'])
 provider=ref.torch_provider('cpu',offline_cpu_only=True)
 mdp=PartialReferenceImitationMdp(ns['H1GoalMdp'](provider.states[0,13:43],ref.metadata['partial_phase_contract']['own_task_nominal_chassis_height_m']),provider)
 frames=(age[ids]-1).clamp_min(0).int()+1
 terms=mdp.objective_terms(pred,frames,action,obs[:,73:79])
 task=terms['own_task_forward']*terms['own_task_landing_alignment']*terms['upright']*terms['demo_alignment']
 task_jac=torch.autograd.grad(task.sum(),action,retain_graph=True)[0]
 reg_jac=torch.autograd.grad(terms['regularization'].sum(),action,retain_graph=True)[0]
 eps=.05
 with torch.no_grad():
  fd=[]
  for k in range(6):
   perturb=torch.zeros_like(action);perturb[:,k]=eps
   fd.append((wm.step(state,action+perturb,context)[0][:,2]-wm.step(state,action-perturb,context)[0][:,2])/(2*eps))
  fd=torch.stack(fd,-1)
 records=[dict(env=int(ids[k]),age=int(age[ids[k]]),cached_z=float(pos[k,2]),cached_normalized_request=float(context[k,-1]),
               d_next_z_d_action=z_jac[k].tolist(),d_next_vz_d_action=vz_jac[k].tolist(),d_next_joint0_d_action=q0_jac[k].tolist(),
               task_only_reward_action_gradient=task_jac[k].tolist(),regularization_action_gradient=reg_jac[k].tolist()) for k in range(len(ids))]
 result=dict(epoch=time.time(),status='ACTUAL_NATIVE85_WM_CPU_SENSITIVITY_AND_FINAL_PHASE_ONLY',actual_final_snapshot=actual,
             selected_env_count=len(ids),d_next_z_d_action_abs=summary(z_jac.abs()),d_next_vz_d_action_abs=summary(vz_jac.abs()),
             d_next_joint0_d_action_abs=summary(q0_jac.abs()),task_reward_gradient_abs=summary(task_jac.abs()),regularization_gradient_abs=summary(reg_jac.abs()),
             finite_difference_z_abs_error=summary((fd-z_jac.detach()).abs()),records=records,
             reconstruction='heading-neutral equivalence from actual cached invariant obs; worldXY set0 because absent, absolute yaw unavailable. normalized context used directly without atanh/double tanh.',
             action_probe='latest cached previous action, not claimed future executed action; no policy forward',
             frames_scope='saved age_control used as next-frame proxy for latest preaction obs; reset/callback alignment not exactly reconstructed',
             limitations=['nonzero WM/reward Jacobian proves mathematical responsiveness at these probes only, not correct real-world gradient or jump convergence',
                          'no matched real next-state or heldout transition was reread; no action-Jacobian groundtruth/sign accuracy claim',
                          'current retained age/request snapshot cannot reconstruct whole-window ages or reset counts',
                          'this does not rerun or alter the consumed model qualification review, FINAL producer, source model, or original fees'],
             no_actor_or_critic_forward=True,no_native_policy_inference=True,no_physics_or_GPU_or_remote=True,model_loaded_once_for_new_user_debug_purpose=True)
 (HERE/'ACTUAL_SAVED_NATIVE85_WM_SENSITIVITY_AND_PHASE_CPU.json').write_text(json.dumps(result,indent=2),'utf8')
 print(json.dumps({k:v for k,v in result.items() if k not in ('records',)},ensure_ascii=False))

if __name__=='__main__':
 try:main()
 except BaseException:
  (HERE/('ORIGINAL_CPU_DEBUG_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps({'error':traceback.format_exc(),'no_training_or_checkpoint_modification':True},indent=2),'utf8')
  raise
