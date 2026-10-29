"""Necessary decoder/action-sequence/anchor tests. No actual input/model read."""
from pathlib import Path
import copy
import hashlib
import json
import math
import os
import time
import torch
from wm_closure121_core import (anchor_errors, closure_stop, decode_records,
    evaluate, quat_apply_xyzw, valid_starts)

S=Path(__file__).resolve().parent
R=S/'reports'


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not torch.cuda.is_initialized()
    out=R/'SOURCE121_SYNTHETIC_TYPED_DOMAIN_AND_ACTUAL_ACTION_SEQUENCE_CPU.json'
    assert not out.exists()
    rng=torch.random.get_rng_state().clone()
    q=torch.tensor([[0.,0.,math.sqrt(.5),math.sqrt(.5)]])
    rotated=quat_apply_xyzw(q,torch.tensor([[1.,0.,0.]]))
    assert torch.allclose(rotated,torch.tensor([[0.,1.,0.]]),atol=2e-7)
    pos=torch.tensor([[[0.,0.,0.],[1.,0.,0.]]])
    rot=torch.eye(3).expand(1,2,3,3).clone()
    ids0=torch.tensor([0]);ids1=torch.tensor([1]);a0=torch.tensor([[1.,0.,0.]]);a1=torch.zeros(1,3)
    assert float(anchor_errors(pos,rot,ids0,ids1,a0,a1).max())==0
    assert torch.equal(anchor_errors(pos+120.,rot,ids0,ids1,a0,a1),torch.zeros(1,1))
    errors=torch.tensor([[.003],[.003],[.002],[.001]])
    assert closure_stop(errors,torch.tensor([9,10,10,10])).tolist()==[False,True,False,False]
    n=212;rows=[]
    for i in range(n):
        request=200<=i<2000
        packed=[0.]*127;packed[3]=1.
        state=dict(executed6=[.001,0.,0.,0.,0.,0.],physical_applied_processed6=[0.]*6,
            q30=[0.]*30,body_position31_world=[[0.,0.,0.],[0.,0.,0.]],
            body_quaternion31_sdk_xyzw=[[0.,0.,0.,1.],[0.,0.,0.,1.]],episode=4)
        rows.append(dict(control=i+1,age_for_action=[i],physics_dt_s=.0025,control_dt_s=.01,
            actual_phase_record=dict(control=i+1,age_for_action=i,public_request_for_action=request,
                both_supported=True,airborne_both_above5mm_and_unloaded=False),
            task_relative_features7_for_action=[0.]*5+[float(request),i*.01],
            actor_obs86_for_action=[0.]*84+[float(request),0.],actual_original_done=i==n-1,
            packed_frame_for_action=i,packed127_for_action=packed.copy(),terminal_packed127_same_point=packed.copy(),
            xi31_for_action=[0.]*31,env_origin3_world=[0.]*3,
            terminal_pre_reset=dict(state=state,termination_terms=dict(values=dict(closure=i==n-1))),
            frozen_WM_one_step=dict(predicted_root_z=0.)))
    data=decode_records(rows,n,body_count=2)
    negatives=0
    for mutate in [lambda x:x[13].update(age_for_action=[999]),
                   lambda x:x[13].update(packed_frame_for_action=999),
                   lambda x:x[13]['xi31_for_action'].__setitem__(0,1.),
                   lambda x:x[13]['terminal_pre_reset']['state']['executed6'].__setitem__(0,float('nan')),
                   lambda x:x[13].update(actual_original_done=True),
                   lambda x:x[200]['task_relative_features7_for_action'].__setitem__(5,0.)]:
        bad=copy.deepcopy(rows);mutate(bad)
        try:decode_records(bad,n,body_count=2)
        except ValueError:negatives+=1
        else:raise AssertionError('negative typed fixture accepted')
    assert negatives==6
    done=torch.zeros(n,dtype=torch.bool);done[20]=True
    assert all(not (i<=20<i+7) for i in valid_starts(data['frames'],done,data['episode'],8))
    frames=data['frames'].clone();frames[30]+=2
    assert len(valid_starts(frames,data['done'],data['episode'],8)) < n-7

    def unpack(x):
        return x[:,:3],torch.eye(3).expand(len(x),3,3),x[:,7:10],x[:,10:13],x[:,13:43],x[:,43:73],x[:,73:]
    class WM:
        def step(self,state,action,context):
            q=state[4].clone();q[:,0]+=action[:,0]
            return *state[:4],q,*state[5:]
    def geometry(state):
        p=torch.zeros(len(state[0]),2,3);p[:,1,0]=state[4][:,0]
        return dict(body_position=p,body_rotation=torch.eye(3).expand(len(p),2,3,3))
    closure=(ids0,ids1,torch.zeros(1,3),torch.zeros(1,3))
    a=evaluate(WM(),unpack,lambda x:x,geometry,closure,data,8,lambda:None)
    changed=dict(data);changed['t']=data['t'].clone();changed['t'][:,13]=100.
    b=evaluate(WM(),unpack,lambda x:x,geometry,closure,changed,8,lambda:None)
    assert all(abs(x['steps'][-1]['predicted_max_closure_m']-.008)<1e-8 for x in a)
    assert [x['steps'] for x in a]==[x['steps'] for x in b], 'future truth entered prediction'
    assert any(x['any_predicted_stop_on_cached_nonclosure_step'] for x in a)
    assert torch.equal(rng,torch.random.get_rng_state()) and not torch.cuda.is_initialized()
    report=dict(epoch=time.time(),passed_source_CPU_only=True,negative_typed_checks=negatives,
        exact_original_threshold_and_grace_boundary=True,xyzw_rotation_and_anchor_translation_checked=True,
        actual_action_sequence_linear_closed_form_checked=True,future_truth_injection_negative_checked=True,
        done_frame_episode_and_request_domains_checked=True,torch_version=str(torch.__version__),
        checkpoint_raw_NPZ_model_GPU_SDK_physics_reads=0,RNG_unchanged=True,
        scope='Synthetic necessary source admission only; not actual121 numerical result or physical validity.')
    out.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    main()
