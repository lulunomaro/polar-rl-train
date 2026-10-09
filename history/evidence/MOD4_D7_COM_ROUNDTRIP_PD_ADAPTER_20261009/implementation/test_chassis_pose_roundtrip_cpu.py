"""CPU fake-backend tests verify selection/audit boundaries; real SDK still required."""
from types import SimpleNamespace
import torch
import chassis_com_pose_roundtrip_sdk_adapter as module
from chassis_com_pose_roundtrip_sdk_adapter import ChassisCOMSDK
module.transform_array=lambda x:x
def fixture():
    n,b=10,5;pose=torch.zeros(n,b,7);pose[...,6]=1;pose[:,3,0]=.01
    class Data:
        def __init__(self):
            self._body_com_pose_b=SimpleNamespace(data=pose.clone(),timestamp=5.)
        @property
        def body_com_pose_b(self):
            if self._body_com_pose_b.timestamp<5.:
                self._body_com_pose_b.data.copy_(pose);self._body_com_pose_b.timestamp=5.
            return self._body_com_pose_b.data
    data=Data()
    for k in ('_body_com_pose_w','_root_com_pose_w','_body_link_vel_w','_root_link_vel_w','_root_link_lin_vel_b','_root_link_ang_vel_b'):setattr(data,k,SimpleNamespace(timestamp=5))
    view=SimpleNamespace(get_coms=lambda:pose.clone(),get_masses=lambda:torch.tensor([[1.,1.,1.,3.,1.]]).repeat(n,1))
    r=SimpleNamespace(pose=pose,body_names=['b0','b1','b2','chassis','b4'],data=data,root_view=view,writes=[])
    def setter(**kw):
        ids=kw['env_ids'];bid=kw['body_ids'];p=kw['coms'];assert bid==[3] and not kw['full_data'] and p.shape==(len(ids),1,7)
        # Mirror installed setter: update cached selected body, send FULL selected row.
        data._body_com_pose_b.data[ids[:,None],torch.tensor(bid)[None,:]]=p
        pose[ids]=data._body_com_pose_b.data[ids];r.writes.append((ids.clone(),p.clone()))
    r.set_coms_index=setter
    mild=SimpleNamespace(com=data.body_com_pose_b[...,:3].clone())
    def audit():
        assert torch.equal(mild.com,data.body_com_pose_b[...,:3]);return dict(actual_parameters_pass=True)
    mild.audit=audit
    env=SimpleNamespace(scene={'robot':r},num_envs=n,device='cpu',_mild_dr=mild,parent_resets=[])
    env._reset_idx=lambda ids:env.parent_resets.append(ids.clone())
    return env,r
def test_contracts():
    passed=[];env,r=fixture();old=env._mild_dr.com;global_rng=torch.get_rng_state().clone()
    a=ChassisCOMSDK(env,True,9);assert a.body_id==3 and a.setter_calls==1;passed.append('actual_named_body_selection_partial_setter_shape')
    initial=a.state_dict();original=a.original_pose
    assert torch.equal(r.data.body_com_pose_b[...,3:],original[...,3:]);passed.append('orientation_exact')
    otherbody=torch.tensor([0,1,2,4]);assert torch.equal(r.data.body_com_pose_b[:,otherbody],original[:,otherbody]);passed.append('other_body_COM_exact')
    ids=torch.tensor([1,4,7]);other=torch.tensor([0,2,3,5,6,8,9]);oldpose=r.data.body_com_pose_b.clone();env._reset_idx(ids)
    assert len(env.parent_resets)==1 and torch.equal(a.component.episode[ids],initial['episode'][ids]+1);passed.append('parent_reset_then_selected_episode_once')
    assert torch.equal(r.data.body_com_pose_b[other],oldpose[other]);passed.append('other_env_COM_exact')
    assert env._mild_dr.audit()['actual_parameters_pass'] and env._mild_dr.com is old;passed.append('independent_expected_audit_finally_original_reference')
    altered=r.data.body_com_pose_b[0,0,0].clone();r.data.body_com_pose_b[0,0,0]=99
    try:a.audit_parameters()
    except AssertionError:pass
    else:raise AssertionError('Wrong buffer was not rejected')
    r.data.body_com_pose_b[0,0,0]=altered;passed.append('wrong_buffer_rejected')
    r.pose[ids,:,3:]=torch.tensor([0.,1.,0.,0.])
    assert not torch.equal(r.data._body_com_pose_b.data,r.pose)
    passed.append('same_tick_parent_orientation_changes_leave_stale_full_row_cache')
    env._reset_idx(ids)
    assert torch.equal(r.root_view.get_coms()[ids,...,3:],torch.tensor([0.,1.,0.,0.]).expand(3,5,4))
    a.audit_parameters();passed.append('same_tick_refresh_prevents_full_row_orientation_clobber')
    state=a.state_dict();a.component.delta_m.zero_();a.load_state_dict(state);assert torch.equal(a.component.delta_m,state['delta_m']);a.audit_parameters();passed.append('state_restore_applies_exact_backend_buffer')
    assert all(getattr(r.data,k).timestamp<0 for k in ('_root_com_pose_w','_body_com_pose_w','_root_link_vel_w'));passed.append('COM_dependent_cache_invalidation')
    assert torch.equal(global_rng,torch.get_rng_state());passed.append('global_RNG_unchanged')
    e2,r2=fixture();off=ChassisCOMSDK(e2,False,9);assert off.setter_calls==0 and r2.writes==[];passed.append('off_no_parameter_writes')
    assert not torch.cuda.is_initialized();passed.append('CPU_only_not_SDK_or_GPU_proof')
    from chassis_com_pose_roundtrip_sdk_adapter import verify_rotation_preserved
    q=torch.tensor([[.035981763154268265,.32348647713661194,.10452976077795029,.9397527575492859]])
    after=torch.tensor([[.03598176687955856,.3234865069389343,.10452977567911148,.9397528767585754]])
    p=verify_rotation_preserved(q,after);assert not p['raw_quaternion_bytes_exact'];passed.append('measured_PhysX_float32_normalization_geometric_equivalence')
    assert verify_rotation_preserved(q,-q)['rotation_preserved_within_dtype_roundtrip'];passed.append('quaternion_sign_equivalent_rotation')
    bad=q.clone();bad[0,0]+=.001
    try:verify_rotation_preserved(q,bad/bad.norm(dim=-1,keepdim=True))
    except AssertionError:pass
    else:raise AssertionError('Physical orientation change was accepted')
    passed.append('actual_orientation_change_rejected')
    try:verify_rotation_preserved(q,q*1.001)
    except AssertionError:pass
    else:raise AssertionError('Nonunit quaternion accepted')
    passed.append('nonunit_parameter_change_rejected')
    try:verify_rotation_preserved(q,q*float('nan'))
    except AssertionError:pass
    else:raise AssertionError('Nonfinite orientation accepted')
    passed.append('nonfinite_orientation_rejected')
    return passed
if __name__=='__main__':
    import json
    print(json.dumps(dict(passed=test_contracts(),torch_version=torch.__version__,CUDA_initialized=torch.cuda.is_initialized(),actual_SDK=False)))
