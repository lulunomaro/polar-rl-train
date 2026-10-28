from pathlib import Path
import ast,hashlib,importlib.util,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';T=B.parent.parent
P=T/'MOD4_H1_FLAT20_NATIVE_PRODUCER_FIX_RESOURCE_V101_20261028/payloads/seed27';S=P/'source'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 import torch
 torch.set_num_threads(2);assert not torch.cuda.is_initialized()
 old=(B/'native_fudan_step_adapter_candidate_v1.py').read_text('utf8');needle='class OwnFudanStepMdp(ConvertedMOD4JumpMdp):\n';assert old.count(needle)==1
 new=old.replace(needle,needle+'    max_step_reward=.1385  # conservative clipped-component upper bound, log normalization only\n',1);ast.parse(new);selected=B/'native_fudan_step_adapter_candidate_v2.py'
 with selected.open('x',encoding='utf8') as f:f.write(new)
 sys.path[:0]=[str(B),str(S)];spec=importlib.util.spec_from_file_location('native_fudan102_actual_geometry_candidate',selected);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 prior=json.loads((S/'OWN_FLAT5CM_TASK_REFERENCE_SOURCE.json').read_bytes());c=json.loads((P/'job0/assets/import_contract.json').read_bytes());g=json.loads((S/'OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json').read_bytes())
 standing=prior['metadata']['stance_calibration']['baseline_body_height_m'];metadata=dict(prior['metadata']);metadata.update(control_dt_s=.01,request_age_ticks=200,legacy_env_stagger_not_used_for_new_request=True,source_is_measured_successful_Fudan_joint_motion=False,physical270_success_unchanged=True,task='actual authored270mm step',terminal_goal_not_prescribed_limb_trajectory=True,
  bound_own_step_reward=dict(extension_length_m=.31,tuck_length_m=.16,standing_body_height_m=standing,apex_body_height_m=standing+.27,step_edge_x_m=.35,platform_end_x_m=1.15,step_top_z_m=.27,goal_root_x_m=.75,approach_speed_m_s=.5,control_dt_s=.01),
  original_Fudan_length_targets_are_proposals_pending_actual_own_resetbank_FK_admission=True,
  Fudan_original_apex_body_height_m=.65,actual_hardware_or_measured_force_changes=False,
  next_typed_input_native_SHA='35e1657815fc972ed954d258fe62326074ebeb862e5bcfce7150b3ef58dc2b9f')
 doc=dict(schema='mod4.own_fudan_step_terminal_goal.v1',joint_names=prior['joint_names'],neutral_packed73=prior['neutral_packed73'],metadata=metadata)
 with (B/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json').open('x',encoding='utf8') as f:json.dump(doc,f,indent=2)
 provider=m.OwnFudanStepReference(doc).bind_named_order(prior['joint_names'],scope='source_CPU_fixture');mdp=m.OwnFudanStepMdp(provider,c,g)
 from private_phase_frame_v1 import encode
 ages=torch.tensor([0,199,200,230,350,499]);frames=encode(ages,torch.arange(6));q=provider.neutral[13:43].expand(6,30).clone().requires_grad_();p=provider.neutral[:3].expand(6,3).clone().requires_grad_();R0=torch.eye(3).expand(6,3,3).clone();v=torch.zeros(6,3);v[:,2]=torch.tensor([0.,0.,.3,1.,0.,0.]);aux=torch.zeros(6,54);aux[:,:18]=100.;state=(p,R0,v,torch.zeros(6,3),q,torch.zeros(6,30),aux);action=torch.full((6,6),.05);previous=torch.zeros_like(action)
 goal=mdp.goal(frames,10);assert goal.shape==(6,1460);view=goal.reshape(6,10,146);assert set(view[...,73:].flatten().tolist())<={0.,1.};assert (view[:2,:,0]==0).all() and (view[2:,:,0]==.75).all() and (view[...,86:]==0).all()
 obs=mdp.obs(state,previous,torch.zeros(6,31),frames);assert obs.shape==(6,86)
 terms=mdp.objective_terms(state,frames,action,previous);assert torch.isfinite(terms['total']).all() and (terms['total']<=mdp.max_step_reward+1e-6).all()
 terms['total'].sum().backward();assert torch.isfinite(q.grad).all() and torch.isfinite(p.grad).all() and (q.grad.abs().sum(-1)>0).any() and (p.grad.abs().sum(-1)>0).any()
 # No linear vertical-speed penalty from recovery is active in pure jump mode.
 # Real callbacks, supported footprint and exact200stable counts remain separate.
 impossible=(p.detach().clone(),R0,v,torch.zeros(6,3),q.detach(),torch.zeros(6,30),aux);soft=mdp.soft_termination(impossible,frames);assert torch.isfinite(soft).all()
 geo=mdp.wheel_geometry(state);local=(R0.transpose(-1,-2).unsqueeze(-3)@(geo['centre']-p.unsqueeze(-2)).unsqueeze(-1)).squeeze(-1)-mdp.hip_anchors;length=local[...,[0,2]].norm(dim=-1)
 put('FUDAN102_NATIVE127_OWN_GEOMETRY_TERMINAL_GOAL_AND_GRADIENT_CPU_ACTUAL.json',dict(epoch=time.time(),passed_source_CPU_only=True,selected_adapter=str(selected),selected_adapter_SHA=hashlib.sha256(new.encode()).hexdigest(),bound_goal_candidate=str(B/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json'),bound_goal_SHA=hashlib.sha256((B/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json').read_bytes()).hexdigest(),native_obs86_goal146x10_and_mask_passed=True,actual_recorded_own30_joint31body_FK_used=True,synthetic_q_root_gradients_finite_nonzero=True,synthetic_neutral_joint_pose_virtual_leg_lengths_m=length.detach().tolist(),neutral_pose_is_shape_witness_not_grounded_new_plant_rollout=True,length_targets_not_yet_admitted_from_actual_resetbank=True,no_saved_model_or_normalizer_loads=True,no_actor_WMforward_SDK_GPU_or_physics=True,no_learning_Task_GO_or_source_promotion=True,physical270_criterion_unchanged=True))
 print(json.dumps(dict(passed_source_CPU_only=True,obs=list(obs.shape),goal=list(goal.shape),q_grad_nonzero=True,actual_geometry_shape_witness_L0=length.detach()[0].tolist(),needs_actual_resetbank_and_typed_SDK_admission=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('FUDAN102_OWN_GEOMETRY_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_models_SDK_GPU_or_physics=True));raise
