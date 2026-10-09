"""Meaningful reset/corruption equivalence tests; CPU fixture is not SDK evidence."""
from pathlib import Path
import sys,copy,json,torch
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D/'baseline'))
sys.path.insert(0,str(D.parent/'MOD4_D7_COM_PD_PREPARE_20261009'))
import chassis_com_pose_roundtrip_sdk_adapter as old
import selected_com_readback as new
from test_chassis_pose_roundtrip_cpu import fixture
old.transform_array=new.transform_array=lambda x:x

def main():
    passed=[]
    for enabled in (False,True):
        aenv,ar=fixture();benv,br=fixture()
        a=old.ChassisCOMSDK(aenv,enabled,913);b=new.SelectedCOMSDK(benv,enabled,913)
        for ids in (torch.tensor([1,4,7]),torch.tensor([0]),torch.arange(10),torch.tensor([],dtype=torch.long)):
            # Model real same-tick parent D0 orientation changes with stale cache.
            ar.pose[ids,:,3:]=br.pose[ids,:,3:]=torch.tensor([0.,1.,0.,0.])
            aenv._reset_idx(ids);benv._reset_idx(ids)
            assert torch.equal(ar.pose,br.pose)
            assert torch.equal(a.component.delta_m,b.component.delta_m)
            assert torch.equal(a.component.episode,b.component.episode)
            assert all(torch.equal(x,y) for x,y in zip(a.state_dict()['private_xyz_RNG'],b.state_dict()['private_xyz_RNG']))
            a.audit_parameters();b.audit_parameters()
        passed.append('off_on_single_subset_all_empty_reset_exact_with_stale_D0_orientation_'+str(enabled))
        state=b.state_dict();b.component.delta_m.zero_();b.load_state_dict(state);b.audit_parameters()
        assert torch.equal(b.component.delta_m,state['delta_m']);passed.append('state_restore_applies_exact_'+str(enabled))
    for where in ('backend_translation','buffer_translation','unselected_rotation','nonfinite_backend'):
        env,r=fixture();b=new.SelectedCOMSDK(env,True,9)
        if where=='backend_translation':r.pose[0,0,0]=99
        elif where=='buffer_translation':r.data._body_com_pose_b.data[0,0,0]=99
        elif where=='unselected_rotation':r.pose[0,:,3:]=torch.tensor([0.,1.,0.,0.])
        else:r.pose[0,0,0]=float('nan')
        try:
            if where=='buffer_translation':b.audit_parameters()
            else:env._reset_idx(torch.tensor([1,4,7]))
        except AssertionError:passed.append(where+'_still_rejected')
        else:raise AssertionError('Corruption silently accepted: '+where)
    # Setter corruption in an unselected row must be rejected even though only
    # selected rotations undergo the expensive normalized-double calculation.
    env,r=fixture();b=new.SelectedCOMSDK(env,True,9);setter=r.set_coms_index
    def corrupt(**kw):
        setter(**kw);r.pose[0,:,3:]=torch.tensor([0.,1.,0.,0.])
    r.set_coms_index=corrupt
    try:env._reset_idx(torch.tensor([1,4,7]))
    except AssertionError:passed.append('unselected_setter_corruption_still_rejected')
    else:raise AssertionError('Unselected setter corruption accepted')
    assert not torch.cuda.is_initialized()
    return dict(passed=passed,CUDA_initialized=False,not_actual_SDK=True,unchanged_full_row_fault_detection=True)
if __name__=='__main__':print(json.dumps(main()))
