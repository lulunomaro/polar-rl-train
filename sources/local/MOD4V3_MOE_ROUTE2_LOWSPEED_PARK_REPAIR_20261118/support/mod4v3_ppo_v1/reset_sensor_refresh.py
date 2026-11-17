"""Refresh derived E1 reset sensors after SDK root writes, preserving other rows exactly."""
import torch
from .scut_flat_env import tensor

def refresh_reset_sensors(env,ids):
    raw=env.robot.data
    keep=torch.ones(env.num_envs,dtype=torch.bool,device=env.device);keep[ids]=False
    stats=getattr(env,'reset_sensor_cache_stats',dict(calls=0,max_gravity_change=0.,max_body_velocity_change=0.,nonreset_rows_max_change=0.))
    for prop in ['projected_gravity_b','root_link_lin_vel_b','root_link_ang_vel_b','root_com_lin_vel_b','root_com_ang_vel_b']:
        old=tensor(getattr(raw,prop)).clone()
        buffer=getattr(raw,'_'+prop)
        buffer.timestamp=-1.
        updated=tensor(getattr(raw,prop))
        delta=float((updated[ids]-old[ids]).abs().max())if len(ids)else 0.
        updated[keep]=old[keep]
        unchanged=float((updated[keep]-old[keep]).abs().max())if bool(keep.any())else 0.
        assert unchanged==0.
        stats['nonreset_rows_max_change']=max(stats['nonreset_rows_max_change'],unchanged)
        key='max_gravity_change'if prop=='projected_gravity_b'else'max_body_velocity_change'
        stats[key]=max(stats[key],delta)
    stats['calls']+=1;env.reset_sensor_cache_stats=stats
    env._sensor_pending[ids]=True;env._execution_pending[ids]=True
