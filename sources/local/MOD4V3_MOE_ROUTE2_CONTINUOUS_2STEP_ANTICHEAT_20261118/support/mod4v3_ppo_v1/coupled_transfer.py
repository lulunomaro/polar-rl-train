"""Finite per-wheel credit for real rear/up movement and subsequent placement."""
import torch

def transfer_scores(longitudinal,wheel_z,stage,inward,cleared):
 lower=stage[:,None]*.2
 lift=((wheel_z-.0625-lower-.005)/.210).clamp(0.,1.)
 rear=(-longitudinal/.20).clamp(0.,1.)
 rear_up=torch.sqrt(rear*lift)
 upper_clearance=wheel_z-.0625-(lower+.2)
 placement=((inward-.02)/.15).clamp(0.,1.)
 placement=placement*cleared*(upper_clearance>=-.01)
 return torch.stack((rear_up,placement),dim=-1),lift

def transfer_credit(current,best,enabled):
 on=enabled[:,None,None]
 gain=(current-best).clamp_min(0.)*on
 updated=torch.where(on,torch.maximum(best,current),best)
 weighted=.8*gain[:,:,0]+.2*gain[:,:,1]
 return weighted.mean(1),updated

def lift_regression(lift,best_lift,enabled):
 return ((best_lift-lift-.05).clamp(0.,1.)).mean(1)*enabled
