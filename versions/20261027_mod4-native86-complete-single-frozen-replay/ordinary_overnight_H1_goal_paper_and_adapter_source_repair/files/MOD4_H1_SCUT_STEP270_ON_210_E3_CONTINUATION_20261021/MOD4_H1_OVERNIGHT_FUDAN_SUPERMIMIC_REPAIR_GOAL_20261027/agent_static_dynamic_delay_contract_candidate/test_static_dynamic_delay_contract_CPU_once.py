"""Tiny CPU/source tests, not actual DR/SDK/model or physical admission."""
from pathlib import Path
import importlib.util, json, hashlib, traceback, sys, datetime
import torch
import static_dynamic_delay_contract_v1 as c

D=Path(__file__).resolve().parent
T=D.parent.parent
Q=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2/job0/runtime/isaac/mod4/action_delay_physics_queue.py'
spec=importlib.util.spec_from_file_location('original_queue_cpu_reference',Q)
qmodule=importlib.util.module_from_spec(spec);spec.loader.exec_module(qmodule)
rows=[]
def check(name, function):
    try:
        detail=function()
        rows.append(dict(name=name,passed=True,detail=detail))
    except Exception:
        rows.append(dict(name=name,passed=False,traceback=traceback.format_exc()))
def yes(condition):
    assert bool(condition)
def rejects(fn):
    try:fn()
    except (ValueError,NotImplementedError):return True
    raise AssertionError('Expected rejection')

def original_queue_comparison():
    n=9;queue=qmodule.PhysicsActionQueue(n,'cpu',20261027)
    ids=torch.arange(n);neutral=torch.arange(n*6,dtype=torch.float32).reshape(n,6)*.001
    for key, sl in [('legs',slice(0,4)),('wheels',slice(4,6))]:queue.reset(key,ids,neutral[:,sl])
    lag=torch.tensor([(i,j) for i in range(3) for j in range(3)])
    for i,key in enumerate(('legs','wheels')):queue.groups[key]['lag_steps'].copy_(lag[:,i])
    old=neutral.clone();comparisons=0
    for control in range(3):
        if control==2:
            selected=torch.tensor([1,4,8]);neutral2=-neutral-.25
            previous=old.clone()
            old=c.reset_old_applied(old,selected,neutral2)
            yes(torch.equal(old[[0,2,3,5,6,7]],previous[[0,2,3,5,6,7]]))
            for key,sl in [('legs',slice(0,4)),('wheels',slice(4,6))]:queue.reset(key,selected,neutral2[:,sl])
            lag=torch.stack([queue.groups[k]['lag_steps'] for k in ('legs','wheels')],-1)
        target=torch.arange(n*6,dtype=torch.float32).reshape(n,6)*.03+control+.5
        tick=control*4
        expected=c.unroll_processed_target_control(target,old,lag,issue_tick=tick,last_apply_tick=tick-1)
        for key,sl in [('legs',slice(0,4)),('wheels',slice(4,6))]:
            queue.submit(key,target[:,sl],tick)
            queue.submit(key,target[:,sl],tick) # same callback repeat, original semantics
        actual=[]
        for sub in range(4):
            groups=[]
            for key in ('legs','wheels'):
                value=queue.apply(key,tick+sub)
                yes(torch.equal(value,queue.apply(key,tick+sub)))
                groups.append(value)
            actual.append(torch.cat(groups,-1))
        actual=torch.stack(actual,1)
        yes(torch.equal(actual,expected.applied_substeps));comparisons+=n*4*6
        old=expected.next_old_applied
        yes(torch.equal(old,torch.cat([queue.groups[k]['applied'] for k in ('legs','wheels')],-1)))
        for i,key in enumerate(('legs','wheels')):
            receipt=queue.receipt(key,tick+3)
            yes(torch.equal(receipt['actual_first_transition_delay_us'],lag[:,i]*2500))
    return dict(original_queue_tensor_entries_compared=comparisons,all_nine_leg_wheel_lag_pairs=True,
                continuous_controls=3,selected_reset_between_controls=True,original_queue_not_modified=True)
