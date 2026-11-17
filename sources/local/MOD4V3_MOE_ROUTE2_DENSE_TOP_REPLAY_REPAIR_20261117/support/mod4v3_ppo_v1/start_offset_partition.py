"""Balance five offsets separately inside the unchanged native DR groups."""
import torch
OFFSETS_MM=(-60,-30,0,30,60)
def assign_offset_indices(stair_mask,nominal_mask):
    out=torch.zeros_like(stair_mask,dtype=torch.long)
    for nominal in (False,True):
        ids=(stair_mask & (nominal_mask==nominal)).nonzero().flatten()
        out[ids]=torch.arange(len(ids),device=ids.device)%5
    return out
def population_by_dr_offset(environment_ids,nominal_mask,assigned):
    return (nominal_mask[environment_ids].long()*5+assigned[environment_ids]).bincount(minlength=10).reshape(2,5)
