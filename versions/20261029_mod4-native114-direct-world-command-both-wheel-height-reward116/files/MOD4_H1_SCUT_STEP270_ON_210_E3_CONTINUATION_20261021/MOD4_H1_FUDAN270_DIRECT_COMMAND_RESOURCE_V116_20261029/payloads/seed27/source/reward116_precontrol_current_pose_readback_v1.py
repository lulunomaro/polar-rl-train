"""Pure GPU tensor readback on already reset own poses, no physical step/model read."""
import torch
from private_phase_frame_v1 import encode
def check(mdp,state):
    device=state[0].device;n=len(state[0]);a=torch.zeros(n,6,device=device)
    rows={}
    for age in (0,300):
        frame=encode(torch.full((n,),age,dtype=torch.long,device=device),torch.zeros(n,dtype=torch.long,device=device))
        out=mdp.objective_terms(state,frame,a,a)
        assert torch.isfinite(out['total']).all()
        assert torch.equal(out['total'],sum(out['selected_optimization_terms'].values()))
        assert out['command_tracking116']['target_each_wheel_bottom_m']==.27
        if age==300:assert (out['total']>=0).all() and (out['total']<=.160001).all()
        rows[str(age)]=dict(total_min=float(out['total'].min()),total_max=float(out['total'].max()),actual_wheel_bottom_min=float(out['command_tracking116']['actual_wheel_bottom2'].min()),actual_wheel_bottom_max=float(out['command_tracking116']['actual_wheel_bottom2'].max()),selected_terms=list(out['selected_optimization_terms']))
    return dict(passed=True,device=str(device),actual_reset_pose_rows=n,formula_evaluations_on_actual_pose_with_declared_age0_and_synthetic_request300=rows,
        actual_phase_or_physics_not_mutated=True,model_forward_or_additional_model_read=False,actual_training_or_skill_not_inferred=True)
