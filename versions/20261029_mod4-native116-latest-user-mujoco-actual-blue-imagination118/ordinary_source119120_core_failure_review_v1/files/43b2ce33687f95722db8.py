"""Source-only query/feature review, zero checkpoint/raw/SDK/physics/GPU reads."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,sys,time,traceback
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent;B=T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029/payloads/seed27/source';R=D/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def methods(text):
    return {(c.name,f.name):ast.dump(f,include_attributes=False) for c in ast.parse(text).body if isinstance(c,ast.ClassDef) for f in c.body if isinstance(f,ast.FunctionDef)}
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    marker=R/'SOURCE119_CPU_REVIEW_CONSUMED.json';assert not marker.exists();marker.write_text(json.dumps(dict(epoch=time.time(),source_only=True,no_model_raw_remote_or_GPU=True)),encoding='utf8')
    import torch
    torch.set_num_threads(2);assert not torch.cuda.is_initialized();before=torch.get_rng_state().clone()
    sys.path.insert(0,str(B))
    old=load('source119_baseline',B/'native_fudan_step_adapter_candidate_v2.py');new=load('source119_candidate',D/'native119_pre_request_neutral_X_adapter_SOURCE_ONLY.py')
    doc=json.loads((D/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json').read_bytes())
    p0=old.OwnFudanStepReference(doc).bind_named_order(doc['joint_names'],scope='source_CPU_fixture');p1=new.OwnFudanStepReference(doc).bind_named_order(doc['joint_names'],scope='source_CPU_fixture')
    from private_phase_frame_v1 import encode,decode
    ages=torch.tensor([0,1,180,189,190,198,199,200,201,1999,2000],dtype=torch.long)
    age=ages.repeat(250);ids=torch.arange(250).repeat_interleave(len(ages));frame=encode(age,ids);assert torch.equal(decode(frame)['public_age'],age)
    v0,m0=p0.query(frame);v1,m1=p1.query(frame);pre=age<200;post=~pre
    assert torch.equal(m0,m1) and torch.equal(v0[post],v1[post])
    assert torch.equal(v0[...,1:],v1[...,1:]) and bool((v0[pre,0]==0).all()) and bool((v1[pre,0]==p1.neutral[0]).all())
    assert bool((m0[...,13:]==0).all()) and m0.shape[-1]==73
    g0=p0.future_goal(frame,10);g1=p1.future_goal(frame,10);assert g0.shape==g1.shape==(len(frame),1460)
    expected=g0.clone().reshape(-1,10,146)
    for offset in range(10):expected[:,offset,0]=torch.where(age+offset<200,p1.neutral[0],expected[:,offset,0])
    assert torch.equal(expected.reshape(-1,1460),g1)
    a=old.OwnFudanStepMdp.__new__(old.OwnFudanStepMdp);a.provider=p0
    b=new.OwnFudanStepMdp.__new__(new.OwnFudanStepMdp);b.provider=p1
    root=torch.tensor([[.05603908747434616,-.095,.248]],dtype=torch.float32).expand(len(frame),3).clone().requires_grad_(True)
    state=(root,None,None,None,None,None,None)
    f0=a.relative_features(state,frame);f1=b.relative_features(state,frame)
    assert torch.equal(f0[...,1:],f1[...,1:]) and torch.equal(f0[post],f1[post])
    assert torch.allclose(f1[pre,0]-f0[pre,0],p1.neutral[0].expand(int(pre.sum())),rtol=0,atol=1e-8)
    assert bool(((f1[...,5]>0)==((age>=200)&(age<2000))).all()) and torch.equal(f0[...,6],f1[...,6])
    grad=torch.autograd.grad(f1.sum(),root)[0];assert bool(torch.isfinite(grad).all())
    om=methods((B/'native_fudan_step_adapter_candidate_v2.py').read_text(encoding='utf8'));nm=methods((D/'native119_pre_request_neutral_X_adapter_SOURCE_ONLY.py').read_text(encoding='utf8'))
    changed=[list(k) for k in om if om[k]!=nm[k]];assert set(map(tuple,changed))=={('OwnFudanStepReference','query'),('OwnFudanStepMdp','contract_manifest')}
    assert torch.equal(before,torch.get_rng_state()) and not torch.cuda.is_initialized()
    first=json.loads((T/'H1_NATIVE116_LATEST_USER_MUJOCO_MOTION_WM_V118_20261029/user_action_sequence_review/USER_OBSERVED_SEQUENCE_AND_ORIGINAL_CLOSURE_ACTUAL.json').read_bytes())['start'];x=float(first['root_x']);neutral_x=float(p1.neutral[0])
    out=dict(epoch=time.time(),passed_source_CPU_only=True,source_method_changes=changed,query_rows=len(frame),private_delays=250,ages=ages.tolist(),policy_future_frames=10,goal_width=1460,
        original_pre_request_goal_x_m=0.,declared_neutral_pose_x_m=neutral_x,original_error_at_declared_neutral_m=-neutral_x,candidate_error_at_declared_neutral_m=0.,
        recorded_first_completed_control_seconds=first['seconds'],recorded_first_completed_control_x_m=x,original_goal_error_at_that_sample_m=-x,candidate_goal_error_at_that_sample_m=neutral_x-x,
        post_request_all_goal_values_masks_literal_unchanged=True,all_masks_literal_unchanged=True,all_joint_and_joint_velocity_goal_masks_zero_before_and_after=True,
        current_reference_is_terminal_body_goal_not_measured_tuck_trajectory=True,relative_feature_only_target_dx_changes_before_request=True,request_feature_clock_and_age_units_unchanged=True,
        all_other_methods_AST_equal=True,RNG_unchanged=True,finite_root_feature_gradient=True,
        raw_goal_shift_max_m=neutral_x,normalized_shift_upper_bound_using_source_eps01_only=neutral_x/.01,actual_inherited_goal_normalizer_stats_read=False,
        not_an_assertion_normalized_shift_is_at_most_one=True,actual_target_fullstate_and_goal_normalizer_readback_required_before_use=True,
        no_reward_physics_learner_architecture_weights_norm_tensors_optimizers_or_20s_contract_changed=True,
        no_checkpoint_or_physical_raw_NPZ_SDK_GPU_remote_or_account_action=True,not_runtime_admitted=True,
        limits=['Backward goal cue is confirmed; its causal contribution to22.2cm actual retreat is unknown.','Declaredneutral X is not a captured per-environment reset anchor. Candidate is not exact per-env positionhold.','Current off-request recovery reward unchanged; no guarantee actor stops drifting.','Validjump/cross history gap and4.31sclosure cause remain unresolved.','No tuck joint trajectory fabricated; no newlearning authorized by sourceCPU pass.'])
    (R/'SOURCE119_PRE_REQUEST_BACKWARD_GOAL_CUE_AND_NARROW_CANDIDATE_CPU_ACTUAL.json').write_text(json.dumps(out,indent=2),encoding='utf8')
    print(json.dumps(dict(passed_source_CPU_only=True,original_goal_error_at_recorded_first_control=-x,candidate_goal_error=neutral_x-x,query_rows=len(frame),joint_masks_still_zero=True,no_model_or_GPU=True)))
if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('SOURCE119_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),no_model_raw_or_remote=True),f,indent=2)
        raise
