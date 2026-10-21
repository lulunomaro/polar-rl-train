"""Original tensor/proxy readback body, no environment or dynamics imports."""
import torch
def tensor(v):
    if hasattr(v, 'torch'):
        return v.torch
    if torch.is_tensor(v):
        return v
    import warp as wp
    return wp.to_torch(v)
