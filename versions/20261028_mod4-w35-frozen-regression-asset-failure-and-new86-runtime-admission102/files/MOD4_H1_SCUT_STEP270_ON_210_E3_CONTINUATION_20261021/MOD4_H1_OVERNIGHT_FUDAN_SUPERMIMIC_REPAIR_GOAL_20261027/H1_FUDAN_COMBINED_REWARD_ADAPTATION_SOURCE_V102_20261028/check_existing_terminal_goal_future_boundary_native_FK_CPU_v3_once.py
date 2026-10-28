from pathlib import Path
import hashlib, importlib.util, json, os, sys, time, traceback

B=Path(__file__).resolve().parent; R=B/'reports'; T=B.parent.parent
P=T/'MOD4_H1_FLAT20_NATIVE_PRODUCER_FIX_RESOURCE_V101_20261028/payloads/seed27'; S=P/'source'
def put(name, value):
    with (R/name).open('x',encoding='utf8') as f: json.dump(value,f,indent=2)

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    import torch
    torch.set_num_threads(2); assert not torch.cuda.is_initialized()
    sys.path[:0]=[str(B),str(S)]
    selected=B/'native_fudan_step_adapter_candidate_v2.py'
    spec=importlib.util.spec_from_file_location('fudan102_boundary_v3',selected)
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)
    doc=json.loads((B/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json').read_bytes())
    c=json.loads((P/'job0/assets/import_contract.json').read_bytes()); g=json.loads((S/'OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json').read_bytes())
    provider=m.OwnFudanStepReference(doc).bind_named_order(doc['joint_names'],scope='source_CPU_fixture'); mdp=m.OwnFudanStepMdp(provider,c,g)
    from private_phase_frame_v1 import encode,decode
    ages=torch.tensor([0,199,200,230,350,499]); frames=encode(ages,torch.arange(6))
    goal=mdp.goal(frames,10); assert goal.shape==(6,1460); view=goal.reshape(6,10,146)
    future_ages=torch.stack([decode(frames+i)['public_age'] for i in range(10)],dim=-1)
    expected=torch.where(future_ages>=200,.75,0.)
    assert torch.equal(view[...,0],expected)
    assert view[1,0,0]==0 and (view[1,1:,0]==.75).all()
    assert set(view[...,73:].flatten().tolist())<={0.,1.} and (view[...,86:]==0).all()
    assert (view[...,13:73]==0).all()
    q=provider.neutral[13:43].expand(6,30).clone().requires_grad_(); p=provider.neutral[:3].expand(6,3).clone().requires_grad_()
    rotation=torch.eye(3).expand(6,3,3).clone(); v=torch.zeros(6,3); v[:,2]=torch.tensor([0.,0.,.3,1.,0.,0.])
    aux=torch.zeros(6,54); aux[:,:18]=100.; state=(p,rotation,v,torch.zeros(6,3),q,torch.zeros(6,30),aux)
    action=torch.full((6,6),.05); previous=torch.zeros_like(action)
    obs=mdp.obs(state,previous,torch.zeros(6,31),frames); assert obs.shape==(6,86)
    terms=mdp.objective_terms(state,frames,action,previous)
    assert torch.isfinite(terms['total']).all() and (terms['total']<=mdp.max_step_reward+1e-6).all()
    terms['total'].sum().backward()
    assert torch.isfinite(q.grad).all() and torch.isfinite(p.grad).all()
    assert (q.grad.abs().sum(-1)>0).any() and (p.grad.abs().sum(-1)>0).any()
    assert torch.isfinite(mdp.soft_termination(state,frames)).all()
    geo=mdp.wheel_geometry(state)
    local=(rotation.transpose(-1,-2).unsqueeze(-3)@(geo['centre']-p.unsqueeze(-2)).unsqueeze(-1)).squeeze(-1)-mdp.hip_anchors
    lengths=local[...,[0,2]].norm(dim=-1)
    result=dict(epoch=time.time(),passed_source_CPU_only=True,selected_adapter=str(selected),selected_adapter_SHA=hashlib.sha256(selected.read_bytes()).hexdigest(),bound_goal_candidate=str(B/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json'),bound_goal_SHA=hashlib.sha256((B/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json').read_bytes()).hexdigest(),original_failed_assertion_retained=True,repair_is_test_expectation_for_future_age199_crossing200_not_adapter_change=True,future_goal_request_boundary_actual=view[1,:,0].tolist(),native_obs86_goal146x10_and_mask_passed=True,actual_recorded_own30_joint31body_FK_used=True,synthetic_q_root_gradients_finite_nonzero=True,synthetic_neutral_joint_pose_virtual_leg_lengths_m=lengths.detach().tolist(),neutral_pose_is_shape_witness_not_grounded_new_plant_rollout=True,length_targets_not_yet_admitted_from_actual_resetbank=True,no_saved_model_or_normalizer_loads=True,no_actor_WMforward_SDK_GPU_or_physics=True,no_learning_Task_GO_or_source_promotion=True,physical270_criterion_unchanged=True)
    put('FUDAN102_NATIVE127_OWN_GEOMETRY_TERMINAL_GOAL_AND_GRADIENT_CPU_V3_ACTUAL.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='synthetic_neutral_joint_pose_virtual_leg_lengths_m'}))
if __name__=='__main__':
    try: main()
    except BaseException:
        put('FUDAN102_BOUNDARY_CPU_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_models_SDK_GPU_or_physics=True));raise
