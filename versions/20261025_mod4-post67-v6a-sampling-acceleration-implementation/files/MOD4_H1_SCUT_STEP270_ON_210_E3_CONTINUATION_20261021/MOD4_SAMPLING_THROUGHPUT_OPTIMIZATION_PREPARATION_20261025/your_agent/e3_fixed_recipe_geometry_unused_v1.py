"""UNUSED pure tensor geometry cache candidate, with no environment or SDK access.

Build only from the source-identified immutable selected bank points, after the
original pick and joint permutation. No approximation, sampled-point reduction,
new fall pose, physical reset, RNG draw, or CPU/GPU transfer is introduced here.
The active reset recipe list is exactly the existing 12 falls plus recipe 12.
Production adoption additionally needs same-source device validation and an
explicit immutable cache contract; CPU synthetic equality does not provide that.
"""


def original_geometry(torch, points, recipe, *, chunk_size=128):
    """Literal arithmetic extracted from existing place_declared_fall, no SDK."""
    device = points.device
    degrees = torch.tensor([-90., -60., -30., 30., 60., 90.], device=device)
    angle = torch.where(recipe < 12, degrees[recipe.clamp(max=11) % 6], 0.) * torch.pi / 180
    quat = torch.zeros((len(recipe), 4), device=device)
    quat[torch.arange(len(recipe), device=device), torch.where(recipe < 6, 0, 1)] = torch.sin(angle / 2)
    quat[:, 3] = torch.cos(angle / 2)
    minimum = torch.empty(len(recipe), device=device)
    for first in range(0, len(recipe), chunk_size):
        last = min(first + chunk_size, len(recipe))
        v = quat[first:last, None, :3]
        p = points[None].expand(last - first, -1, -1)
        rot = p + 2 * torch.cross(v.expand_as(p), torch.cross(v.expand_as(p), p, dim=-1)
                                  + quat[first:last, None, 3:4] * p, dim=-1)
        minimum[first:last] = rot[:, :, 2].amin(-1)
    return dict(quat=quat, minimum=minimum, initial=(1 + torch.cos(angle)) / 2)


def build_table(torch, points):
    if points.ndim != 2 or points.shape[1] != 3 or points.dtype != torch.float32:
        raise ValueError('Expected the existing float32 selected points_root[P,3]')
    recipe = torch.arange(13, device=points.device)
    return original_geometry(torch, points, recipe)


def lookup_table(torch, table, recipe):
    if recipe.dtype != torch.int64 or not bool(((recipe >= 0) & (recipe <= 12)).all()):
        raise ValueError('Existing recipe identifiers must lie in 0..12')
    return {key: value[recipe] for key, value in table.items()}
