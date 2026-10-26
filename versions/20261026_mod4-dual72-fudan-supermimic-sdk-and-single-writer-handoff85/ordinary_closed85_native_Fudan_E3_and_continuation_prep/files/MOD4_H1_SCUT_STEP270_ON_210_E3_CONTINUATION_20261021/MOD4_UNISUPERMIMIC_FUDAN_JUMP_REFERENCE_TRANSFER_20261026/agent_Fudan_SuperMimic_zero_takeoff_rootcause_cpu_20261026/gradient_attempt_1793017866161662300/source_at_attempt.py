"""Actual-source AST + small reference + toy tensor gradients. No real model."""
from pathlib import Path
import ast
import csv
import hashlib
import json
import math
import statistics
import sys
import time
import traceback
from types import SimpleNamespace

import torch

P=Path(__file__).resolve().parent
J=P.parent
N=J.parent/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026'
B=N/'payloads/e2/source'
sys.path.insert(0,str(B))
from supermimic_reference_adapter_v1 import read_json_reference,PartialReferenceImitationMdp
from supermimic_vendor_v2.geometry import invariant_features,unflatten_state


def pin(path):
    raw=path.read_bytes()
    return dict(path=str(path),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())


def create(path,value):
    with path.open('x',encoding='utf8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')


def main():
    attempt=P/('gradient_attempt_'+str(time.time_ns()));attempt.mkdir()
    (attempt/'source_at_attempt.py').write_bytes(Path(__file__).read_bytes())
    bridge_path=B/'h1_supermimic_bridge_v1.py'
    learner_path=B/'supermimic_vendor_v2/learner.py'
    bridge=ast.parse(bridge_path.read_text('utf8'))
    learner=ast.parse(learner_path.read_text('utf8'))
    mdp_cls=next(n for n in bridge.body if isinstance(n,ast.ClassDef) and n.name=='H1GoalMdp')
    learner_cls=next(n for n in learner.body if isinstance(n,ast.ClassDef) and n.name=='SuperMimicLearner')
    names=('_imag_step','_reward_term','_wm_rollout')
    methods=[n for n in learner_cls.body if isinstance(n,ast.FunctionDef) and n.name in names]
    scope=dict(torch=torch,invariant_features=invariant_features,unflatten_state=unflatten_state,State=tuple)
    exec(compile(ast.Module(body=[mdp_cls,*methods],type_ignores=[]),'<actual_MDP_and_learner_tensor_methods_AST>','exec'),scope)
    reference_path=J/'agent_reference_retarget_cpu/ACTUAL_PARTIAL_STEP270_PHASE_V3_1793006590678125700/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json'
    order_path=N/'current_three_closed_text/e2/job0/production/NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json'
    names=json.loads(order_path.read_bytes())['actual_robot_joint_names']
    reference=read_json_reference(reference_path).for_offline_joint_order(names)
    provider=reference.torch_provider('cpu',offline_cpu_only=True)
    base=scope['H1GoalMdp'](torch.tensor(reference.states[0,13:43],dtype=torch.float32),.337742301121)
    mdp=PartialReferenceImitationMdp(base,provider)
    rows=[]
    for z in (.337742301121,.30,.25,.23,.20,.15):
        for zz in (1.,.9,.7,.5):
            angle=math.acos(zz);cs,sn=math.cos(angle),math.sin(angle)
            rot=torch.tensor([[[1.,0,0],[0,cs,-sn],[0,sn,cs]]])
            state=(torch.tensor([[.1,0,z]]),rot,torch.zeros(1,3),torch.zeros(1,3),torch.zeros(1,30),torch.zeros(1,30))
            done=float(base.soft_termination(state,torch.tensor([120]))[0])
            rows.append(dict(z_m=z,Rzz=zz,soft_done=done,survival16=(1-done)**16,discounted_survival16=.99**16*(1-done)**16))

    class TensorPolicy:
        def __init__(self,action):self.action=action
        def __call__(self,history,goal):return self.action[None].expand(history.shape[0],-1)
    class AnalyticToyWM:
        def __init__(self,gain):self.gain=gain;self.contexts=[]
        def step(self,state,action,context):
            self.contexts.append(context.detach().clone())
            pos,rot,vel,ang,q,dq=state
            dx=self.gain*torch.stack((.01*action[:,4],action[:,0]*0,.005*action[:,0]+.003*action[:,1]),-1)
            dv=self.gain*torch.stack((action[:,4]*0,action[:,4]*0,.05*action[:,0]),-1)
            return pos+dx,rot,vel+dv,ang,q,dq

    gradient_rows=[]
    for gain in (1.,0.):
        action=torch.tensor([.1,-.15,.2,.05,.3,-.2],requires_grad=True)
        raw=provider.raw_reference_at_frames(torch.tensor([120]))
        state=list(unflatten_state(raw));state[0]=torch.tensor([[.1,0,.28]])
        state[2]=torch.zeros(1,3);state=tuple(state)
        frame=torch.tensor([120]);context=torch.zeros(1,49)
        previous=torch.zeros(1,6);history=mdp.obs(state,previous,context,frame)[:,None].expand(-1,10,-1)
        wm=AnalyticToyWM(gain)
        obj=SimpleNamespace(pi=TensorPolicy(action),wm=wm,mdp=mdp,cfg=SimpleNamespace(goal_frames=1))
        goal=mdp.goal(frame,1);task_terms=[];reg_terms=[];dones=[]
        for k in range(16):
            before=previous
            state,previous,history,frame,goal=scope['_imag_step'](obj,state,history,previous,frame,context,mdp.normalize_context(context),goal)
            reward,done=scope['_reward_term'](obj,state,frame,previous,before)
            terms=mdp.objective_terms(state,frame,previous,before)
            assert torch.equal(reward,terms['total'])
            task_terms.append(reward+terms['regularization']);reg_terms.append(terms['regularization']);dones.append(done)
        done=torch.stack(dones);alive=torch.cumprod(1-done,0)
        continuation=torch.cat((torch.ones(1,1),alive[:-1]),0)
        discount=.99**torch.arange(16,dtype=torch.float32)[:,None]
        task_objective=(discount*continuation*torch.stack(task_terms)).sum()
        regularizer=(discount*continuation*torch.stack(reg_terms)).sum()
        task_grad=torch.autograd.grad(-task_objective,action,retain_graph=True)[0]
        reg_grad=torch.autograd.grad(regularizer,action,retain_graph=True)[0]
        full_grad=torch.autograd.grad(-task_objective+regularizer,action)[0]
        assert torch.isfinite(full_grad).all()
        assert (float(task_grad.norm())>0) if gain else (float(task_grad.norm())==0)
        assert float(reg_grad.norm())>0
        gradient_rows.append(dict(toy_WM_action_gain=gain,task_only_grad=task_grad.tolist(),regularizer_grad=reg_grad.tolist(),total_grad=full_grad.tolist(),task_only_grad_norm=float(task_grad.norm()),regularizer_grad_norm=float(reg_grad.norm()),total_grad_norm=float(full_grad.norm()),survival16=float(alive[-1,0]),real_learned_WM_or_actor_used=False))

    # Exact _wm_rollout consumes time-varying xi during supervised training.
    raw=provider.raw_reference_at_frames(torch.tensor([120]));states=raw[:,None].expand(-1,3,-1)
    contexts=torch.stack([torch.full((1,49),float(i)) for i in range(3)],1)
    recording=AnalyticToyWM(0.)
    obj=SimpleNamespace(wm=recording,mdp=mdp,cfg=SimpleNamespace(wm_window=3))
    scope['_wm_rollout'](obj,states,torch.zeros(1,3,6),contexts)
    supervised_contexts=[float(x[0,0]) for x in recording.contexts]
    assert len(set(supervised_contexts))==3
    assert all(torch.equal(x,torch.zeros_like(x)) for x in wm.contexts)

    csv_path=N/'current_three_closed_text/e2/job0/production/native_supermimic/train_log.csv'
    curve=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(csv_path.open())]
    active=[row for row in curve if row['iteration']>=11]
    def summary(key,part):
        vals=[row[key] for row in part]
        return dict(min=min(vals),max=max(vals),mean=statistics.mean(vals),first=vals[0],last=vals[-1])
    metrics={k:summary(k,active) for k in ('pi_gradnorm','pi_loss','v_loss','imag_rew','imag_survival','wm_loss','wm_err8')}
    report=dict(epoch=time.time(),passed=True,scope='ACTUAL_SOURCE_SMALL_REFERENCE_TOY_TENSORS_NO_REAL_MODEL',
        evidence_pins=[pin(bridge_path),pin(learner_path),pin(B/'supermimic_reference_adapter_v1.py'),pin(csv_path),pin(order_path)],
        quaternion=dict(actual_SDK_convention='xyzw',bridge_conversion='xyzw_to_vendor_wxyz_correct',prior_initial_bug_claim='WITHDRAWN_WRONG_INPUT_CONVENTION_FIXTURE',source_contrary_evidence=str(N/'payloads/e2/job0/runtime/isaac/mod4/mod4_task.py')+':24-27'),
        soft_termination_grid=rows,gradient_fixtures=gradient_rows,
        fixed_xi=dict(supervised_xi_first_channel_by_time=supervised_contexts,imagination_xi='same initial xi for all16 steps',xi_layout='contact_history18+applied_torque30+public_request1',status='CONFIRMED_SOURCE_TRAIN_IMAGINATION_CONTEXT_EVOLUTION_MISMATCH_CAUSAL_EFFECT_PENDING_REAL_WM_DIAGNOSTIC'),
        actual_log=dict(rows=len(curve),Pi_rows=len(active),all_Pi_gradnorm_positive_finite=all(math.isfinite(r['pi_gradnorm']) and r['pi_gradnorm']>0 for r in active),last_iteration=int(curve[-1]['iteration']),metrics=metrics,code_inference='58 finite-gradnorm rows plus opt_pi.step finite guard imply58 optimizer calls absent exceptions; not direct native optimizer state read',world_model_error_units='normalizer/floor scaled mean over72 state-error features, not meters, not heldout validation',zero_ep_len_ret_term_columns='bridge transition omits ep_len/ep_ret_norm/term metadata; zeros are logging omissions, not proof of zero resets or long-lived episodes'),
        source_gradient_audit=dict(task_objective_not_detached=True,collection_no_grad_expected=True,initial_history_no_grad_expected=True,freeze_WM_critic_parameters_does_not_freeze_action_input_derivatives=True,logging_detach_after_objective_only=True,real_saved_WM_action_JVP='NOT_MEASURED_NO_MODEL_READ_AUTHORIZED'),
        age_alignment=dict(transition_f='pre-action h1_phase.age_control from bridge.state',next_f='post selected-reset current age_control',done_mask='WM sample_windows masks after real done; sample_starts clamps history by ep_step and age',request='100<=age_control<180',reference='own age100 maps source1.5s via offset-.5; initial hold through age50',actual85_age_request_distribution='MISSING_NOT_IN_SMALL_CURVE_DO_NOT_SUBSTITUTE82Q'),
        no_PT_raw_NPZ_actor_forward_optimizer_training_physics_GPU_remote_Git_or_budget_action=True,
        actual_zero_takeoff_unique_cause='UNPROVEN',not_training_or_runtime_admission=True)
    create(attempt/'ACTUAL_SOURCE_GRADIENT_TERMINATION_XI_AND_LOG_CPU.json',report)
    print(json.dumps(dict(passed=True,report=str(attempt/'ACTUAL_SOURCE_GRADIENT_TERMINATION_XI_AND_LOG_CPU.json'),Pi_rows=len(active),gradient_fixtures=gradient_rows,actual_last=curve[-1])))


if __name__=='__main__':
    try:main()
    except BaseException:
        create(P/('GRADIENT_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),passed=False,error=traceback.format_exc(),no_real_model_or_environment=True))
        raise
