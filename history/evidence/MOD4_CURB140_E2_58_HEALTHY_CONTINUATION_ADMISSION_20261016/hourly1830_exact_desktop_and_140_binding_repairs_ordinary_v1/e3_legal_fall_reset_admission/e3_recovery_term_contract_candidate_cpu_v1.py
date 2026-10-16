"""Isolated CPU contract candidate, not installed runtime or learning approval."""
import torch
SOFT_TASK_TERMS=('bad_orientation','base_contact')
def task_terms(original,public_rescue,age_controls,grace_controls=300):
 assert set(SOFT_TASK_TERMS).issubset(original) and public_rescue.dtype==torch.bool and age_controls.dtype==torch.int64 and grace_controls>0
 assert public_rescue.shape==age_controls.shape and (age_controls>=0).all()
 active=public_rescue & (age_controls<grace_controls);out={}
 for name,value in original.items():
  assert value.dtype==torch.bool and value.shape==active.shape
  out[name]=value & ~active if name in SOFT_TASK_TERMS else value.clone()
 return out
def bounded_upright_candidate(previous_peak,projected_gravity_z,public_rescue):
 assert previous_peak.shape==projected_gravity_z.shape==public_rescue.shape and public_rescue.dtype==torch.bool
 assert torch.isfinite(previous_peak).all() and torch.isfinite(projected_gravity_z).all() and ((previous_peak>=0)&(previous_peak<=1)).all() and (projected_gravity_z.abs()<=1.00001).all()
 # Unit-free candidate only. No coefficient or actual RewardManager is released.
 upright=((1-projected_gravity_z)/2).clamp(0,1);now=torch.where(public_rescue,torch.maximum(previous_peak,upright),previous_peak);return now,now-previous_peak
