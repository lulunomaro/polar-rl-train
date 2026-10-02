"""Ray observations for translated copies of ONE static CAD collision mesh.

Import after AppLauncher starts Isaac Sim. Uses Isaac Lab 2.3 public Warp helpers.
This queries terrain only, not robots or dynamic obstacles. World directions
must already include the sensor orientation. No height-field conversion is used.
"""
from pathlib import Path
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1]

class SharedTerrainRaycast:
    def __init__(self, env_origins):
        from isaaclab.utils.warp import convert_to_warp_mesh, raycast_mesh
        self.origins=env_origins
        self.device=env_origins.device
        with np.load(ROOT/'data/arena_collision.npz') as data:
            self.mesh=convert_to_warp_mesh(data['vertices'],data['faces'],device=str(self.device))
        self._raycast=raycast_mesh

    def cast(self, starts_w, directions_w, max_distance=10., env_ids=None):
        """Input [N, rays, 3], unit directions; output world hits and hit mask.

        N equals all environments or len(env_ids). Misses have infinite distance
        and coordinates: mask them BEFORE constructing policy observations.
        Directions are unchanged because every arena is translated, not rotated.
        Use upward/forward rays as well as downward ones to observe tunnel roofs.
        """
        origins=self.origins if env_ids is None else self.origins[env_ids]
        if starts_w.ndim!=3 or starts_w.shape[-1]!=3 or directions_w.shape!=starts_w.shape:
            raise ValueError('Ray starts and directions must both have shape [N, rays, 3].')
        if len(starts_w)!=len(origins):raise ValueError('Mismatch between environment IDs and ray batches.')
        if max_distance<=0:raise ValueError('max_distance must be positive.')
        local_starts=(starts_w-origins[:,None,:]).contiguous()
        hits,distance,normal,face_id=self._raycast(
            local_starts,directions_w.contiguous(),self.mesh,max_dist=float(max_distance),
            return_distance=True,return_normal=True,return_face_id=True)
        return dict(hits_w=hits+origins[:,None,:],distance=distance,normal_w=normal,
                    face_id=face_id,hit=torch.isfinite(distance))

def out_of_arena(root_pos_w, env_origins, margin_m=0.):
    """Reset escaped agents before they can enter a neighboring arena.

    Positive margin expands the allowed rectangle; default is inside arena walls.
    Add your existing fall/tip/timeout/contact terminations separately.
    """
    p=root_pos_w-env_origins
    return (p[:,0].abs()>14.50+margin_m)|(p[:,1].abs()>8.00+margin_m)