check('exact_original_queue_all_lags_two_controls_and_selected_reset',original_queue_comparison)

def gradients():
    lag=torch.tensor([[0,2],[1,0],[2,1]])
    target=torch.ones(3,6,requires_grad=True);old=torch.zeros(3,6,requires_grad=True)
    result=c.unroll_processed_target_control(target,old,lag)
    result.applied_substeps.sum().backward()
    lag6=torch.cat([lag[:,:1].expand(-1,4),lag[:,1:].expand(-1,2)],-1)
    yes(torch.equal(target.grad,(4-lag6).float()))
    yes(torch.equal(old.grad,lag6.float()))
    return dict(target_gradient_equals_4_minus_lag=True,old_applied_gradient_equals_lag=True,lag_discrete_not_differentiated=True)
check('processed_target_and_old_applied_gradients',gradients)

def dynamic_layout():
    contact=torch.arange(36,dtype=torch.float32).reshape(2,3,2,3)
    torque=torch.arange(60,dtype=torch.float32).reshape(2,30)
    previous=torch.arange(12,dtype=torch.float32).reshape(2,6)
    value=c.pack_dynamic_aux(contact,torque,previous);parts=c.unpack_dynamic_aux(value)
    yes(value.shape==(2,54));yes(torch.equal(parts['contact_history'],contact))
    yes(torch.equal(parts['applied_torque'],torque));yes(torch.equal(parts['old_processed_applied'],previous))
    return dict(dim=54,contact_dim=18,no_virtual_joints=True)
check('dynamic54_named_roundtrip',dynamic_layout)
check('contact12_rejected',lambda:rejects(lambda:c.pack_dynamic_aux(torch.zeros(2,2,2,3),torch.zeros(2,30),torch.zeros(2,6))))
check('dynamic_nonfinite_rejected',lambda:rejects(lambda:c.unpack_dynamic_aux(torch.full((2,54),float('nan')))))

def age_contract():
    age=torch.tensor([0,99,100,179,180,200])
    yes(torch.equal(c.request_from_age(age),torch.tensor([False,False,True,True,False,False])))
    age2=c.advance_age(torch.tensor([99,179]),torch.tensor([False,True]))
    yes(torch.equal(age2,torch.tensor([100,0])))
    return dict(original_request_100_inclusive_180_exclusive=True,after_control_then_selected_reset=True)
check('request_advances_and_selected_age_reset',age_contract)
check('negative_age_rejected',lambda:rejects(lambda:c.request_from_age(torch.tensor([-1]))))

def relative_contract():
    root=torch.tensor([[.1,0.,.34],[.4,0.,.34]],requires_grad=True)
    target=torch.tensor([[.65,0.,.607742],[.65,0.,.607742]])
    edge=torch.full((2,),.35);top=torch.full((2,),.27);age=torch.tensor([140,140])
    first=c.task_relative_observation(root,target,edge,top,age)
    yes(first.shape==(2,7));yes(first[0,3]!=first[1,3])
    shift=torch.tensor([2.,3.,4.])
    shifted=c.task_relative_observation(root+shift,target+shift,edge+shift[0],top+shift[2],age)
    yes(torch.allclose(first,shifted,atol=1e-6,rtol=0))
    first[:,:5].sum().backward();yes(bool(torch.isfinite(root.grad).all()))
    return dict(edge_x_visible=True,task_translation_invariant=True,root_position_gradient_present=True)
check('relative_task_position_no_x_alias',relative_contract)

layout=c.static_layout(body_names=('chassis','left_wheel','right_wheel'),joint_names=('j0','j1'),
                       material_names=('left','right'),gas_joint_names=('gas0','gas1'))
