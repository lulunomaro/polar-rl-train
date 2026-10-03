"""Read-only point-velocity reference and finite-width shadow diagnostics.

Every quantity is control-rate input-mesh geometry, NOT a PhysX contact manifold.
Original reward, original slip, and original admission gates stay untouched.
"""
import numpy as np
import torch
from isaaclab.utils.math import quat_apply


def tensor(value):
    return value.torch if hasattr(value, 'torch') else value


class SlipShadow:
    def __init__(self, env, geometry):
        self.env=env;self.geometry=geometry;self.robot=env.scene['robot']
        self.ids=geometry.ids;self.points=geometry.vertices[0]
        centers=[];axes=[];meta=[]
        for points in self.points:
            p=points.cpu().numpy();center=p.mean(0)
            eig,vec=np.linalg.eigh(np.cov((p-center).T))
            axis=vec[:,0];axial=(p-center)@axis
            centers.append(center);axes.append(axis)
            meta.append(dict(vertex_count=len(p),mesh_center_body_m=center.tolist(),axle_pca_unit_body=axis.tolist(),covariance_eigenvalues=eig.tolist(),axial_extent_m=[float(axial.min()),float(axial.max())],half_width_m=float((axial.max()-axial.min())/2)))
        self.centers=torch.tensor(np.array(centers),device=env.device,dtype=self.points.dtype)[None]
        self.axes=torch.tensor(np.array(axes),device=env.device,dtype=self.points.dtype)[None]
        self.meta=meta;self.sums={};self.loaded_sums={};self.counts=torch.zeros((env.num_envs,2),device=env.device)
        self.loaded_counts=self.counts.clone();self.peaks={};self.traces=[];self.trace_ids=None
        self.com_body=tensor(self.robot.data.body_com_pos_b)[:,self.ids].clone()

    def read(self, old_slip, force, mask, step):
        r=self.robot;n=self.env.num_envs;m=self.points.shape[1]
        q=tensor(r.data.body_quat_w)[:,self.ids]
        points=self.geometry.vertices
        rotated=quat_apply(q[:,:,None,:].expand(-1,-1,m,-1).reshape(-1,4),points.reshape(-1,3)).reshape(n,2,m,3)
        low=rotated[:,:,:,2].argmin(2)
        support=rotated.gather(2,low[:,:,None,None].expand(-1,-1,1,3)).squeeze(2)
        local=points.gather(2,low[:,:,None,None].expand(-1,-1,1,3)).squeeze(2)
        w=tensor(r.data.body_ang_vel_w)[:,self.ids]
        legacy_v=tensor(r.data.body_lin_vel_w)[:,self.ids]+torch.cross(w,support,dim=-1)
        link_v=tensor(r.data.body_link_lin_vel_w)[:,self.ids]+torch.cross(w,support,dim=-1)
        point_w=tensor(r.data.body_link_pos_w)[:,self.ids]+support
        com_v=tensor(r.data.body_com_lin_vel_w)[:,self.ids]+torch.cross(w,point_w-tensor(r.data.body_com_pos_w)[:,self.ids],dim=-1)
        com_arm=quat_apply(q.reshape(-1,4),self.com_body.reshape(-1,3)).reshape(n,2,3)
        # Second COM-correct implementation avoids world-position subtraction cancellation.
        com_v_local=tensor(r.data.body_com_lin_vel_w)[:,self.ids]+torch.cross(w,support-com_arm,dim=-1)
        assert (link_v[:,:,:2].norm(dim=-1)-old_slip).abs().max()<=1e-6,'Shadow input must reproduce corrected link reference'
        axis_w=quat_apply(q.reshape(-1,4),self.axes.expand(n,-1,-1).reshape(-1,3)).reshape(n,2,3)
        axial=((local-self.centers)*self.axes).sum(-1)
        center_support=support-axial[:,:,None]*axis_w
        middle_v=tensor(r.data.body_link_lin_vel_w)[:,self.ids]+torch.cross(w,center_support,dim=-1)
        up=torch.zeros_like(axis_w);up[:,:,2]=1
        roll=torch.cross(axis_w,up,dim=-1);roll=roll/roll.norm(dim=-1,keepdim=True).clamp_min(1e-8)
        lateral=axis_w.clone();lateral[:,:,2]=0;lateral=lateral/lateral.norm(dim=-1,keepdim=True).clamp_min(1e-8)
        yaw_w=w.clone();yaw_w[:,:,:2]=0
        yaw_scrub=torch.cross(yaw_w,axial[:,:,None]*axis_w,dim=-1)
        values=dict(legacy_slip=legacy_v[:,:,:2].norm(dim=-1),input_mesh_slip=old_slip,link_reference_slip=link_v[:,:,:2].norm(dim=-1),com_reference_slip=com_v_local[:,:,:2].norm(dim=-1),mesh_midplane_slip=middle_v[:,:,:2].norm(dim=-1),velocity_reference_error=(legacy_v-link_v).norm(dim=-1),link_vs_com_local_error=(link_v-com_v_local).norm(dim=-1),link_vs_com_world_error=(link_v-com_v).norm(dim=-1),selected_axial_offset_m=axial.abs(),yaw_edge_speed=yaw_scrub[:,:,:2].norm(dim=-1),rolling_abs_speed=(link_v*roll).sum(-1).abs(),axial_abs_speed=(link_v*lateral).sum(-1).abs())
        valid=mask[:,None].expand(-1,2);loaded=valid & (force>=10.)
        self.counts+=valid;self.loaded_counts+=loaded
        for name,value in values.items():
            if name not in self.sums:self.sums[name]=torch.zeros_like(value);self.loaded_sums[name]=torch.zeros_like(value);self.peaks[name]=torch.zeros_like(value)
            self.sums[name]+=value*valid;self.loaded_sums[name]+=value*loaded
            self.peaks[name]=torch.maximum(self.peaks[name],torch.where(valid,value,0))
        ids=self.trace_ids
        if ids is not None:
            packed=torch.cat([legacy_v,link_v,com_v_local,middle_v,w,support,local,axis_w,yaw_scrub,force[:,:,None],low[:,:,None].float(),valid[:,:,None].float()],dim=-1)[ids]
            self.traces.append(packed.cpu().numpy())

    def result(self, trace_path):
        columns=['legacy_vx','legacy_vy','legacy_vz','link_vx','link_vy','link_vz','com_vx','com_vy','com_vz','midplane_vx','midplane_vy','midplane_vz','angular_wx','angular_wy','angular_wz','support_world_dx','support_world_dy','support_world_dz','support_body_x','support_body_y','support_body_z','axle_wx','axle_wy','axle_wz','yaw_edge_vx','yaw_edge_vy','yaw_edge_vz','force_mean_control_N','support_vertex_id','valid_mask']
        np.savez_compressed(trace_path,trace=np.stack(self.traces),environment_ids=self.trace_ids.cpu().numpy(),columns=np.array(columns),step_dt=np.array(self.env.step_dt),wheel_com_body_m=self.com_body.cpu().numpy())
        return dict(version='corrected_input_legacy_shadow_v2',metadata=self.meta,wheel_com_body_m=self.com_body.cpu().tolist(),per_environment_mean={k:(v/self.counts.clamp_min(1)).cpu().tolist() for k,v in self.sums.items()},per_environment_loaded_mean={k:(v/self.loaded_counts.clamp_min(1)).cpu().tolist() for k,v in self.loaded_sums.items()},per_environment_max={k:v.cpu().tolist() for k,v in self.peaks.items()},loaded_fraction=(self.loaded_counts/self.counts.clamp_min(1)).cpu().tolist(),trace_file=str(trace_path),trace_sha256=__import__('hashlib').sha256(__import__('pathlib').Path(trace_path).read_bytes()).hexdigest(),trace_columns=columns,trace_environment_ids=self.trace_ids.cpu().tolist(),original_gate_changed=False,midplane_is_not_contact_manifold=True,loaded_force_threshold_N=10.,control_step_sampling_s=self.env.step_dt)
