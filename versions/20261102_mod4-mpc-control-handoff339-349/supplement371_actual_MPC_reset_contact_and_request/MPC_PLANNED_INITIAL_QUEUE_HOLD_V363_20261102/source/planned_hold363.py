"""Seed only the held target after a caller writes a fresh physical pose.
No reset method, RNG, lag, episode count, control clock or PD is changed.
"""
import torch
def seed_planned_leg_hold(queue,ids,actual_leg_q):
    ids=torch.as_tensor(ids,device=queue.device,dtype=torch.long)
    if not len(ids):return
    g=queue.groups['legs']
    assert actual_leg_q.shape==(len(ids),4)and actual_leg_q.dtype==torch.float32
    assert bool(torch.isfinite(actual_leg_q).all())
    assert not bool(g['pending_valid'][ids].any())and not bool(g['applied_valid'][ids].any())
    assert bool((g['last_submit_tick'][ids]==-1).all())
    g['applied'][ids]=actual_leg_q
    g['pending'][ids]=actual_leg_q
