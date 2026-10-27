"""One NEW purpose: distinguish false imagined flight from a non-jumping policy.

Uses the already collected NEW91 500-control case only. No new physics,
rollout retry, GPU or training. One qualified91 model load for this purpose.
"""
from pathlib import Path
import os,sys,json,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;N=T/'MOD4_H1_FLAT05_MASK_AWARE_MIXED72_RESOURCE_V91_20261027';B=N/'payload';R=S/'reports'

def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)

def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 m=json.loads((R/'FROZEN91_CASE_FULL_TEXT_AND_NEW_RAW_TRANSFER_ACTUAL.json').read_bytes());rows={x['relative']:Path(x['local_path']) for x in m['rows']}
 actual=[json.loads(x) for x in rows['case/episode/ACTUAL_100HZ_CONTROLS.jsonl'].read_text('utf8').splitlines()]
 assert len(actual)==500
 q=json.loads((N/'reports/NATIVE91_FORMAL_NATIVE_FULLSTATE_INITIAL_CPU_AND_COST_ACTUAL.json').read_bytes());assert q['passed']
 put('NEW91_CLOSED_LOOP_CPU_PURPOSE_STARTED_ACTUAL.json',dict(epoch=time.time(),purpose='Match reconstructed observed policy then run exactly32 imagined closed-loop steps at ten fixed real starts; distinguish teacher-action accuracy from policy imagination exploitation',model=q['model'],one_new_purpose_model_load=True,no_old_model_raw_or_new_physics=True))
 import torch
 torch.set_num_threads(2);sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps'),str(B/'job0/runtime/isaac/mod4')]
 from native_flat_jump_adapter_v1 import OwnFlatJumpReference,OwnFlatJumpMdp,encode_frame
 from supermimic_wheel_leg_v3.networks import Policy,Critic
 from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel
 from supermimic_wheel_leg_v3.geometry import unflatten_state
 c=json.loads((B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json').read_bytes())
 provider=OwnFlatJumpReference(json.loads((B/'source/OWN_FLAT5CM_TASK_REFERENCE_SOURCE.json').read_bytes())).bind_named_order(c['expected_runtime_joint_names'],scope='source_CPU_fixture')
 mdp=OwnFlatJumpMdp(provider,json.loads((B/'job0/assets/import_contract.json').read_bytes()),json.loads((B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json').read_bytes()),c['actual_encoder_joint_names'])
 full=torch.load(q['model']['local_path'],map_location='cpu',weights_only=False);native=full['UniSuperMimic_H1_test'];args=native['args']
 assert native['iteration']==9256 and full['UniSuperMimic_publication']['policy_updates']==9000
 modules=dict(pi=Policy(86,1460,hist=10,z_dim=32,num_joints=6,hidden=args['policy_hidden']),wm=AugmentedWheelLegWorldModel(context_dim=31,hidden=args['wm_hidden'],num_joints=30,auxiliary_dim=54,action_dim=6),critic=Critic(1625,hidden=args['critic_hidden']))
 for name,module in modules.items():
  module.load_state_dict(native[name],strict=True);module.eval()
  for p in module.parameters():p.requires_grad_(False)
 histories=[];previous=[];history=torch.zeros(1,10,86);prev=torch.zeros(1,6);frame_rows=[];state_rows=[];xi_rows=[]
 with torch.inference_mode():
  for i,row in enumerate(actual):
   s=torch.tensor([row['packed127_for_action']],dtype=torch.float32);xi=torch.tensor([row['xi31_for_action']],dtype=torch.float32);f=torch.tensor(row['age_for_action'],dtype=torch.long)
   obs=mdp.obs(unflatten_state(s),prev,xi,f)
   history=obs[:,None].expand(-1,10,-1).clone() if i==0 else torch.cat((history[:,1:],obs[:,None]),1)
   histories.append(history.clone());previous.append(prev.clone());frame_rows.append(f);state_rows.append(s);xi_rows.append(xi)
   prev=torch.tensor([row['terminal_pre_reset']['state']['executed6']],dtype=torch.float32)
  results=[]
  for start in (160,180,192,200,208,216,224,240,260,300):
   state=unflatten_state(state_rows[start]);xi=xi_rows[start];normalized=mdp.normalize_context(xi);f=frame_rows[start].clone();hist=histories[start].clone();prev=previous[start].clone()
   reconstructed=modules['pi'](hist,mdp.goal(f,10));observed=torch.tensor([actual[start]['mean6']],dtype=torch.float32)
   control_error=(reconstructed-observed).abs().max().item();survival=torch.ones(1);reward_sum=torch.zeros(1);steps=[]
   for t in range(32):
    action=modules['pi'](hist,mdp.goal(f,10)).clamp(-6,6);state=modules['wm'].step(state,action,normalized);f=f+1
    terms=mdp.objective_terms(state,f,action,prev);reward=mdp.reward(state,f,action,prev)
    assert torch.equal(reward,terms['total']) # Same new objective dispatch, not a physical bitwise gate.
    survival=survival*(1-mdp.soft_termination(state,f));reward_sum+=args['gamma']**t*survival*reward
    geom=mdp.wheel_geometry(state)
    steps.append(dict(t=t+1,frame=int(f[0]),wheel_bottom_m=geom['low'][0,:,2].tolist(),root_z=float(state[0][0,2]),reward=float(reward[0]),action=action[0].tolist(),survival=float(survival[0])))
    obs=mdp.obs(state,action,xi,f);hist=torch.cat((hist[:,1:],obs[:,None]),1);prev=action
   critic_input=torch.cat((mdp.critic_features(state,f,normalized),mdp.goal(f,10)),-1);value=modules['critic'](critic_input)
   tail=args['gamma']**32*survival*value
   results.append(dict(start_control=start+1,start_age=int(frame_rows[start][0]),reconstructed_vs_actual_mean_max_abs=control_error,discounted_local_rewards=float(reward_sum[0]),terminal_value=float(value[0]),discounted_critic_tail=float(tail[0]),objective=float((reward_sum+tail)[0]),steps=steps))
  literal=all(set(module.state_dict())==set(native[name]) and all(torch.equal(v,native[name][k]) for k,v in module.state_dict().items()) for name,module in modules.items())
 assert literal and not torch.cuda.is_initialized()
 put('NEW91_SAME_REAL_CASE_CLOSED_LOOP_IMAGINATION_CPU_ACTUAL.json',dict(passed=True,results=results,goal_source_neutral_z=float(provider.neutral[2]),reward_dispatch_calls_current_flat_objective=True,all_native_parameters_normalizers_literal_unchanged=literal,no_optimizer_training_physics_or_GPU=True,actual_case_unchanged_no_new_episode=True,one_qualified91_model_load_this_purpose=True,CPU_vs_GPU_TF32_and_N1_scope_limit=True,not_unique_rootcause_or_global_gradient_accuracy_proof=True))
 print(json.dumps(dict(passed=True,source_objective_connected=True,max_reconstructed_action_error=max(x['reconstructed_vs_actual_mean_max_abs'] for x in results))))

if __name__=='__main__':
 try:main()
 except BaseException:put('NEW91_CLOSED_LOOP_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_blind_model_reload=True));raise
