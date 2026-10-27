from pathlib import Path
import json,time,math,hashlib
import torch
from flat_jump_phase_objective_source_v1 import FlatJumpPhase,flat_jump_terms,physical_skill_scope
O=Path(__file__).resolve().parent
def main():
    report=O/'FLAT5CM_PHASE_AND_FAILED_STANDING_SOURCE_CPU_ACTUAL.json'
    assert not report.exists()
    p=FlatJumpPhase();ages=torch.arange(0,701)[:,None].expand(-1,4096);ids=torch.arange(4096)[None,:].expand_as(ages)
    target=p.targets(ages,ids)
    assert target['height'][:200].count_nonzero()==0
    assert (target['height']>=0).all() and target['height'].max()<=.05
    # Requests occur while a continued learner can sample them, unlike the old
    # one early request lost entirely from a no-reset replay ring after warmup.
    after=target['flight'][226:290];assert after.any()
    rows=[]
    for scenario in ('standing_during_requested_flight','target_at_flight_apex','standing_stable','tilted_before_request'):
        flight=scenario in ('standing_during_requested_flight','target_at_flight_apex')
        t=dict(height=torch.tensor([.05 if flight else 0.]),vertical_v=torch.zeros(1),ground=torch.tensor([not flight]))
        h=torch.tensor([[.05,.05]] if scenario=='target_at_flight_apex' else [[0.,0.]],requires_grad=True)
        support=torch.tensor([[0.,0.]] if scenario=='target_at_flight_apex' else [[1.,1.]])
        z=torch.tensor([math.cos(.7507237792) if scenario=='tilted_before_request' else 1.])
        r=flat_jump_terms(h,torch.zeros_like(h),z,torch.zeros(1,2),support,t,torch.zeros(1,6),torch.zeros(1,6))
        grad=torch.autograd.grad(r['total'].sum(),h)[0]
        rows.append(dict(scenario=scenario,reward=float(r['total'].item()),height_gradient=grad.tolist(),tilt_failure_probability=float(r['tilt_failure_probability'].item())))
    d={x['scenario']:x for x in rows}
    assert d['target_at_flight_apex']['reward']>d['standing_during_requested_flight']['reward']
    assert d['standing_stable']['reward']>d['tilted_before_request']['reward']
    assert d['standing_during_requested_flight']['height_gradient'][0][0]>0
    value=dict(epoch=time.time(),source_math_passed=True,physics_GPU_model_or_SDK_not_run=True,
        real_video_phase_evidence_used_not_3D_mocap=True,selected_initial_native_control_dt_s=.01,
        expert_PPO50Hz_is_separate_typed_data_domain=True,first_goal_height_m=.05,
        sampled_request_envframes_after_old_firstPi226_in_next64=int(after.sum()),
        sample_count_is_not_real_exposure_or_skill=True,scenarios=rows,scope=physical_skill_scope(),
        runtime_adapter_and_geometry_force_phase_context_validation_pending=True,
        original_native88C_and_E0_training_unmodified=True,
        source_SHA=hashlib.sha256((O/'flat_jump_phase_objective_source_v1.py').read_bytes()).hexdigest())
    with report.open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
    print(json.dumps(value))
if __name__=='__main__':main()
