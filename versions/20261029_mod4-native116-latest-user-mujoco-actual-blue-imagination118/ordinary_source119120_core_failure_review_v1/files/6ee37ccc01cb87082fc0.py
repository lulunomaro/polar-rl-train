"""Separate source-candidate qualification purpose; no checkpoint/raw/GPU reads."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent.parent;B=T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029/payloads/seed27';R=D/'reports'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    put('SOURCE120_CANDIDATE_CPU_PURPOSE_CONSUMED.json',dict(epoch=time.time(),new_purpose='Qualify closure-stop source candidate against saved118terminal and isolated neutral/grace/timeout fixtures',cached_terminal_JSON_text_reads_planned=1,prior_source120_audit_cached_report_reads=1,total_cached_small_report_reads_across_two_purposes_planned=2,checkpoint_raw_JSONL_NPZ_SDK_GPU_remote_reads=0))
    import torch
    torch.set_num_threads(2);assert not torch.cuda.is_initialized();rng=torch.get_rng_state().clone();sys.path.insert(0,str(B/'source'))
    old=module('source120_old116',B/'source/native_fudan_step_adapter_candidate_v2.py');new=module('source120_candidate',D/'native120_imagined_original_closure_stop_SOURCE_ONLY.py')
    read=lambda p:json.loads(Path(p).read_bytes())
    contract=read(B/'job0/assets/import_contract.json');geom=read(B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json');doc=read(B/'source/OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json')
    A=T/'H1_NATIVE116_LATEST_USER_MUJOCO_MOTION_WM_V118_20261029';fresh=read(next((A/'actual_case_text').glob('*FRESH_N1_SOURCE_SDK_RESET_GAS_BEFORE_FORWARD_ACTUAL.json')));names=fresh['actual_names']
    cached=read(A/'reports/FROZEN118_SINGLE_CASE_AND_WM_DIAGNOSTIC_RETURNED_ACTUAL.json');last=cached['case']['result']['last_original_state']
    p0=old.OwnFudanStepReference(doc).bind_named_order(names,scope='source_CPU_fixture');p1=new.OwnFudanStepReference(doc).bind_named_order(names,scope='source_CPU_fixture')
    m0=old.OwnFudanStepMdp(p0,contract,geom,names[:4] if False else p0.metadata['actuator_leg_joint_names']);m1=new.OwnFudanStepMdp(p1,contract,geom,p1.metadata['actuator_leg_joint_names'])
    from own_step_differentiable_geometry_v1 import qmat
    from private_phase_frame_v1 import encode
    tensor=lambda x:torch.tensor(x,dtype=torch.float32)
    root=tensor(last['root13_sdk_xyzw']);rotation=qmat(torch.cat((root[6:7],root[3:6])))[None]
    aux=torch.cat((tensor(last['contact_history18']).flatten(),tensor(last['applied_torque30']),tensor(last['physical_applied_processed6'])))[None]
    actual=(root[None,:3],rotation,root[None,7:10],root[None,10:13],tensor(last['q30'])[None],tensor(last['qd30'])[None],aux)
    frame=encode(torch.tensor([last['public_age']],dtype=torch.long),torch.tensor([0],dtype=torch.long));before=m0.soft_termination(actual,frame);after=m1.soft_termination(actual,frame)
    assert before.item()<.01 and after.item()==1 and m1.closure_surrogate_error_m(actual).item()>.002
    neutral=p1.neutral;safe=(neutral[None,:3],qmat(neutral[3:7])[None],neutral[None,7:10],neutral[None,10:13],neutral[None,13:43],neutral[None,43:73],torch.zeros(1,54))
    assert m1.closure_surrogate_error_m(safe).item()<.002
    ages=torch.tensor([0,9,10,199,200,431,1999,2000],dtype=torch.long);frames=encode(ages,torch.zeros_like(ages))
    batched=lambda state:tuple(x.expand(len(ages),*x.shape[1:]).clone() for x in state)
    bs,ba=batched(safe),batched(actual);old_safe=m0.soft_termination(bs,frames);new_safe=m1.soft_termination(bs,frames);new_bad=m1.soft_termination(ba,frames);old_bad=m0.soft_termination(ba,frames)
    assert torch.equal(old_safe,new_safe) and torch.equal(new_bad[ages<10],old_bad[ages<10]) and bool((new_bad[ages>=10]==1).all())
    assert new_safe[-1].item()==1 and torch.equal(m0.goal(frames,10),m1.goal(frames,10))
    bad_q=actual[4].clone().requires_grad_(True);s=(*actual[:4],bad_q,*actual[5:]);e=m1.closure_surrogate_error_m(s);gradient=torch.autograd.grad(e.sum(),bad_q)[0]
    assert bool(torch.isfinite(gradient).all()) and gradient.norm().item()>0
    def methods(p):
        return {(c.name,f.name):ast.dump(f,include_attributes=False) for c in ast.parse(Path(p).read_text(encoding='utf8')).body if isinstance(c,ast.ClassDef) for f in c.body if isinstance(f,ast.FunctionDef)}
    om=methods(B/'source/native_fudan_step_adapter_candidate_v2.py');nm=methods(D/'native120_imagined_original_closure_stop_SOURCE_ONLY.py');changed=[list(k) for k in om if om[k]!=nm[k]]
    assert set(map(tuple,changed))=={('OwnFudanStepMdp','__init__'),('OwnFudanStepMdp','soft_termination'),('OwnFudanStepMdp','contract_manifest')}
    assert om[('OwnFudanStepMdp','reward')]==nm[('OwnFudanStepMdp','reward')] and om[('OwnFudanStepReference','query')]==nm[('OwnFudanStepReference','query')]
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    out=dict(epoch=time.time(),passed_source_CPU_only=True,old_real_terminal_softdone=float(before.item()),candidate_real_terminal_softdone=float(after.item()),actual_state_closure_surrogate_m=float(e.item()),neutral_kinematic_fixture_closure_m=float(m1.closure_surrogate_error_m(safe).item()),
        original_threshold_m=.002,original_grace_controls=10,test_ages=ages.tolist(),candidate_bad_state_stops=new_bad.tolist(),candidate_neutral_stops=new_safe.tolist(),all_masks_goal_tensor_and_other_methods_literal_or_AST_equal=True,changed_existing_methods=changed,
        finite_nonzero_FK_q_gradient_norm=float(gradient.norm().item()),not_Pi_parameter_gradient_or_optimizer=True,RNG_unchanged=True,
        source119_goal_cue_change_NOT_selected_or_bundled=True,actual_saved_failure_caught_by_source_candidate=True,neutral_fixture_is_synthetic_kinematics_not_actual_physics_acceptance=True,
        no_checkpoint_raw_JSONL_NPZ_SDK_GPU_physics_remote_or_account=True,not_deployed_or_runtime_admitted=True,
        remaining_before_use=['Actual-action WM predicted-q closure error and false-stop calibration over phase-contiguous windows is still required.','Current validjump/cross/landing-process reward gap remains; this patch does not teach jump maneuvers by itself.','Newtypedsource/producer/actualSDK/fullstate/precontrolreadback/freshresources/singlewriterTaskGO all still required.','One savedterminal plus source fixtures do not establish global rootcause, generalphysicalequivalence or270skill.'])
    put('SOURCE120_CLOSURE_STOP_CANDIDATE_SAVED_FAILURE_GRACE_NEUTRAL_CPU_ACTUAL.json',out)
    print(json.dumps(dict(passed_source_CPU_only=True,old_failure_stop=float(before.item()),candidate_failure_stop=float(after.item()),actual_failure_closure_m=float(e.item()),neutral_closure_m=out['neutral_kinematic_fixture_closure_m'],runtime_used=False)))
if __name__=='__main__':
    try:main()
    except BaseException:put('SOURCE120_CANDIDATE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_model_raw_GPU_or_remote=True));raise
