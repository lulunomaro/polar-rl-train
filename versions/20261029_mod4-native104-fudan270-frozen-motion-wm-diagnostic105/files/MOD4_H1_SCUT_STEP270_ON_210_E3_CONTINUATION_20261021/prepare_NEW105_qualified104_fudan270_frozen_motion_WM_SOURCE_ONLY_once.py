from pathlib import Path
import ast,hashlib,json,time,traceback
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';OLD=T/'H1_NATIVE97_FLAT_FROZEN_MOTION_WM_N1_V98_20261028';S=T/'H1_NATIVE104_FUDAN270_FROZEN_MOTION_WM_N1_V105_20261029';N=T/'MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028';B=N/'payloads_v4/seed27'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
def replace(s,a,b,n=1):
 assert s.count(a)==n,(a,s.count(a),n)
 return s.replace(a,b)
def main():
 assert not S.exists();S.mkdir();(S/'code').mkdir();(S/'reports').mkdir()
 changes={}
 for name in ['flat98_eval_contract_v1.py','flat98_eval_environment_v1.py','flat98_frozen_diag_driver_v1.py','run_native98_frozen_flat_WM_N1_once.py']:
  raw=(OLD/'code'/name).read_text(encoding='utf8');s=raw.replace('flat98','fudan105').replace('native98','native105').replace('NEW98','NEW105').replace('qualified97','qualified104').replace('original97','original104')
  if name=='flat98_frozen_diag_driver_v1.py':
   s=replace(s,'wm,flat_counter):','wm,critic,model_args,original_counter):')
   s=replace(s,"from native_flat_jump_adapter_v1 import encode_frame","from private_phase_frame_v1 import encode as encode_frame")
   s=replace(s,"before={k:v.detach().cpu().clone() for k,v in pi.state_dict().items()}","before={k:v.detach().cpu().clone() for k,v in pi.state_dict().items()}\n critic_before={k:v.detach().cpu().clone() for k,v in critic.state_dict().items()}")
   s=replace(s,"paired.append((s.clone(),xi.clone(),last['executed6'][None].clone(),s1.clone(),frames.clone()))","paired.append((s.clone(),xi.clone(),last['executed6'][None].clone(),s1.clone(),frames.clone(),history.clone(),previous.clone()))\n     original_counter.record(last)\n     value,known=bridge.mdp.provider.query(frames)\n     from flat91_mask_aware_goal_conditioning_v1 import masked_goal_conditioning\n     conditioned=masked_goal_conditioning(pi.goal_norm(goal),goal)\n     p0,R0,_,_,_,_,aux0=unflatten_state(s1)\n     sagittal=(R0.transpose(-1,-2).unsqueeze(-3)@(actual_geometry['centre']-p0.unsqueeze(-2)).unsqueeze(-1)).squeeze(-1)-bridge.mdp.hip_anchors\n     diagnostics=dict(goal_value73=value[0],goal_mask73=known[0],actor_conditioned1460=conditioned[0],virtual_leg_length2=sagittal[...,[0,2]].norm(dim=-1)[0],virtual_leg_angle2=torch.atan2(sagittal[...,0],-sagittal[...,2])[0],actual_contact_force_z2=torch.maximum(aux0[...,:18].reshape(1,3,2,3)[:,0,:,2],aux0[...,:18].reshape(1,3,2,3)[:,1,:,2])[0],fudan_contact_step_modes=objective['contact_step_modes'],raw_original_command3=e.command_manager.get_term('twist').command[0].clone())")
   s=replace(s,"actual_ownwheel_V2_objective=objective,","actual_Fudan270_objective=objective,own_actual_goal_contact_geometry=diagnostics,")
   s=replace(s,"status['flat_real_physics_events']=flat_counter.snapshot()","status['original270_terminal_physics_events']=original_counter.snapshot()")
   s=replace(s,"frozen_WM_prediction_diagnostic=True,","frozen_WM_prediction_diagnostic=True,actual_Fudan270_target=True,")
   s=replace(s,"from supermimic_wheel_leg_v3.geometry import unflatten_state as unpack","from supermimic_wheel_leg_v3.geometry import unflatten_state as unpack")
   needle=" require(literal(pi.state_dict(),before) and literal(wm.state_dict(),wm_before),'frozen model or normalizers changed')\n return status"
   addition=''' # First-action sensitivity uses frozen models and the original32-step native
 # imagined reward/soft-done/critic form. It is NOT a policy parameter gradient,
 # learner update, physical counterfactual, or a new mechanical success test.
 sensitivity=[]
 for start in (0,160,184,192,200,208,216,240):
  if start>=len(paired):continue
  row=paired[start]
  with torch.inference_mode(False),torch.enable_grad():
   state=unpack(row[0].detach().clone());context=row[1].detach().clone();frames=row[4].detach().clone();hist=row[5].detach().clone();previous=row[6].detach().clone();normal=bridge.mdp.normalize_context(context)
   action0=pi(hist,bridge.mdp.goal(frames,10)).clamp(-6,6).detach().requires_grad_(True)
   reward_objective=action0.sum()*0;survival=action0.new_ones((1,));gamma=float(model_args['gamma']);rows=[]
   for h in range(32):
    action=action0 if h==0 else pi(hist,bridge.mdp.goal(frames,10)).clamp(-6,6)
    state=wm.step(state,action,normal);frames=frames+1
    terms=bridge.mdp.objective_terms(state,frames,action,previous);reward=terms['total'];done=bridge.mdp.soft_termination(state,frames)
    reward_objective=reward_objective+(gamma**h)*survival*reward;survival=survival*(1-done)
    geometry=bridge.mdp.wheel_geometry(state)
    rows.append(dict(offset=h+1,frame=json_value(frames),root_xyz=json_value(state[0]),wheel_bottom2=json_value(geometry['low'][...,2]),reward=json_value(reward),soft_done=json_value(done),contact_step_modes=json_value(terms['contact_step_modes'])))
    obs=bridge.mdp.add_noise(bridge.mdp.obs(state,action,context,frames));hist=torch.cat((hist[:,1:],obs.unsqueeze(1)),1);previous=action
   tail=action0.sum()*0
   if not model_args['no_critic']:
    goal=bridge.mdp.goal(frames,10);features=bridge.mdp.critic_features(state,frames,normal);tail=(gamma**32)*survival*critic(torch.cat((features,goal),-1))
   gr=torch.autograd.grad(reward_objective.sum(),action0,retain_graph=True)[0]
   gt=torch.autograd.grad(tail.sum(),action0)[0]
   sensitivity.append(dict(start_control=start+1,initial_frame=json_value(row[4]),reward_objective=json_value(reward_objective),critic_tail=json_value(tail),first_action_reward_gradient6=json_value(gr),first_action_critic_tail_gradient6=json_value(gt),all_values_finite=bool(torch.isfinite(gr).all() and torch.isfinite(gt).all()),predicted32=rows))
 with (out/'FROZEN_FUDAN270_32STEP_FIRST_ACTION_SENSITIVITY_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(rows=sensitivity,only_frozen_first_action_derivative=True,all_physical_controls_finished_before_imagination=True,no_policy_or_optimizer_step=True,noise_draws_in_imagination_not_same_training_RNG_replay=True,not_causal_or_mechanical_proof=True),f,indent=2,allow_nan=False)
 require(literal(pi.state_dict(),before) and literal(wm.state_dict(),wm_before) and literal(critic.state_dict(),critic_before),'frozen model or normalizers changed')
 return status'''
   s=replace(s,needle,addition)
  if name=='run_native98_frozen_flat_WM_N1_once.py':
   s=replace(s,'MOD4_H1_FLAT97_FROZEN_MOTION_WM_DIAG_','MOD4_H1_NATIVE104_FUDAN270_FROZEN_MOTION_WM_DIAG_')
   s=replace(s,'6b3c8e9ddb56cac053e7ab386a4ec89723b799a6d4147f65232ad1e889824074','764129c1b4c9ec4560d83423856e9f4f5867f8f18c841215f43ed5552415b89c')
   s=replace(s,'256231497','256232841')
   old="gpu='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(',');users=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)\n  require(line[0].strip()==gpu and '4090' in line[1] and int(line[2])>15669 and gpu not in users,'fresh unused disjoint c27, leave foreign tasks alone')"
   new="gpu='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',');users=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)\n  require(line[0].strip()==gpu and '4090' in line[1] and int(line[2])>15669 and int(line[3])<=30,'user-authorized light occupation with original VRAM headroom')\n  put(out,'FRESH_USER_LIGHT_GPU_RESOURCE_ACTUAL.json',dict(line=line,compute_UUID_rows=users.splitlines(),no_unknown_PID_read=True,policy=q['resource_policy']))"
   s=replace(s,old,new)
   s=replace(s,"OWN_E2_H1_KIND='FROZEN_NATIVE97_FLAT_MOTION_WM_DIAGNOSTIC'","OWN_E2_H1_KIND='FROZEN_NATIVE104_FUDAN270_MOTION_WM_DIAGNOSTIC'")
   s=replace(s,"   cfg.terminations.mimic.params={**cfg.terminations.mimic.params,'threshold':.01};return cfg","   return cfg")
   s=replace(s,'from native_flat_jump_bridge_v2_original_support import FlatWheelLegBridge,install_flat_real_counter,install_stationary_flat_command','from native_fudan_step_bridge_v1 import FudanStepBridge,install_fudan_step_request_and_command')
   s=replace(s,'from native_flat_jump_adapter_v1 import OwnFlatJumpReference,OwnFlatJumpMdp','from native_fudan_step_adapter_candidate_v2 import OwnFudanStepReference,OwnFudanStepMdp')
   s=replace(s,'from supermimic_wheel_leg_v3.networks import Policy','from supermimic_wheel_leg_v3.networks import Policy,Critic')
   s=replace(s,"provider=OwnFlatJumpReference(read(B/'source/OWN_FLAT5CM_TASK_REFERENCE_SOURCE.json'),env.device)","provider=OwnFudanStepReference(read(B/'source/OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json'),env.device)")
   s=replace(s,'mdp=OwnFlatJumpMdp(provider,','mdp=OwnFudanStepMdp(provider,')
   s=replace(s,'command=install_stationary_flat_command(env);counter,floor=install_flat_real_counter(env)','command=install_fudan_step_request_and_command(env)\n  class OriginalCounter:\n   def __init__(self):self.last=None\n   def record(self,state):self.last=state\n   def snapshot(self):return dict(actual_terminal_before_autoreset=None if self.last is None else {k:self.last[k] for k in (\'takeoff_count\',\'landing_count\',\'recovery_count\',\'success\',\'stable_callback_ticks\')},one_episode_only=True,original270_counter_unchanged=True)\n  counter=OriginalCounter()')
   s=replace(s,'bridge=FlatWheelLegBridge(','bridge=FudanStepBridge(')
   s=replace(s,'flat_floor=floor,','actual_Fudan270_task=True,')
   s=replace(s,"native['iteration']==12066 and publication['world_updates']==120660 and publication['policy_updates']==11682","native['iteration']==16063 and publication['world_updates']==160630 and publication['policy_updates']==15487")
   s=replace(s,"   wm=AugmentedWheelLegWorldModel(context_dim=31,hidden=native['args']['wm_hidden'],num_joints=30,auxiliary_dim=54,action_dim=6)","   wm=AugmentedWheelLegWorldModel(context_dim=31,hidden=native['args']['wm_hidden'],num_joints=30,auxiliary_dim=54,action_dim=6)\n   critic=Critic(1625,hidden=native['args']['critic_hidden'])")
   s=replace(s,"[(pi,'pi'),(wm,'wm')]","[(pi,'pi'),(wm,'wm'),(critic,'critic')]")
   s=replace(s,'wm=wm,flat_counter=counter)','wm=wm,critic=critic,model_args=native[\'args\'],original_counter=counter)')
  dest=S/'code'/name.replace('flat98','fudan105').replace('native98','native105')
  ast.parse(s);dest.write_text(s,encoding='utf8');changes[name]=dict(original_source_path=str(OLD/'code'/name),old_source_SHA=H(OLD/'code'/name),new_source_path=str(dest),new_source_SHA=H(dest))
 # The coordinator remains a new frozen-case purpose, not a learning controller.
 s=(OLD/'run_NEW98_qualified97_fixed_motion_WM_case_once.py').read_text(encoding='utf8')
 s=s.replace('NEW98','NEW105').replace('FROZEN98','FROZEN105').replace('native98','native105').replace('qualified97','qualified104').replace('97 formal','104 formal')
 s=replace(s,"N=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028'","N=T/'MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028'")
 s=replace(s,"ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT97_FROZEN_MOTION_WM_DIAG_20261028r1'","ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_NATIVE104_FUDAN270_FROZEN_MOTION_WM_DIAG_20261029r1'")
 s=replace(s," if d.suffix.lower() in ('.pt','.pth','.npz'):continue"," if d.suffix.lower() in ('.pt','.pth'):continue\n if d.suffix.lower()=='.npz':\n  d.parent.mkdir(parents=True,exist_ok=True);os.link(src,d);assert os.path.samestat(src.stat(),d.stat());continue")
 s=replace(s,'import json,shutil,hashlib','import json,shutil,hashlib,os')
 s=replace(s,"cpu=L/'TWO97_NEW_H1_NATIVE_FORMAL_INITIAL_CPU_SOURCE_V1/reports/NATIVE97_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json'","cpu=L/'TWO104_FUDAN270_CLOSING_INITIAL_CPU_SCHEMA_REPAIRED_SOURCE_V3/reports/NATIVE103_seed27_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json'")
 s=replace(s,"L/'TWO97_correct_normal900_dual_native_PPO_collector_source_v1/reports/TWO97_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json'","L/'TWO104_FUDAN270_CLOSING_INITIAL_CPU_SCHEMA_REPAIRED_SOURCE_V3/reports/TWO103_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_V2_ACTUAL.json'")
 s=replace(s,"prep=json.loads((N/'reports/NATIVE97_DIAGNOSTIC_IO_SOURCE_PREPARED_ACTUAL.json').read_bytes())['spec_pending_actual_new_source_CPU'];old='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_TASK_FOCUSED_2610v97/h1'","prep=dict(payload_manifest_SHA=H(N/'payloads_v4/seed27/THREE_SLOT_COMPLETE_MANIFEST_V1.json'));old='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FUDAN270_BANK_READER_2610v103CPUv3/seed27'")
 s=replace(s,"eval_code_SHAs={p.name:H(p) for p in (S/'code').glob('*.py')}","resource_policy=dict(schema='mod4.user_allowed_light_compute.20261029.v1',free_MiB_strictly_above=15669,utilization_percent_max=30,compute_UUID_rows_allowed=True,other_processes_untouched=True),eval_code_SHAs={p.name:H(p) for p in (S/'code').glob('*.py')}")
 s=replace(s,"flat=result['case']['result']['flat_real_physics_events']['lifetime']","original270=result['case']['result']['original270_terminal_physics_events']")
 entry=S/'run_NEW105_qualified104_fixed_Fudan270_motion_WM_case_UNUSED_once.py';ast.parse(s);entry.write_text(s,encoding='utf8')
 tree=ast.parse(s)
 for n in tree.body:
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('PRE','RUN') for t in n.targets):ast.parse(ast.literal_eval(n.value))
 put(S/'SOURCE_DERIVATION_AST_ONLY_ACTUAL.json',dict(epoch=time.time(),status='SOURCE_ONLY_NO_MODEL_OR_REMOTE_EXECUTION',new_purpose='qualified104 actualFudan270 frozenmean N1 motion+pairedWM+32step first-action reward/critic sensitivity',source_model_SHA='764129c1b4c9ec4560d83423856e9f4f5867f8f18c841215f43ed5552415b89c',original98_raw_model_case_not_reread=True,source_changes=changes,entry_SHA=H(entry),AST_and_embedded_remote_AST=True,no_saved_model_load_or_forward=True,no_runtime_SDK_asset_reward_learner_physics_action_or_acceptance_change=True,unexecuted_until_root_complete_source_review=True))
 print(json.dumps(dict(prepared_source_only=True,folder=str(S),entry_SHA=H(entry))))
if __name__=='__main__':
 try:main()
 except BaseException:
  if S.exists():put(S/('SOURCE_PREPARER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_remote_or_model_action=True))
  raise
