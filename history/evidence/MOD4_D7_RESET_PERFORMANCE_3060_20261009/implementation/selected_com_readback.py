"""Isolated candidate: share COM reads and limit quaternion arithmetic to written rows.

Full backend/buffer/expected-pose checks remain at every reset and boundary.
No source in the active training checkout is changed.
"""
import torch
from chassis_com_pose_roundtrip_sdk_adapter import ChassisCOMSDK as OriginalCOM
from chassis_com_pose_roundtrip_sdk_adapter import tensor,transform_array,verify_rotation_preserved

class SelectedCOMSDK(OriginalCOM):
    def reset(self,ids):
        ids=torch.as_tensor(ids,device=self.env.device,dtype=torch.long)
        if not len(ids):return
        current=tensor(self.robot.root_view.get_coms()).to(self.env.device)
        other=[i for i in range(current.shape[1]) if i!=self.body_id]
        assert torch.equal(current[:,other,:3],self.original_pose[:,other,:3])
        self.orientation_after_parent_reset[ids]=current[ids,...,3:]
        self.component.reset(ids)
        self.apply(ids,_current=current)
        self.reset_calls+=1

    def apply(self,ids,_current=None):
        expected=self.expected_full_pose()
        current=tensor(self.robot.root_view.get_coms()).to(expected.device) if _current is None else _current
        # Preserve the installed SDK's full-row cache refresh before partial setter.
        self.robot.data._body_com_pose_b.timestamp=-float('inf')
        refreshed=tensor(self.robot.data.body_com_pose_b).to(expected.device)
        assert torch.equal(current,refreshed),'Current full backend/buffer mismatch'
        assert torch.equal(current[...,3:],self.orientation_after_parent_reset)
        if self.component.enabled:
            before=current[ids,...,3:].clone()
            self.robot.set_coms_index(coms=transform_array(expected[ids][:,[self.body_id],:].contiguous()),
                body_ids=[self.body_id],env_ids=ids,full_data=False)
            after=tensor(self.robot.root_view.get_coms()).to(expected.device).clone()
            proof=verify_rotation_preserved(before,after[ids,...,3:])
            self.orientation_roundtrip_max=max(self.orientation_roundtrip_max,proof['normalized_double_quaternion_max_component_delta'])
            self.raw_quaternion_bytes_always_exact &= proof['raw_quaternion_bytes_exact']
            self.orientation_after_parent_reset[ids]=after[ids,...,3:]
            expected[...,3:]=self.orientation_after_parent_reset
            self.robot.data._body_com_pose_b.timestamp=-float('inf')
            buffered=tensor(self.robot.data.body_com_pose_b).to(expected.device)
            self.setter_calls+=1;self.invalidate_COM_dependent_cache()
        else:
            after=current;buffered=refreshed
        # All rows, including unselected rows, must still equal the independently
        # constructed expected value. No unchanged-row corruption is exempted.
        self.audit_parameters(_actual=after,_expected=expected,_buffered=buffered)

    def audit_parameters(self,_actual=None,_expected=None,_buffered=None):
        expected=self.expected_full_pose() if _expected is None else _expected
        actual=tensor(self.robot.root_view.get_coms()).to(expected.device) if _actual is None else _actual
        buffered=tensor(self.robot.data.body_com_pose_b).to(expected.device) if _buffered is None else _buffered
        assert torch.equal(actual,expected) and torch.equal(buffered,expected)
        assert torch.equal(actual[...,3:],self.orientation_after_parent_reset)
        other=[i for i in range(expected.shape[1]) if i!=self.body_id]
        assert torch.equal(actual[:,other,:3],self.original_pose[:,other,:3])
        return actual
