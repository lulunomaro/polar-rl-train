"""Finite, independent rearward and upward progress; no credit for revisiting a pose."""
import torch

def scores(longitudinal,clearance):
 return torch.stack(((-longitudinal/.24).clamp(0,1).mean(1),((clearance+.2)/.215).clamp(0,1).mean(1)),dim=1)

def credit(current,best,active):
 gain=(current-best).clamp_min(0)*active[:,None]
 return gain,torch.where(active[:,None],torch.maximum(best,current),best)