values={s.name:torch.ones((3,*s.shape)) for s in layout}
values['action_lag_steps']=torch.tensor([[0.,1.],[2.,0.],[1.,2.]])
episode=torch.tensor([3,4,5])
context=c.EpisodeStaticContext(layout,values,episode)
def reset_context():
    before=context.xi();new=context.snapshot()
    for k in new:
        if k!='action_lag_steps':new[k][1]*=.5
    new['action_lag_steps'][1]=torch.tensor([1.,2.])
    result=context.selected_reset(torch.tensor([1]),new,torch.tensor([3,5,5]))
    yes(torch.equal(before[[0,2]],context.xi()[[0,2]]));yes(context.assert_unchanged(new))
    return result
check('static_selected_reset_nonselected_exact',reset_context)
def bad_nonreset():
    before=context.xi().clone();new=context.snapshot();new['body_mass'][0,0]+=.01
    rejects(lambda:context.selected_reset(torch.tensor([1]),new,torch.tensor([3,6,5])))
    yes(torch.equal(before,context.xi()))
    return dict(failed_update_atomic=True)
check('nonreset_static_change_rejected_without_mutation',bad_nonreset)
check('mid_episode_static_drift_rejected',lambda:rejects(lambda:context.assert_unchanged(values)))
check('dynamic_field_forbidden_in_xi',lambda:rejects(lambda:c.EpisodeStaticContext((c.FieldSpec('applied_torque',(30,),'Nm','dynamic'),),{'applied_torque':torch.zeros(3,30)},episode)))
check('static_missing_component_rejected',lambda:rejects(lambda:c.EpisodeStaticContext(layout,{},episode)))
check('SDK_getter_is_explicit_pending',lambda:rejects(lambda:c.read_actual_episode_parameters(None)))
check('duplicate_reset_ids_rejected',lambda:rejects(lambda:context.selected_reset(torch.tensor([1,1]),context.snapshot(),torch.tensor([3,6,5]))))
check('wrong_episode_increment_rejected',lambda:rejects(lambda:context.selected_reset(torch.tensor([1]),context.snapshot(),torch.tensor([3,5,5]))))

target=torch.zeros(2,6);old=torch.zeros(2,6);lag=torch.zeros(2,2,dtype=torch.long)
check('nonoriginal_clock_rejected',lambda:rejects(lambda:c.unroll_processed_target_control(target,old,lag,physics_us=1000)))
check('out_of_range_lag_rejected',lambda:rejects(lambda:c.unroll_processed_target_control(target,old,lag+3)))
check('float_lag_rejected',lambda:rejects(lambda:c.unroll_processed_target_control(target,old,lag.float())))
check('pending_command_boundary_rejected',lambda:rejects(lambda:c.unroll_processed_target_control(target,old,lag,pending_valid=torch.ones(2,2,dtype=torch.bool))))
check('skipped_physics_tick_rejected',lambda:rejects(lambda:c.unroll_processed_target_control(target,old,lag,issue_tick=4,last_apply_tick=2)))
check('mid_control_projection_rejected',lambda:rejects(lambda:c.unroll_processed_target_control(target,old,lag,issue_tick=1,last_apply_tick=0)))
check('nonfinite_processed_target_rejected',lambda:rejects(lambda:c.unroll_processed_target_control(target+float('inf'),old,lag)))

value=dict(schema='mod4.static_dynamic_delay_contract.synthetic_CPU.v1',
    UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=all(r['passed'] for r in rows),
    passed_count=sum(r['passed'] for r in rows),total=len(rows),torch_version=torch.__version__,device='cpu',
    original_queue=dict(path=str(Q),SHA=hashlib.sha256(Q.read_bytes()).hexdigest()),
    candidate_SHA=hashlib.sha256((D/'static_dynamic_delay_contract_v1.py').read_bytes()).hexdigest(),
    tests=rows, actual_installed_SDK_admission=False,actual_DR_mapping_pending=True,
    no_PT_raw_actor_WM_physics_GPU_SSH_training_or_Git=True)
report=D/'STATIC_DYNAMIC_DELAY_CONTRACT_CPU_V1_ACTUAL.json'
with report.open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False)
print(json.dumps(dict(passed=value['passed'],passed_count=value['passed_count'],total=value['total'],report=str(report)),ensure_ascii=False))
if not value['passed']:sys.exit(1)
